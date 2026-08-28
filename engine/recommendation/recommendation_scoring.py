"""
recommendation_scoring.py — Configurable Multi-Factor Scoring Engine for
Shelter Material and Construction Recommendations.
"""

from typing import Dict, Any, Optional

DEFAULT_WEIGHTS = {
    "thermal": 0.35,
    "cost": 0.25,
    "resilience": 0.20,
    "constructability": 0.10,
    "availability": 0.10
}


def calculate_composite_score(
    thermal_score: float,
    cost_score: float,
    resilience_score: float,
    constructability_score: float,
    availability_score: float,
    weights: Optional[Dict[str, float]] = None
) -> float:
    """
    Computes a transparent, normalized 0-100 score based on multi-factor engineering attributes.
    """
    w = weights or DEFAULT_WEIGHTS
    total_w = sum(w.values()) or 1.0

    score = (
        (thermal_score * w.get("thermal", 0.35)) +
        (cost_score * w.get("cost", 0.25)) +
        (resilience_score * w.get("resilience", 0.20)) +
        (constructability_score * w.get("constructability", 0.10)) +
        (availability_score * w.get("availability", 0.10))
    ) / total_w

    return round(max(0.0, min(100.0, score)), 1)
