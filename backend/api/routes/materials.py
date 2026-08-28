"""
materials.py — REST API endpoints for Materials Catalog, Thermo-Physical Properties & Assemblies.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.schemas.material import MaterialItem, AssemblyUValueRequest, AssemblyUValueResponse
from backend.services.material_service import get_all_materials, get_material, calculate_u_value

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.get("", response_model=List[MaterialItem])
def list_materials(category: Optional[str] = Query(None, description="Filter by Wall, Roof, Glazing, Insulation")):
    """Returns complete catalog of envelope construction materials with physical and economic properties."""
    materials = get_all_materials()
    if category:
        materials = [m for m in materials if m.category.lower() == category.lower()]
    return materials


@router.get("/{material_id}", response_model=MaterialItem)
def get_single_material(material_id: str):
    """Retrieves physical thermal properties and cost for a single material."""
    mat = get_material(material_id)
    if not mat:
        raise HTTPException(status_code=404, detail=f"Material '{material_id}' not found in catalog.")
    return mat


@router.post("/u-value", response_model=AssemblyUValueResponse)
def compute_assembly_u_value(req: AssemblyUValueRequest):
    """Calculates overall U-value, thermal resistance (R-value), and thermal mass for a layered envelope assembly."""
    return calculate_u_value(req)
