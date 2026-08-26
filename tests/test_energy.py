import pytest
import numpy as np
from engine.energy import (
    calculate_hourly_hvac_loads,
    calculate_annual_energy_loads,
    compare_design_energy,
)


def test_hourly_cooling_loads():
    # Indoor temp 35°C vs target 27°C -> active cooling demand
    t_hourly = [35.0] * 24
    res = calculate_hourly_hvac_loads(t_hourly, floor_area_m2=24.0, t_target_cool=27.0)
    assert all(kw > 0 for kw in res["cooling_thermal_kw"])
    assert all(kw == 0 for kw in res["heating_thermal_kw"])
    assert res["peak_cooling_kw"] > 0.0
    assert res["daily_cooling_kwh"] > 0.0


def test_hourly_heating_loads():
    # Indoor temp 12°C vs target 20°C -> active heating demand
    t_hourly = [12.0] * 24
    res = calculate_hourly_hvac_loads(t_hourly, floor_area_m2=24.0, t_target_heat=20.0)
    assert all(kw > 0 for kw in res["heating_thermal_kw"])
    assert all(kw == 0 for kw in res["cooling_thermal_kw"])
    assert res["peak_heating_kw"] > 0.0
    assert res["daily_heating_kwh"] > 0.0


def test_annual_energy_breakdown():
    t_hourly = [24.0, 26.0, 28.0, 32.0, 35.0, 33.0, 29.0, 25.0] * 3
    ann_res = calculate_annual_energy_loads(t_hourly[:24], floor_area_m2=24.0, t_base_cool=26.0, t_base_heat=20.0)
    assert "annual_cooling_kwh" in ann_res
    assert "annual_heating_kwh" in ann_res
    assert "total_annual_kwh" in ann_res
    assert len(ann_res["monthly_cooling_kwh"]) == 12
    assert "eui_kwh_m2_yr" in ann_res
    assert ann_res["annual_electricity_cost_inr"] > 0.0


def test_compare_design_energy_scenario():
    design_a = {"annual_cooling_kwh": 1450.0, "annual_heating_kwh": 100.0, "total_annual_kwh": 1550.0}
    design_b = {"annual_cooling_kwh": 2400.0, "annual_heating_kwh": 120.0, "total_annual_kwh": 2520.0}
    comp = compare_design_energy(design_a, design_b, label_a="Design A", label_b="Design B")
    assert comp["savings_kwh_yr"] == pytest.approx(970.0, 0.1)
    assert comp["savings_pct"] == pytest.approx(38.5, 0.5)
    assert comp["cost_saved_inr_yr"] > 0.0
