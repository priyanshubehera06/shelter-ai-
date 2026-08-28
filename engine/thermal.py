"""
thermal.py — Dynamic transient thermal physics and multi-component heat balance engine for ShelterAI.
Simulates time-dependent 24-hour heat flow (Solar capture, envelope conduction, subfloor ground flux,
fenestration loss, thermal mass storage/release, and ventilation) with day/night thermal analysis.
"""

import math
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from engine.materials import calculate_assembly_u_value, calculate_composite_assembly_u_value, get_material_by_id
from engine.geometry import ShelterGeometry
from engine.solar import calculate_incident_radiation_on_surface, calculate_fenestration_solar_gain, calculate_solar_position


def calculate_internal_heat_gain(
    occupancy_type: str = "humans",
    occupants: int = 4,
    livestock_count: int = 0,
    livestock_type: str = "cattle",
    equipment_power_w: float = 50.0,
) -> float:
    """
    Computes total internal sensible heat gain (Watts) based on shelter usage archetype:
    - Humans: Sensible metabolic rate (~100 W/person adult avg) + baseline lighting/appliances
    - Livestock: Animal metabolic heat (Cattle: ~400 W, Goats/Sheep: ~90 W, Poultry: ~15 W)
    - Agriculture: Auxiliary equipment / storage lighting
    """
    occ_type = str(occupancy_type).lower()
    total_w = max(0.0, float(equipment_power_w))

    if "human" in occ_type or "residential" in occ_type or "transitional" in occ_type or "emergency" in occ_type or "school" in occ_type or "clinic" in occ_type:
        total_w += max(0, int(occupants)) * 100.0
    elif "livestock" in occ_type or "animal" in occ_type:
        l_type = str(livestock_type).lower()
        if "cattle" in l_type or "cow" in l_type or "buffalo" in l_type:
            heat_per_animal = 400.0
        elif "goat" in l_type or "sheep" in l_type:
            heat_per_animal = 90.0
        elif "poultry" in l_type or "chicken" in l_type:
            heat_per_animal = 15.0
        else:
            heat_per_animal = 150.0
        total_w += max(0, int(livestock_count or occupants)) * heat_per_animal
    elif "agri" in occ_type or "greenhouse" in occ_type or "storage" in occ_type:
        total_w += 150.0

    return round(total_w, 1)


def simulate_shelter_thermal_dynamics(
    geometry: ShelterGeometry,
    wall_mat_id: str = "brick_standard",
    wall_thickness_cm: float = 20.0,
    roof_mat_id: str = "roof_cgi_insulated",
    glazing_mat_id: str = "glazing_single",
    floor_mat_id: str = "floor_concrete_screed",
    door_mat_id: str = "door_solid_timber",
    insulation_mat_id: Optional[str] = None,
    insulation_thickness_cm: float = 0.0,
    wall_layers: Optional[List[Dict[str, Any]]] = None,
    roof_layers: Optional[List[Dict[str, Any]]] = None,
    climate_records: Optional[List[Dict[str, Any]]] = None,
    ach: float = 2.0,
    occupants: int = 4,
    occupancy_type: str = "humans",
    livestock_count: int = 0,
    livestock_type: str = "cattle",
    equipment_power_w: float = 50.0,
    thermal_mass_level: str = "medium",  # "low", "medium", "high"
    temp_threshold_high: float = 26.0,
    temp_threshold_low: float = 18.0,
    lat_deg: float = 34.1526,
    lon_deg: float = 77.5771,
    day_of_year: int = 15
) -> Dict[str, Any]:
    """
    Simulates 24-hour transient multi-node thermal dynamics using fundamental first-principles heat balance:
    C_air · dT_in/dt + C_mass · dT_mass/dt =
      + Q_solar(t)
      - Q_wall(t) - Q_roof(t) - Q_floor(t) - Q_window(t) - Q_door(t)
      - Q_vent(t) ± Q_mass(t) + Q_internal(t)
    """
    if climate_records is None or len(climate_records) < 24:
        from engine.climate import get_climate_profile
        climate_records = get_climate_profile("leh_ladakh", month=1)

    # 1. Envelope Thermo-physical Properties
    if wall_layers:
        wall_u_res = calculate_composite_assembly_u_value(wall_layers)
    else:
        wall_u_res = calculate_assembly_u_value(wall_mat_id, wall_thickness_cm, insulation_mat_id, insulation_thickness_cm)
    u_wall = wall_u_res["u_value_w_m2k"]
    thermal_mass_wall = wall_u_res["thermal_mass_kj_m2k"]

    if roof_layers:
        roof_u_res = calculate_composite_assembly_u_value(roof_layers)
        u_roof = roof_u_res["u_value_w_m2k"]
        thermal_mass_roof = roof_u_res["thermal_mass_kj_m2k"]
    else:
        roof_mat = get_material_by_id(roof_mat_id)
        r_roof_base = 0.13 + 0.04 + (0.10 / max(0.01, roof_mat["thermal_cond_w_mk"]))
        if insulation_mat_id and insulation_thickness_cm > 0:
            ins_mat = get_material_by_id(insulation_mat_id)
            r_roof_ins = (insulation_thickness_cm / 100.0) / max(0.001, ins_mat["thermal_cond_w_mk"])
            r_roof_base += r_roof_ins
        u_roof = 1.0 / max(0.05, r_roof_base)
        thermal_mass_roof = 25.0

    # Glazing properties
    glz_lower = glazing_mat_id.lower()
    if "triple" in glz_lower:
        u_glazing, shgc = 0.85, 0.35
    elif "double" in glz_lower:
        u_glazing, shgc = 1.80, 0.45
    elif "polycarb" in glz_lower:
        u_glazing, shgc = 2.80, 0.60
    elif "louver" in glz_lower:
        u_glazing, shgc = 5.20, 0.75
    else:
        u_glazing, shgc = 5.70, 0.82

    # Floor & Door properties
    floor_mat = get_material_by_id(floor_mat_id)
    u_floor = 1.0 / (0.13 + 0.05 + 0.15 / max(0.01, floor_mat["thermal_cond_w_mk"]))

    door_mat = get_material_by_id(door_mat_id)
    u_door = 1.0 / (0.13 + 0.04 + 0.04 / max(0.01, door_mat["thermal_cond_w_mk"]))

    # 2. Surface Areas & Capacitance
    a_wall = geometry.net_wall_area()
    a_roof = geometry.roof_area()
    a_floor = geometry.floor_area()
    a_glazing = geometry.glazing_area()
    a_door = geometry.door_area()
    volume = geometry.volume()
    orientation_deg = float(geometry.orientation)

    # Thermal Mass Storage Node Capacitance (kJ/K)
    mass_multiplier = 2.0 if thermal_mass_level == "high" else (0.5 if thermal_mass_level == "low" else 1.0)
    if "trombe" in wall_mat_id.lower() or "rammed" in wall_mat_id.lower():
        mass_multiplier *= 1.8

    c_air = volume * 1.204 * 1.005  # kJ/K
    c_mass_core = (a_wall * thermal_mass_wall + a_roof * thermal_mass_roof + a_floor * 35.0) * 0.50 * mass_multiplier
    c_mass_core = max(600.0, c_mass_core)  # kJ/K

    # Internal heat gains
    q_internal = calculate_internal_heat_gain(
        occupancy_type=occupancy_type,
        occupants=occupants,
        livestock_count=livestock_count,
        livestock_type=livestock_type,
        equipment_power_w=equipment_power_w,
    )

    t_outdoor = [float(rec["dry_bulb_temp_c"]) for rec in climate_records[:24]]
    rh_outdoor = [float(rec["relative_humidity_pct"]) for rec in climate_records[:24]]
    ghi_outdoor = [float(rec["solar_ghi_w_m2"]) for rec in climate_records[:24]]

    t_indoor = np.zeros(24)
    t_mass_node = np.zeros(24)
    t_sol_air_wall = np.zeros(24)
    t_sol_air_roof = np.zeros(24)

    q_solar_list = np.zeros(24)
    q_wall_list = np.zeros(24)
    q_roof_list = np.zeros(24)
    q_floor_list = np.zeros(24)
    q_window_list = np.zeros(24)
    q_door_list = np.zeros(24)
    q_vent_list = np.zeros(24)
    q_mass_exchange_list = np.zeros(24)
    q_internal_list = np.full(24, q_internal)
    net_heat_flow_list = np.zeros(24)

    # Initial state
    t_in_current = float(np.mean(t_outdoor))
    t_mass_current = t_in_current

    # Run 3 consecutive cycles for numerical stabilization of thermal inertia
    for cycle in range(3):
        for h in range(24):
            t_out = t_outdoor[h]
            ghi = ghi_outdoor[h]

            # NOAA Solar Position for current hour
            alt_deg, az_deg, is_day = calculate_solar_position(lat_deg, lon_deg, day_of_year, float(h))

            # Incident solar radiation on tilted roof and South-oriented facade
            # Glazing orientation: primary front facade oriented at orientation_deg (180° = True South)
            i_rad_glaze = calculate_incident_radiation_on_surface(
                ghi, alt_deg, az_deg, surface_tilt_deg=90.0, surface_az_deg=orientation_deg
            ) if is_day else 0.0

            i_rad_roof = calculate_incident_radiation_on_surface(
                ghi, alt_deg, az_deg, surface_tilt_deg=geometry.roof_pitch, surface_az_deg=orientation_deg
            ) if is_day else 0.0

            i_rad_wall = calculate_incident_radiation_on_surface(
                ghi, alt_deg, az_deg, surface_tilt_deg=90.0, surface_az_deg=(orientation_deg + 90.0) % 360.0
            ) if is_day else 0.0

            # Shading factor from overhang
            shade_factor = geometry.shading_factor(solar_elevation_deg=alt_deg) if is_day else 0.0

            # Direct Fenestration Solar Heat Gain (Watts)
            q_solar = calculate_fenestration_solar_gain(a_glazing, shgc, i_rad_glaze, shade_factor)

            # Sol-Air Temperatures
            alpha_wall = 0.70
            alpha_roof = 0.80 if "cool" not in roof_mat_id.lower() else 0.25
            h_ext = 22.7  # W/m²K
            t_sa_wall = t_out + (alpha_wall * i_rad_wall / h_ext) - 2.0
            t_sa_roof = t_out + (alpha_roof * i_rad_roof / h_ext) - 4.0

            # Numerical sub-stepping (12 steps of 300s per hour) for unconditional numerical stability
            n_substeps = 12
            dt_sub = 3600.0 / n_substeps
            c_air_joules = max(100.0, c_air + 0.15 * c_mass_core) * 1000.0
            c_mass_joules = max(500.0, c_mass_core) * 1000.0

            t_ground = max(4.0, min(14.0, float(np.mean(t_outdoor)) + 5.0))
            v_rate_w_k = (ach * volume * 1.204 * 1005.0) / 3600.0
            a_mass = a_wall + a_floor
            q_solar_absorbed_by_mass = q_solar * 0.35
            q_solar_direct_air = q_solar * 0.65

            for _ in range(n_substeps):
                q_wall = u_wall * a_wall * (t_sa_wall - t_in_current)
                q_roof = u_roof * a_roof * (t_sa_roof - t_in_current)
                q_win = u_glazing * a_glazing * (t_out - t_in_current)
                q_door = u_door * a_door * (t_out - t_in_current)
                q_floor = u_floor * a_floor * (t_ground - t_in_current)
                q_vent = v_rate_w_k * (t_out - t_in_current)

                # Mass to air convective exchange
                q_mass_to_air = 4.5 * a_mass * (t_mass_current - t_in_current) * 0.15

                q_net_air = q_solar_direct_air + q_wall + q_roof + q_floor + q_win + q_door + q_vent + q_internal + q_mass_to_air
                t_in_current += (q_net_air * dt_sub) / c_air_joules

                q_net_mass = q_solar_absorbed_by_mass - q_mass_to_air
                t_mass_current += (q_net_mass * dt_sub) / c_mass_joules

            if cycle == 2:
                t_indoor[h] = t_in_current
                t_mass_node[h] = t_mass_current
                t_sol_air_wall[h] = t_sa_wall
                t_sol_air_roof[h] = t_sa_roof
                q_solar_list[h] = q_solar
                q_wall_list[h] = q_wall
                q_roof_list[h] = q_roof
                q_floor_list[h] = q_floor
                q_window_list[h] = q_win
                q_door_list[h] = q_door
                q_vent_list[h] = q_vent
                q_mass_exchange_list[h] = q_mass_to_air
                net_heat_flow_list[h] = q_net_air

    # 4. Comprehensive Performance & Day/Night Analytics
    max_t_in = float(np.max(t_indoor))
    min_t_in = float(np.min(t_indoor))
    avg_t_in = float(np.mean(t_indoor))
    max_t_out = float(np.max(t_outdoor))
    min_t_out = float(np.min(t_outdoor))
    avg_t_out = float(np.mean(t_outdoor))

    # Day vs Night Metrics (Day: 07:00 - 18:00, Night: 19:00 - 06:00)
    day_indices = list(range(7, 19))
    night_indices = list(range(0, 7)) + list(range(19, 24))

    daytime_avg_in = float(np.mean(t_indoor[day_indices]))
    nighttime_avg_in = float(np.mean(t_indoor[night_indices]))
    nighttime_min_in = float(np.min(t_indoor[night_indices]))

    # Sunset temperature drop (Temp at 18:00 - Temp at 05:00 next morning)
    sunset_drop = round(t_indoor[18] - t_indoor[5], 2)

    # Cumulative Daily Energy Balance (kWh/day)
    total_solar_kwh = float(np.sum(q_solar_list)) / 1000.0
    total_conduction_loss_kwh = float(np.sum([abs(min(0.0, q_wall_list[h] + q_roof_list[h] + q_floor_list[h] + q_window_list[h] + q_door_list[h])) for h in range(24)])) / 1000.0
    total_vent_loss_kwh = float(np.sum([abs(min(0.0, q_vent_list[h])) for h in range(24)])) / 1000.0
    total_heat_loss_kwh = total_conduction_loss_kwh + total_vent_loss_kwh

    # Thermal damping & lag
    amplitude_out = max(0.1, max_t_out - min_t_out)
    amplitude_in = max(0.1, max_t_in - min_t_in)
    damping_factor = round(amplitude_in / amplitude_out, 3)
    peak_out_hr = int(np.argmax(t_outdoor))
    peak_in_hr = int(np.argmax(t_indoor))
    time_lag_hrs = (peak_in_hr - peak_out_hr) % 24

    return {
        "hours": list(range(24)),
        "t_outdoor": [round(x, 2) for x in t_outdoor],
        "t_indoor": [round(x, 2) for x in t_indoor],
        "t_mass": [round(x, 2) for x in t_mass_node],
        "t_sol_air_wall": [round(x, 2) for x in t_sol_air_wall],
        "t_sol_air_roof": [round(x, 2) for x in t_sol_air_roof],
        "rh_outdoor": rh_outdoor,
        "ghi_outdoor": ghi_outdoor,
        "u_wall": round(u_wall, 4),
        "u_roof": round(u_roof, 4),
        "u_glazing": round(u_glazing, 2),
        "u_floor": round(u_floor, 3),
        "u_door": round(u_door, 3),
        "q_solar_watts": [round(x, 1) for x in q_solar_list],
        "q_wall_watts": [round(x, 1) for x in q_wall_list],
        "q_roof_watts": [round(x, 1) for x in q_roof_list],
        "q_floor_watts": [round(x, 1) for x in q_floor_list],
        "q_window_watts": [round(x, 1) for x in q_window_list],
        "q_door_watts": [round(x, 1) for x in q_door_list],
        "q_vent_watts": [round(x, 1) for x in q_vent_list],
        "q_mass_watts": [round(x, 1) for x in q_mass_exchange_list],
        "q_internal_watts": [round(x, 1) for x in q_internal_list],
        "net_heat_flow_watts": [round(x, 1) for x in net_heat_flow_list],
        # Compatibility aliases
        "q_wall": [round(x, 1) for x in q_wall_list],
        "q_roof": [round(x, 1) for x in q_roof_list],
        "q_solar": [round(x, 1) for x in q_solar_list],
        "q_vent": [round(x, 1) for x in q_vent_list],
        "q_internal": [round(x, 1) for x in q_internal_list],
        "thermal_shift": round(max_t_out - max_t_in, 2),
        "daytime_avg_indoor_temp_c": round(daytime_avg_in, 2),
        "nighttime_avg_indoor_temp_c": round(nighttime_avg_in, 2),
        "nighttime_min_indoor_temp_c": round(nighttime_min_in, 2),
        "sunset_temp_drop_c": sunset_drop,
        "avg_t_indoor": round(avg_t_in, 2),
        "max_t_indoor": round(max_t_in, 2),
        "min_t_indoor": round(min_t_in, 2),
        "avg_t_outdoor": round(avg_t_out, 2),
        "max_t_outdoor": round(max_t_out, 2),
        "min_t_outdoor": round(min_t_out, 2),
        "damping_factor": damping_factor,
        "time_lag_hours": time_lag_hrs,
        "total_daily_solar_captured_kwh": round(total_solar_kwh, 2),
        "total_daily_heat_loss_kwh": round(total_heat_loss_kwh, 2),
        "net_thermal_balance_kwh": round(total_solar_kwh - total_heat_loss_kwh, 2),
        "hourly_df": pd.DataFrame({
            "Time": [f"{h:02d}:00" for h in range(24)],
            "Outdoor (°C)": [round(x, 1) for x in t_outdoor],
            "Indoor (°C)": [round(x, 1) for x in t_indoor],
            "Sol-Air (°C)": [round(x, 1) for x in t_sol_air_wall],
            "Q_Wall (W)": [round(x, 1) for x in q_wall_list],
            "Q_Roof (W)": [round(x, 1) for x in q_roof_list],
            "Q_Solar (W)": [round(x, 1) for x in q_solar_list],
            "Q_Vent (W)": [round(x, 1) for x in q_vent_list],
            "Q_Internal (W)": [round(x, 1) for x in q_internal_list],
        }),
    }


def compare_thermal_scenarios(
    geometry: ShelterGeometry,
    baseline_config: Dict[str, Any],
    modified_config: Dict[str, Any],
    climate_records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Side-by-side thermal sensitivity comparison between baseline and retrofitted design.
    """
    sim_base = simulate_shelter_thermal_dynamics(
        geometry=geometry,
        climate_records=climate_records,
        **baseline_config,
    )

    sim_mod = simulate_shelter_thermal_dynamics(
        geometry=geometry,
        climate_records=climate_records,
        **modified_config,
    )

    peak_temp_drop = round(sim_base["max_t_indoor"] - sim_mod["max_t_indoor"], 2)
    nighttime_gain = round(sim_mod["nighttime_min_indoor_temp_c"] - sim_base["nighttime_min_indoor_temp_c"], 2)
    solar_delta = round(sim_mod["total_daily_solar_captured_kwh"] - sim_base["total_daily_solar_captured_kwh"], 2)
    loss_reduction = round(sim_base["total_daily_heat_loss_kwh"] - sim_mod["total_daily_heat_loss_kwh"], 2)

    df_compare = pd.DataFrame({
        "Hour": [f"{h:02d}:00" for h in range(24)],
        "Outdoor (°C)": sim_base["t_outdoor"],
        "Baseline Indoor (°C)": sim_base["t_indoor"],
        "Modified Indoor (°C)": sim_mod["t_indoor"],
        "Temperature Drop (°C)": [round(b - m, 2) for b, m in zip(sim_base["t_indoor"], sim_mod["t_indoor"])],
        "Baseline Roof Heat (W)": sim_base["q_roof"],
        "Modified Roof Heat (W)": sim_mod["q_roof"],
    })

    return {
        "baseline_simulation": sim_base,
        "modified_simulation": sim_mod,
        "peak_temperature_drop_c": peak_temp_drop,
        "nighttime_temperature_gain_c": nighttime_gain,
        "solar_capture_delta_kwh": solar_delta,
        "heat_loss_reduction_kwh": loss_reduction,
        "comparison_table": df_compare,
        "summary_statement": (
            f"Optimized design increased nighttime indoor minimum by +{nighttime_gain:.1f}°C "
            f"and reduced daily envelope thermal loss by {loss_reduction:.1f} kWh/day."
        ),
    }
