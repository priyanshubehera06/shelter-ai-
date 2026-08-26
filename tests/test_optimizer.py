import pytest
from engine.optimizer import evaluate_design_candidate, run_pareto_optimization


def test_evaluate_design_candidate():
    candidate = {
        "length_m": 6.0,
        "width_m": 4.0,
        "height_m": 2.8,
        "roof_type": "pitched",
        "roof_pitch_deg": 15.0,
        "wall_mat_id": "cseb_interlocking",
        "wall_thickness_cm": 20.0,
        "roof_mat_id": "roof_cgi_insulated",
        "glazing_mat_id": "glazing_double",
        "insulation_mat_id": "insulation_rockwool",
        "insulation_thickness_cm": 5.0,
        "wwr_pct": 15.0,
        "overhang_m": 0.6,
        "orientation_deg": 0.0,
    }
    res = evaluate_design_candidate(candidate)
    assert "cost_inr" in res
    assert "annual_energy_kwh" in res
    assert "comfort_score" in res
    assert "resilience_score" in res
    assert res["cost_inr"] > 0.0
    assert res["annual_energy_kwh"] > 0.0
    assert 0 <= res["comfort_score"] <= 100


def test_run_pareto_optimization():
    opt_res = run_pareto_optimization(population_size=15)
    assert "pareto_front" in opt_res
    assert "top_4_designs" in opt_res
    assert len(opt_res["all_candidates"]) == 15
    assert len(opt_res["pareto_front"]) > 0

    top_4 = opt_res["top_4_designs"]
    assert "best_balanced" in top_4
    assert "best_comfort" in top_4
    assert "lowest_energy" in top_4
    assert "lowest_cost" in top_4

    # Verify best comfort has top comfort score
    assert top_4["best_comfort"]["comfort_score"] >= 0
    # Verify lowest cost has minimal cost in population
    all_costs = [c["cost_inr"] for c in opt_res["all_candidates"]]
    assert top_4["lowest_cost"]["cost_inr"] == min(all_costs)
    # Verify lowest energy has minimal annual energy in population
    all_energies = [c["annual_energy_kwh"] for c in opt_res["all_candidates"]]
    assert top_4["lowest_energy"]["annual_energy_kwh"] == min(all_energies)
