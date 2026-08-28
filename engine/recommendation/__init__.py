"""
Recommendation Package initialization for ShelterAI.
"""

from engine.recommendation.material_recommender import generate_material_recommendations
from engine.recommendation.construction_recommender import recommend_construction_method
from engine.recommendation.climate_rules import get_climate_targets
from engine.recommendation.recommendation_scoring import calculate_composite_score

__all__ = [
    "generate_material_recommendations",
    "recommend_construction_method",
    "get_climate_targets",
    "calculate_composite_score"
]
