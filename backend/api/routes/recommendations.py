"""
recommendations.py — REST API endpoints for Material and Construction Recommendations.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from backend.schemas.recommendations import (
    RecommendationRequest,
    RecommendationResponse,
)
from backend.services.recommendation_service import run_recommendations
from engine.recommendation.construction_recommender import CONSTRUCTION_SYSTEMS

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/run", response_model=RecommendationResponse)
def get_recommendations(req: RecommendationRequest):
    """
    Evaluates multi-factor thermo-physical, cost, constructability, and disaster suitability
    for envelope components (Wall, Roof, Floor, Windows, Doors, Insulation, Shading, and Construction Methods).
    """
    try:
        return run_recommendations(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation engine error: {str(e)}")


@router.get("/systems")
def list_construction_systems():
    """Returns the catalog of modular and traditional construction systems with speed and carbon metrics."""
    return {"systems": CONSTRUCTION_SYSTEMS}
