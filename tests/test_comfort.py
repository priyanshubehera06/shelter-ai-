import pytest
import numpy as np
from engine.comfort import (
    calculate_pmv_fanger,
    calculate_adaptive_comfort,
    get_comfort_category,
    evaluate_human_comfort,
    evaluate_livestock_comfort,
    evaluate_agricultural_suitability,
    evaluate_multi_application_suitability,
    calculate_thi,
)


def test_pmv_fanger_bounds():
    pmv, ppd = calculate_pmv_fanger(ta=24.0, rh=50.0, vel=0.15, met=1.1, clo=0.5)
    assert -3.0 <= pmv <= 3.0
    assert 5.0 <= ppd <= 100.0


def test_adaptive_comfort_ashrae55():
    t_hourly = [22.0, 24.0, 26.0, 28.0, 30.0, 28.0, 25.0, 23.0] * 3
    res = calculate_adaptive_comfort(t_hourly[:24], t_outdoor_mean=28.0)
    assert "t_comfort_target_c" in res
    assert "upper_limit_80_c" in res
    assert "lower_limit_80_c" in res
    assert 0.0 <= res["compliance_pct"] <= 100.0


def test_evaluate_human_comfort():
    t_hourly = [24.0, 25.0, 26.0, 27.0, 29.0, 31.0, 28.0, 25.0] * 3
    res = evaluate_human_comfort(t_hourly[:24], rh_hourly=50.0, t_outdoor_mean=28.0)
    assert 0 <= res["comfort_score"] <= 100
    assert res["comfortable_hours_annual"] + res["too_hot_hours_annual"] + res["too_cold_hours_annual"] == 8760
    assert "status_label" in res


def test_livestock_thi_and_stress():
    thi = calculate_thi(temp_c=32.0, rh_pct=75.0)
    assert thi > 78.0  # Moderate/severe stress range
    
    t_hourly = [28.0, 30.0, 32.0, 34.0, 35.0, 33.0, 30.0, 28.0] * 3
    c_res = evaluate_livestock_comfort(t_hourly[:24], rh_hourly=70.0, species="cattle")
    assert 0.0 <= c_res["thermal_suitability_pct"] <= 100.0
    assert c_res["heat_stress_pct"] > 0.0


def test_agricultural_storage_suitability():
    t_hourly = [20.0, 21.0, 22.0, 23.0, 22.0, 21.0, 20.0, 19.0] * 3
    m_res = evaluate_agricultural_suitability(t_hourly[:24], rh_hourly=85.0, ach=3.5, application="mushroom_cultivation")
    assert "agricultural_suitability_pct" in m_res
    assert m_res["temperature_suitability_pct"] == 100.0
    assert m_res["humidity_suitability_pct"] == 100.0


def test_multi_application_cross_evaluation():
    t_hourly = [24.0, 26.0, 28.0, 30.0, 28.0, 26.0, 25.0, 24.0] * 3
    m_res = evaluate_multi_application_suitability(t_hourly[:24], rh_hourly=55.0, ach=3.0)
    assert "scores_summary" in m_res
    assert "Human" in m_res["scores_summary"]
    assert "Cattle" in m_res["scores_summary"]
    assert "Mushrooms" in m_res["scores_summary"]
