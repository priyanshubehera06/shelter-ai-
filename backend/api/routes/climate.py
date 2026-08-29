"""
climate.py — REST API endpoints for Location and Climate Intelligence.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from backend.schemas.climate import LocationInfo, IPLocationResponse, ClimateAnalysisResponse
from backend.services.climate_service import (
    get_all_locations,
    get_location_by_id,
    detect_user_ip_location,
    analyze_climate
)

router = APIRouter(prefix="/climate", tags=["Climate"])


@router.get("/locations", response_model=List[LocationInfo])
def list_locations():
    """Returns all available climate locations and major Indian meteorological stations."""
    return get_all_locations()


@router.get("/ip-location", response_model=IPLocationResponse)
def get_current_ip_location(
    lat: Optional[float] = Query(None, description="Optional GPS latitude from client"),
    lon: Optional[float] = Query(None, description="Optional GPS longitude from client")
):
    """Auto-detects the client's geographic location via GPS coordinates or IP and resolves nearest Indian weather station."""
    return detect_user_ip_location(lat=lat, lon=lon)


@router.get("/locations/{location_id}", response_model=LocationInfo)
def get_location(location_id: str):
    """Returns detailed geographic and climate zone metadata for a location."""
    loc = get_location_by_id(location_id)
    if not loc:
        raise HTTPException(status_code=404, detail=f"Location '{location_id}' not found.")
    return loc


@router.get("/analyze/{location_id}", response_model=ClimateAnalysisResponse)
def analyze_location_climate(
    location_id: str,
    month: int = Query(5, ge=1, le=12, description="Month of year (1-12)")
):
    """Executes physics-based climate intelligence, extreme scenarios, and diurnal weather cycles."""
    return analyze_climate(location_id=location_id, month=month)
