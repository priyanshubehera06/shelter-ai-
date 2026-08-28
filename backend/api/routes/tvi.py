"""
tvi.py — REST API endpoints for India State-Wise Thermal Vulnerability Index (TVI).
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.schemas.tvi import (
    AllStatesTVIResponse,
    StateTVIResponse
)
from backend.services.tvi_service import query_all_tvi, query_state_tvi, query_tvi_sources

router = APIRouter(prefix="/thermal-vulnerability", tags=["Thermal Vulnerability Index"])


@router.get("", response_model=AllStatesTVIResponse)
def get_all_thermal_vulnerability(
    w_heat_exposure: Optional[float] = Query(0.20),
    w_extreme_heat: Optional[float] = Query(0.20),
    w_thermal_stress: Optional[float] = Query(0.15),
    w_cooling_burden: Optional[float] = Query(0.15),
    w_pop_vuln: Optional[float] = Query(0.15),
    w_bldg_vuln: Optional[float] = Query(0.15),
    w_adaptive_cap: Optional[float] = Query(0.15),
):
    """
    Computes transparent TVI across all Indian states and UTs with dynamic rankings,
    component breakdowns, and data source disclosure.
    """
    weights = {
        "heat_exposure": w_heat_exposure,
        "extreme_heat": w_extreme_heat,
        "thermal_stress": w_thermal_stress,
        "cooling_burden": w_cooling_burden,
        "population_vulnerability": w_pop_vuln,
        "building_vulnerability": w_bldg_vuln,
        "adaptive_capacity": w_adaptive_cap
    }
    return query_all_tvi(weights)


@router.get("/sources")
def get_tvi_sources():
    """Returns provenance and methodological details for each TVI variable."""
    return query_tvi_sources()


@router.get("/{state_name}", response_model=StateTVIResponse)
def get_state_thermal_vulnerability(
    state_name: str,
    w_heat_exposure: Optional[float] = Query(0.20),
    w_extreme_heat: Optional[float] = Query(0.20),
    w_thermal_stress: Optional[float] = Query(0.15),
    w_cooling_burden: Optional[float] = Query(0.15),
    w_pop_vuln: Optional[float] = Query(0.15),
    w_bldg_vuln: Optional[float] = Query(0.15),
    w_adaptive_cap: Optional[float] = Query(0.15),
):
    """Retrieves single-state TVI breakdown and design priorities."""
    weights = {
        "heat_exposure": w_heat_exposure,
        "extreme_heat": w_extreme_heat,
        "thermal_stress": w_thermal_stress,
        "cooling_burden": w_cooling_burden,
        "population_vulnerability": w_pop_vuln,
        "building_vulnerability": w_bldg_vuln,
        "adaptive_capacity": w_adaptive_cap
    }
    res = query_state_tvi(state_name, weights)
    if not res:
        raise HTTPException(status_code=404, detail=f"Thermal vulnerability data not found for state '{state_name}'")
    return res
