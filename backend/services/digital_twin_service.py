"""
digital_twin_service.py — Service adapter generating 3D geometric, solar, and thermal telemetry for React Three Fiber.
"""

import math
from typing import List, Dict, Any, Optional
import numpy as np
from engine.geometry import ShelterGeometry
from engine.materials import get_material_by_id, calculate_assembly_u_value
from engine.climate import get_climate_profile
from engine.solar import calculate_solar_position, get_solar_vector, calculate_surface_thermal_color
from backend.services.climate_service import get_location_by_id
from backend.schemas.digital_twin import (
    DigitalTwinConfigRequest,
    DigitalTwinConfigResponse,
    SolarPositionData,
    ComponentGeometryData
)


def get_digital_twin_config(req: DigitalTwinConfigRequest) -> DigitalTwinConfigResponse:
    """Computes exact 3D coordinates, real-time NOAA sun trajectory, and component Sol-Air metrics for React Three Fiber."""
    loc = get_location_by_id(req.location_id or "sambalpur")
    lat = loc.lat if loc else 21.46
    lon = loc.lon if loc else 83.98
    
    geom = ShelterGeometry(
        length_m=req.geometry.length_m,
        width_m=req.geometry.width_m,
        height_m=req.geometry.height_m,
        roof_type=req.geometry.roof_type,
        roof_pitch_deg=req.geometry.roof_pitch_deg,
        wall_thickness_cm=req.geometry.wall_thickness_cm,
        wwr_pct=req.geometry.wwr_pct,
        overhang_m=req.geometry.overhang_m,
        orientation_deg=req.geometry.orientation_deg
    )
    
    # Climate hourly metrics
    climate_records = get_climate_profile(month=req.month)
    h_idx = min(23, max(0, int(req.hour_of_day)))
    curr_climate = climate_records[h_idx]
    curr_ghi = float(curr_climate["solar_ghi_w_m2"])
    curr_temp = float(curr_climate["dry_bulb_temp_c"])
    curr_wind = float(curr_climate.get("wind_speed_m_s", 3.0))
    curr_wind_dir = float(curr_climate.get("wind_direction_deg", 180.0))
    
    # NOAA Solar astronomy
    sol_alt, sol_az, is_day = calculate_solar_position(lat, lon, day_of_year=135, hour_of_day=req.hour_of_day)
    sun_vec = get_solar_vector(sol_alt, sol_az)
    
    # Calculate diurnal solar arc spline for 3D trajectory
    solar_spline = []
    for h in np.linspace(6.0, 18.0, 25):
        alt_h, az_h, _ = calculate_solar_position(lat, lon, day_of_year=135, hour_of_day=h)
        if alt_h > 0:
            v_h = get_solar_vector(alt_h, az_h)
            r_dist = max(geom.length, geom.width) * 2.2
            solar_spline.append([
                float(v_h[0] * r_dist),
                float(v_h[1] * r_dist),
                float(v_h[2] * r_dist)
            ])
            
    r_sun = max(geom.length, geom.width) * 2.2
    sun_pos_3d = [float(sun_vec[0] * r_sun), float(sun_vec[1] * r_sun), float(sun_vec[2] * r_sun)] if is_day else [0.0, 0.0, -10.0]
    
    solar_data = SolarPositionData(
        hour=req.hour_of_day,
        altitude_deg=round(sol_alt, 2),
        azimuth_deg=round(sol_az, 2),
        is_daylight=is_day,
        solar_vector=[float(sun_vec[0]), float(sun_vec[1]), float(sun_vec[2])],
        sun_position_3d=sun_pos_3d,
        solar_path_spline=solar_spline,
        solar_ghi_w_m2=curr_ghi
    )
    
    # Compute component-level geometries and Sol-Air temperatures
    components: List[ComponentGeometryData] = []
    
    wall_mat = get_material_by_id(req.materials.wall_mat_id)
    roof_mat = get_material_by_id(req.materials.roof_mat_id)
    u_wall = calculate_assembly_u_value(req.materials.wall_mat_id, req.materials.wall_thickness_cm)["u_value_w_m2k"]
    u_roof = calculate_assembly_u_value(req.materials.roof_mat_id, 10.0)["u_value_w_m2k"]
    
    # South Wall (Front)
    s_col, s_temp = calculate_surface_thermal_color(np.array([0.0, -1.0, 0.0]), sun_vec, base_temp=curr_temp, max_ghi=curr_ghi)
    components.append(ComponentGeometryData(
        name="Front Wall (South)",
        component_type="wall",
        dimensions={"length": geom.length, "height": geom.height, "thickness": geom.wall_thickness},
        position=[0.0, -geom.width/2.0, geom.height/2.0],
        rotation=[0.0, 0.0, 0.0],
        material_id=req.materials.wall_mat_id,
        material_name=wall_mat["name"],
        u_value=round(u_wall, 3),
        sol_air_temp_c=s_temp,
        thermal_color_hex=s_col
    ))
    
    # North Wall (Back)
    n_col, n_temp = calculate_surface_thermal_color(np.array([0.0, 1.0, 0.0]), sun_vec, base_temp=curr_temp, max_ghi=curr_ghi)
    components.append(ComponentGeometryData(
        name="Back Wall (North)",
        component_type="wall",
        dimensions={"length": geom.length, "height": geom.height, "thickness": geom.wall_thickness},
        position=[0.0, geom.width/2.0, geom.height/2.0],
        rotation=[0.0, 0.0, 0.0],
        material_id=req.materials.wall_mat_id,
        material_name=wall_mat["name"],
        u_value=round(u_wall, 3),
        sol_air_temp_c=n_temp,
        thermal_color_hex=n_col
    ))
    
    # East Wall (Right)
    e_col, e_temp = calculate_surface_thermal_color(np.array([1.0, 0.0, 0.0]), sun_vec, base_temp=curr_temp, max_ghi=curr_ghi)
    components.append(ComponentGeometryData(
        name="East Wall",
        component_type="wall",
        dimensions={"length": geom.width, "height": geom.height, "thickness": geom.wall_thickness},
        position=[geom.length/2.0, 0.0, geom.height/2.0],
        rotation=[0.0, 0.0, 90.0],
        material_id=req.materials.wall_mat_id,
        material_name=wall_mat["name"],
        u_value=round(u_wall, 3),
        sol_air_temp_c=e_temp,
        thermal_color_hex=e_col
    ))
    
    # West Wall (Left)
    w_col, w_temp = calculate_surface_thermal_color(np.array([-1.0, 0.0, 0.0]), sun_vec, base_temp=curr_temp, max_ghi=curr_ghi)
    components.append(ComponentGeometryData(
        name="West Wall",
        component_type="wall",
        dimensions={"length": geom.width, "height": geom.height, "thickness": geom.wall_thickness},
        position=[-geom.length/2.0, 0.0, geom.height/2.0],
        rotation=[0.0, 0.0, 90.0],
        material_id=req.materials.wall_mat_id,
        material_name=wall_mat["name"],
        u_value=round(u_wall, 3),
        sol_air_temp_c=w_temp,
        thermal_color_hex=w_col
    ))
    
    # Roof Assembly
    r_col, r_temp = calculate_surface_thermal_color(np.array([0.0, 0.0, 1.0]), sun_vec, base_temp=curr_temp, max_ghi=curr_ghi)
    components.append(ComponentGeometryData(
        name=f"Roof ({geom.roof_type.title()})",
        component_type="roof",
        dimensions={"length": geom.length + 2*geom.overhang, "width": geom.width + 2*geom.overhang, "thickness": 0.08},
        position=[0.0, 0.0, geom.height + geom.roof_height_delta()/2.0],
        rotation=[0.0, 0.0, 0.0],
        material_id=req.materials.roof_mat_id,
        material_name=roof_mat["name"],
        u_value=round(u_roof, 3),
        sol_air_temp_c=r_temp,
        thermal_color_hex=r_col
    ))
    
    # Foundation Plinth
    components.append(ComponentGeometryData(
        name="Foundation Plinth Slab",
        component_type="foundation",
        dimensions={"length": geom.length + 0.4, "width": geom.width + 0.4, "thickness": 0.20},
        position=[0.0, 0.0, -0.10],
        rotation=[0.0, 0.0, 0.0],
        material_id="roof_concrete_slab",
        material_name="Reinforced Concrete Slab",
        u_value=1.80,
        sol_air_temp_c=curr_temp,
        thermal_color_hex="#7f8c8d"
    ))
    
    camera_presets = {
        "isometric": {"position": [geom.length * 1.5, -geom.width * 1.8, geom.height * 1.7], "target": [0.0, 0.0, geom.height * 0.4]},
        "front": {"position": [0.0, -geom.width * 2.5, geom.height * 0.6], "target": [0.0, 0.0, geom.height * 0.4]},
        "side": {"position": [geom.length * 2.5, 0.0, geom.height * 0.6], "target": [0.0, 0.0, geom.height * 0.4]},
        "top": {"position": [0.0, 0.01, geom.height * 4.0], "target": [0.0, 0.0, 0.0]},
        "north": {"position": [0.0, geom.width * 2.5, geom.height * 0.6], "target": [0.0, 0.0, geom.height * 0.4]},
    }
    
    airflow_vectors = [
        {"start": [-geom.length * 0.8, 0.0, geom.height * 0.5], "end": [geom.length * 0.8, 0.0, geom.height * 0.5], "speed": curr_wind, "direction_deg": curr_wind_dir}
    ]
    
    return DigitalTwinConfigResponse(
        geometry=req.geometry,
        materials=req.materials,
        components=components,
        solar=solar_data,
        ambient={"temperature_c": curr_temp, "humidity_pct": float(curr_climate["relative_humidity_pct"]), "wind_speed_m_s": curr_wind, "wind_dir_deg": curr_wind_dir},
        camera_presets=camera_presets,
        airflow_vectors=airflow_vectors
    )
