"""
digital_twin.py — Pydantic schemas for the 3D Digital Twin configuration and real-time telemetry.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.schemas.design import GeometryParams, MaterialSelection


class DigitalTwinConfigRequest(BaseModel):
    geometry: GeometryParams = Field(default_factory=GeometryParams)
    materials: MaterialSelection = Field(default_factory=MaterialSelection)
    hour_of_day: float = Field(12.0, ge=0.0, le=23.99)
    location_id: Optional[str] = "sambalpur"
    month: int = 5
    view_mode: str = "architectural"


class SolarPositionData(BaseModel):
    hour: float
    altitude_deg: float
    azimuth_deg: float
    is_daylight: bool
    solar_vector: List[float]
    sun_position_3d: List[float]
    solar_path_spline: List[List[float]]
    solar_ghi_w_m2: float


class ComponentGeometryData(BaseModel):
    name: str
    component_type: str  # wall, roof, window, door, foundation, shading
    dimensions: Dict[str, float]
    position: List[float]
    rotation: List[float]
    material_id: str
    material_name: str
    u_value: float
    sol_air_temp_c: Optional[float] = None
    thermal_color_hex: Optional[str] = None
    heat_flux_w: Optional[float] = None


class DigitalTwinConfigResponse(BaseModel):
    geometry: GeometryParams
    materials: MaterialSelection
    components: List[ComponentGeometryData]
    solar: SolarPositionData
    ambient: Dict[str, float]
    camera_presets: Dict[str, Dict[str, List[float]]]
    airflow_vectors: Optional[List[Dict[str, Any]]] = None
