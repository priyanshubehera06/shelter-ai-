"""
optimization.py — REST API endpoints for Multi-Objective NSGA-II Pareto Optimization.
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.optimization import OptimizationRequest, OptimizationResponse
from backend.services.optimization_service import run_optimization

router = APIRouter(prefix="/optimization", tags=["Optimization"])


@router.post("/run", response_model=OptimizationResponse)
def execute_pareto_optimization(req: OptimizationRequest):
    """
    Executes NSGA-II multi-objective genetic algorithm searching across materials,
    insulation thicknesses, and glazing ratios to find the non-dominated Pareto front.
    """
    try:
        return run_optimization(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Optimization error: {str(e)}")
