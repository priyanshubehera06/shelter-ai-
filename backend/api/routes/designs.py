"""
designs.py — REST API endpoints for Parametric Shelter Designs and Structural Calculations.
"""

from typing import List
from fastapi import APIRouter, HTTPException
from backend.schemas.design import ShelterDesign, GeometryParams, MaterialSelection, StructuralMetrics
from backend.services.design_service import get_default_designs, calculate_structural_summary

router = APIRouter(prefix="/designs", tags=["Designs"])


@router.get("", response_model=List[ShelterDesign])
def list_designs():
    """Returns baseline and pre-configured climate-resilient shelter archetypes."""
    return get_default_designs()


@router.post("/metrics", response_model=StructuralMetrics)
def compute_structural_metrics(
    geometry: GeometryParams,
    materials: MaterialSelection,
    occupants: int = 4
):
    """Calculates geometric, surface, volume, and envelope metrics for real-time parametric changes."""
    return calculate_structural_summary(geometry, materials, occupants)
