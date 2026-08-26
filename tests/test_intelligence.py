import pytest
from engine.climate_intelligence import analyze_climate_intelligence
from engine.extreme_analysis import analyze_extreme_climate_events
from engine.passive_design import generate_passive_design_recommendations
from engine.material_recommender import recommend_materials
from engine.resilience import evaluate_shelter_resilience
from engine.geometry import ShelterGeometry


def test_climate_intelligence_analysis():
    res = analyze_climate_intelligence()
    assert "climate_zone" in res
    assert "mean_temp_c" in res
    assert "avg_diurnal_swing_c" in res
    assert len(res["structured_insights"]) >= 2
    for insight in res["structured_insights"]:
        assert "category" in insight
        assert "recommendation" not in insight or "insight" in insight
        assert "priority" in insight


def test_extreme_analysis_scenarios_and_risk_score():
    ext = analyze_extreme_climate_events()
    assert "extreme_climate_risk_score" in ext
    assert 0.0 <= ext["extreme_climate_risk_score"] <= 100.0
    assert "scenarios" in ext
    for sc in ["NORMAL", "HOT", "EXTREME_HOT", "COLD", "EXTREME_COLD"]:
        assert sc in ext["scenarios"]
        assert len(ext["scenarios"][sc]) == 24


def test_passive_design_recommendations():
    recs = generate_passive_design_recommendations()
    assert "recommendations" in recs
    assert len(recs["recommendations"]) == 6  # 6 core pillars
    categories = [r["category"] for r in recs["recommendations"]]
    assert "ORIENTATION" in categories
    assert "MATERIALS" in categories
    assert "GEOMETRY" in categories
    assert "VENTILATION" in categories
    assert "OPENINGS" in categories
    assert "SHADING" in categories
    for r in recs["recommendations"]:
        assert "recommendation" in r
        assert "reason" in r
        assert "priority" in r
        assert "expected_benefit" in r


def test_material_recommender():
    mat_res = recommend_materials(climate_zone="Hot and Arid", budget_level="medium")
    assert "top_ranked_assemblies" in mat_res
    assert len(mat_res["top_ranked_assemblies"]) > 0
    best = mat_res["best_assembly"]
    assert best is not None
    assert "wall_name" in best
    assert "roof_name" in best
    assert 0.0 <= best["composite_suitability_score"] <= 100.0


def test_shelter_resilience_stress_test():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8)
    res_eval = evaluate_shelter_resilience(
        geometry=geom,
        wall_mat_id="cseb_interlocking",
        wall_thickness_cm=20.0,
        roof_mat_id="roof_cgi_insulated",
        insulation_mat_id="insulation_rockwool",
        insulation_thickness_cm=5.0,
    )
    assert "thermal_resilience_score" in res_eval
    assert 0.0 <= res_eval["thermal_resilience_score"] <= 100.0
    assert "scenario_results" in res_eval
    assert "EXTREME_HOT" in res_eval["scenario_results"]
    assert len(res_eval["scenario_performance_table"]) == 5
