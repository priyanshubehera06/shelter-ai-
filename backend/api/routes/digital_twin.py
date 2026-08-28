"""
digital_twin.py — REST API endpoints for 3D Digital Twin geometry, solar vectors, and thermal scalar fields.
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.digital_twin import DigitalTwinConfigRequest, DigitalTwinConfigResponse
from backend.services.digital_twin_service import get_digital_twin_config

router = APIRouter(prefix="/digital-twin", tags=["Digital Twin"])


@router.post("/config", response_model=DigitalTwinConfigResponse)
def compute_digital_twin_configuration(req: DigitalTwinConfigRequest):
    """
    Computes precise 3D component bounding geometry, NOAA solar trajectory,
    incident solar radiation angles, and Sol-Air thermal scalar colors for React Three Fiber.
    """
    try:
        return get_digital_twin_config(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Digital Twin config error: {str(e)}")
