"""
recommendation_service.py — Service layer connecting API requests to the Recommendation Subsystem.
"""

from typing import Dict, Any, Optional
from backend.schemas.recommendations import RecommendationRequest, RecommendationResponse
from engine.recommendation.material_recommender import generate_material_recommendations
from engine.recommendation.construction_recommender import recommend_construction_method


def run_recommendations(req: RecommendationRequest) -> Dict[str, Any]:
    """Orchestrates multi-criteria recommendation for materials and construction systems."""
    w_dict = req.weights.model_dump() if req.weights else None

    # 1. Material Recommendations
    mat_res = generate_material_recommendations(
        climate_zone=req.climate_zone,
        state_code=req.state_code,
        budget_level=req.budget_level,
        shelter_type=req.shelter_type,
        disaster_mode=req.disaster_mode,
        weights=w_dict
    )

    # 2. Construction Method Recommendations
    const_res = recommend_construction_method(
        climate_zone=req.climate_zone,
        shelter_type=req.shelter_type,
        disaster_mode=req.disaster_mode,
        rapid_deployment_needed=req.rapid_deployment_needed,
        budget_level=req.budget_level,
        weights=w_dict
    )

    return {
        "climate_zone": req.climate_zone,
        "state_code": req.state_code,
        "budget_level": req.budget_level,
        "disaster_mode": req.disaster_mode,
        "material_recommendations": mat_res["recommendations"],
        "construction_recommendation": const_res,
        "climate_targets": mat_res["climate_targets"]
    }
