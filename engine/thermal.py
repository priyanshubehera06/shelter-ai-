"""
thermal.py — Dynamic transient thermal physics engine for Shelter-AI.
Calculates hourly indoor temperatures, multi-surface heat balance (walls, roof,
glazing, ventilation, internal metabolic gains), and comparative scenario analyses.
"""

import math
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from engine.materials import calculate_assembly_u_value, get_material_by_id
from engine.geometry import ShelterGeometry


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
    - Agriculture: Grow lights, pumps, greenhouse equipment
    """
    occ_type = str(occupancy_type).lower()
    total_w = max(0.0, float(equipment_power_w))

    if "human" in occ_type or "residential" in occ_type or "transitional" in occ_type or "emergency" in occ_type:
        # Sensible metabolic heat ~ 90 - 110 W/person
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
        # Auxiliary agricultural / crop storage equipment
        total_w += 150.0

    return round(total_w, 1)


def simulate_shelter_thermal_dynamics(
    geometry: ShelterGeometry,
    wall_mat_id: str = "brick_standard",
    wall_thickness_cm: float = 20.0,
    roof_mat_id: str = "roof_cgi_insulated",
    glazing_mat_id: str = "glazing_single",
    insulation_mat_id: Optional[str] = None,
    insulation_thickness_cm: float = 0.0,
    climate_records: Optional[List[Dict[str, Any]]] = None,
    ach: float = 3.0,
    occupants: int = 4,
    occupancy_type: str = "humans",
    livestock_count: int = 0,
    livestock_type: str = "cattle",
    equipment_power_w: float = 50.0,
    temp_threshold_high: float = 30.0,
    temp_threshold_low: float = 18.0,
) -> Dict[str, Any]:
    """
    Simulates 24-hour transient multi-node thermal dynamics using fundamental
    first-principles heat balance:
    - Q_wall = U_wall * A_wall * (T_sol_air - T_in)
    - Q_roof = U_roof * A_roof * (T_sol_air - T_in)
    - Q_glazing_cond = U_glazing * A_glazing * (T_out - T_in)
    - Q_solar_gain = A_glazing * SHGC * GHI * (1 - Shading_Factor)
    - Q_vent = m_dot * Cp * (T_out - T_in) = 0.33 * ACH * Volume * (T_out - T_in)
    - Q_internal = Human / Livestock / Equipment heat
    """
    if climate_records is None or len(climate_records) < 24:
        from engine.climate import get_climate_profile
        climate_records = get_climate_profile("sambalpur", month=5)

    # 1. Thermo-physical Envelope Properties
    wall_u_res = calculate_assembly_u_value(wall_mat_id, wall_thickness_cm, insulation_mat_id, insulation_thickness_cm)
    u_wall = wall_u_res["u_value_w_m2k"]
    thermal_mass_wall = wall_u_res["thermal_mass_kj_m2k"]

    # Roof assembly U-value (incorporates roof material properties & insulation)
    roof_mat = get_material_by_id(roof_mat_id)
    r_roof_base = 0.13 + 0.04 + (0.10 / max(0.01, roof_mat["thermal_cond_w_mk"]))
    if insulation_mat_id and insulation_thickness_cm > 0:
        ins_mat = get_material_by_id(insulation_mat_id)
        r_roof_ins = (insulation_thickness_cm / 100.0) / max(0.001, ins_mat["thermal_cond_w_mk"])
        r_roof_base += r_roof_ins
    u_roof = 1.0 / max(0.05, r_roof_base)

    # Glazing assembly U-value and Solar Heat Gain Coefficient (SHGC)
    if "double" in glazing_mat_id.lower():
        u_glazing, shgc = 2.8, 0.55
    elif "polycarb" in glazing_mat_id.lower():
        u_glazing, shgc = 3.2, 0.65
    else:
        u_glazing, shgc = 5.7, 0.78

    # 2. Surface Areas & Zone Capacitance
    a_wall = geometry.net_wall_area()
    a_roof = geometry.roof_area()
    a_glazing = geometry.glazing_area()
    volume = geometry.volume()

    # Total Thermal Capacitance (kJ/K) = Air + Envelope participation
    c_air = volume * 1.204 * 1.005  # density 1.204 kg/m³, Cp 1.005 kJ/kgK
    c_envelope = (a_wall * thermal_mass_wall + a_roof * 15.0) * 0.45  # active thermal mass
    c_total = max(400.0, c_air + c_envelope)  # kJ/K

    # Solar absorptance and outer surface film coefficient
    alpha_solar = 0.65
    h_ext = 17.0  # W/m²K

    # 3. Internal Heat Gains (Watts)
    q_internal = calculate_internal_heat_gain(
        occupancy_type=occupancy_type,
        occupants=occupants,
        livestock_count=livestock_count,
        livestock_type=livestock_type,
        equipment_power_w=equipment_power_w,
    )

    t_outdoor = [rec["dry_bulb_temp_c"] for rec in climate_records[:24]]
    rh_outdoor = [rec["relative_humidity_pct"] for rec in climate_records[:24]]
    ghi_outdoor = [rec["solar_ghi_w_m2"] for rec in climate_records[:24]]

    t_indoor = np.zeros(24)
    t_sol_air = np.zeros(24)
    q_wall_list = np.zeros(24)
    q_roof_list = np.zeros(24)
    q_glazing_cond_list = np.zeros(24)
    q_solar_win_list = np.zeros(24)
    q_vent_list = np.zeros(24)
    q_internal_list = np.full(24, q_internal)

    # Initial state: steady-state starting point
    t_in_current = float(np.mean(t_outdoor))

    # Run 3 consecutive 24h cycles to stabilize thermal storage dynamics
    for cycle in range(3):
        for h in range(24):
            t_out = t_outdoor[h]
            ghi = ghi_outdoor[h]

            # Sol-Air temperature for opaque building envelopes
            t_sa = t_out + (alpha_solar * ghi / h_ext)
            t_sol_air[h] = t_sa

            # Solar elevation & overhang shading geometry
            is_day = 6 <= h <= 18
            sol_elev = max(10.0, 75.0 * np.sin(np.pi * (h - 6) / 12)) if is_day else 0.0
            shade_factor = geometry.shading_factor(solar_elevation_deg=sol_elev) if is_day else 0.0

            # 1. Wall Heat Transfer (Watts): Q = U * A * (T_sol_air - T_in)
            q_wall = u_wall * a_wall * (t_sa - t_in_current)

            # 2. Roof Heat Transfer (Watts): Q = U * A * (T_sol_air - T_in)
            q_roof = u_roof * a_roof * (t_sa - t_in_current)

            # 3. Window Conduction (Watts): Q = U * A * (T_out - T_in)
            q_win_cond = u_glazing * a_glazing * (t_out - t_in_current)

            # 4. Direct Solar Heat Gain (Watts): Q = A * (1 - shade) * GHI * SHGC
            q_solar_win = a_glazing * (1.0 - shade_factor) * ghi * shgc

            # 5. Ventilation / Infiltration Heat Exchange (Watts)
            # Q_vent = (ACH * Volume * rho * Cp / 3600) * (T_out - T_in)
            v_rate_w_k = (ach * volume * 1.204 * 1005.0) / 3600.0
            q_vent = v_rate_w_k * (t_out - t_in_current)

            # Net Zone Heat Flux (Watts)
            q_net_watts = q_wall + q_roof + q_win_cond + q_solar_win + q_vent + q_internal

            # Differential temperature step: dT = (Q_net * dt) / (C_total * 1000 J/K)
            dt_sec = 3600.0
            d_temp = (q_net_watts * dt_sec) / (c_total * 1000.0)
            t_in_current += d_temp

            if cycle == 2:
                t_indoor[h] = t_in_current
                q_wall_list[h] = q_wall
                q_roof_list[h] = q_roof
                q_glazing_cond_list[h] = q_win_cond
                q_solar_win_list[h] = q_solar_win
                q_vent_list[h] = q_vent

    # 4. Performance Metrics & Analytics
    max_t_in = float(np.max(t_indoor))
    min_t_in = float(np.min(t_indoor))
    avg_t_in = float(np.mean(t_indoor))
    max_t_out = float(np.max(t_outdoor))
    min_t_out = float(np.min(t_outdoor))
    avg_t_out = float(np.mean(t_outdoor))

    hours_above = int(np.sum(t_indoor > temp_threshold_high))
    hours_below = int(np.sum(t_indoor < temp_threshold_low))

    # Time lag: Hour of peak outdoor temp vs Hour of peak indoor temp
    peak_out_hr = int(np.argmax(t_outdoor))
    peak_in_hr = int(np.argmax(t_indoor))
    time_lag_hrs = (peak_in_hr - peak_out_hr) % 24

    # Thermal damping factor (Amplitude reduction ratio)
    amplitude_out = max(0.1, max_t_out - min_t_out)
    amplitude_in = max(0.1, max_t_in - min_t_in)
    damping_factor = round(amplitude_in / amplitude_out, 3)

    # Hourly formatted breakdown table
    hourly_records = []
    for h in range(24):
        time_str = f"{h:02d}:00"
        hourly_records.append({
            "Time": time_str,
            "Outdoor (°C)": round(t_outdoor[h], 1),
            "Indoor (°C)": round(t_indoor[h], 1),
            "Sol-Air (°C)": round(t_sol_air[h], 1),
            "Q_Wall (W)": round(q_wall_list[h], 1),
            "Q_Roof (W)": round(q_roof_list[h], 1),
            "Q_Solar (W)": round(q_solar_win_list[h], 1),
            "Q_Vent (W)": round(q_vent_list[h], 1),
            "Q_Internal (W)": round(q_internal_list[h], 1),
        })

    df_hourly = pd.DataFrame(hourly_records)

    return {
        "hours": list(range(24)),
        "t_outdoor": [round(x, 2) for x in t_outdoor],
        "t_indoor": [round(x, 2) for x in t_indoor],
        "t_sol_air": [round(x, 2) for x in t_sol_air],
        "rh_outdoor": rh_outdoor,
        "ghi_outdoor": ghi_outdoor,
        "u_wall": round(u_wall, 3),
        "u_roof": round(u_roof, 3),
        "u_glazing": round(u_glazing, 2),
        "q_wall": [round(x, 1) for x in q_wall_list],
        "q_roof": [round(x, 1) for x in q_roof_list],
        "q_solar": [round(x, 1) for x in q_solar_win_list],
        "q_vent": [round(x, 1) for x in q_vent_list],
        "q_internal": [round(x, 1) for x in q_internal_list],
        "avg_t_indoor": round(avg_t_in, 2),
        "max_t_indoor": round(max_t_in, 2),
        "min_t_indoor": round(min_t_in, 2),
        "avg_t_outdoor": round(avg_t_out, 2),
        "max_t_outdoor": round(max_t_out, 2),
        "min_t_outdoor": round(min_t_out, 2),
        "thermal_shift": round(max_t_out - max_t_in, 2),
        "damping_factor": damping_factor,
        "time_lag_hours": time_lag_hrs,
        "hours_above_threshold": hours_above,
        "hours_below_threshold": hours_below,
        "temp_threshold_high": temp_threshold_high,
        "temp_threshold_low": temp_threshold_low,
        "hourly_df": df_hourly,
    }


def compare_thermal_scenarios(
    geometry: ShelterGeometry,
    baseline_config: Dict[str, Any],
    modified_config: Dict[str, Any],
    climate_records: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Reruns comparative thermal simulations between a baseline design and an improved
    design (e.g. Uninsulated CGI Metal Sheet vs. Insulated RCC / Composite Roof).

    Returns side-by-side delta metrics, peak temperature drop, and hourly comparison traces.
    """
    # 1. Simulate Baseline
    sim_base = simulate_shelter_thermal_dynamics(
        geometry=geometry,
        climate_records=climate_records,
        **baseline_config,
    )

    # 2. Simulate Modified
    sim_mod = simulate_shelter_thermal_dynamics(
        geometry=geometry,
        climate_records=climate_records,
        **modified_config,
    )

    # 3. Calculate Comparative Differences (Deltas)
    peak_temp_drop = round(sim_base["max_t_indoor"] - sim_mod["max_t_indoor"], 2)
    avg_temp_drop = round(sim_base["avg_t_indoor"] - sim_mod["avg_t_indoor"], 2)
    discomfort_hours_reduced = sim_base["hours_above_threshold"] - sim_mod["hours_above_threshold"]

    # Comparative hourly dataframe
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
        "avg_temperature_drop_c": avg_temp_drop,
        "discomfort_hours_reduced": discomfort_hours_reduced,
        "comparison_table": df_compare,
        "summary_statement": (
            f"Modifications achieved a {peak_temp_drop:+.1f}°C peak indoor temperature reduction "
            f"and eliminated {max(0, discomfort_hours_reduced)} hours of severe overheating."
        ),
    }
