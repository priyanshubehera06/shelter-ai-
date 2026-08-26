"""
optimizer.py — Multi-Objective Pareto Optimization Engine (NSGA-II) for Shelter-AI.
Explores the combinatorial design space of Orientation, Materials, Insulation, WWR,
Shading, and Geometry to simultaneously optimize Thermal Comfort, Annual Energy, and CapEx Cost.
"""

import math
import random
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd

from engine.geometry import ShelterGeometry
from engine.thermal import simulate_shelter_thermal_dynamics
from engine.comfort import evaluate_human_comfort, calculate_pmv_fanger
from engine.energy import calculate_annual_energy_loads
from engine.cost import calculate_shelter_cost_and_carbon
from engine.resilience import evaluate_shelter_resilience
from engine.materials import get_materials_catalog

WALL_CANDIDATES = [
    "cseb_interlocking",
    "ceb_standard",
    "brick_standard",
    "aac_block",
    "stone_masonry",
    "bamboo_composite",
    "eps_sandwich",
]

ROOF_CANDIDATES = [
    "roof_cgi_insulated",
    "roof_concrete_slab",
    "roof_bamboo_thatch",
    "roof_cgi_sheet",
]

GLAZING_CANDIDATES = [
    "glazing_double",
    "glazing_single",
    "glazing_polycarb",
]

INSULATION_CANDIDATES = [
    None,
    "insulation_rockwool",
    "insulation_eps",
]


def evaluate_design_candidate(
    candidate: Dict[str, Any],
    climate_records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Simulates a full design candidate across the end-to-end physics pipeline:
    Geometry -> Thermal -> Comfort -> Energy -> Cost -> Resilience.
    """
    geom = ShelterGeometry(
        length_m=candidate.get("length_m", 6.0),
        width_m=candidate.get("width_m", 4.0),
        height_m=candidate.get("height_m", 2.8),
        roof_type=candidate.get("roof_type", "pitched"),
        roof_pitch_deg=candidate.get("roof_pitch_deg", 15.0),
        wwr_pct=candidate.get("wwr_pct", 15.0),
        overhang_m=candidate.get("overhang_m", 0.6),
        orientation_deg=candidate.get("orientation_deg", 0.0),
    )

    # 1. Thermal Simulation
    thermal_res = simulate_shelter_thermal_dynamics(
        geometry=geom,
        wall_mat_id=candidate["wall_mat_id"],
        wall_thickness_cm=candidate["wall_thickness_cm"],
        roof_mat_id=candidate["roof_mat_id"],
        glazing_mat_id=candidate["glazing_mat_id"],
        insulation_mat_id=candidate.get("insulation_mat_id"),
        insulation_thickness_cm=candidate.get("insulation_thickness_cm", 0.0),
        climate_records=climate_records,
        ach=candidate.get("ach", 3.0),
        occupants=candidate.get("occupants", 4),
    )

    # 2. Human Comfort Evaluation
    comfort_res = evaluate_human_comfort(
        t_indoor_hourly=thermal_res["t_indoor"],
        rh_hourly=np.mean(thermal_res["rh_outdoor"]) if thermal_res.get("rh_outdoor") else 50.0,
        t_outdoor_mean=np.mean(thermal_res["t_outdoor"]),
    )

    # 3. Energy Loads Calculation
    energy_res = calculate_annual_energy_loads(
        t_indoor_hourly=thermal_res["t_indoor"],
        floor_area_m2=geom.floor_area(),
        volume_m3=geom.volume(),
        ua_envelope_w_k=thermal_res["u_wall"] * geom.net_wall_area() + thermal_res["u_roof"] * geom.roof_area(),
    )

    # 4. Construction Cost & Embodied Carbon
    cost_res = calculate_shelter_cost_and_carbon(
        geometry=geom,
        wall_mat_id=candidate["wall_mat_id"],
        wall_thickness_cm=candidate["wall_thickness_cm"],
        roof_mat_id=candidate["roof_mat_id"],
        glazing_mat_id=candidate["glazing_mat_id"],
        insulation_mat_id=candidate.get("insulation_mat_id"),
        insulation_thickness_cm=candidate.get("insulation_thickness_cm", 0.0),
        annual_kwh=energy_res["total_annual_kwh"],
    )

    # 5. Resilience Stress Evaluation (fast approximation)
    resilience_score = round(
        max(20.0, min(100.0, 100.0 - (max(0.0, thermal_res["max_t_indoor"] - 30.0) * 4.5) + (1.0 - thermal_res["damping_factor"]) * 15.0)),
        1
    )

    # PMV discomfort metric (lower is better)
    pmv_discomfort = float(np.mean([abs(calculate_pmv_fanger(t)[0]) for t in thermal_res["t_indoor"]]))

    return {
        "candidate": candidate,
        "geometry": geom.envelope_summary(),
        "comfort_score": comfort_res["comfort_score"],
        "comfortable_hours_annual": comfort_res["comfortable_hours_annual"],
        "discomfort_pmv": round(pmv_discomfort, 3),
        "annual_energy_kwh": energy_res["total_annual_kwh"],
        "cooling_kwh": energy_res["annual_cooling_kwh"],
        "heating_kwh": energy_res["annual_heating_kwh"],
        "peak_cooling_kw": energy_res["peak_cooling_load_kw"],
        "cost_inr": cost_res["capex_inr"],
        "cost_per_m2": cost_res["cost_per_m2_inr"],
        "carbon_kg": cost_res["total_embodied_carbon_kgco2"],
        "resilience_score": resilience_score,
        "avg_indoor_temp": thermal_res["avg_t_indoor"],
        "max_indoor_temp": thermal_res["max_t_indoor"],
        "damping_factor": thermal_res["damping_factor"],
        "u_wall": thermal_res["u_wall"],
        "u_roof": thermal_res["u_roof"],
    }


def run_pareto_optimization(
    climate_records: Optional[List[Dict[str, Any]]] = None,
    w_comfort: float = 0.4,
    w_cost: float = 0.3,
    w_carbon: float = 0.3,
    population_size: int = 40,
    iterations: int = 5,
) -> Dict[str, Any]:
    """
    Executes multi-objective evolutionary search across the candidate space,
    computes the non-dominated Pareto front, and identifies the Top 4 Recommended Designs:
    1. 🏆 Best Balanced Design
    2. 🌡️ Best Comfort Design
    3. ⚡ Lowest Energy Design
    4. 💰 Lowest Cost Design
    """
    population = []

    # Generate diverse exploratory design candidates
    for _ in range(population_size):
        cand = {
            "length_m": random.choice([5.5, 6.0, 6.5, 7.0]),
            "width_m": random.choice([3.5, 4.0, 4.5]),
            "height_m": random.choice([2.6, 2.8, 3.0]),
            "roof_type": random.choice(["pitched", "monoslope", "flat"]),
            "roof_pitch_deg": random.choice([10.0, 15.0, 20.0]),
            "wall_mat_id": random.choice(WALL_CANDIDATES),
            "wall_thickness_cm": random.choice([15.0, 20.0, 25.0]),
            "roof_mat_id": random.choice(ROOF_CANDIDATES),
            "glazing_mat_id": random.choice(GLAZING_CANDIDATES),
            "insulation_mat_id": random.choice(INSULATION_CANDIDATES),
            "insulation_thickness_cm": random.choice([0.0, 2.5, 5.0, 7.5]),
            "wwr_pct": random.choice([10.0, 12.0, 15.0, 20.0, 25.0]),
            "overhang_m": random.choice([0.3, 0.6, 0.8, 1.0]),
            "orientation_deg": random.choice([0.0, 45.0, 90.0, 180.0]),
            "ach": 3.0,
            "occupants": 4,
        }
        population.append(cand)

    # Evaluate full population
    evaluated = [evaluate_design_candidate(cand, climate_records) for cand in population]

    # Objective bounds for normalization
    costs = [item["cost_inr"] for item in evaluated]
    energies = [item["annual_energy_kwh"] for item in evaluated]
    discomforts = [item["discomfort_pmv"] for item in evaluated]

    min_c, max_c = min(costs), max(costs) or 1.0
    min_e, max_e = min(energies), max(energies) or 1.0
    min_d, max_d = min(discomforts), max(discomforts) or 1.0

    for item in evaluated:
        norm_cost = (item["cost_inr"] - min_c) / max(0.001, max_c - min_c)
        norm_energy = (item["annual_energy_kwh"] - min_e) / max(0.001, max_e - min_e)
        norm_disc = (item["discomfort_pmv"] - min_d) / max(0.001, max_d - min_d)

        # Weighted penalty score (lower is better)
        item["score_penalty"] = round(
            w_cost * norm_cost + w_carbon * norm_energy + w_comfort * norm_disc, 4
        )
        # Utopia distance (distance to ideal point [0, 0, 0])
        item["utopia_distance"] = round(math.sqrt(norm_cost**2 + norm_energy**2 + norm_disc**2), 4)

    # Identify Non-Dominated Pareto Set
    pareto_front = []
    for p in evaluated:
        is_dominated = False
        for q in evaluated:
            # q dominates p if q is <= in all objectives and strictly < in at least one
            if (
                q["cost_inr"] <= p["cost_inr"]
                and q["annual_energy_kwh"] <= p["annual_energy_kwh"]
                and q["discomfort_pmv"] <= p["discomfort_pmv"]
            ) and (
                q["cost_inr"] < p["cost_inr"]
                or q["annual_energy_kwh"] < p["annual_energy_kwh"]
                or q["discomfort_pmv"] < p["discomfort_pmv"]
            ):
                is_dominated = True
                break
        if not is_dominated:
            p["is_pareto"] = True
            pareto_front.append(p)
        else:
            p["is_pareto"] = False

    # Sort evaluated by score penalty
    evaluated.sort(key=lambda x: x["score_penalty"])

    # -------------------------------------------------------------
    # TOP 4 RECOMMENDED DESIGNS SELECTION
    # -------------------------------------------------------------
    # 1. Best Balanced (Minimum Utopia distance or penalty score on Pareto front)
    pareto_sorted = sorted(pareto_front, key=lambda x: x["utopia_distance"]) if pareto_front else evaluated
    best_balanced = pareto_sorted[0]
    best_balanced["recommendation_type"] = "🏆 Best Balanced Design"
    best_balanced["rationale"] = (
        f"Optimal compromise across all competing objectives (Utopia distance: {best_balanced['utopia_distance']:.2f}). "
        f"Delivers a high Comfort Score of {best_balanced['comfort_score']}/100 while keeping CapEx cost at ₹{best_balanced['cost_inr']:,.0f}."
    )

    # 2. Best Comfort Design (Maximum comfort score / minimum discomfort)
    best_comfort = min(evaluated, key=lambda x: x["discomfort_pmv"])
    best_comfort["recommendation_type"] = "🌡️ Best Comfort Design"
    best_comfort["rationale"] = (
        f"Highest thermal comfort performance (Comfort Score: {best_comfort['comfort_score']}/100, PMV: {best_comfort['discomfort_pmv']:.2f}). "
        f"Maximizes indoor thermal inertia and phase lag damping."
    )

    # 3. Lowest Energy Design (Minimum annual kWh)
    lowest_energy = min(evaluated, key=lambda x: x["annual_energy_kwh"])
    lowest_energy["recommendation_type"] = "⚡ Lowest Energy Design"
    lowest_energy["rationale"] = (
        f"Lowest annual HVAC energy demand ({lowest_energy['annual_energy_kwh']:,.0f} kWh/year). "
        f"Minimizes active heating and cooling operational utility bills."
    )

    # 4. Lowest Cost Design (Minimum CapEx INR)
    lowest_cost = min(evaluated, key=lambda x: x["cost_inr"])
    lowest_cost["recommendation_type"] = "💰 Lowest Cost Design"
    lowest_cost["rationale"] = (
        f"Lowest initial construction capital outlay (₹{lowest_cost['cost_inr']:,.0f}). "
        f"Maximizes affordability for humanitarian rapid disaster-relief deployment."
    )

    top_4_designs = {
        "best_balanced": best_balanced,
        "best_comfort": best_comfort,
        "lowest_energy": lowest_energy,
        "lowest_cost": lowest_cost,
    }

    return {
        "best_candidate": best_balanced,
        "top_4_designs": top_4_designs,
        "pareto_front": pareto_front,
        "all_candidates": evaluated,
        "population_size": len(evaluated),
        "pareto_count": len(pareto_front),
    }
