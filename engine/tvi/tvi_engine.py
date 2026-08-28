"""
tvi_engine.py — Transparent Thermal Vulnerability Index (TVI) Engine for Indian States & UTs.
Calculates normalized multi-factor vulnerability scores, dual Cold vs. Heat vulnerability profiles,
and maps regional thermal challenges directly to passive shelter design imperatives.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any

DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "tvi" / "state_vulnerability_data.json"
SOURCES_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "tvi" / "sources_registry.json"

DEFAULT_TVI_WEIGHTS = {
    "heat_exposure": 0.20,
    "extreme_heat": 0.20,
    "thermal_stress": 0.15,
    "cooling_burden": 0.15,
    "population_vulnerability": 0.15,
    "building_vulnerability": 0.15,
    "adaptive_capacity": 0.15
}


def load_tvi_raw_data() -> Dict[str, Any]:
    """Loads the state vulnerability dataset from JSON."""
    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"states": {}}


def load_tvi_sources() -> List[Dict[str, Any]]:
    """Loads the scientific source registry from JSON."""
    if os.path.exists(SOURCES_PATH):
        with open(SOURCES_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("sources", [])
    return []


def get_tvi_category(tvi_score: float) -> str:
    """Classifies TVI score into documented severity tiers."""
    if tvi_score < 20.0:
        return "Very Low"
    elif tvi_score < 40.0:
        return "Low"
    elif tvi_score < 60.0:
        return "Moderate"
    elif tvi_score < 80.0:
        return "High"
    else:
        return "Very High"


def calculate_state_tvi(
    state_name: str,
    weights: Optional[Dict[str, float]] = None
) -> Optional[Dict[str, Any]]:
    """
    Computes transparent dual-dimension TVI score for a specific Indian State or UT.
    Evaluates Overall TVI, Cold Vulnerability, Heat Vulnerability, and Solar Potential.
    """
    data = load_tvi_raw_data()
    states_dict = data.get("states", {})

    matched_key = next((k for k in states_dict if k.lower() == state_name.lower()), None)
    if not matched_key:
        return None

    s = states_dict[matched_key]
    w = weights or DEFAULT_TVI_WEIGHTS

    # Cold vs Heat dimensions
    cold_exp = s.get("cold_exposure_score", 20.0)
    heat_exp = s.get("heat_exposure_score", 50.0)
    ext_heat = s.get("extreme_heat_score", 50.0)
    therm_stress = s.get("thermal_stress_score", 50.0)
    heat_burden = s.get("heating_burden_score", 20.0)
    cool_burden = s.get("cooling_burden_score", 50.0)
    pop_vuln = s.get("population_vulnerability_score", 50.0)
    bldg_vuln = s.get("building_vulnerability_score", 50.0)
    adapt_cap = s.get("adaptive_capacity_score", 50.0)
    solar_pot = s.get("solar_potential_score", 70.0)

    # Sub-indices
    cold_vuln_score = round(0.40 * cold_exp + 0.35 * heat_burden + 0.25 * bldg_vuln, 1)
    heat_vuln_score = round(0.35 * heat_exp + 0.35 * ext_heat + 0.30 * cool_burden, 1)

    # Overall Composite TVI
    # If region is Cold & High-Altitude, cold components drive overall vulnerability
    is_cold_dominant = "cold" in str(s.get("dominant_climate", "")).lower()

    if is_cold_dominant:
        raw_tvi = (
            cold_exp * 0.30 +
            heat_burden * 0.25 +
            therm_stress * 0.20 +
            pop_vuln * 0.15 +
            bldg_vuln * 0.20 -
            adapt_cap * 0.15
        ) / 1.10
    else:
        raw_tvi = (
            heat_exp * w.get("heat_exposure", 0.20) +
            ext_heat * w.get("extreme_heat", 0.20) +
            therm_stress * w.get("thermal_stress", 0.15) +
            cool_burden * w.get("cooling_burden", 0.15) +
            pop_vuln * w.get("population_vulnerability", 0.15) +
            bldg_vuln * w.get("building_vulnerability", 0.15) -
            adapt_cap * w.get("adaptive_capacity", 0.15)
        ) / 1.00

    normalized_tvi = round(max(0.0, min(100.0, raw_tvi)), 1)
    category = get_tvi_category(normalized_tvi)

    return {
        "state_name": matched_key,
        "state_code": s.get("state_code", ""),
        "region": s.get("region", ""),
        "dominant_climate": s.get("dominant_climate", ""),
        "tvi_score": normalized_tvi,
        "category": category,
        "cold_vulnerability_score": cold_vuln_score,
        "heat_vulnerability_score": heat_vuln_score,
        "solar_potential_score": solar_pot,
        "adaptive_capacity_score": adapt_cap,
        "variables": {
            "cold_exposure": cold_exp,
            "heating_burden": heat_burden,
            "heat_exposure": heat_exp,
            "extreme_heat": ext_heat,
            "thermal_stress": therm_stress,
            "cooling_burden": cool_burden,
            "population_vulnerability": pop_vuln,
            "building_vulnerability": bldg_vuln,
            "adaptive_capacity": adapt_cap,
            "solar_potential": solar_pot
        },
        "weights_used": w,
        "key_hazard_profiles": s.get("key_hazard_profiles", []),
        "passive_priorities": s.get("passive_priorities", []),
        "confidence": s.get("confidence", "HIGH"),
        "data_year": s.get("data_year", 2025),
        "disclaimer": "The ShelterAI Thermal Vulnerability Index is a research/decision-support indicator constructed from the documented input variables and sources. It is not an official Government of India vulnerability ranking."
    }


def get_all_states_tvi(
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Computes TVI for all states and generates dynamically calculated rankings.
    """
    data = load_tvi_raw_data()
    states_dict = data.get("states", {})
    results = []

    for name in states_dict.keys():
        res = calculate_state_tvi(name, weights)
        if res:
            results.append(res)

    # Sort descending by TVI score
    results.sort(key=lambda x: x["tvi_score"], reverse=True)

    for idx, item in enumerate(results):
        item["rank"] = idx + 1

    return {
        "total_states": len(results),
        "ranking_basis": "States with the highest ShelterAI Thermal Vulnerability Index scores",
        "disclaimer": "The ShelterAI Thermal Vulnerability Index is a research/decision-support indicator constructed from the documented input variables and sources. It is not an official Government of India vulnerability ranking.",
        "states_ranked": results,
        "sources": load_tvi_sources()
    }
