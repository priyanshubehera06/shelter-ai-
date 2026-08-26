"""
comfort.py — Thermal comfort, livestock heat stress, and agricultural storage suitability engine.
Evaluates indoor conditions for Humans (PMV/PPD, Adaptive ASHRAE 55),
Livestock (THI Heat Stress, Cattle/Poultry/Swine), and Agricultural Storage (Mushrooms, Grains, Vegetables).
"""

import math
from typing import Dict, List, Optional, Any, Tuple, Union
import numpy as np
import pandas as pd


# ----------------------------------------------------------------------
# 1. Human Thermal Comfort (ISO 7730 PMV/PPD & ASHRAE 55 Adaptive)
# ----------------------------------------------------------------------

def calculate_pmv_fanger(
    ta: float,
    tr: Optional[float] = None,
    rh: float = 50.0,
    vel: float = 0.15,
    met: float = 1.1,
    clo: float = 0.5
) -> Tuple[float, float]:
    """
    Calculates PMV (Predicted Mean Vote) and PPD (%) using the ISO 7730 Fanger model.
    - ta: Indoor dry-bulb air temp (°C)
    - tr: Mean radiant temperature (°C)
    - rh: Relative humidity (%)
    - vel: Air velocity (m/s)
    - met: Metabolic activity rate (met, 1.0 = resting 58 W/m², 1.2 = sedentary)
    - clo: Clothing thermal resistance (clo, 0.5 = light summer, 1.0 = winter)
    """
    ta = max(-40.0, min(60.0, float(ta)))
    tr = ta if tr is None else max(-40.0, min(60.0, float(tr)))
    rh = max(5.0, min(100.0, float(rh)))
    vel = max(0.05, min(5.0, float(vel)))

    m = met * 58.15  # W/m²
    w = 0.0
    mw = m - w

    icl = 0.155 * clo
    fcl = 1.0 + 1.29 * icl if icl <= 0.078 else 1.05 + 0.645 * icl
    hcf = 12.1 * math.sqrt(vel)

    # Water vapor pressure (Pa)
    p_a = rh * 10.0 * 0.6105 * math.exp((17.27 * ta) / (ta + 237.3))

    # Iterative calculation of clothing surface temperature (tcl)
    tcl = ta + (35.5 - ta) / (3.5 * (6.3 + 2.29 * math.sqrt(vel)))
    for _ in range(30):
        tcl_old = tcl
        hc = 2.38 * math.pow(abs(tcl - ta), 0.25)
        if hc < hcf:
            hc = hcf
        rad_term = 3.96e-8 * fcl * (math.pow(max(100.0, tcl + 273.0), 4) - math.pow(max(100.0, tr + 273.0), 4))
        tcl = 35.7 - 0.028 * mw - icl * (rad_term + fcl * hc * (tcl - ta))
        tcl = max(-50.0, min(100.0, tcl))
        if abs(tcl - tcl_old) < 0.001:
            break

    # Heat loss mechanisms (W/m²)
    hl1 = 3.96e-8 * fcl * (math.pow(tcl + 273.0, 4) - math.pow(tr + 273.0, 4))  # radiation
    hl2 = fcl * hc * (tcl - ta)                                                # convection
    hl3 = 3.05e-3 * (5733.0 - 6.99 * mw - p_a)                                  # skin diffusion
    hl4 = 0.42 * (mw - 58.15) if mw > 58.15 else 0.0                           # sweating
    hl5 = 1.7e-5 * m * (5867.0 - p_a)                                           # latent respiration
    hl6 = 0.0014 * m * (34.0 - ta)                                              # dry respiration

    l_total = hl1 + hl2 + hl3 + hl4 + hl5 + hl6
    ts = 0.303 * math.exp(-0.036 * m) + 0.028

    pmv = max(-3.0, min(3.0, ts * (mw - l_total)))
    ppd = max(5.0, min(100.0, 100.0 - 95.0 * math.exp(-0.03353 * math.pow(pmv, 4) - 0.2179 * math.pow(pmv, 2))))

    return round(pmv, 2), round(ppd, 1)


def calculate_adaptive_comfort(
    t_indoor_hourly: Union[List[float], np.ndarray],
    t_outdoor_mean: float
) -> Dict[str, Any]:
    """
    ASHRAE 55 Adaptive Comfort Model for naturally ventilated spaces.
    T_comfort = 17.8 + 0.31 * T_outdoor_mean
    Comfort band (80% acceptability): T_comfort ± 3.5 °C
    """
    t_comf = 17.8 + 0.31 * float(t_outdoor_mean)
    upper_80 = t_comf + 3.5
    lower_80 = t_comf - 3.5

    t_arr = np.array(t_indoor_hourly)
    in_band_hours = int(np.sum((t_arr >= lower_80) & (t_arr <= upper_80)))
    compliance_pct = round((in_band_hours / float(len(t_arr))) * 100.0, 1)

    return {
        "t_comfort_target_c": round(t_comf, 1),
        "upper_limit_80_c": round(upper_80, 1),
        "lower_limit_80_c": round(lower_80, 1),
        "comfortable_hours": in_band_hours,
        "compliance_pct": compliance_pct,
    }


def get_comfort_category(pmv: float) -> Tuple[str, str]:
    """Returns classification label and status HEX color for a PMV score."""
    if -0.5 <= pmv <= 0.5:
        return "Comfortable (Neutral)", "#2ecc71"
    elif 0.5 < pmv <= 1.5:
        return "Slightly Warm", "#f39c12"
    elif 1.5 < pmv <= 2.5:
        return "Warm", "#e67e22"
    elif pmv > 2.5:
        return "Hot (Uncomfortable)", "#e74c3c"
    elif -1.5 <= pmv < -0.5:
        return "Slightly Cool", "#3498db"
    elif -2.5 <= pmv < -1.5:
        return "Cool", "#2980b9"
    else:
        return "Cold (Uncomfortable)", "#9b59b6"


def evaluate_human_comfort(
    t_indoor_hourly: Union[List[float], np.ndarray],
    rh_hourly: Union[List[float], float] = 50.0,
    vel: float = 0.15,
    met: float = 1.1,
    clo: float = 0.5,
    t_outdoor_mean: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Comprehensive 24-hour / annual human comfort assessment.
    Returns Comfort Score (0-100), PMV/PPD, annual comfortable/too hot/too cold hours.
    """
    t_arr = np.array(t_indoor_hourly)
    n = len(t_arr)
    rh_arr = np.full(n, rh_hourly) if isinstance(rh_hourly, (int, float)) else np.array(rh_hourly[:n])

    pmv_list = []
    ppd_list = []
    for t_in, rh_val in zip(t_arr, rh_arr):
        p, d = calculate_pmv_fanger(ta=t_in, rh=rh_val, vel=vel, met=met, clo=clo)
        pmv_list.append(p)
        ppd_list.append(d)

    avg_pmv = float(np.mean(pmv_list))
    avg_ppd = float(np.mean(ppd_list))
    status_label, status_color = get_comfort_category(avg_pmv)

    # Comfortable hours (PMV between -0.7 and +0.7)
    comf_mask = np.abs(np.array(pmv_list)) <= 0.7
    hot_mask = np.array(pmv_list) > 0.7
    cold_mask = np.array(pmv_list) < -0.7

    comf_frac = float(np.mean(comf_mask))
    hot_frac = float(np.mean(hot_mask))
    cold_frac = float(np.mean(cold_mask))

    # Scale to 8,760 annual hours
    annual_comf_hrs = int(round(comf_frac * 8760))
    annual_hot_hrs = int(round(hot_frac * 8760))
    annual_cold_hrs = int(round(cold_frac * 8760))

    # Overall Human Comfort Score (0-100)
    score = int(round(max(0.0, min(100.0, (1.0 - (avg_ppd / 100.0)) * 100.0 * 0.5 + comf_frac * 50.0))))

    # Adaptive comfort compliance if outdoor mean provided
    adaptive_res = None
    if t_outdoor_mean is not None:
        adaptive_res = calculate_adaptive_comfort(t_arr, t_outdoor_mean)

    return {
        "mode": "Human Comfort",
        "comfort_score": score,
        "avg_pmv": round(avg_pmv, 2),
        "avg_ppd": round(avg_ppd, 1),
        "status_label": status_label,
        "status_color": status_color,
        "comfortable_hours_annual": annual_comf_hrs,
        "too_hot_hours_annual": annual_hot_hrs,
        "too_cold_hours_annual": annual_cold_hrs,
        "comfortable_pct": round(comf_frac * 100.0, 1),
        "too_hot_pct": round(hot_frac * 100.0, 1),
        "too_cold_pct": round(cold_frac * 100.0, 1),
        "adaptive_comfort": adaptive_res,
    }


# ----------------------------------------------------------------------
# 2. Livestock Thermal Suitability & Heat Stress Engine
# ----------------------------------------------------------------------

LIVESTOCK_PROFILES = {
    "cattle": {
        "name": "Dairy & Beef Cattle",
        "temp_opt_min": 5.0,
        "temp_opt_max": 20.0,
        "temp_crit_max": 26.0,
        "thi_threshold_mild": 72.0,
        "thi_threshold_mod": 79.0,
        "thi_threshold_severe": 88.0,
    },
    "poultry": {
        "name": "Poultry (Broilers & Layers)",
        "temp_opt_min": 18.0,
        "temp_opt_max": 24.0,
        "temp_crit_max": 29.0,
        "thi_threshold_mild": 70.0,
        "thi_threshold_mod": 76.0,
        "thi_threshold_severe": 84.0,
    },
    "swine": {
        "name": "Swine / Pigs",
        "temp_opt_min": 15.0,
        "temp_opt_max": 22.0,
        "temp_crit_max": 26.0,
        "thi_threshold_mild": 72.0,
        "thi_threshold_mod": 78.0,
        "thi_threshold_severe": 85.0,
    },
    "goats_sheep": {
        "name": "Goats & Sheep",
        "temp_opt_min": 10.0,
        "temp_opt_max": 24.0,
        "temp_crit_max": 30.0,
        "thi_threshold_mild": 74.0,
        "thi_threshold_mod": 82.0,
        "thi_threshold_severe": 90.0,
    },
}


def calculate_thi(temp_c: float, rh_pct: float) -> float:
    """
    Temperature-Humidity Index (THI) for livestock heat stress (NRC Standard).
    THI = (1.8 * T + 32) - (0.55 - 0.0055 * RH) * (1.8 * T - 26)
    """
    t = float(temp_c)
    rh = float(rh_pct)
    thi = (1.8 * t + 32.0) - (0.55 - 0.0055 * rh) * (1.8 * t - 26.0)
    return round(thi, 1)


def evaluate_livestock_comfort(
    t_indoor_hourly: Union[List[float], np.ndarray],
    rh_hourly: Union[List[float], float] = 50.0,
    species: str = "cattle",
) -> Dict[str, Any]:
    """
    Evaluates livestock thermal comfort, THI heat stress risk, and cold stress.
    Returns Suitability %, Optimal %, Heat Stress %, and Cold Stress % of time.
    """
    spec_key = str(species).lower().replace(" ", "_")
    profile = LIVESTOCK_PROFILES.get(spec_key, LIVESTOCK_PROFILES["cattle"])

    t_arr = np.array(t_indoor_hourly)
    n = len(t_arr)
    rh_arr = np.full(n, rh_hourly) if isinstance(rh_hourly, (int, float)) else np.array(rh_hourly[:n])

    thi_list = [calculate_thi(t, rh) for t, rh in zip(t_arr, rh_arr)]

    opt_mask = (t_arr >= profile["temp_opt_min"]) & (t_arr <= profile["temp_opt_max"]) & (np.array(thi_list) < profile["thi_threshold_mild"])
    heat_stress_mask = (t_arr > profile["temp_opt_max"]) | (np.array(thi_list) >= profile["thi_threshold_mild"])
    cold_stress_mask = t_arr < profile["temp_opt_min"]

    opt_pct = round(float(np.mean(opt_mask)) * 100.0, 1)
    heat_stress_pct = round(float(np.mean(heat_stress_mask)) * 100.0, 1)
    cold_stress_pct = round(float(np.mean(cold_stress_mask)) * 100.0, 1)

    max_thi = float(np.max(thi_list))
    if max_thi >= profile["thi_threshold_severe"]:
        stress_status = "Severe Heat Stress (Critical Risk)"
        stress_color = "#e74c3c"
    elif max_thi >= profile["thi_threshold_mod"]:
        stress_status = "Moderate Heat Stress"
        stress_color = "#e67e22"
    elif max_thi >= profile["thi_threshold_mild"]:
        stress_status = "Mild Heat Stress"
        stress_color = "#f39c12"
    else:
        stress_status = "Optimal / Normal Thermal Zone"
        stress_color = "#2ecc71"

    # Overall Livestock Thermal Suitability (0-100%)
    suitability_pct = round(max(0.0, min(100.0, opt_pct + 0.5 * (100.0 - opt_pct - heat_stress_pct))), 1)

    return {
        "mode": "Livestock Comfort",
        "species": profile["name"],
        "thermal_suitability_pct": suitability_pct,
        "optimal_pct": opt_pct,
        "heat_stress_pct": heat_stress_pct,
        "cold_stress_pct": cold_stress_pct,
        "max_thi": max_thi,
        "avg_thi": round(float(np.mean(thi_list)), 1),
        "stress_status": stress_status,
        "stress_color": stress_color,
    }


# ----------------------------------------------------------------------
# 3. Agricultural & Storage Suitability Engine
# ----------------------------------------------------------------------

AGRICULTURAL_PROFILES = {
    "mushroom_cultivation": {
        "name": "Mushroom Cultivation (Oyster / Button)",
        "temp_min": 18.0,
        "temp_max": 24.0,
        "rh_min": 75.0,
        "rh_max": 92.0,
        "ach_min": 3.0,
    },
    "potato_onion_storage": {
        "name": "Potato & Onion Ventilated Storage",
        "temp_min": 10.0,
        "temp_max": 18.0,
        "rh_min": 70.0,
        "rh_max": 85.0,
        "ach_min": 2.0,
    },
    "grain_seed_storage": {
        "name": "Grain & Seed Dry Storage",
        "temp_min": 8.0,
        "temp_max": 22.0,
        "rh_min": 30.0,
        "rh_max": 65.0,
        "ach_min": 0.5,
    },
    "greenhouse_horticulture": {
        "name": "Greenhouse Horticulture (Vegetables/Flowers)",
        "temp_min": 20.0,
        "temp_max": 28.0,
        "rh_min": 55.0,
        "rh_max": 80.0,
        "ach_min": 2.5,
    },
}


def evaluate_agricultural_suitability(
    t_indoor_hourly: Union[List[float], np.ndarray],
    rh_hourly: Union[List[float], float] = 60.0,
    ach: float = 3.0,
    application: str = "mushroom_cultivation",
) -> Dict[str, Any]:
    """
    Evaluates agricultural and crop storage suitability:
    - Temperature suitability (%)
    - Humidity suitability (%)
    - Ventilation suitability (%)
    - Overall Agricultural Suitability Score (%)
    """
    app_key = str(application).lower().replace(" ", "_")
    profile = AGRICULTURAL_PROFILES.get(app_key, AGRICULTURAL_PROFILES["mushroom_cultivation"])

    t_arr = np.array(t_indoor_hourly)
    n = len(t_arr)
    rh_arr = np.full(n, rh_hourly) if isinstance(rh_hourly, (int, float)) else np.array(rh_hourly[:n])

    # 1. Temperature Suitability
    temp_in_range = (t_arr >= profile["temp_min"]) & (t_arr <= profile["temp_max"])
    temp_score_pct = round(float(np.mean(temp_in_range)) * 100.0, 1)

    # 2. Humidity Suitability
    rh_in_range = (rh_arr >= profile["rh_min"]) & (rh_arr <= profile["rh_max"])
    rh_score_pct = round(float(np.mean(rh_in_range)) * 100.0, 1)

    # 3. Ventilation Suitability
    vent_score_pct = round(min(100.0, (ach / profile["ach_min"]) * 100.0), 1)

    # Overall Weighted Agricultural Suitability (0-100%)
    overall_agri_pct = round(
        0.45 * temp_score_pct + 0.35 * rh_score_pct + 0.20 * vent_score_pct, 1
    )

    return {
        "mode": "Agricultural Storage",
        "application": profile["name"],
        "agricultural_suitability_pct": overall_agri_pct,
        "temperature_suitability_pct": temp_score_pct,
        "humidity_suitability_pct": rh_score_pct,
        "ventilation_suitability_pct": vent_score_pct,
    }


# ----------------------------------------------------------------------
# 4. Multi-Application Universal Suitability Matrix
# ----------------------------------------------------------------------

def evaluate_multi_application_suitability(
    t_indoor_hourly: Union[List[float], np.ndarray],
    rh_hourly: Union[List[float], float] = 50.0,
    ach: float = 3.0,
    t_outdoor_mean: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Evaluates the SAME physical shelter across different application archetypes:
    - 🏠 Human Residential (Comfort Score %)
    - 🐄 Dairy Cattle (Thermal Suitability %)
    - 🌾 Agricultural Storage / Mushrooms (Storage Suitability %)

    Returns a cross-domain comparison dictionary and formatted dataframe.
    """
    human_res = evaluate_human_comfort(
        t_indoor_hourly=t_indoor_hourly,
        rh_hourly=rh_hourly,
        t_outdoor_mean=t_outdoor_mean,
    )
    cattle_res = evaluate_livestock_comfort(
        t_indoor_hourly=t_indoor_hourly,
        rh_hourly=rh_hourly,
        species="cattle",
    )
    poultry_res = evaluate_livestock_comfort(
        t_indoor_hourly=t_indoor_hourly,
        rh_hourly=rh_hourly,
        species="poultry",
    )
    mushroom_res = evaluate_agricultural_suitability(
        t_indoor_hourly=t_indoor_hourly,
        rh_hourly=rh_hourly,
        ach=ach,
        application="mushroom_cultivation",
    )
    grain_res = evaluate_agricultural_suitability(
        t_indoor_hourly=t_indoor_hourly,
        rh_hourly=rh_hourly,
        ach=ach,
        application="grain_seed_storage",
    )

    comparison_rows = [
        {
            "Domain / Archetype": "🏠 Human Shelter",
            "Target Requirement": "PMV -0.5 to +0.5 | Adaptive Comfort",
            "Suitability Score": f"{human_res['comfort_score']}%",
            "Optimal Time": f"{human_res['comfortable_pct']}%",
            "Risk / Discomfort": f"{human_res['too_hot_pct']}% Hot | {human_res['too_cold_pct']}% Cold",
        },
        {
            "Domain / Archetype": "🐄 Cattle Housing",
            "Target Requirement": "5°C – 20°C | THI < 72",
            "Suitability Score": f"{cattle_res['thermal_suitability_pct']}%",
            "Optimal Time": f"{cattle_res['optimal_pct']}%",
            "Risk / Discomfort": f"{cattle_res['heat_stress_pct']}% Heat Stress",
        },
        {
            "Domain / Archetype": "🐔 Poultry Housing",
            "Target Requirement": "18°C – 24°C | THI < 70",
            "Suitability Score": f"{poultry_res['thermal_suitability_pct']}%",
            "Optimal Time": f"{poultry_res['optimal_pct']}%",
            "Risk / Discomfort": f"{poultry_res['heat_stress_pct']}% Heat Stress",
        },
        {
            "Domain / Archetype": "🍄 Mushroom Cultivation",
            "Target Requirement": "18°C – 24°C | RH 75–92% | ACH ≥ 3",
            "Suitability Score": f"{mushroom_res['agricultural_suitability_pct']}%",
            "Optimal Time": f"{mushroom_res['temperature_suitability_pct']}% (Temp)",
            "Risk / Discomfort": f"RH Fit: {mushroom_res['humidity_suitability_pct']}%",
        },
        {
            "Domain / Archetype": "🌾 Grain & Seed Storage",
            "Target Requirement": "8°C – 22°C | RH < 65%",
            "Suitability Score": f"{grain_res['agricultural_suitability_pct']}%",
            "Optimal Time": f"{grain_res['temperature_suitability_pct']}% (Temp)",
            "Risk / Discomfort": f"RH Fit: {grain_res['humidity_suitability_pct']}%",
        },
    ]

    df_multi = pd.DataFrame(comparison_rows)

    return {
        "human_comfort": human_res,
        "cattle_suitability": cattle_res,
        "poultry_suitability": poultry_res,
        "mushroom_storage": mushroom_res,
        "grain_storage": grain_res,
        "comparison_table": df_multi,
        "scores_summary": {
            "Human": human_res["comfort_score"],
            "Cattle": cattle_res["thermal_suitability_pct"],
            "Poultry": poultry_res["thermal_suitability_pct"],
            "Mushrooms": mushroom_res["agricultural_suitability_pct"],
            "Grain Storage": grain_res["agricultural_suitability_pct"],
        },
    }
