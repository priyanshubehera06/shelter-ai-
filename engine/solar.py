"""
solar.py — Astronomical Solar Calculations and Surface Thermal Physics Engine for ShelterAI.
Provides pure mathematical implementations for NOAA solar positioning, directional surface
incidence angles, beam/diffuse irradiance decomposition, fenestration solar heat gains,
and surface Sol-Air thermal field mappings.
"""

import math
from typing import Dict, List, Optional, Any, Tuple
import numpy as np


# ==============================================================================
# 1. SOLAR ASTRONOMY & POSITION CALCULATIONS (NOAA STANDARD)
# ==============================================================================

def calculate_solar_position(
    lat_deg: float = 34.1526,  # Default: Leh, Ladakh (34.15° N)
    lon_deg: float = 77.5771,  # Default: Leh, Ladakh (77.58° E)
    day_of_year: int = 15,     # Winter January baseline
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
# 2. SURFACE SOLAR IRRADIANCE & FENESTRATION HEAT GAIN
# ==============================================================================

def calculate_surface_incidence_angle(
    solar_alt_deg: float,
    solar_az_deg: float,
    surface_tilt_deg: float,
    surface_az_deg: float
) -> float:
    """
    Calculates the angle of incidence theta between solar rays and surface normal:
    cos(theta) = sin(alpha_s)*cos(beta) + cos(alpha_s)*sin(beta)*cos(gamma_s - gamma)
    where alpha_s = solar altitude, beta = surface tilt (0 = horizontal, 90 = vertical),
          gamma_s = solar azimuth, gamma = surface azimuth.
    """
    if solar_alt_deg <= 0.0:
        return 90.0

    alt_rad = math.radians(solar_alt_deg)
    tilt_rad = math.radians(surface_tilt_deg)
    gamma_diff_rad = math.radians(solar_az_deg - surface_az_deg)

    cos_theta = (
        math.sin(alt_rad) * math.cos(tilt_rad) +
        math.cos(alt_rad) * math.sin(tilt_rad) * math.cos(gamma_diff_rad)
    )
    cos_theta = max(0.0, min(1.0, cos_theta))
    return math.degrees(math.acos(cos_theta))


def calculate_incident_radiation_on_surface(
    ghi_w_m2: float,
    solar_alt_deg: float,
    solar_az_deg: float,
    surface_tilt_deg: float,
    surface_az_deg: float,
    ground_albedo: float = 0.20
) -> float:
    """
    Computes total solar irradiance incident on a tilted/vertical surface (W/m²),
    decomposing global horizontal into beam, diffuse sky, and ground-reflected components (Perez/Liu-Jordan model).
    """
    if ghi_w_m2 <= 0.0 or solar_alt_deg <= 0.0:
        return 0.0

    theta_deg = calculate_surface_incidence_angle(solar_alt_deg, solar_az_deg, surface_tilt_deg, surface_az_deg)
    cos_theta = math.cos(math.radians(theta_deg))
    sin_alt = math.sin(math.radians(solar_alt_deg))

    # Approximate direct-beam fraction based on clear-sky index
    c_ratio = max(0.15, min(0.85, (ghi_w_m2 / 1000.0) ** 0.8))
    dhi = ghi_w_m2 * (1.0 - c_ratio)
    dni = (ghi_w_m2 - dhi) / max(0.05, sin_alt)

    # Beam on surface
    i_beam = max(0.0, dni * cos_theta)
    # Sky diffuse (isotropic view factor)
    tilt_rad = math.radians(surface_tilt_deg)
    i_diffuse = dhi * ((1.0 + math.cos(tilt_rad)) / 2.0)
    # Ground reflected
    i_ground = ghi_w_m2 * ground_albedo * ((1.0 - math.cos(tilt_rad)) / 2.0)

    total_i = i_beam + i_diffuse + i_ground
    return round(float(total_i), 2)


def calculate_fenestration_solar_gain(
    glazed_area_m2: float,
    shgc: float,
    incident_radiation_w_m2: float,
    shading_factor: float = 0.0
) -> float:
    """
    Computes transmitted solar thermal heat gain through window openings in Watts:
    Q_solar = Area * SHGC * I_T * (1 - Shading_Factor)
    """
    unshaded_fraction = max(0.0, min(1.0, 1.0 - shading_factor))
    q_sol = glazed_area_m2 * shgc * incident_radiation_w_m2 * unshaded_fraction
    return round(max(0.0, float(q_sol)), 2)


def calculate_sol_air_temperature(
    t_ambient_c: float,
    incident_rad_w_m2: float,
    solar_absorptivity: float = 0.70,
    h_outdoor: float = 22.7,
    longwave_correction_c: float = 4.0
) -> float:
    """
    Calculates the equivalent Sol-Air temperature for an exterior building surface:
    T_sol-air = T_amb + (alpha * I_T / h_o) - dR_lw
    """
    t_sol = t_ambient_c + (solar_absorptivity * incident_rad_w_m2 / h_outdoor) - longwave_correction_c
    return round(float(t_sol), 2)


# ==============================================================================
# 3. SURFACE THERMAL COLOR MAPPING
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
        'name': 'Dressed Stone / Granite Masonry',
        'color': '#7f8c8d',
        'diffuse': 0.85,
        'specular': 0.05,
        'ambient': 0.25,
        'category': 'Heavy Thermal Mass',
        'description': 'High-density indigenous stone masonry providing high thermal mass damping for high altitudes.'
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
        'description': 'CGI sheet with polyurethane/rockwool core preventing extreme winter radiant heat loss.'
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
    'roof_cool_tile': {
        'name': 'High-SRI Solar Reflective Roof Deck',
        'color': '#f8f9fa',
        'diffuse': 0.95,
        'specular': 0.05,
        'ambient': 0.45,
        'category': 'Cool Roof Coating',
        'description': 'High solar reflectance index ceramic tile coating cutting solar absorption.'
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
    base_temp: float = 20.0,
    max_ghi: float = 850.0
) -> Tuple[str, float]:
    """
    Computes directional Sol-Air temperature and maps it to a continuous engineering heat-flux hex color.
    """
    cos_theta = max(0.0, float(np.dot(normal_vector, sun_vector)))
    sol_air_t = base_temp + (cos_theta * (max_ghi / 30.0))
    norm = float(np.clip((sol_air_t - (-10.0)) / 50.0, 0.0, 1.0))
    if norm < 0.5:
        t = norm * 2.0
        r, g, b = int(41 + t * 202), int(128 + t * 28), int(185 - t * 167)
    else:
        t = (norm - 0.5) * 2.0
        r, g, b = int(243 - t * 12), int(156 - t * 80), int(18 + t * 42)
    return f"#{r:02x}{g:02x}{b:02x}", round(sol_air_t, 1)
