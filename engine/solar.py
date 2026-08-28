"""
solar.py — Astronomical Solar Calculations and Surface Thermal Physics Engine for ShelterAI.
Provides pure mathematical implementations for NOAA solar positioning, solar vector projection,
and surface Sol-Air thermal color mappings with ZERO external 3D/graphics dependencies.
"""

import math
from typing import Dict, List, Optional, Any, Tuple
import numpy as np


# ==============================================================================
# 1. SOLAR ASTRONOMY & POSITION CALCULATIONS (NOAA STANDARD)
# ==============================================================================

def calculate_solar_position(
    lat_deg: float = 21.4669,
    lon_deg: float = 83.9812,
    day_of_year: int = 135,
    hour_of_day: float = 12.0,
    timezone_offset: float = 5.5
) -> Tuple[float, float, bool]:
    """
    Computes precise astronomical solar altitude and azimuth angles using the NOAA Solar Geometry model.

    Returns:
        altitude_deg: Solar elevation above the local horizon (0 to 90 degrees).
        azimuth_deg: Solar azimuth angle from True North (0 to 360 degrees, clockwise).
        is_daylight: Boolean flag indicating if sun is above horizon.
    """
    lat_rad = math.radians(lat_deg)
    gamma = 2.0 * math.pi / 365.0 * (day_of_year - 1 + (hour_of_day - 12.0) / 24.0)
    eqtime = 229.18 * (
        0.000075
        + 0.001868 * math.cos(gamma)
        - 0.032077 * math.sin(gamma)
        - 0.014615 * math.cos(2 * gamma)
        - 0.040849 * math.sin(2 * gamma)
    )
    decl = (
        0.006918
        - 0.399912 * math.cos(gamma)
        + 0.070257 * math.sin(gamma)
        - 0.006758 * math.cos(2 * gamma)
        + 0.000907 * math.sin(2 * gamma)
        - 0.002697 * math.cos(3 * gamma)
        + 0.00148 * math.sin(3 * gamma)
    )
    time_offset = eqtime + 4.0 * lon_deg - 60.0 * timezone_offset
    tst = hour_of_day * 60.0 + time_offset
    ha_deg = (tst / 4.0) - 180.0
    ha_rad = math.radians(ha_deg)

    cos_zenith = math.sin(lat_rad) * math.sin(decl) + math.cos(lat_rad) * math.cos(decl) * math.cos(ha_rad)
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    zenith_rad = math.acos(cos_zenith)
    altitude_deg = 90.0 - math.degrees(zenith_rad)

    is_daylight = altitude_deg > 0.0
    if not is_daylight:
        altitude_deg = 0.0

    cos_az = (math.sin(decl) - math.cos(zenith_rad) * math.sin(lat_rad)) / (
        math.sin(zenith_rad) * math.cos(lat_rad) + 1e-9
    )
    cos_az = max(-1.0, min(1.0, cos_az))
    azimuth_rad = math.acos(cos_az)
    azimuth_deg = math.degrees(azimuth_rad)

    if ha_deg > 0:
        azimuth_deg = (360.0 - azimuth_deg) % 360.0
    else:
        azimuth_deg = azimuth_deg % 360.0

    return round(altitude_deg, 2), round(azimuth_deg, 2), is_daylight


def get_solar_vector(altitude_deg: float, azimuth_deg: float) -> np.ndarray:
    """
    Converts spherical solar coordinates into a 3D Cartesian unit direction vector [vx, vy, vz].
    Coordinate system: X = East, Y = North, Z = Zenith/Up.
    """
    alt_rad = math.radians(altitude_deg)
    az_rad = math.radians(azimuth_deg)
    vx = math.sin(az_rad) * math.cos(alt_rad)
    vy = math.cos(az_rad) * math.cos(alt_rad)
    vz = math.sin(alt_rad)
    vec = np.array([vx, vy, vz], dtype=float)
    norm = np.linalg.norm(vec)
    return vec / norm if norm > 0 else np.array([0.0, 0.0, 1.0])


# ==============================================================================
# 2. SURFACE THERMAL COLOR & SOL-AIR TEMPERATURE MAPPING
# ==============================================================================

MATERIAL_SPECS = {
    'cseb_interlocking': {
        'name': 'Compressed Earth Block (CSEB)',
        'color': '#c0392b',
        'diffuse': 0.85,
        'specular': 0.08,
        'ambient': 0.30,
        'category': 'High Thermal Mass',
        'description': 'Eco-friendly stabilized earth block with excellent diurnal thermal inertia.'
    },
    'brick_standard': {
        'name': 'Burnt Clay Brick Masonry',
        'color': '#d35400',
        'diffuse': 0.85,
        'specular': 0.10,
        'ambient': 0.30,
        'category': 'High Thermal Mass',
        'description': 'Traditional burnt clay brick wall with high durability.'
    },
    'aac_block': {
        'name': 'Autoclaved Aerated Concrete (AAC)',
        'color': '#bdc3c7',
        'diffuse': 0.80,
        'specular': 0.05,
        'ambient': 0.35,
        'category': 'Insulative Lightweight',
        'description': 'Lightweight precast foam concrete with superior thermal insulation.'
    },
    'stone_masonry': {
        'name': 'Dressed Stone Masonry',
        'color': '#7f8c8d',
        'diffuse': 0.85,
        'specular': 0.05,
        'ambient': 0.25,
        'category': 'Heavy Thermal Mass',
        'description': 'High-density indigenous stone masonry with high thermal damping.'
    },
    'eps_sandwich_panel': {
        'name': 'EPS Insulated Sandwich Panel',
        'color': '#ecf0f1',
        'diffuse': 0.90,
        'specular': 0.15,
        'ambient': 0.40,
        'category': 'Super-Insulated',
        'description': 'Prefabricated structural insulated panel with high thermal resistance.'
    },
    'bamboo_composite': {
        'name': 'Treated Bamboo Composite',
        'color': '#d4ac0d',
        'diffuse': 0.85,
        'specular': 0.08,
        'ambient': 0.30,
        'category': 'Bio-Based Lightweight',
        'description': 'Rapid-renewable engineered bamboo panel for tropical humid climates.'
    },
    'roof_cgi_sheet': {
        'name': 'Corrugated Galvanized Iron (CGI)',
        'color': '#95a5a6',
        'diffuse': 0.70,
        'specular': 0.40,
        'ambient': 0.20,
        'category': 'Lightweight Metal',
        'description': 'Economical corrugated iron sheet requiring radiant under-roof insulation.'
    },
    'roof_cgi_insulated': {
        'name': 'Insulated Sandwich CGI Roof',
        'color': '#7f8c8d',
        'diffuse': 0.75,
        'specular': 0.25,
        'ambient': 0.30,
        'category': 'Insulated Metal',
        'description': 'CGI sheet with polyurethane core preventing severe summer radiant heat gain.'
    },
    'roof_insulated_cgi': {
        'name': 'Insulated Sandwich CGI Roof',
        'color': '#7f8c8d',
        'diffuse': 0.75,
        'specular': 0.25,
        'ambient': 0.30,
        'category': 'Insulated Metal',
        'description': 'CGI sheet with polyurethane core preventing severe summer radiant heat gain.'
    },
    'roof_terracotta_tile': {
        'name': 'Mangalore Terracotta Clay Tile',
        'color': '#e67e22',
        'diffuse': 0.88,
        'specular': 0.05,
        'ambient': 0.30,
        'category': 'Breathable Clay',
        'description': 'Traditional pitched clay roof allowing natural attic convective cooling.'
    },
    'roof_concrete_slab': {
        'name': 'Reinforced Concrete Slab (RCC)',
        'color': '#34495e',
        'diffuse': 0.88,
        'specular': 0.08,
        'ambient': 0.25,
        'category': 'Heavy Thermal Mass',
        'description': 'Monolithic concrete slab with high thermal storage and long lifespan.'
    },
    'roof_bamboo_thatch': {
        'name': 'Bamboo Thatch & Mud Tile',
        'color': '#a0522d',
        'diffuse': 0.90,
        'specular': 0.05,
        'ambient': 0.30,
        'category': 'Organic Passive',
        'description': 'Natural thatched roofing providing superior radiant heat rejection.'
    },
    'roof_solar_pv': {
        'name': 'Building Integrated PV (BIPV) Roof',
        'color': '#1a252f',
        'diffuse': 0.60,
        'specular': 0.60,
        'ambient': 0.20,
        'category': 'Active Solar',
        'description': 'High-efficiency monocrystalline solar roof generating clean electricity.'
    }
}


def get_material_colors(wall_mat_id: str, roof_mat_id: str) -> Tuple[str, str, str, str]:
    """Retrieves wall and roof hex color codes and human-readable names."""
    w_key = str(wall_mat_id).lower()
    r_key = str(roof_mat_id).lower()
    w_spec = MATERIAL_SPECS.get(w_key, None)
    if not w_spec:
        for k, v in MATERIAL_SPECS.items():
            if k in w_key or any(w in w_key for w in k.split('_')):
                w_spec = v
                break
    if not w_spec:
        w_spec = {'name': str(wall_mat_id).replace('_', ' ').title(), 'color': '#c0392b'}

    r_spec = MATERIAL_SPECS.get(r_key, None)
    if not r_spec:
        for k, v in MATERIAL_SPECS.items():
            if k in r_key or any(w in r_key for w in k.split('_')):
                r_spec = v
                break
    if not r_spec:
        r_spec = {'name': str(roof_mat_id).replace('_', ' ').title(), 'color': '#2980b9'}

    return w_spec['color'], r_spec['color'], w_spec['name'], r_spec['name']


def calculate_surface_thermal_color(
    normal_vector: np.ndarray,
    sun_vector: np.ndarray,
    base_temp: float = 30.0,
    max_ghi: float = 850.0
) -> Tuple[str, float]:
    """
    Computes directional Sol-Air temperature and maps it to a continuous engineering heat-flux hex color.
    """
    cos_theta = max(0.0, float(np.dot(normal_vector, sun_vector)))
    sol_air_t = base_temp + (cos_theta * (max_ghi / 30.0))
    norm = float(np.clip((sol_air_t - 20.0) / 35.0, 0.0, 1.0))
    if norm < 0.5:
        t = norm * 2.0
        r, g, b = int(41 + t * 202), int(128 + t * 28), int(185 - t * 167)
    else:
        t = (norm - 0.5) * 2.0
        r, g, b = int(243 - t * 12), int(156 - t * 80), int(18 + t * 42)
    return f"#{r:02x}{g:02x}{b:02x}", round(sol_air_t, 1)
