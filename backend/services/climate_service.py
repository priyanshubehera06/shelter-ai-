"""
climate_service.py — Service adapter interfacing with engine.climate and engine.geolocation.
"""

import math
import re
from typing import List, Dict, Any, Optional
import pandas as pd
from engine.climate import (
    load_climate_dataset,
    get_climate_profile,
    calculate_psychrometrics,
    calculate_degree_days,
    validate_climate_data
)
from engine.geolocation import MAJOR_INDIAN_CITIES, get_ip_location
from backend.schemas.climate import (
    LocationInfo,
    IPLocationResponse,
    HourlyClimateRecord,
    ClimateSummary,
    ClimateAnalysisResponse
)


def _slugify(text: str) -> str:
    """Converts city string to a clean identifier slug."""
    text = text.lower().strip()
    text = re.sub(r'[\(\),&]', '', text)
    text = re.sub(r'\s+', '_', text)
    return text


def get_all_locations() -> List[LocationInfo]:
    """Retrieves all major Indian cities from the catalog with climate classifications."""
    locations: List[LocationInfo] = []
    
    # Priority locations with detailed benchmark metrics
    benchmarks = {
        "sambalpur": {
            "t_max": 43.5, "t_min": 12.1, "rh": 78.0, "solar": 950.0,
            "desc": "Hot dry summers with intense monsoons and mild winters."
        },
        "barmer": {
            "t_max": 45.0, "t_min": 8.0, "rh": 35.0, "solar": 1050.0,
            "desc": "Extreme diurnal temperature range with high direct solar irradiation."
        },
        "puri": {
            "t_max": 35.0, "t_min": 22.0, "rh": 84.0, "solar": 850.0,
            "desc": "Coastal tropical environment requiring high natural cross-ventilation."
        },
        "leh": {
            "t_max": 22.0, "t_min": -15.0, "rh": 38.0, "solar": 980.0,
            "desc": "Extreme winter freezing requiring high thermal insulation envelope."
        },
        "delhi": {
            "t_max": 44.0, "t_min": 5.0, "rh": 50.0, "solar": 950.0,
            "desc": "Extreme composite climate with hot summers and cold winters."
        },
        "mumbai": {
            "t_max": 36.0, "t_min": 19.0, "rh": 80.0, "solar": 880.0,
            "desc": "Coastal warm-humid climate requiring shaded high ventilation."
        },
        "bengaluru": {
            "t_max": 34.0, "t_min": 15.0, "rh": 65.0, "solar": 900.0,
            "desc": "Temperate climate with comfortable year-round temperatures."
        },
        "chennai": {
            "t_max": 39.0, "t_min": 21.0, "rh": 75.0, "solar": 920.0,
            "desc": "Hot and humid coastal climate requiring active shading."
        },
        "kolkata": {
            "t_max": 38.5, "t_min": 14.0, "rh": 78.0, "solar": 890.0,
            "desc": "Warm and humid delta region with heavy monsoon precipitation."
        },
        "jaipur": {
            "t_max": 43.0, "t_min": 8.5, "rh": 42.0, "solar": 980.0,
            "desc": "Hot and semi-arid climate with high summer solar exposure."
        },
        "hyderabad": {
            "t_max": 41.0, "t_min": 14.5, "rh": 52.0, "solar": 940.0,
            "desc": "Semi-arid plateau climate with warm summers and mild winters."
        },
        "shimla": {
            "t_max": 25.0, "t_min": 1.0, "rh": 60.0, "solar": 850.0,
            "desc": "Mountain temperate climate with cool summers and cold winters."
        },
        "srinagar": {
            "t_max": 30.0, "t_min": -2.0, "rh": 70.0, "solar": 850.0,
            "desc": "Cold valley climate with freezing winter months."
        },
        "guwahati": {
            "t_max": 34.0, "t_min": 10.5, "rh": 82.0, "solar": 820.0,
            "desc": "Subtropical humid river basin with prolonged monsoons."
        },
        "ahmedabad": {
            "t_max": 43.5, "t_min": 12.0, "rh": 48.0, "solar": 960.0,
            "desc": "Hot and dry climate with intense summer temperatures."
        }
    }
    
    seen_ids = set()
    
    # Process all cities from MAJOR_INDIAN_CITIES in engine.geolocation
    for key, info in MAJOR_INDIAN_CITIES.items():
        city_name = info.get("city", key.split(",")[0].strip())
        state_name = info.get("state", "")
        zone = info.get("zone", "Composite")
        loc_id = "leh_ladakh" if city_name.lower() == "leh" else _slugify(city_name)
        
        # Avoid duplicate ids
        if loc_id in seen_ids:
            loc_id = _slugify(f"{city_name}_{state_name}")
        seen_ids.add(loc_id)
        
        # Fetch benchmark or estimate from climate zone
        bench = benchmarks.get(loc_id, benchmarks.get(_slugify(city_name), {}))
        
        t_max = bench.get("t_max", 38.0 if "Hot" in zone else 33.0 if "Warm" in zone else 24.0 if "Cold" in zone else 35.0)
        t_min = bench.get("t_min", 8.0 if "Arid" in zone else 20.0 if "Humid" in zone else 0.0 if "Cold" in zone else 14.0)
        rh = bench.get("rh", 75.0 if "Humid" in zone else 38.0 if "Arid" in zone else 55.0)
        solar = bench.get("solar", 1000.0 if "Arid" in zone else 850.0 if "Humid" in zone else 920.0)
        desc = bench.get("desc", f"{zone} climate zone in {state_name}, India.")
        
        locations.append(LocationInfo(
            id=loc_id,
            name=f"{city_name}, {state_name}",
            city=city_name,
            state=state_name,
            region_type=zone,
            lat=float(info["lat"]),
            lon=float(info["lon"]),
            source="Major Indian Cities Catalog",
            t_max_summer=t_max,
            t_min_winter=t_min,
            rh_avg_pct=rh,
            solar_irradiance_peak=solar,
            description=desc
        ))
        
    return locations


def get_location_by_id(location_id: str) -> Optional[LocationInfo]:
    """Retrieves single location metadata by ID or city name."""
    loc_clean = location_id.lower().strip().replace("-", "_").replace(" ", "_")
    all_locs = get_all_locations()
    for loc in all_locs:
        if loc.id.lower() == loc_clean or (loc_clean in ["leh", "leh_ladakh", "ladakh"] and "leh" in loc.id.lower()):
            return loc
        if loc_clean in loc.id.lower() or (loc.city and loc_clean in loc.city.lower()):
            return loc
    return None


def detect_user_ip_location() -> IPLocationResponse:
    """Auto-detects user location via IP and maps to the nearest Indian city in catalog."""
    ip_data = get_ip_location()
    user_lat = float(ip_data.get("lat", 21.4669))
    user_lon = float(ip_data.get("lon", 83.9812))
    
    # Find nearest Indian city by Euclidean distance
    all_locs = get_all_locations()
    nearest_loc = min(
        all_locs,
        key=lambda l: (l.lat - user_lat)**2 + (l.lon - user_lon)**2
    )
    
    return IPLocationResponse(
        ip=ip_data.get("ip", "Auto-detected"),
        city=ip_data.get("city", nearest_loc.city or "Sambalpur"),
        region=ip_data.get("region", nearest_loc.state or "Odisha"),
        country=ip_data.get("country", "India"),
        lat=user_lat,
        lon=user_lon,
        climate_zone=nearest_loc.region_type,
        nearest_station_id=nearest_loc.id,
        source=ip_data.get("source", "IP Geolocation")
    )


def analyze_climate(location_id: str = "leh_ladakh", month: int = 1) -> ClimateAnalysisResponse:
    """Performs deep climate intelligence analysis on the location and month."""
    loc = get_location_by_id(location_id)
    loc_name = loc.name if loc else location_id.title()
    loc_zone = loc.region_type if loc else "Cold & High-Altitude"
    loc_lat = loc.lat if loc else 34.15
    loc_lon = loc.lon if loc else 77.58
    
    # Load 24-hr representative diurnal cycle from physics engine for target location
    records = get_climate_profile(location_id=loc.id if loc else location_id, month=month)
    hourly_objs: List[HourlyClimateRecord] = []
    
    temps = []
    rhs = []
    ghis = []
    for r in records:
        h = int(r["hour"])
        t = float(r["dry_bulb_temp_c"])
        rh = float(r["relative_humidity_pct"])
        ghi = float(r["solar_ghi_w_m2"])
        w_spd = float(r.get("wind_speed_m_s", 3.0))
        w_dir = float(r.get("wind_direction_deg", 180.0))
        
        temps.append(t)
        rhs.append(rh)
        ghis.append(ghi)
        
        hourly_objs.append(HourlyClimateRecord(
            hour=h,
            dry_bulb_temp_c=t,
            relative_humidity_pct=rh,
            solar_ghi_w_m2=ghi,
            wind_speed_m_s=w_spd,
            wind_direction_deg=w_dir
        ))
        
    df_raw = load_climate_dataset()
    
    t_mean = float(df_raw["temperature"].mean()) if not df_raw.empty else float(sum(temps)/len(temps))
    t_max = float(df_raw["temperature"].max()) if not df_raw.empty else max(temps)
    t_min = float(df_raw["temperature"].min()) if not df_raw.empty else min(temps)
    hot_hours = int((df_raw["temperature"] > 35.0).sum()) if not df_raw.empty else sum(1 for x in temps if x > 35) * 30
    cold_hours = int((df_raw["temperature"] < 15.0).sum()) if not df_raw.empty else sum(1 for x in temps if x < 15) * 30
    high_solar = int((df_raw["solar_radiation"] > 700.0).sum()) if not df_raw.empty else sum(1 for x in ghis if x > 700) * 30
    
    insights = [
        f"Critical Solar Heat Load: Peak GHI reaches {max(ghis):.0f} W/m² requiring continuous reflective/insulated roofing.",
        f"Diurnal Thermal Lag: Diurnal swing of {max(temps) - min(temps):.1f}°C indicates high efficacy for high thermal mass wall assemblies (CSEB/Masonry).",
        f"Natural Ventilation: Prevailing breezes ({sum(r.wind_speed_m_s for r in hourly_objs)/len(hourly_objs):.1f} m/s) support cross-ventilation through operable louvers."
    ]
    
    summary = ClimateSummary(
        location_id=location_id,
        location_name=loc_name,
        climate_zone=loc_zone,
        lat=float(loc_lat),
        lon=float(loc_lon),
        annual_mean_temp=round(t_mean, 1),
        peak_summer_temp=round(t_max, 1),
        min_winter_temp=round(t_min, 1),
        diurnal_range_c=round(max(temps) - min(temps), 1),
        avg_relative_humidity=round(sum(rhs)/len(rhs), 1),
        peak_solar_ghi=round(max(ghis), 1),
        hot_hours_count=hot_hours,
        cold_hours_count=cold_hours,
        high_solar_hours_count=high_solar,
        actionable_insights=insights
    )
    
    return ClimateAnalysisResponse(
        summary=summary,
        hourly_records_24h=hourly_objs,
        extreme_scenarios={
            "extreme_hot": {"peak_temp_c": 44.5, "solar_ghi_peak": 1050.0, "risk": "High Overheating"},
            "normal": {"peak_temp_c": max(temps), "solar_ghi_peak": max(ghis), "risk": "Moderate"},
            "extreme_cold": {"min_temp_c": -2.0, "solar_ghi_peak": 400.0, "risk": "Freezing Risk"}
        }
    )
