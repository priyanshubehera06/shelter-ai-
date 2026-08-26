"""
climate.py — Climate Intelligence, Historical Parsing, and Validation Engine for Shelter-AI.
Loads, validates, and standardizes multi-source climate data (CSV uploads, sample files,
Open-Meteo live API), providing consistent hourly data streams across the platform.
"""

import os
from typing import Dict, List, Optional, Any, Tuple, Union
import numpy as np
import pandas as pd

CLIMATE_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "climate")
SAMPLE_CSV = os.path.join(CLIMATE_DIR, "sample_location.csv")

REQUIRED_CLIMATE_FIELDS = [
    "datetime",
    "temperature",
    "humidity",
    "solar_radiation",
    "wind_speed",
    "wind_direction",
]

FIELD_ALIASES = {
    "datetime": ["datetime", "date", "time", "timestamp", "DateTime"],
    "temperature": ["temperature", "dry_bulb_temp_c", "temp", "temp_c", "dry_bulb_temp", "T_out"],
    "humidity": ["humidity", "relative_humidity_pct", "rh", "relative_humidity", "RH"],
    "solar_radiation": ["solar_radiation", "solar_ghi_w_m2", "ghi", "radiation", "solar_irradiance", "GHI"],
    "wind_speed": ["wind_speed", "wind_speed_m_s", "wind", "windspeed", "WS"],
    "wind_direction": ["wind_direction", "wind_dir", "wind_direction_deg", "WD"],
}


def validate_climate_data(df: pd.DataFrame) -> Tuple[bool, List[str]]:
    """
    Validates that a climate DataFrame contains all required columns and reasonable value ranges.
    Returns (is_valid, error_or_warning_messages).
    """
    issues = []
    if df is None or df.empty:
        return False, ["Climate DataFrame is empty or None."]

    # Check column coverage
    cols = list(df.columns)
    for req_field, aliases in FIELD_ALIASES.items():
        if not any(alias in cols for alias in aliases):
            issues.append(f"Missing required field '{req_field}' (acceptable aliases: {', '.join(aliases)})")

    if issues:
        return False, issues

    # Validate value ranges if columns are present
    t_col = next((c for c in cols if c in FIELD_ALIASES["temperature"]), None)
    rh_col = next((c for c in cols if c in FIELD_ALIASES["humidity"]), None)
    ghi_col = next((c for c in cols if c in FIELD_ALIASES["solar_radiation"]), None)

    if t_col:
        t_vals = df[t_col].dropna().values
        if len(t_vals) == 0 or np.min(t_vals) < -60.0 or np.max(t_vals) > 65.0:
            issues.append(f"Temperature values in '{t_col}' exceed plausible terrestrial limits (-60°C to +65°C).")

    if rh_col:
        rh_vals = df[rh_col].dropna().values
        if len(rh_vals) == 0 or np.min(rh_vals) < 0.0 or np.max(rh_vals) > 100.0:
            issues.append(f"Relative humidity in '{rh_col}' out of bounds (0% - 100%).")

    if ghi_col:
        ghi_vals = df[ghi_col].dropna().values
        if len(ghi_vals) == 0 or np.min(ghi_vals) < 0.0 or np.max(ghi_vals) > 1400.0:
            issues.append(f"Solar radiation in '{ghi_col}' out of bounds (0 - 1400 W/m²).")

    is_valid = len(issues) == 0
    return is_valid, issues


def standardize_climate_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalizes arbitrary column names in climate dataset into canonical schema:
    [datetime, temperature, humidity, solar_radiation, wind_speed, wind_direction]
    """
    if df is None or df.empty:
        return pd.DataFrame()

    out_df = pd.DataFrame()
    cols = df.columns

    for canonical_field, aliases in FIELD_ALIASES.items():
        matched = next((c for c in cols if c in aliases), None)
        if matched:
            out_df[canonical_field] = df[matched]
        else:
            # Provide sensible fallback series
            if canonical_field == "wind_direction":
                out_df[canonical_field] = 180.0
            elif canonical_field == "wind_speed":
                out_df[canonical_field] = 3.0
            elif canonical_field == "humidity":
                out_df[canonical_field] = 50.0
            elif canonical_field == "solar_radiation":
                out_df[canonical_field] = 0.0
            elif canonical_field == "temperature":
                out_df[canonical_field] = 25.0
            elif canonical_field == "datetime":
                out_df[canonical_field] = pd.date_range("2026-01-01", periods=len(df), freq="h").astype(str)

    # Convert datetimes and sort
    try:
        out_df["datetime"] = pd.to_datetime(out_df["datetime"])
        out_df = out_df.sort_values("datetime").reset_index(drop=True)
    except Exception:
        pass

    # Ensure numeric columns are floats
    num_cols = ["temperature", "humidity", "solar_radiation", "wind_speed", "wind_direction"]
    for c in num_cols:
        out_df[c] = pd.to_numeric(out_df[c], errors="coerce").fillna(0.0)

    # Also add dual-compatibility aliases for thermal simulation engine
    out_df["dry_bulb_temp_c"] = out_df["temperature"]
    out_df["relative_humidity_pct"] = out_df["humidity"]
    out_df["solar_ghi_w_m2"] = out_df["solar_radiation"]
    out_df["wind_speed_m_s"] = out_df["wind_speed"]

    return out_df


def load_climate_dataset(
    source: str = "sample_location.csv",
    uploaded_file: Optional[Any] = None
) -> pd.DataFrame:
    """
    Loads climate data from user-uploaded CSV, sample dataset, or saved location file.
    Falls back gracefully to data/climate/sample_location.csv.
    """
    if uploaded_file is not None:
        try:
            raw_df = pd.read_csv(uploaded_file)
            is_valid, _ = validate_climate_data(raw_df)
            if is_valid:
                return standardize_climate_dataframe(raw_df)
        except Exception:
            pass

    # Try local sample_location.csv
    if os.path.exists(SAMPLE_CSV):
        try:
            df = pd.read_csv(SAMPLE_CSV)
            return standardize_climate_dataframe(df)
        except Exception:
            pass

    # Synthetic fallback if file system is inaccessible
    dates = pd.date_range("2026-01-01", periods=8760, freq="h")
    h = dates.hour.values
    t = 25.0 + 8.0 * np.sin((h - 9) * np.pi / 12)
    rh = np.clip(60.0 - (t - 25.0) * 2.0, 20.0, 95.0)
    ghi = np.maximum(0.0, 850.0 * np.sin(np.pi * (h - 6) / 12.0))
    ghi[(h < 6) | (h > 18)] = 0.0

    df_synth = pd.DataFrame({
        "datetime": dates,
        "temperature": t,
        "humidity": rh,
        "solar_radiation": ghi,
        "wind_speed": 3.0,
        "wind_direction": 180.0,
    })
    return standardize_climate_dataframe(df_synth)


def get_climate_profile(location_id: str = "sambalpur", month: int = 5) -> List[Dict[str, Any]]:
    """
    Extracts or generates 24-hour diurnal profile for simulation modules.
    Supports auto-detected geolocation data, city catalogs, and sample_location.csv.
    """
    loc_str = str(location_id)
    loc_lower = loc_str.lower()

    # 1. Check Streamlit session state for live GPS / auto-detected weather
    if any(k in loc_lower for k in ["auto", "current", "live", "detected"]):
        try:
            import streamlit as st
            if "auto_geo_data" in st.session_state and st.session_state["auto_geo_data"]:
                return st.session_state["auto_geo_data"]["climate_records"]
        except Exception:
            pass

    # 2. Check geolocation city catalog live API
    try:
        from engine.geolocation import get_city_climate_profile
        records = get_city_climate_profile(loc_str)
        if records and len(records) >= 24:
            return records
    except Exception:
        pass

    # 3. Load from standardized sample_location.csv
    df_std = load_climate_dataset()
    if not df_std.empty and "datetime" in df_std.columns and hasattr(df_std["datetime"], "dt"):
        m_df = df_std[df_std["datetime"].dt.month == month]
        if not m_df.empty:
            # Group by hour to get average diurnal profile for the month
            hourly_avg = m_df.groupby(m_df["datetime"].dt.hour).mean(numeric_only=True)
            records = []
            for h in range(24):
                row = hourly_avg.loc[h] if h in hourly_avg.index else hourly_avg.iloc[h % len(hourly_avg)]
                records.append({
                    "month": month,
                    "day": 15,
                    "hour": h,
                    "dry_bulb_temp_c": round(float(row.get("temperature", 28.0)), 2),
                    "relative_humidity_pct": round(float(row.get("humidity", 50.0)), 1),
                    "solar_ghi_w_m2": round(float(row.get("solar_radiation", 0.0)), 1),
                    "wind_speed_m_s": round(float(row.get("wind_speed", 3.0)), 1),
                })
            return records

    # 4. Deterministic synthetic diurnal curve
    hours = np.arange(24)
    t_max, t_min = 40.0, 26.0
    t_out = (t_max + t_min) / 2.0 + ((t_max - t_min) / 2.0) * np.sin((hours - 8) * np.pi / 12.0)
    rh = np.clip(65.0 - (t_out - np.mean(t_out)) * 1.5, 15.0, 95.0)
    ghi = np.maximum(0.0, 920.0 * np.sin((hours - 6) * np.pi / 12.0))
    ghi[(hours < 6) | (hours > 18)] = 0.0

    records = []
    for h in range(24):
        records.append({
            "month": month,
            "day": 15,
            "hour": h,
            "dry_bulb_temp_c": round(float(t_out[h]), 2),
            "relative_humidity_pct": round(float(rh[h]), 1),
            "solar_ghi_w_m2": round(float(ghi[h]), 1),
            "wind_speed_m_s": 3.2,
        })
    return records


def calculate_psychrometrics(t_db: float, rh: float) -> Dict[str, float]:
    """Computes vapor pressure, dew point temperature, wet bulb, and enthalpy."""
    p_sat = 0.61078 * np.exp((17.27 * t_db) / (t_db + 237.3))
    p_v = (rh / 100.0) * p_sat

    a, b = 17.27, 237.3
    alpha = ((a * t_db) / (b + t_db)) + np.log(max(0.01, rh / 100.0))
    t_dp = (b * alpha) / (a - alpha)

    h = 1.006 * t_db + (rh / 100.0) * p_sat * (2501.0 + 1.805 * t_db) * 0.001

    # Stull formula for wet-bulb temperature
    t_wb = (
        t_db * np.arctan(0.151977 * (rh + 8.313659) ** 0.5)
        + np.arctan(t_db + rh)
        - np.arctan(rh - 1.676331)
        + 0.00391838 * (rh) ** 1.5 * np.arctan(0.023101 * rh)
        - 4.686035
    )

    return {
        "vapor_pressure_kpa": round(float(p_v), 3),
        "dew_point_c": round(float(t_dp), 2),
        "wet_bulb_c": round(float(t_wb), 2),
        "enthalpy_kj_kg": round(float(h), 2),
    }


def calculate_degree_days(hourly_temps: List[float], base_heat: float = 18.0, base_cool: float = 24.0) -> Dict[str, float]:
    """Calculates Heating Degree Days (HDD) and Cooling Degree Days (CDD)."""
    hdd = sum(max(0.0, base_heat - t) for t in hourly_temps) / 24.0
    cdd = sum(max(0.0, t - base_cool) for t in hourly_temps) / 24.0
    return {"hdd": round(hdd, 2), "cdd": round(cdd, 2)}
