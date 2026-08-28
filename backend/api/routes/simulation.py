"""
simulation.py — REST API endpoints for Physics-Based Simulation and Scenario Comparison.
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.simulation import (
    SimulationRequest,
    SimulationResponse,
    WhatIfCompareRequest,
    WhatIfCompareResponse
)
from backend.services.simulation_service import run_thermal_simulation, compare_what_if_scenarios

router = APIRouter(prefix="/simulation", tags=["Simulation"])


@router.post("/run", response_model=SimulationResponse)
def execute_simulation(req: SimulationRequest):
    """
    Executes 24-hour transient RC thermal simulation, ASHRAE 55 PMV comfort calculation,
    HVAC electrical load balance, and construction CapEx / carbon estimation.
    """
    try:
        return run_thermal_simulation(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation error: {str(e)}")


@router.post("/what-if", response_model=WhatIfCompareResponse)
def execute_what_if_comparison(req: WhatIfCompareRequest):
    """Performs side-by-side sensitivity comparison between baseline and modified shelter configurations."""
    try:
        return compare_what_if_scenarios(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comparison error: {str(e)}")
