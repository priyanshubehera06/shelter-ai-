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
    
    if req.custom_climate_records and len(req.custom_climate_records) >= 24:
        climate_records = req.custom_climate_records
    else:
        loc_id = req.location_id or "leh_ladakh"
        climate_records = get_climate_profile(loc_id, month=req.month)
    
    sim_res = simulate_shelter_thermal_dynamics(
        geometry=geom,
        wall_mat_id=req.materials.wall_mat_id,
        wall_thickness_cm=req.materials.wall_thickness_cm,
        roof_mat_id=req.materials.roof_mat_id,
        glazing_mat_id=req.materials.glazing_mat_id,
        floor_mat_id=req.materials.floor_mat_id or "floor_concrete_screed",
        door_mat_id=req.materials.door_mat_id or "door_solid_timber",
        insulation_mat_id=req.materials.insulation_mat_id,
        insulation_thickness_cm=req.materials.insulation_thickness_cm,
        climate_records=climate_records,
        ach=2.0,
        occupants=req.occupants,
        thermal_mass_level=req.thermal_mass_level or "medium"
    )
    
    # Calculate comfort across 24 hours
    hourly_records: List[HourlySimulationRecord] = []
    pmv_list = []
    discomfort_hrs = 0
    
    for h in range(24):
        t_in = sim_res["t_indoor"][h]
        t_out = sim_res["t_outdoor"][h]
        t_sa = sim_res["t_sol_air_wall"][h] if "t_sol_air_wall" in sim_res else sim_res.get("t_sol_air", [0]*24)[h]
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
            t_mass=round(sim_res.get("t_mass", [t_in]*24)[h], 2),
            q_roof_w=round(sim_res.get("q_roof_watts", sim_res.get("q_roof", [0]*24))[h], 1),
            q_wall_w=round(sim_res.get("q_wall_watts", sim_res.get("q_wall", [0]*24))[h], 1),
            q_floor_w=round(sim_res.get("q_floor_watts", [0]*24)[h], 1),
            q_window_w=round(sim_res.get("q_window_watts", [0]*24)[h], 1),
            q_door_w=round(sim_res.get("q_door_watts", [0]*24)[h], 1),
            q_solar_w=round(sim_res.get("q_solar_watts", sim_res.get("q_solar", [0]*24))[h], 1),
            q_vent_w=round(sim_res.get("q_vent_watts", sim_res.get("q_vent", [0]*24))[h], 1),
            q_mass_w=round(sim_res.get("q_mass_watts", [0]*24)[h], 1),
            q_internal_w=round(sim_res.get("q_internal_watts", sim_res.get("q_internal", [0]*24))[h], 1),
            net_heat_flow_w=round(sim_res.get("net_heat_flow_watts", [0]*24)[h], 1),
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
    
    comfort_pct = max(0.0, min(100.0, float(100.0 - (discomfort_hrs / 24.0 * 100.0))))
    resilience_score = max(0.0, min(100.0, float(100.0 - abs(t_in_arr.mean() - 20.0) * 4.0)))
    
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
        daytime_avg_indoor_temp_c=round(sim_res.get("daytime_avg_indoor_temp_c", float(t_in_arr.mean())), 1),
        nighttime_avg_indoor_temp_c=round(sim_res.get("nighttime_avg_indoor_temp_c", float(t_in_arr.mean())), 1),
        nighttime_min_indoor_temp_c=round(sim_res.get("nighttime_min_indoor_temp_c", float(t_in_arr.min())), 1),
        sunset_temp_drop_c=round(sim_res.get("sunset_temp_drop_c", 4.5), 1),
        indoor_temperature_swing_c=round(float(t_in_arr.max() - t_in_arr.min()), 1),
        peak_ambient_temp_c=round(float(t_out_arr.max()), 1),
        thermal_damping_pct=round(float(100.0 * (1.0 - (t_in_arr.max() - t_in_arr.min()) / max(0.1, t_out_arr.max() - t_out_arr.min()))), 1),
        thermal_lag_hours=float(np.argmax(t_in_arr) - np.argmax(t_out_arr)),
        total_daily_solar_captured_kwh=round(sim_res.get("total_daily_solar_captured_kwh", 15.0), 1),
        total_daily_heat_loss_kwh=round(sim_res.get("total_daily_heat_loss_kwh", 12.0), 1),
        net_thermal_balance_kwh=round(sim_res.get("net_thermal_balance_kwh", 3.0), 1),
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
        f"The selected envelope achieves a daytime indoor average of {summary.daytime_avg_indoor_temp_c}°C "
        f"and retains a nighttime minimum of {summary.nighttime_min_indoor_temp_c}°C with {summary.thermal_damping_pct}% thermal damping. "
        f"Captures {summary.total_daily_solar_captured_kwh} kWh/day of solar energy to offset nighttime losses."
    )
    
    return SimulationResponse(
        summary=summary,
        hourly_results=hourly_records,
        u_wall=round(sim_res["u_wall"], 3),
        u_roof=round(sim_res["u_roof"], 3),
        u_glazing=round(sim_res["u_glazing"], 3),
        u_floor=round(sim_res.get("u_floor", 1.2), 3),
        u_door=round(sim_res.get("u_door", 1.8), 3),
        explanation_narrative=explanation
    )


def compare_what_if_scenarios(req: WhatIfCompareRequest) -> WhatIfCompareResponse:
    """Executes side-by-side What-If scenario comparator via engine.thermal."""
    base_req = SimulationRequest(
        location_id=req.location_id,
        month=req.month,
        geometry=req.geometry,
        materials=req.baseline_materials,
        occupants=req.occupants,
        custom_climate_records=req.custom_climate_records
    )
    mod_req = SimulationRequest(
        location_id=req.location_id,
        month=req.month,
        geometry=req.geometry,
        materials=req.modified_materials,
        occupants=req.occupants,
        custom_climate_records=req.custom_climate_records
    )
    
    base_res = run_thermal_simulation(base_req)
    mod_res = run_thermal_simulation(mod_req)
    
    peak_drop = base_res.summary.peak_indoor_temp_c - mod_res.summary.peak_indoor_temp_c
    avg_drop = base_res.summary.avg_indoor_temp_c - mod_res.summary.avg_indoor_temp_c
    nighttime_gain = (mod_res.summary.nighttime_min_indoor_temp_c or 0.0) - (base_res.summary.nighttime_min_indoor_temp_c or 0.0)
    solar_delta = (mod_res.summary.total_daily_solar_captured_kwh or 0.0) - (base_res.summary.total_daily_solar_captured_kwh or 0.0)
    loss_reduction = (base_res.summary.total_daily_heat_loss_kwh or 0.0) - (mod_res.summary.total_daily_heat_loss_kwh or 0.0)
    disc_reduced = base_res.summary.discomfort_hours - mod_res.summary.discomfort_hours
    
    statement = (
        f"Modified configuration increased nighttime indoor minimum by +{nighttime_gain:+.1f}°C, "
        f"reduced envelope heat loss by {loss_reduction:.1f} kWh/day, and eliminated {max(0, disc_reduced)} hours of discomfort."
    )
    
    return WhatIfCompareResponse(
        peak_temperature_drop_c=round(peak_drop, 2),
        avg_temperature_drop_c=round(avg_drop, 2),
        nighttime_temperature_gain_c=round(nighttime_gain, 2),
        solar_capture_delta_kwh=round(solar_delta, 2),
        heat_loss_reduction_kwh=round(loss_reduction, 2),
        discomfort_hours_reduced=disc_reduced,
        summary_statement=statement,
        baseline_hourly=base_res.hourly_results,
        modified_hourly=mod_res.hourly_results,
        baseline_summary=base_res.summary,
        modified_summary=mod_res.summary
    )


def generate_ansys_export_service(req: SimulationRequest) -> Dict[str, Any]:
    """Generates PyANSYS Fluent Python script and APDL macro deck for ANSYS CFD validation."""
    from engine.ansys_export import generate_pyansys_fluent_script, generate_ansys_apdl_deck
    
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
    )
    
    climate_info = {
        "lat": 34.1526 if "ladakh" in (req.location_id or "").lower() else 21.4667,
        "lon": 77.5771 if "ladakh" in (req.location_id or "").lower() else 83.9833,
        "month": req.month or 1,
        "day": 15,
        "t_min_c": -15.0 if "ladakh" in (req.location_id or "").lower() else 10.0,
    }
    
    mat_dict = req.materials.model_dump() if hasattr(req.materials, "model_dump") else req.materials.dict()
    
    pyfluent_script = generate_pyansys_fluent_script(
        geometry=geom,
        materials=mat_dict,
        climate_data=climate_info,
        simulation_summary={}
    )
    
    apdl_deck = generate_ansys_apdl_deck(
        geometry=geom,
        materials=mat_dict,
        climate_data=climate_info
    )
    
    return {
        "shelter_name": "Ladakh Passive Thermal Shelter Model",
        "location": req.location_id or "leh_ladakh",
        "pyansys_fluent_script": pyfluent_script,
        "ansys_apdl_deck": apdl_deck,
        "instructions": (
            "1. To run 3D CHT in PyANSYS Fluent: `pip install ansys-fluent-core` and execute script.\n"
            "2. To run thermal diffusion in MAPDL: Read the APDL macro into ANSYS Mechanical APDL / PyMAPDL."
        )
    }

