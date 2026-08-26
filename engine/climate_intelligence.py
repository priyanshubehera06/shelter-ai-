"""
climate_intelligence.py — Climate Intelligence, Statistical Diagnostics & Heuristic Insights for Shelter-AI.
Analyzes full historical climate datasets to extract mean/max/min temperatures, diurnal swings,
hot/cold hours, solar radiation statistics, wind patterns, and structured architectural insights.
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from engine.climate import load_climate_dataset, calculate_psychrometrics


def analyze_climate_intelligence(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Performs comprehensive statistical, diurnal, and seasonal climate analysis.
    Returns statistical metrics, monthly distributions, and structured design insights.
    """
    if df is None or df.empty:
        df = load_climate_dataset()

    # Ensure datetime parsing
    if "datetime" in df.columns:
        try:
            df["datetime"] = pd.to_datetime(df["datetime"])
        except Exception:
            pass

    t_arr = df["temperature"].dropna().values
    rh_arr = df["humidity"].dropna().values
    ghi_arr = df["solar_radiation"].dropna().values
    wind_arr = df["wind_speed"].dropna().values

    # 1. Primary Statistical Metrics
    t_mean = float(np.mean(t_arr))
    t_max = float(np.max(t_arr))
    t_min = float(np.min(t_arr))
    t_std = float(np.std(t_arr))

    rh_mean = float(np.mean(rh_arr))
    rh_max = float(np.max(rh_arr))
    rh_min = float(np.min(rh_arr))

    ghi_max = float(np.max(ghi_arr))
    ghi_mean = float(np.mean(ghi_arr))
    ghi_daily_kwh_m2 = float(np.sum(ghi_arr) / 1000.0 / (len(df) / 24.0))

    wind_mean = float(np.mean(wind_arr))
    wind_max = float(np.max(wind_arr))

    # 2. Temperature Threshold Analysis
    hot_hours = int(np.sum(t_arr > 35.0))
    severe_hot_hours = int(np.sum(t_arr > 40.0))
    cold_hours = int(np.sum(t_arr < 15.0))
    severe_cold_hours = int(np.sum(t_arr < 5.0))
    comfort_band_hours = int(np.sum((t_arr >= 20.0) & (t_arr <= 26.0)))

    total_hours = len(df)
    comfort_potential_pct = round((comfort_band_hours / max(1, total_hours)) * 100.0, 1)

    # 3. Diurnal Temperature Swing (Average daily T_max - T_min)
    if "datetime" in df.columns and hasattr(df["datetime"], "dt"):
        daily_swings = df.groupby(df["datetime"].dt.date)["temperature"].apply(lambda s: s.max() - s.min())
        avg_diurnal_swing = float(daily_swings.mean())
        max_diurnal_swing = float(daily_swings.max())
    else:
        # Reshape to 24h chunks
        n_days = len(t_arr) // 24
        if n_days > 0:
            daily_matrix = t_arr[: n_days * 24].reshape((n_days, 24))
            swings = np.max(daily_matrix, axis=1) - np.min(daily_matrix, axis=1)
            avg_diurnal_swing = float(np.mean(swings))
            max_diurnal_swing = float(np.max(swings))
        else:
            avg_diurnal_swing = t_max - t_min
            max_diurnal_swing = t_max - t_min

    # 4. Psychrometric Baseline
    psychro_res = calculate_psychrometrics(t_mean, rh_mean)

    # 5. Climate Zone Classification Heuristic
    if t_mean >= 25.0 and rh_mean <= 45.0:
        climate_zone = "Hot and Arid"
    elif t_mean >= 25.0 and rh_mean > 55.0:
        climate_zone = "Warm and Humid"
    elif t_mean < 18.0:
        climate_zone = "Cold and High-Altitude"
    else:
        climate_zone = "Composite / Moderate"

    # 6. Structured Human-Readable Design Insights
    structured_insights = []

    # Insight 1: Solar Radiation Risk
    if ghi_max > 900.0 or ghi_daily_kwh_m2 > 5.5:
        structured_insights.append({
            "category": "Solar Radiation",
            "observation": f"High peak solar irradiance ({ghi_max:.0f} W/m²) and intense daily solar flux ({ghi_daily_kwh_m2:.1f} kWh/m²/day).",
            "insight": "High afternoon solar radiation is a major thermal risk for the overhead building envelope.",
            "action": "Mandate continuous roof insulation (min 50mm) and deep south/west overhang eaves (≥0.6m).",
            "priority": "HIGH",
        })

    # Insight 2: Diurnal Swing & Thermal Mass
    if avg_diurnal_swing >= 10.0:
        structured_insights.append({
            "category": "Thermal Mass",
            "observation": f"Large daily temperature variation (avg diurnal swing of {avg_diurnal_swing:.1f}°C, peak {max_diurnal_swing:.1f}°C).",
            "insight": "Large daily temperature variation suggests high thermal mass envelope construction will significantly dampen indoor peak temperatures.",
            "action": "Use high-density compressed stabilized earth blocks (CSEB) or stone masonry with night flush ventilation.",
            "priority": "HIGH",
        })
    else:
        structured_insights.append({
            "category": "Thermal Mass",
            "observation": f"Low diurnal temperature swing ({avg_diurnal_swing:.1f}°C) with persistent humid ambient warmth.",
            "insight": "Thermal mass provides limited benefit when night temperatures remain high.",
            "action": "Favor lightweight, low thermal capacitance breathable wallboards with high emissivity.",
            "priority": "MEDIUM",
        })

    # Insight 3: Natural Ventilation Potential
    if wind_mean >= 2.5 and rh_mean > 50.0:
        structured_insights.append({
            "category": "Ventilation",
            "observation": f"Frequent ambient breeze (avg {wind_mean:.1f} m/s) with elevated humidity ({rh_mean:.0f}% RH).",
            "insight": "Frequent wind currents indicate high potential for cross-ventilation to enhance physiological cooling.",
            "action": "Design large operable window-to-wall ratios (20-25%) aligned with prevailing wind axes and elevated floor/ceiling vents.",
            "priority": "HIGH",
        })
    elif wind_mean < 1.8:
        structured_insights.append({
            "category": "Ventilation",
            "observation": f"Low ambient wind speeds (avg {wind_mean:.1f} m/s).",
            "insight": "Low wind velocities require stack ventilation and thermal buoyancy chimneys rather than relying on cross-breeze.",
            "action": "Incorporate high roof clerestories or solar chimneys for stack-driven air exhaust.",
            "priority": "MEDIUM",
        })

    # Insight 4: Overheating vs Underheating Risk
    if hot_hours > 500:
        structured_insights.append({
            "category": "Thermal Extremes",
            "observation": f"{hot_hours} hours/year above 35°C ({severe_hot_hours} severe hours >40°C).",
            "insight": "Severe seasonal heat stress requires aggressive passive cooling envelopes to prevent indoor heat exhaustion.",
            "action": "Minimize East and West glazing; utilize cool-roof reflective coatings with solar reflectance ≥ 0.70.",
            "priority": "HIGH",
        })

    if cold_hours > 500:
        structured_insights.append({
            "category": "Winter Heating",
            "observation": f"{cold_hours} hours/year below 15°C ({severe_cold_hours} freezing hours <5°C).",
            "insight": "Winter underheating requires airtight envelope sealing and south-facing direct solar gain apertures.",
            "action": "Double glazed windows and operable insulated night shutters.",
            "priority": "MEDIUM",
        })

    return {
        "climate_zone": climate_zone,
        "mean_temp_c": round(t_mean, 1),
        "max_temp_c": round(t_max, 1),
        "min_temp_c": round(t_min, 1),
        "std_temp_c": round(t_std, 1),
        "avg_diurnal_swing_c": round(avg_diurnal_swing, 1),
        "max_diurnal_swing_c": round(max_diurnal_swing, 1),
        "mean_humidity_pct": round(rh_mean, 1),
        "max_solar_radiation_w_m2": round(ghi_max, 1),
        "mean_solar_radiation_w_m2": round(ghi_mean, 1),
        "daily_solar_kwh_m2": round(ghi_daily_kwh_m2, 1),
        "mean_wind_speed_m_s": round(wind_mean, 1),
        "hot_hours_above_35c": hot_hours,
        "severe_hot_hours_above_40c": severe_hot_hours,
        "cold_hours_below_15c": cold_hours,
        "comfort_band_hours": comfort_band_hours,
        "comfort_potential_pct": comfort_potential_pct,
        "psychrometrics": psychro_res,
        "structured_insights": structured_insights,
    }
