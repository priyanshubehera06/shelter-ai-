"""
test_tvi_compliance.py — Unit and integration tests for TVI, Policy Compliance, and Recommendation engines.
"""

import pytest
from engine.tvi.tvi_engine import calculate_state_tvi, get_all_states_tvi, load_tvi_sources
from engine.compliance.compliance_engine import run_compliance_audit
from engine.recommendation.material_recommender import generate_material_recommendations
from engine.recommendation.construction_recommender import recommend_construction_method


def test_tvi_odisha_and_rajasthan():
    od_res = calculate_state_tvi("Odisha")
    assert od_res is not None
    assert od_res["state_name"] == "Odisha"
    assert od_res["tvi_score"] > 0.0
    assert od_res["category"] in ["Moderate", "High", "Very High"]
    assert "passive_priorities" in od_res
    assert len(od_res["passive_priorities"]) > 0

    rj_res = calculate_state_tvi("Rajasthan")
    assert rj_res is not None
    assert rj_res["tvi_score"] >= od_res["tvi_score"] or rj_res["variables"]["heat_exposure"] > 80.0


def test_tvi_all_states_ranking():
    all_res = get_all_states_tvi()
    assert all_res["total_states"] >= 10
    assert len(all_res["states_ranked"]) >= 10
    # Verify descending sort
    scores = [s["tvi_score"] for s in all_res["states_ranked"]]
    assert scores == sorted(scores, reverse=True)
    assert len(all_res["sources"]) >= 5


def test_compliance_audit_odisha():
    design_params = {
        "geometry": {
            "length_m": 6.0,
            "width_m": 4.0,
            "height_m": 2.8,
            "wwr_pct": 15.0,
            "overhang_m": 0.6,
            "roof_pitch_deg": 15.0
        },
        "materials": {
            "wall_mat_id": "cseb_interlocking",
            "roof_mat_id": "roof_concrete_slab",
            "glazing_mat_id": "glazing_single"
        }
    }
    sim_metrics = {"u_wall": 0.52, "u_roof": 0.85}
    audit = run_compliance_audit(design_params, sim_metrics, state_name="Odisha")
    assert "summary" in audit
    assert audit["summary"]["total_rules_checked"] > 0
    assert any(r["jurisdiction"] == "Central" for r in audit["results"])
    assert any("State" in r["jurisdiction"] for r in audit["results"])


def test_material_recommendations():
    rec_hot_dry = generate_material_recommendations(climate_zone="Hot & Dry", budget_level="medium")
    assert len(rec_hot_dry["recommendations"]) >= 8
    wall_rec = next(r for r in rec_hot_dry["recommendations"] if r["item"] == "WALL SYSTEM")
    assert wall_rec["score"] > 50.0
    assert "reason" in wall_rec

    rec_flood = generate_material_recommendations(climate_zone="Warm & Humid", disaster_mode="Flood")
    assert len(rec_flood["recommendations"]) >= 8


def test_construction_method_recommendation():
    const_rec = recommend_construction_method(climate_zone="Warm & Humid", disaster_mode="Flood")
    assert "best_construction_method" in const_rec
    assert len(const_rec["ranked_methods"]) >= 4
