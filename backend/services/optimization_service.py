"""
optimization_service.py — Service adapter interfacing with engine.optimizer (NSGA-II).
"""

from typing import List, Dict, Any, Optional
from engine.optimizer import run_pareto_optimization
from engine.climate import get_climate_profile
from engine.geometry import ShelterGeometry
from backend.schemas.optimization import (
    OptimizationRequest,
    OptimizationResponse,
    ParetoCandidate,
    RecommendedTop4
)


def run_optimization(req: OptimizationRequest) -> OptimizationResponse:
    """Executes multi-objective genetic search over envelope design space."""
    climate_records = get_climate_profile(month=req.month)
    
    res = run_pareto_optimization(
        climate_records=climate_records,
        w_comfort=req.w_comfort,
        w_cost=req.w_cost,
        w_carbon=req.w_carbon,
        population_size=req.population_size
    )
    
    pareto_candidates = []
    for idx, item in enumerate(res.get("pareto_front", [])):
        pareto_candidates.append(ParetoCandidate(
            id=f"pareto_{idx+1}",
            rank=idx+1,
            is_pareto=True,
            candidate=item["candidate"],
            comfort_score=round(item["comfort_score"], 1),
            annual_energy_kwh=round(item["annual_energy_kwh"], 0),
            cost_inr=round(item["cost_inr"], 0),
            carbon_kg=round(item["carbon_kg"], 0),
            resilience_score=round(item.get("resilience_score", 80.0), 1),
            discomfort_pmv=round(item.get("discomfort_pmv", 0.3), 2),
            avg_indoor_temp=round(item.get("avg_indoor_temp", 28.0), 1),
            peak_indoor_temp=round(item.get("peak_indoor_temp", 33.0), 1),
            fitness_score=round(item.get("fitness", 0.8), 3),
            rationale=item.get("rationale")
        ))
        
    all_cand_list = []
    for idx, item in enumerate(res.get("all_candidates", [])):
        all_cand_list.append(ParetoCandidate(
            id=f"cand_{idx+1}",
            rank=idx+1,
            is_pareto=bool(item.get("is_pareto", False)),
            candidate=item["candidate"],
            comfort_score=round(item["comfort_score"], 1),
            annual_energy_kwh=round(item["annual_energy_kwh"], 0),
            cost_inr=round(item["cost_inr"], 0),
            carbon_kg=round(item["carbon_kg"], 0),
            resilience_score=round(item.get("resilience_score", 80.0), 1),
            discomfort_pmv=round(item.get("discomfort_pmv", 0.3), 2),
            avg_indoor_temp=round(item.get("avg_indoor_temp", 28.0), 1),
            peak_indoor_temp=round(item.get("peak_indoor_temp", 33.0), 1),
            fitness_score=round(item.get("fitness", 0.8), 3),
            rationale=item.get("rationale")
        ))
        
    top_4_raw = res.get("top_4_designs", {})
    fallback = pareto_candidates[0] if pareto_candidates else all_cand_list[0]
    
    def _to_cand(raw_item, fallback_item):
        if not raw_item:
            return fallback_item
        return ParetoCandidate(
            id="rec_top",
            rank=1,
            is_pareto=True,
            candidate=raw_item["candidate"],
            comfort_score=round(raw_item["comfort_score"], 1),
            annual_energy_kwh=round(raw_item["annual_energy_kwh"], 0),
            cost_inr=round(raw_item["cost_inr"], 0),
            carbon_kg=round(raw_item["carbon_kg"], 0),
            resilience_score=round(raw_item.get("resilience_score", 80.0), 1),
            discomfort_pmv=round(raw_item.get("discomfort_pmv", 0.3), 2),
            avg_indoor_temp=round(raw_item.get("avg_indoor_temp", 28.0), 1),
            peak_indoor_temp=round(raw_item.get("peak_indoor_temp", 33.0), 1),
            fitness_score=round(raw_item.get("fitness", 0.8), 3),
            rationale=raw_item.get("rationale")
        )
        
    top_4 = RecommendedTop4(
        best_balanced=_to_cand(top_4_raw.get("best_balanced"), fallback),
        best_comfort=_to_cand(top_4_raw.get("best_comfort"), fallback),
        lowest_energy=_to_cand(top_4_raw.get("lowest_energy"), fallback),
        lowest_cost=_to_cand(top_4_raw.get("lowest_cost"), fallback)
    )
    
    return OptimizationResponse(
        location_id=req.location_id or "sambalpur",
        population_size=req.population_size,
        weights={"w_comfort": req.w_comfort, "w_cost": req.w_cost, "w_carbon": req.w_carbon},
        total_evaluated=len(all_cand_list),
        pareto_front_count=len(pareto_candidates),
        pareto_front=pareto_candidates,
        all_candidates=all_cand_list,
        top_4_designs=top_4
    )
