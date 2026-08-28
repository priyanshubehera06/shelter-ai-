"""
simulation_service.py — Service adapter interfacing with engine.thermal, engine.comfort, engine.energy, engine.cost, and engine.scoring.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from engine.geometry import ShelterGeometry
from engine.climate import get_climate_profile
from engine.thermal import simulate_shelter_thermal_dynamics, compare_thermal_scenarios
from engine.comfort import calculate_pmv_fanger, evaluate_human_comfort
from engine.energy import calculate_annual_energy_loads
from engine.cost import calculate_shelter_cost_and_carbon
from engine.scoring import calculate_mcda_shelter_score
from engine.explainability import generate_design_explanation

from backend.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
    SimulationSummary,
    HourlySimulationRecord,
    WhatIfCompareRequest,
    WhatIfCompareResponse
)


def run_thermal_simulation(req: SimulationRequest) -> SimulationResponse:
    """Executes physics-based transient RC simulation using pure Python engine calculations."""
    geom = ShelterGeometry(
        length_m=req.geometry.length_m,
        width_m=req.geometry.width_m,
        height_m=req.geometry.height_m,
        roof_type=req.geometry.roof_type,
        roof_pitch_deg=req.geometry.roof_pitch_deg,
        wall_thickness_cm=req.geometry.wall_thickness_cm,
        wwr_pct=req.geometry.wwr_pct,
        overhang_m=req.geometry.overhang_m,
        orientation_deg=req.geometry.orientation_deg,
        door_width_m=req.geometry.door_width_m,
        door_height_m=req.geometry.door_height_m,
        door_count=req.geometry.door_count
    )
    
    climate_records = get_climate_profile(month=req.month)
    
    sim_res = simulate_shelter_thermal_dynamics(
        geometry=geom,
        wall_mat_id=req.materials.wall_mat_id,
        wall_thickness_cm=req.materials.wall_thickness_cm,
        roof_mat_id=req.materials.roof_mat_id,
        glazing_mat_id=req.materials.glazing_mat_id,
        insulation_mat_id=req.materials.insulation_mat_id,
        insulation_thickness_cm=req.materials.insulation_thickness_cm,
        climate_records=climate_records,
        occupants=req.occupants
    )
    
    # Calculate comfort across 24 hours
    hourly_records: List[HourlySimulationRecord] = []
    pmv_list = []
    discomfort_hrs = 0
    
    for h in range(24):
        t_in = sim_res["t_indoor"][h]
        t_out = sim_res["t_outdoor"][h]
        t_sa = sim_res["t_sol_air"][h]
        rh = climate_records[h].get("relative_humidity_pct", 50.0)
        
        pmv, ppd = calculate_pmv_fanger(t_in, rh)
        pmv_list.append(pmv)
        is_comf = abs(pmv) <= 0.85
        if not is_comf:
            discomfort_hrs += 1
            
        hourly_records.append(HourlySimulationRecord(
            hour=h,
            t_outdoor=round(t_out, 2),
            t_indoor=round(t_in, 2),
            t_sol_air=round(t_sa, 2),
            q_roof_w=round(sim_res["q_roof"][h], 1),
            q_wall_w=round(sim_res["q_wall"][h], 1),
            q_solar_w=round(sim_res["q_solar"][h], 1),
            q_vent_w=round(sim_res["q_vent"][h], 1),
            q_internal_w=round(sim_res["q_internal"][h], 1),
            pmv=round(pmv, 2),
            ppd_pct=round(ppd, 1),
            is_comfortable=is_comf
        ))
        
    t_in_arr = np.array(sim_res["t_indoor"])
    t_out_arr = np.array(sim_res["t_outdoor"])
    ua_envelope = (
        (geom.gross_wall_area() * sim_res["u_wall"]) +
        (geom.roof_area() * sim_res["u_roof"]) +
        (geom.window_area() * sim_res["u_glazing"])
    )
    
    # Calculate energy loads via engine.energy
    energy_res = calculate_annual_energy_loads(
        t_indoor_hourly=sim_res["t_indoor"],
        floor_area_m2=geom.floor_area(),
        volume_m3=geom.volume(),
        ua_envelope_w_k=ua_envelope
    )
    
    # Calculate cost and carbon via engine.cost
    cost_res = calculate_shelter_cost_and_carbon(
        geometry=geom,
        wall_mat_id=req.materials.wall_mat_id,
        wall_thickness_cm=req.materials.wall_thickness_cm,
        roof_mat_id=req.materials.roof_mat_id,
        glazing_mat_id=req.materials.glazing_mat_id,
        insulation_mat_id=req.materials.insulation_mat_id,
        insulation_thickness_cm=req.materials.insulation_thickness_cm
    )
    
    # Holistic score
    comfort_pct = max(0.0, min(100.0, float(100.0 - (discomfort_hrs / 24.0 * 100.0))))
    resilience_score = max(0.0, min(100.0, float(100.0 - (t_in_arr.max() - 28.0) * 8.0)))
    
    mcda_res = calculate_mcda_shelter_score(
        pmv_score=float(np.mean(pmv_list)),
        comfort_compliance_pct=comfort_pct,
        carbon_intensity_kg_m2=float(cost_res.get("carbon_intensity_kg_m2", 20.0)),
        capex_inr=float(cost_res.get("capex_inr", 75000.0)),
        thermal_mass_kj_m2k=250.0,
        energy_savings_pct=max(0.0, min(100.0, 100.0 - (energy_res["total_annual_energy_kwh"] / 50.0)))
    )
    holistic = mcda_res["overall_score"]
    
    summary = SimulationSummary(
        peak_indoor_temp_c=round(float(t_in_arr.max()), 1),
        avg_indoor_temp_c=round(float(t_in_arr.mean()), 1),
        min_indoor_temp_c=round(float(t_in_arr.min()), 1),
        indoor_temperature_swing_c=round(float(t_in_arr.max() - t_in_arr.min()), 1),
        peak_ambient_temp_c=round(float(t_out_arr.max()), 1),
        thermal_damping_pct=round(float(100.0 * (1.0 - (t_in_arr.max() - t_in_arr.min()) / max(0.1, t_out_arr.max() - t_out_arr.min()))), 1),
        thermal_lag_hours=float(np.argmax(t_in_arr) - np.argmax(t_out_arr)),
        comfort_score=round(comfort_pct, 1),
        avg_pmv=round(float(np.mean(pmv_list)), 2),
        discomfort_hours=discomfort_hrs,
        annual_cooling_kwh=round(energy_res.get("annual_cooling_kwh", 0.0), 0),
        annual_heating_kwh=round(energy_res.get("annual_heating_kwh", 0.0), 0),
        total_annual_energy_kwh=round(energy_res["total_annual_energy_kwh"], 0),
        total_capex_cost_inr=round(float(cost_res.get("capex_inr", 75000.0)), 0),
        embodied_carbon_kgco2e=round(float(cost_res.get("total_embodied_carbon_kgco2", 350.0)), 0),
        resilience_score=round(resilience_score, 1),
        holistic_score=round(holistic, 1)
    )
    
    explanation = (
        f"The selected envelope achieves a peak indoor temperature of {summary.peak_indoor_temp_c}°C "
        f"({summary.peak_ambient_temp_c - summary.peak_indoor_temp_c:+.1f}°C vs ambient). "
        f"Thermal damping of {summary.thermal_damping_pct}% maintains indoor conditions across diurnal cycles."
    )
    
    return SimulationResponse(
        summary=summary,
        hourly_results=hourly_records,
        u_wall=round(sim_res["u_wall"], 3),
        u_roof=round(sim_res["u_roof"], 3),
        u_glazing=round(sim_res["u_glazing"], 3),
        explanation_narrative=explanation
    )


def compare_what_if_scenarios(req: WhatIfCompareRequest) -> WhatIfCompareResponse:
    """Executes side-by-side What-If scenario comparator via engine.thermal."""
    base_req = SimulationRequest(
        location_id=req.location_id,
        month=req.month,
        geometry=req.geometry,
        materials=req.baseline_materials,
        occupants=req.occupants
    )
    mod_req = SimulationRequest(
        location_id=req.location_id,
        month=req.month,
        geometry=req.geometry,
        materials=req.modified_materials,
        occupants=req.occupants
    )
    
    base_res = run_thermal_simulation(base_req)
    mod_res = run_thermal_simulation(mod_req)
    
    peak_drop = base_res.summary.peak_indoor_temp_c - mod_res.summary.peak_indoor_temp_c
    avg_drop = base_res.summary.avg_indoor_temp_c - mod_res.summary.avg_indoor_temp_c
    disc_reduced = base_res.summary.discomfort_hours - mod_res.summary.discomfort_hours
    
    statement = (
        f"Modified configuration reduces peak indoor temperature by {peak_drop:+.1f}°C "
        f"and avoids {max(0, disc_reduced)} hours of severe thermal discomfort per day."
    )
    
    return WhatIfCompareResponse(
        peak_temperature_drop_c=round(peak_drop, 2),
        avg_temperature_drop_c=round(avg_drop, 2),
        discomfort_hours_reduced=disc_reduced,
        summary_statement=statement,
        baseline_hourly=base_res.hourly_results,
        modified_hourly=mod_res.hourly_results,
        baseline_summary=base_res.summary,
        modified_summary=mod_res.summary
    )
