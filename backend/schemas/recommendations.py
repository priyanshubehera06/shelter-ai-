"""
recommendations.py — Pydantic Schemas for Material & Construction Recommendation Endpoints.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class RecommendationWeights(BaseModel):
    thermal: float = 0.35
    cost: float = 0.25
    resilience: float = 0.20
    constructability: float = 0.10
    availability: float = 0.10


class RecommendationRequest(BaseModel):
    climate_zone: str = Field(default="Composite", description="Target climate classification")
    state_code: Optional[str] = Field(default=None, description="Two letter state code or name")
    budget_level: str = Field(default="medium", description="low, medium, or high")
    shelter_type: str = Field(default="Standard Residential", description="Building typology or disaster mode")
    disaster_mode: Optional[str] = Field(default=None, description="Heatwave, Flood, Cyclone, Earthquake, Extreme Rain")
    rapid_deployment_needed: bool = Field(default=False, description="Whether rapid post-disaster assembly is required")
    weights: Optional[RecommendationWeights] = None


class RecommendationItem(BaseModel):
    item: str
    recommended_option: str
    material_id: Optional[str] = None
    score: float
    sub_scores: Optional[Dict[str, float]] = None
    reason: str
    thermal_benefit: str
    cost_impact: str
    confidence: str
    data_sources: List[str]


class ConstructionMethodItem(BaseModel):
    system_id: str
    name: str
    archetype: str
    deployment_speed_days: int
    labor_skill: str
    embodied_carbon: str
    thermal_inertia: str
    base_cost_inr_m2: float
    description: str
    score: float
    sub_scores: Dict[str, float]


class RecommendationResponse(BaseModel):
    climate_zone: str
    state_code: Optional[str]
    budget_level: str
    disaster_mode: Optional[str]
    material_recommendations: List[RecommendationItem]
    construction_recommendation: Dict[str, Any]
    climate_targets: Dict[str, Any]
