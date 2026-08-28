"""
tvi.py — Pydantic Schemas for Thermal Vulnerability Index (TVI) Endpoints.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class TVIWeights(BaseModel):
    heat_exposure: float = 0.20
    extreme_heat: float = 0.20
    thermal_stress: float = 0.15
    cooling_burden: float = 0.15
    population_vulnerability: float = 0.15
    building_vulnerability: float = 0.15
    adaptive_capacity: float = 0.15


class StateTVIResponse(BaseModel):
    state_name: str
    state_code: str
    region: str
    dominant_climate: str
    tvi_score: float
    category: str  # "Very Low", "Low", "Moderate", "High", "Very High"
    variables: Dict[str, float]
    weights_used: Dict[str, float]
    key_hazard_profiles: List[str]
    passive_priorities: List[str]
    confidence: str
    data_year: int
    disclaimer: str
    rank: Optional[int] = None


class TVISourceItem(BaseModel):
    variable_id: str
    variable_name: str
    primary_source: str
    source_url: str
    publication_year: int
    data_year_range: str
    spatial_resolution: str
    units: str
    methodology: str
    limitations: str


class AllStatesTVIResponse(BaseModel):
    total_states: int
    ranking_basis: str
    disclaimer: str
    states_ranked: List[StateTVIResponse]
    sources: List[TVISourceItem]
