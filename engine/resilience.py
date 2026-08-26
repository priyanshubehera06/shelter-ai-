"""
resilience.py — Climate Resilience & Extreme Stress Testing Engine for Shelter-AI.
Evaluates shelter performance across all 5 canonical meteorological scenarios
(NORMAL, HOT, EXTREME_HOT, COLD, EXTREME_COLD), computing Thermal Resilience Scores (0-100),
peak temperature risk, and comfort degradation factors.
"""

from typing import Dict, List, Optional, Any
import numpy as np
from engine.geometry import ShelterGeometry
from engine.thermal import simulate_shelter_thermal_dynamics
from engine.comfort import evaluate_human_comfort
from engine.extreme_analysis import analyze_extreme_climate_events


def evaluate_shelter_resilience(
    geometry: ShelterGeometry,
    wall_mat_id: str = "brick_standard",
    wall_thickness_cm: float = 20.0,
    roof_mat_id: str = "roof_cgi_insulated",
    glazing_mat_id: str = "glazing_single",
    insulation_mat_id: Optional[str] = None,
    insulation_thickness_cm: float = 0.0,
    extreme_data: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Stress-tests a shelter configuration across all 5 canonical extreme scenarios.
    Returns:
    - Scenario performance matrix (Peak T_in, Avg T_in, Comfort Score)
    - Peak indoor overheating risk (°C above 30°C)
    - Peak indoor freezing risk (°C below 15°C)
    - Thermal Resilience Score (0 to 100)
    """
    if extreme_data is None:
        extreme_data = analyze_extreme_climate_events()

    scenarios = extreme_data["scenarios"]
    scenario_results = {}

    for sc_name, sc_records in scenarios.items():
        sim_res = simulate_shelter_thermal_dynamics(
            geometry=geometry,
            wall_mat_id=wall_mat_id,
            wall_thickness_cm=wall_thickness_cm,
            roof_mat_id=roof_mat_id,
            glazing_mat_id=glazing_mat_id,
            insulation_mat_id=insulation_mat_id,
            insulation_thickness_cm=insulation_thickness_cm,
            climate_records=sc_records,
            ach=3.0,
            occupants=4,
        )

        comfort_res = evaluate_human_comfort(
            t_indoor_hourly=sim_res["t_indoor"],
            rh_hourly=np.mean(sim_res["rh_outdoor"]) if sim_res.get("rh_outdoor") else 50.0,
            t_outdoor_mean=np.mean(sim_res["t_outdoor"]),
        )

        scenario_results[sc_name] = {
            "max_t_outdoor": sim_res["max_t_outdoor"],
            "min_t_outdoor": sim_res["min_t_outdoor"],
            "max_t_indoor": sim_res["max_t_indoor"],
            "min_t_indoor": sim_res["min_t_indoor"],
            "avg_t_indoor": sim_res["avg_t_indoor"],
            "damping_factor": sim_res["damping_factor"],
            "comfort_score": comfort_res["comfort_score"],
            "comfortable_pct": comfort_res["comfortable_pct"],
        }

    # 1. Evaluate Extreme Heatwave Performance (EXTREME_HOT)
    ext_hot = scenario_results["EXTREME_HOT"]
    peak_overheating = max(0.0, ext_hot["max_t_indoor"] - 30.0)

    # 2. Evaluate Extreme Cold Snap Performance (EXTREME_COLD)
    ext_cold = scenario_results["EXTREME_COLD"]
    peak_underheating = max(0.0, 18.0 - ext_cold["min_t_indoor"])

    # 3. Calculate Thermal Resilience Score (0 to 100)
    # Deductions for exceeding critical biological thresholds under extreme stress
    base_score = 100.0
    heat_penalty = min(50.0, peak_overheating * 5.0)  # e.g. 5°C over 30°C -> -25 pts
    cold_penalty = min(35.0, peak_underheating * 3.5)
    damping_bonus = max(0.0, (1.0 - ext_hot["damping_factor"]) * 15.0)

    resilience_score = round(max(5.0, min(100.0, base_score - heat_penalty - cold_penalty + damping_bonus)), 1)

    if resilience_score >= 85.0:
        resilience_grade = "Exceptional Resilience (High Thermal Safety Margin)"
        resilience_color = "#2ecc71"
    elif resilience_score >= 70.0:
        resilience_grade = "Moderate Resilience (Safe Under Normal Extremes)"
        resilience_color = "#f1c40f"
    elif resilience_score >= 50.0:
        resilience_grade = "Vulnerable (Severe Overheating During Heatwaves)"
        resilience_color = "#e67e22"
    else:
        resilience_grade = "Critically Vulnerable (Uninhabitable in Extreme Events)"
        resilience_color = "#e74c3c"

    # Performance comparison summary table
    matrix_rows = []
    for name, r in scenario_results.items():
        matrix_rows.append({
            "Scenario": name,
            "Peak Outdoor (°C)": r["max_t_outdoor"],
            "Peak Indoor (°C)": r["max_t_indoor"],
            "Passive Damping": f"{r['damping_factor']:.2f}",
            "Comfort Score": f"{r['comfort_score']}/100",
            "Comfort Time": f"{r['comfortable_pct']}%",
        })

    return {
        "thermal_resilience_score": resilience_score,
        "resilience_grade": resilience_grade,
        "resilience_color": resilience_color,
        "peak_overheating_above_30c": round(peak_overheating, 1),
        "peak_underheating_below_18c": round(peak_underheating, 1),
        "scenario_results": scenario_results,
        "scenario_performance_table": matrix_rows,
        "summary": (
            f"Shelter achieves a Thermal Resilience Score of {resilience_score}/100. "
            f"Under extreme heatwaves (Peak {ext_hot['max_t_outdoor']}°C), peak indoor temperature reaches {ext_hot['max_t_indoor']}°C "
            f"(Damping factor: {ext_hot['damping_factor']:.2f})."
        ),
    }
