"""
tvi_service.py — Service layer handling Thermal Vulnerability Index queries and ranking generation.
"""

from typing import Dict, Any, Optional
from engine.tvi.tvi_engine import calculate_state_tvi, get_all_states_tvi, load_tvi_sources


def query_all_tvi(weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """Retrieves dynamic TVI rankings and transparent scores for all states."""
    return get_all_states_tvi(weights)


def query_state_tvi(state_name: str, weights: Optional[Dict[str, float]] = None) -> Optional[Dict[str, Any]]:
    """Calculates and returns transparent TVI profile for a single state."""
    return calculate_state_tvi(state_name, weights)


def query_tvi_sources() -> Dict[str, Any]:
    """Returns provenance data registry."""
    return {"sources": load_tvi_sources()}
