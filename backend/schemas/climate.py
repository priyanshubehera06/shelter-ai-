"""
climate.py — Pydantic models for Climate Analysis & Location Services.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class LocationInfo(BaseModel):
    id: str
    name: str
    city: Optional[str] = None
    state: Optional[str] = None
    region_type: str = "Composite"
    lat: float
    lon: float
    source: str = "Built-in Catalog"
    t_max_summer: float = 38.0
    t_min_winter: float = 18.0
    rh_avg_pct: float = 55.0
    solar_irradiance_peak: float = 900.0
    description: Optional[str] = None


class IPLocationResponse(BaseModel):
    ip: Optional[str] = None
    city: str
    region: str
    country: str
    lat: float
    lon: float
    climate_zone: str
    nearest_station_id: str
    source: str = "IP Geolocation"


class HourlyClimateRecord(BaseModel):
    hour: int
    dry_bulb_temp_c: float
    relative_humidity_pct: float
    solar_ghi_w_m2: float
    wind_speed_m_s: float = 3.0
    wind_direction_deg: float = 180.0
    dew_point_c: Optional[float] = None
    direct_normal_irradiance: Optional[float] = None
    diffuse_horizontal_irradiance: Optional[float] = None


class ClimateSummary(BaseModel):
    location_id: str
    location_name: str
    climate_zone: str
    lat: float
    lon: float
    annual_mean_temp: float
    peak_summer_temp: float
    min_winter_temp: float
    diurnal_range_c: float
    avg_relative_humidity: float
    peak_solar_ghi: float
    hot_hours_count: int
    cold_hours_count: int
    high_solar_hours_count: int
    actionable_insights: List[str]


class ClimateAnalysisResponse(BaseModel):
    summary: ClimateSummary
    hourly_records_24h: List[HourlyClimateRecord]
    monthly_trends: Optional[List[Dict[str, Any]]] = None
    extreme_scenarios: Optional[Dict[str, Any]] = None
