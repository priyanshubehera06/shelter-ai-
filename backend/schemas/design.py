"""
design.py — Pydantic schemas for Parametric Shelter Geometry, Design Variants & Envelopes.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class GeometryParams(BaseModel):
    length_m: float = Field(6.0, gt=1.0, le=50.0, description="Internal shelter length in meters")
    width_m: float = Field(4.0, gt=1.0, le=40.0, description="Internal shelter width in meters")
    height_m: float = Field(2.8, gt=1.8, le=8.0, description="Internal wall eaves height per floor in meters")
    floors_count: int = Field(1, ge=1, le=4, description="Number of stories/floors")
    roof_type: str = Field("pitched", description="pitched, monoslope, hipped, gable, or flat")
    roof_pitch_deg: float = Field(15.0, ge=0.0, le=60.0, description="Roof pitch slope in degrees")
    wall_thickness_cm: float = Field(20.0, gt=2.0, le=60.0, description="Wall thickness in cm")
    wwr_pct: float = Field(15.0, ge=0.0, le=80.0, description="Window to wall ratio in percentage")
    overhang_m: float = Field(0.6, ge=0.0, le=2.5, description="Roof overhang shading projection in meters")
    orientation_deg: float = Field(0.0, ge=0.0, le=360.0, description="Azimuth angle clockwise from North (0° = South-facing front)")
    door_width_m: float = Field(0.9, gt=0.5, le=3.0)
    door_height_m: float = Field(2.1, gt=1.5, le=3.5)
    door_count: int = Field(1, ge=1, le=8)
    plinth_height_m: float = Field(0.45, ge=0.0, le=3.0, description="Plinth / stilt foundation elevation above grade")


class MaterialSelection(BaseModel):
    wall_mat_id: str = "cseb_interlocking"
    wall_thickness_cm: float = 20.0
    roof_mat_id: str = "roof_cgi_insulated"
    insulation_mat_id: Optional[str] = "insulation_rockwool"
    insulation_thickness_cm: float = 5.0
    glazing_mat_id: str = "glazing_single"
    floor_mat_id: Optional[str] = "floor_concrete_screed"
    door_mat_id: Optional[str] = "door_solid_timber"


class ShelterDesign(BaseModel):
    id: Optional[str] = None
    name: str = "Custom Shelter Design"
    archetype: Optional[str] = "Parametric Model"
    mode: Optional[str] = Field("normal", description="normal, disaster, migrant")
    disaster_mode: Optional[str] = Field(None, description="Heatwave, Flood, Cyclone, Earthquake, Extreme Rain")
    geometry: GeometryParams = Field(default_factory=GeometryParams)
    materials: MaterialSelection = Field(default_factory=MaterialSelection)
    occupants: int = Field(4, ge=1, le=100, description="Occupancy capacity (Sphere standard)")
    location_id: Optional[str] = "sambalpur"
    created_at: Optional[str] = None


class StructuralMetrics(BaseModel):
    floor_area_m2: float
    gross_volume_m3: float
    gross_wall_area_m2: float
    net_wall_area_m2: float
    window_area_m2: float
    door_area_m2: float
    roof_area_m2: float
    surface_to_volume_ratio: float
    roof_peak_height_m: float
    area_per_person_m2: float
    wall_u_value_w_m2k: float
    roof_u_value_w_m2k: float
