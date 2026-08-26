"""
extreme_analysis.py — Extreme Climate Risk, Heatwave Diagnostics & Stress Scenarios for Shelter-AI.
Extracts extreme meteorological episodes and generates 5 canonical design scenarios
(NORMAL, HOT, EXTREME_HOT, COLD, EXTREME_COLD) with a composite Extreme Climate Risk Score (0-100).
"""

from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import pandas as pd
from engine.climate import load_climate_dataset


def generate_scenario_diurnal_records(
    t_max: float,
    t_min: float,
    rh_base: float = 50.0,
    ghi_peak: float = 950.0,
    wind_speed: float = 3.0,
    scenario_name: str = "NORMAL",
) -> List[Dict[str, Any]]:
    """
    Generates a realistic 24-hour diurnal meteorological profile for a given stress scenario.
    """
    hours = np.arange(24)
    # Sine wave peaking at 14:00 (hour 14)
    t_out = (t_max + t_min) / 2.0 + ((t_max - t_min) / 2.0) * np.sin((hours - 8) * np.pi / 12.0)
    # Relative humidity inverse to dry bulb temperature
    rh = np.clip(rh_base - (t_out - np.mean(t_out)) * 1.5, 10.0, 98.0)
    # Solar radiation curve
    ghi = np.maximum(0.0, ghi_peak * np.sin((hours - 6) * np.pi / 12.0))
    ghi[(hours < 6) | (hours > 18)] = 0.0

    records = []
    for h in range(24):
        records.append({
            "scenario": scenario_name,
            "hour": h,
            "dry_bulb_temp_c": round(float(t_out[h]), 2),
            "temperature": round(float(t_out[h]), 2),
            "relative_humidity_pct": round(float(rh[h]), 1),
            "humidity": round(float(rh[h]), 1),
            "solar_ghi_w_m2": round(float(ghi[h]), 1),
            "solar_radiation": round(float(ghi[h]), 1),
            "wind_speed_m_s": float(wind_speed),
            "wind_speed": float(wind_speed),
        })
    return records


def analyze_extreme_climate_events(df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
    """
    Identifies heatwave episodes, cold snaps, peak irradiance events, and builds
    the 5 canonical simulation scenarios with a composite Extreme Climate Risk Score (0-100).
    """
    if df is None or df.empty:
        df = load_climate_dataset()

    t_arr = df["temperature"].dropna().values
    rh_arr = df["humidity"].dropna().values
    ghi_arr = df["solar_radiation"].dropna().values

    # Statistical percentiles for extreme definitions
    p99_temp = float(np.percentile(t_arr, 99))
    p95_temp = float(np.percentile(t_arr, 95))
    p50_temp = float(np.percentile(t_arr, 50))
    p05_temp = float(np.percentile(t_arr, 5))
    p01_temp = float(np.percentile(t_arr, 1))

    p99_ghi = float(np.percentile(ghi_arr, 99))
    p50_ghi = float(np.percentile(ghi_arr, 50))

    t_max_record = float(np.max(t_arr))
    t_min_record = float(np.min(t_arr))
    ghi_max_record = float(np.max(ghi_arr))

    # Heatwave detection: Consecutive periods > 38°C
    hot_streak_count = 0
    in_streak = False
    heatwaves = 0
    for t in t_arr:
        if t >= 38.0:
            hot_streak_count += 1
            if hot_streak_count >= 6 and not in_streak:
                heatwaves += 1
                in_streak = True
        else:
            hot_streak_count = 0
            in_streak = False

    # 1. Generate 5 Standard Design Scenarios
    # Scenario 1: NORMAL
    normal_records = generate_scenario_diurnal_records(
        t_max=round(p50_temp + 6.0, 1),
        t_min=round(p50_temp - 6.0, 1),
        rh_base=float(np.mean(rh_arr)),
        ghi_peak=round(p99_ghi * 0.85, 1),
        scenario_name="NORMAL",
    )

    # Scenario 2: HOT
    hot_records = generate_scenario_diurnal_records(
        t_max=round(p95_temp, 1),
        t_min=round(p95_temp - 10.0, 1),
        rh_base=float(np.percentile(rh_arr, 35)),
        ghi_peak=round(p99_ghi * 0.95, 1),
        scenario_name="HOT",
    )

    # Scenario 3: EXTREME_HOT (Heatwave Peak)
    extreme_hot_records = generate_scenario_diurnal_records(
        t_max=round(max(t_max_record, p99_temp + 2.0), 1),
        t_min=round(p99_temp - 8.0, 1),
        rh_base=float(np.percentile(rh_arr, 25)),
        ghi_peak=round(max(ghi_max_record, 1050.0), 1),
        scenario_name="EXTREME_HOT",
    )

    # Scenario 4: COLD
    cold_records = generate_scenario_diurnal_records(
        t_max=round(p05_temp + 8.0, 1),
        t_min=round(p05_temp, 1),
        rh_base=float(np.percentile(rh_arr, 70)),
        ghi_peak=round(p99_ghi * 0.60, 1),
        scenario_name="COLD",
    )

    # Scenario 5: EXTREME_COLD (Severe Cold Snap)
    extreme_cold_records = generate_scenario_diurnal_records(
        t_max=round(p01_temp + 5.0, 1),
        t_min=round(min(t_min_record, p01_temp - 3.0), 1),
        rh_base=float(np.percentile(rh_arr, 80)),
        ghi_peak=round(p99_ghi * 0.45, 1),
        scenario_name="EXTREME_COLD",
    )

    scenarios = {
        "NORMAL": normal_records,
        "HOT": hot_records,
        "EXTREME_HOT": extreme_hot_records,
        "COLD": cold_records,
        "EXTREME_COLD": extreme_cold_records,
    }

    # 2. Compute Extreme Climate Risk Score (0-100)
    # Weighted combination of:
    # - Heat risk (peak temp > 40°C) -> 40 pts
    # - Cold risk (min temp < 10°C) -> 25 pts
    # - Solar peak risk (> 950 W/m²) -> 20 pts
    # - Heatwave frequency -> 15 pts
    heat_subscore = min(40.0, max(0.0, (t_max_record - 32.0) * (40.0 / 14.0)))
    cold_subscore = min(25.0, max(0.0, (18.0 - t_min_record) * (25.0 / 25.0)))
    solar_subscore = min(20.0, max(0.0, (ghi_max_record - 750.0) * (20.0 / 350.0)))
    heatwave_subscore = min(15.0, float(heatwaves) * 3.0)

    risk_score = round(heat_subscore + cold_subscore + solar_subscore + heatwave_subscore, 1)

    if risk_score >= 75.0:
        risk_level = "Severe Extreme Risk (Catastrophic Exposure)"
        risk_badge_color = "#e74c3c"
    elif risk_score >= 50.0:
        risk_level = "High Climate Stress Risk"
        risk_badge_color = "#e67e22"
    elif risk_score >= 25.0:
        risk_level = "Moderate Climate Stress"
        risk_badge_color = "#f1c40f"
    else:
        risk_level = "Low Extreme Risk (Benign / Mild)"
        risk_badge_color = "#2ecc71"

    return {
        "extreme_climate_risk_score": risk_score,
        "risk_level": risk_level,
        "risk_badge_color": risk_badge_color,
        "hottest_temp_c": t_max_record,
        "coldest_temp_c": t_min_record,
        "max_solar_radiation_w_m2": ghi_max_record,
        "heatwave_events_count": heatwaves,
        "scenarios": scenarios,
        "scenario_summaries": {
            "NORMAL": f"Peak {normal_records[14]['dry_bulb_temp_c']}°C | Min {normal_records[5]['dry_bulb_temp_c']}°C",
            "HOT": f"Peak {hot_records[14]['dry_bulb_temp_c']}°C | Min {hot_records[5]['dry_bulb_temp_c']}°C",
            "EXTREME_HOT": f"Peak {extreme_hot_records[14]['dry_bulb_temp_c']}°C | Min {extreme_hot_records[5]['dry_bulb_temp_c']}°C (Heatwave)",
            "COLD": f"Peak {cold_records[14]['dry_bulb_temp_c']}°C | Min {cold_records[5]['dry_bulb_temp_c']}°C",
            "EXTREME_COLD": f"Peak {extreme_cold_records[14]['dry_bulb_temp_c']}°C | Min {extreme_cold_records[5]['dry_bulb_temp_c']}°C (Cold Snap)",
        },
    }
