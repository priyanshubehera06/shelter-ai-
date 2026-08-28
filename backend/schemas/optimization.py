"""
optimization.py — Pydantic schemas for Multi-Objective NSGA-II Pareto Optimization.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.schemas.design import GeometryParams, MaterialSelection


class OptimizationRequest(BaseModel):
    location_id: Optional[str] = "sambalpur"
    month: int = Field(5, ge=1, le=12)
    w_comfort: float = Field(0.40, ge=0.0, le=1.0)
    w_cost: float = Field(0.30, ge=0.0, le=1.0)
    w_carbon: float = Field(0.30, ge=0.0, le=1.0)
    population_size: int = Field(25, ge=10, le=80)
    geometry_override: Optional[GeometryParams] = None


class ParetoCandidate(BaseModel):
    id: str
    rank: int
    is_pareto: bool
    candidate: Dict[str, Any]
    comfort_score: float
    annual_energy_kwh: float
    cost_inr: float
    carbon_kg: float
    resilience_score: float
    discomfort_pmv: float
    avg_indoor_temp: float
    peak_indoor_temp: float
    fitness_score: float
    rationale: Optional[str] = None


class RecommendedTop4(BaseModel):
    best_balanced: ParetoCandidate
    best_comfort: ParetoCandidate
    lowest_energy: ParetoCandidate
    lowest_cost: ParetoCandidate


class OptimizationResponse(BaseModel):
    location_id: str
    population_size: int
    weights: Dict[str, float]
    total_evaluated: int
    pareto_front_count: int
    pareto_front: List[ParetoCandidate]
    all_candidates: List[ParetoCandidate]
    top_4_designs: RecommendedTop4
