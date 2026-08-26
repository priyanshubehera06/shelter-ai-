"""
scenario.py — Interactive What-If Scenario Comparator & Sensitivity Analysis for Shelter-AI.
Enables instant side-by-side delta comparisons between Baseline and Modified shelter variants,
quantifying peak temperature reduction, energy savings, CapEx differences, and comfort gains.
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import plotly.graph_objects as go

from engine.geometry import ShelterGeometry
from engine.thermal import simulate_shelter_thermal_dynamics
from engine.comfort import evaluate_human_comfort
from engine.energy import calculate_annual_energy_loads
from engine.cost import calculate_shelter_cost_and_carbon


def compare_what_if_scenarios(
    geometry_baseline: ShelterGeometry,
    config_baseline: Dict[str, Any],
    geometry_modified: ShelterGeometry,
    config_modified: Dict[str, Any],
    climate_records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Executes full transient simulation and cost/energy evaluation for both Baseline and Modified
    configurations, computing precise physical and financial deltas.
    """
    # 1. Simulate Baseline
    sim_base = simulate_shelter_thermal_dynamics(
        geometry=geometry_baseline,
        wall_mat_id=config_baseline.get("wall_mat_id", "brick_standard"),
        wall_thickness_cm=config_baseline.get("wall_thickness_cm", 20.0),
        roof_mat_id=config_baseline.get("roof_mat_id", "roof_cgi_sheet"),
        glazing_mat_id=config_baseline.get("glazing_mat_id", "glazing_single"),
        insulation_mat_id=config_baseline.get("insulation_mat_id"),
        insulation_thickness_cm=config_baseline.get("insulation_thickness_cm", 0.0),
        climate_records=climate_records,
        ach=config_baseline.get("ach", 3.0),
    )

    comfort_base = evaluate_human_comfort(
        t_indoor_hourly=sim_base["t_indoor"],
        rh_hourly=np.mean(sim_base["rh_outdoor"]) if sim_base.get("rh_outdoor") else 50.0,
        t_outdoor_mean=np.mean(sim_base["t_outdoor"]),
    )

    energy_base = calculate_annual_energy_loads(
        t_indoor_hourly=sim_base["t_indoor"],
        floor_area_m2=geometry_baseline.floor_area(),
    )

    cost_base = calculate_shelter_cost_and_carbon(
        geometry=geometry_baseline,
        wall_mat_id=config_baseline.get("wall_mat_id", "brick_standard"),
        wall_thickness_cm=config_baseline.get("wall_thickness_cm", 20.0),
        roof_mat_id=config_baseline.get("roof_mat_id", "roof_cgi_sheet"),
        glazing_mat_id=config_baseline.get("glazing_mat_id", "glazing_single"),
        insulation_mat_id=config_baseline.get("insulation_mat_id"),
        insulation_thickness_cm=config_baseline.get("insulation_thickness_cm", 0.0),
        annual_kwh=energy_base["total_annual_kwh"],
    )

    # 2. Simulate Modified Scenario
    sim_mod = simulate_shelter_thermal_dynamics(
        geometry=geometry_modified,
        wall_mat_id=config_modified.get("wall_mat_id", "cseb_interlocking"),
        wall_thickness_cm=config_modified.get("wall_thickness_cm", 20.0),
        roof_mat_id=config_modified.get("roof_mat_id", "roof_cgi_insulated"),
        glazing_mat_id=config_modified.get("glazing_mat_id", "glazing_double"),
        insulation_mat_id=config_modified.get("insulation_mat_id", "insulation_rockwool"),
        insulation_thickness_cm=config_modified.get("insulation_thickness_cm", 5.0),
        climate_records=climate_records,
        ach=config_modified.get("ach", 3.0),
    )

    comfort_mod = evaluate_human_comfort(
        t_indoor_hourly=sim_mod["t_indoor"],
        rh_hourly=np.mean(sim_mod["rh_outdoor"]) if sim_mod.get("rh_outdoor") else 50.0,
        t_outdoor_mean=np.mean(sim_mod["t_outdoor"]),
    )

    energy_mod = calculate_annual_energy_loads(
        t_indoor_hourly=sim_mod["t_indoor"],
        floor_area_m2=geometry_modified.floor_area(),
    )

    cost_mod = calculate_shelter_cost_and_carbon(
        geometry=geometry_modified,
        wall_mat_id=config_modified.get("wall_mat_id", "cseb_interlocking"),
        wall_thickness_cm=config_modified.get("wall_thickness_cm", 20.0),
        roof_mat_id=config_modified.get("roof_mat_id", "roof_cgi_insulated"),
        glazing_mat_id=config_modified.get("glazing_mat_id", "glazing_double"),
        insulation_mat_id=config_modified.get("insulation_mat_id", "insulation_rockwool"),
        insulation_thickness_cm=config_modified.get("insulation_thickness_cm", 5.0),
        annual_kwh=energy_mod["total_annual_kwh"],
    )

    # 3. Calculate Deltas
    peak_drop_c = round(sim_base["max_t_indoor"] - sim_mod["max_t_indoor"], 1)
    avg_drop_c = round(sim_base["avg_t_indoor"] - sim_mod["avg_t_indoor"], 1)
    
    overheating_hours_base = sum(1 for t in sim_base["t_indoor"] if t > 30.0)
    overheating_hours_mod = sum(1 for t in sim_mod["t_indoor"] if t > 30.0)
    hours_overheating_reduced = max(0, overheating_hours_base - overheating_hours_mod)

    comfort_score_delta = comfort_mod["comfort_score"] - comfort_base["comfort_score"]
    annual_energy_saved_kwh = round(energy_base["total_annual_kwh"] - energy_mod["total_annual_kwh"], 1)
    energy_savings_pct = round((annual_energy_saved_kwh / max(1.0, energy_base["total_annual_kwh"])) * 100.0, 1)

    capex_delta_inr = round(cost_mod["capex_inr"] - cost_base["capex_inr"], 2)
    lcc_savings_inr = round(cost_base["total_lcc_inr"] - cost_mod["total_lcc_inr"], 2)
    carbon_saved_kg = round(cost_base["total_embodied_carbon_kgco2"] - cost_mod["total_embodied_carbon_kgco2"], 1)

    # Explainable summary
    summary_text = (
        f"The Modified design reduces peak indoor temperature by {peak_drop_c:+.1f}°C "
        f"({sim_base['max_t_indoor']}°C → {sim_mod['max_t_indoor']}°C) and avoids {hours_overheating_reduced} hours of daily overheating (>30°C). "
        f"It yields {energy_savings_pct}% annual HVAC energy savings ({annual_energy_saved_kwh:,.0f} kWh/yr) "
        f"with a 20-year net Life Cycle Cost savings of ₹{lcc_savings_inr:,.0f}."
    )

    # Comparison Plotly figure
    fig = go.Figure()
    hours_labels = [f"{h:02d}:00" for h in range(24)]
    fig.add_trace(go.Scatter(
        x=hours_labels, y=sim_base["t_indoor"], name=f"Baseline ({config_baseline.get('roof_mat_id', 'Roof')})",
        line=dict(color="#e74c3c", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=hours_labels, y=sim_mod["t_indoor"], name=f"Modified ({config_modified.get('roof_mat_id', 'Roof')})",
        line=dict(color="#2ecc71", width=3)
    ))
    fig.add_trace(go.Scatter(
        x=hours_labels, y=sim_base["t_outdoor"], name="Outdoor Ambient (°C)",
        line=dict(color="#95a5a6", width=2, dash="dot")
    ))
    fig.add_hrect(y0=20.0, y1=26.0, fillcolor="#2ecc71", opacity=0.1, line_width=0, annotation_text="ASHRAE 55 Comfort Band")
    fig.update_layout(
        title="Baseline vs. Modified Diurnal Indoor Temperature Trajectory",
        xaxis_title="Hour of Day",
        yaxis_title="Temperature (°C)",
        hovermode="x unified",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return {
        "peak_temperature_drop_c": peak_drop_c,
        "avg_temperature_drop_c": avg_drop_c,
        "hours_overheating_reduced": hours_overheating_reduced,
        "comfort_score_delta": comfort_score_delta,
        "annual_energy_saved_kwh": annual_energy_saved_kwh,
        "energy_savings_pct": energy_savings_pct,
        "capex_delta_inr": capex_delta_inr,
        "lcc_savings_inr": lcc_savings_inr,
        "carbon_saved_kg": carbon_saved_kg,
        "summary_text": summary_text,
        "figure": fig,
        "baseline_summary": {
            "max_t_indoor": sim_base["max_t_indoor"],
            "avg_t_indoor": sim_base["avg_t_indoor"],
            "comfort_score": comfort_base["comfort_score"],
            "annual_kwh": energy_base["total_annual_kwh"],
            "capex_inr": cost_base["capex_inr"],
        },
        "modified_summary": {
            "max_t_indoor": sim_mod["max_t_indoor"],
            "avg_t_indoor": sim_mod["avg_t_indoor"],
            "comfort_score": comfort_mod["comfort_score"],
            "annual_kwh": energy_mod["total_annual_kwh"],
            "capex_inr": cost_mod["capex_inr"],
        },
    }
