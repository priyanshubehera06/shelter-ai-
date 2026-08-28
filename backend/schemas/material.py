"""
material.py — Pydantic schemas for Materials Catalog and Thermal Assembly Properties.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class MaterialItem(BaseModel):
    id: str
    name: str
    category: str = Field(..., description="Wall, Roof, Floor, Glazing, Insulation")
    thermal_cond_w_mk: float = Field(..., gt=0.0, description="Thermal conductivity k in W/m-K")
    density_kg_m3: float = Field(..., gt=0.0, description="Density in kg/m3")
    specific_heat_j_kgk: float = Field(..., gt=0.0, description="Specific heat capacity in J/kg-K")
    embodied_carbon_kgco2_kg: float = Field(..., ge=0.0, description="Embodied carbon in kgCO2e/kg")
    unit_cost_inr_m2: float = Field(..., ge=0.0, description="Unit material CapEx cost in INR per m2")
    thickness_options: Optional[str] = "10;15;20"
    availability_score: float = 8.0
    description: Optional[str] = ""
    # Visual / Texture mappings for 3D Digital Twin
    texture_url: Optional[str] = None
    color_hex: Optional[str] = "#b58d6b"
    roughness: Optional[float] = 0.85
    metalness: Optional[float] = 0.05


class AssemblyUValueRequest(BaseModel):
    core_mat_id: str
    thickness_cm: float = Field(..., gt=0.0, description="Thickness in cm")
    ins_mat_id: Optional[str] = None
    ins_thickness_cm: float = Field(0.0, ge=0.0, description="Insulation thickness in cm")


class AssemblyUValueResponse(BaseModel):
    core_mat_id: str
    core_name: str
    thickness_cm: float
    ins_mat_id: Optional[str] = None
    ins_name: Optional[str] = None
    ins_thickness_cm: float
    total_thickness_m: float
    r_value_m2k_w: float
    u_value_w_m2k: float
    thermal_mass_kj_m2k: float
    total_unit_cost_inr_m2: float
    total_embodied_carbon_kgco2_m2: float
