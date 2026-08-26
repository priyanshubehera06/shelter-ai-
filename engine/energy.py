"""
energy.py — HVAC active heating, cooling, and annual energy demand engine for Shelter-AI.
Calculates hourly, daily, monthly, and annual active energy requirements needed
to maintain indoor thermal comfort setpoints after passive design measures.
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import numpy as np
import pandas as pd


def calculate_hourly_hvac_loads(
    t_indoor_hourly: Union[List[float], np.ndarray],
    floor_area_m2: float = 24.0,
    volume_m3: float = 72.0,
    ua_envelope_w_k: float = 120.0,
    t_target_cool: float = 26.0,
    t_target_heat: float = 20.0,
    cop_cooling: float = 3.2,
    cop_heating: float = 2.8,
) -> Dict[str, Any]:
    """
    Computes hourly sensible heating and cooling active loads (kW and kWh)
    to maintain indoor temperature within [t_target_heat, t_target_cool].
    """
    t_arr = np.array(t_indoor_hourly, dtype=float)
    n_hours = len(t_arr)

    cooling_thermal_kw = np.zeros(n_hours)
    heating_thermal_kw = np.zeros(n_hours)
    cooling_elec_kwh = np.zeros(n_hours)
    heating_elec_kwh = np.zeros(n_hours)

    # Air thermal capacitance rate: m_dot * Cp + UA
    # Effective sensible load per degree delta: (UA + 0.33 * ACH * Vol) / 1000 kW/K
    load_factor_kw_k = max(0.05, (ua_envelope_w_k + 0.33 * 2.0 * volume_m3) / 1000.0)

    for i, t_in in enumerate(t_arr):
        if t_in > t_target_cool:
            # Active cooling required
            delta_t = t_in - t_target_cool
            q_th_kw = delta_t * load_factor_kw_k
            cooling_thermal_kw[i] = q_th_kw
            cooling_elec_kwh[i] = q_th_kw / max(1.0, cop_cooling)
        elif t_in < t_target_heat:
            # Active heating required
            delta_t = t_target_heat - t_in
            q_th_kw = delta_t * load_factor_kw_k
            heating_thermal_kw[i] = q_th_kw
            heating_elec_kwh[i] = q_th_kw / max(1.0, cop_heating)

    return {
        "cooling_thermal_kw": [round(float(x), 2) for x in cooling_thermal_kw],
        "heating_thermal_kw": [round(float(x), 2) for x in heating_thermal_kw],
        "cooling_elec_kwh": [round(float(x), 2) for x in cooling_elec_kwh],
        "heating_elec_kwh": [round(float(x), 2) for x in heating_elec_kwh],
        "peak_cooling_kw": round(float(np.max(cooling_thermal_kw)), 2),
        "peak_heating_kw": round(float(np.max(heating_thermal_kw)), 2),
        "daily_cooling_kwh": round(float(np.sum(cooling_elec_kwh)), 2),
        "daily_heating_kwh": round(float(np.sum(heating_elec_kwh)), 2),
        "daily_total_kwh": round(float(np.sum(cooling_elec_kwh) + np.sum(heating_elec_kwh)), 2),
    }


def calculate_annual_energy_loads(
    t_indoor_hourly: Union[List[float], np.ndarray],
    floor_area_m2: float = 24.0,
    volume_m3: Optional[float] = None,
    ua_envelope_w_k: float = 120.0,
    t_base_cool: float = 26.0,
    t_base_heat: float = 20.0,
    cop_cooling: float = 3.2,
    cop_heating: float = 2.8,
    electricity_cost_inr_kwh: float = 7.50,
    grid_emission_factor_kg_kwh: float = 0.72,
) -> Dict[str, Any]:
    """
    Calculates comprehensive annual, monthly, daily, and hourly heating & cooling demand.
    Returns:
    - Hourly cooling & heating loads
    - Peak cooling & heating kW
    - Daily, monthly, and annual electrical energy demand (kWh)
    - Energy Use Intensity (EUI in kWh/m²/yr)
    - Operating cost (₹/yr) and operational carbon emissions (kg CO₂/yr)
    - Percentage energy savings vs. uninsulated baseline
    """
    area = max(1.0, float(floor_area_m2))
    vol = volume_m3 if volume_m3 is not None else area * 2.8

    # 1. Compute 24-Hour Diurnal Dynamics
    hvac_24h = calculate_hourly_hvac_loads(
        t_indoor_hourly=t_indoor_hourly,
        floor_area_m2=area,
        volume_m3=vol,
        ua_envelope_w_k=ua_envelope_w_k,
        t_target_cool=t_base_cool,
        t_target_heat=t_base_heat,
        cop_cooling=cop_cooling,
        cop_heating=cop_heating,
    )

    # 2. Degree-Hours Scaling for Monthly & Annual Estimates
    t_arr = np.array(t_indoor_hourly)
    cdh_24h = float(np.sum(np.maximum(0.0, t_arr - t_base_cool)))
    hdh_24h = float(np.sum(np.maximum(0.0, t_base_heat - t_arr)))

    # Seasonal variation factors across 12 months (for Indian / subtropical climatic variance)
    # Jan (1) to Dec (12)
    cooling_seasonal_weights = [0.15, 0.35, 0.85, 1.35, 1.60, 1.40, 1.10, 1.05, 1.00, 0.80, 0.35, 0.10]
    heating_seasonal_weights = [1.80, 1.20, 0.40, 0.05, 0.00, 0.00, 0.00, 0.00, 0.00, 0.10, 0.80, 1.65]

    days_in_months = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    daily_cool_base = hvac_24h["daily_cooling_kwh"]
    daily_heat_base = hvac_24h["daily_heating_kwh"]

    monthly_cooling_kwh = []
    monthly_heating_kwh = []
    monthly_total_kwh = []

    for m_idx in range(12):
        c_weight = cooling_seasonal_weights[m_idx]
        h_weight = heating_seasonal_weights[m_idx]
        days = days_in_months[m_idx]

        m_cool = round(daily_cool_base * c_weight * days, 1)
        m_heat = round(daily_heat_base * h_weight * days, 1)
        m_tot = round(m_cool + m_heat, 1)

        monthly_cooling_kwh.append(m_cool)
        monthly_heating_kwh.append(m_heat)
        monthly_total_kwh.append(m_tot)

    annual_cooling_kwh = round(float(np.sum(monthly_cooling_kwh)), 1)
    annual_heating_kwh = round(float(np.sum(monthly_heating_kwh)), 1)
    total_annual_kwh = round(annual_cooling_kwh + annual_heating_kwh, 1)

    # 3. Energy Use Intensity (EUI in kWh/m²/yr)
    cooling_load_kwh_m2 = round(annual_cooling_kwh / area, 1)
    heating_load_kwh_m2 = round(annual_heating_kwh / area, 1)
    total_thermal_kwh_m2 = round(total_annual_kwh / area, 1)

    # 4. Energy Cost & Operational Carbon
    annual_opex_inr = round(total_annual_kwh * electricity_cost_inr_kwh, 2)
    annual_co2_kg = round(total_annual_kwh * grid_emission_factor_kg_kwh, 1)

    # 5. Baseline Comparison (Uninsulated shelter benchmark ~ 120-150 kWh/m²/yr)
    baseline_annual_kwh = round(140.0 * area, 1)
    energy_savings_pct = round(max(0.0, min(95.0, (1.0 - (total_annual_kwh / max(1.0, baseline_annual_kwh))) * 100.0)), 1)

    # Monthly breakdown DataFrame
    df_monthly = pd.DataFrame({
        "Month": month_names,
        "Cooling Demand (kWh)": monthly_cooling_kwh,
        "Heating Demand (kWh)": monthly_heating_kwh,
        "Total Energy (kWh)": monthly_total_kwh,
    })

    return {
        # High-level Annual Totals
        "annual_cooling_kwh": annual_cooling_kwh,
        "annual_heating_kwh": annual_heating_kwh,
        "total_annual_kwh": total_annual_kwh,
        "total_annual_energy_kwh": total_annual_kwh,
        # Energy Use Intensity (EUI)
        "cooling_load_kwh_m2": cooling_load_kwh_m2,
        "heating_load_kwh_m2": heating_load_kwh_m2,
        "total_thermal_load_kwh_m2": total_thermal_kwh_m2,
        "eui_kwh_m2_yr": total_thermal_kwh_m2,
        # Peak & Daily Loads
        "peak_cooling_load_kw": hvac_24h["peak_cooling_kw"],
        "peak_heating_load_kw": hvac_24h["peak_heating_kw"],
        "daily_cooling_kwh": hvac_24h["daily_cooling_kwh"],
        "daily_heating_kwh": hvac_24h["daily_heating_kwh"],
        "hourly_cooling_kw": hvac_24h["cooling_thermal_kw"],
        "hourly_heating_kw": hvac_24h["heating_thermal_kw"],
        "hourly_cooling_kwh": hvac_24h["cooling_elec_kwh"],
        "hourly_heating_kwh": hvac_24h["heating_elec_kwh"],
        # Monthly Breakdown
        "monthly_cooling_kwh": monthly_cooling_kwh,
        "monthly_heating_kwh": monthly_heating_kwh,
        "monthly_total_kwh": monthly_total_kwh,
        "monthly_df": df_monthly,
        # Financial & Carbon Impact
        "annual_electricity_cost_inr": annual_opex_inr,
        "annual_operational_carbon_kgco2": annual_co2_kg,
        "baseline_uninsulated_kwh": baseline_annual_kwh,
        "energy_savings_vs_uninsulated_pct": energy_savings_pct,
    }


def compare_design_energy(
    design_a: Dict[str, Any],
    design_b: Dict[str, Any],
    label_a: str = "Design A (Passive Optimized)",
    label_b: str = "Design B (Standard / Baseline)",
    electricity_rate_inr: float = 7.50,
) -> Dict[str, Any]:
    """
    Compares two shelter designs side-by-side:
    - Annual Cooling demand (kWh)
    - Annual Heating demand (kWh)
    - Total energy (kWh/year)
    - Financial OPEX savings (₹/year)
    - Operational carbon savings (kg CO₂/year)
    """
    a_cool = design_a.get("annual_cooling_kwh", design_a.get("cooling_load_kwh_m2", 0.0) * 24.0)
    a_heat = design_a.get("annual_heating_kwh", design_a.get("heating_load_kwh_m2", 0.0) * 24.0)
    a_tot = design_a.get("total_annual_kwh", a_cool + a_heat)

    b_cool = design_b.get("annual_cooling_kwh", design_b.get("cooling_load_kwh_m2", 0.0) * 24.0)
    b_heat = design_b.get("annual_heating_kwh", design_b.get("heating_load_kwh_m2", 0.0) * 24.0)
    b_tot = design_b.get("total_annual_kwh", b_cool + b_heat)

    savings_kwh = round(b_tot - a_tot, 1)
    savings_pct = round((savings_kwh / max(1.0, b_tot)) * 100.0, 1)
    cost_saved_inr = round(savings_kwh * electricity_rate_inr, 2)
    co2_saved_kg = round(savings_kwh * 0.72, 1)

    df_comparison = pd.DataFrame([
        {
            "Metric": "Annual Cooling Demand",
            label_a: f"{a_cool:,.1f} kWh",
            label_b: f"{b_cool:,.1f} kWh",
            "Difference / Savings": f"{b_cool - a_cool:+,.1f} kWh",
        },
        {
            "Metric": "Annual Heating Demand",
            label_a: f"{a_heat:,.1f} kWh",
            label_b: f"{b_heat:,.1f} kWh",
            "Difference / Savings": f"{b_heat - a_heat:+,.1f} kWh",
        },
        {
            "Metric": "Total Annual HVAC Demand",
            label_a: f"{a_tot:,.1f} kWh/year",
            label_b: f"{b_tot:,.1f} kWh/year",
            "Difference / Savings": f"{savings_kwh:+,.1f} kWh/year ({savings_pct:+.1f}%)",
        },
        {
            "Metric": "Estimated Annual OPEX Cost",
            label_a: f"₹{a_tot * electricity_rate_inr:,.2f}/year",
            label_b: f"₹{b_tot * electricity_rate_inr:,.2f}/year",
            "Difference / Savings": f"₹{cost_saved_inr:,.2f}/year",
        },
        {
            "Metric": "Annual Operational Carbon",
            label_a: f"{a_tot * 0.72:,.1f} kg CO₂",
            label_b: f"{b_tot * 0.72:,.1f} kg CO₂",
            "Difference / Savings": f"{co2_saved_kg:,.1f} kg CO₂",
        },
    ])

    return {
        "label_a": label_a,
        "label_b": label_b,
        "design_a_total_kwh": a_tot,
        "design_b_total_kwh": b_tot,
        "savings_kwh_yr": savings_kwh,
        "savings_pct": savings_pct,
        "cost_saved_inr_yr": cost_saved_inr,
        "co2_saved_kg_yr": co2_saved_kg,
        "comparison_table": df_comparison,
        "summary": f"{label_a} achieves {savings_kwh:,.0f} kWh/year ({savings_pct:.1f}%) energy savings over {label_b}, reducing operational costs by ₹{cost_saved_inr:,.2f}/year.",
    }
