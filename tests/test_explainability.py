import pytest
from engine.explainability import generate_design_explanation


def test_generate_design_explanation():
    candidate = {
        "candidate": {
            "wall_mat_id": "cseb_interlocking",
            "roof_mat_id": "roof_cgi_insulated",
            "insulation_mat_id": "insulation_rockwool",
            "insulation_thickness_cm": 5.0,
            "wwr_pct": 15.0,
            "overhang_m": 0.6,
            "orientation_deg": 0.0,
        },
        "comfort_score": 88,
        "annual_energy_kwh": 1450.0,
        "cost_inr": 78500.0,
        "damping_factor": 0.45,
        "max_indoor_temp": 31.5,
    }

    res = generate_design_explanation(candidate, climate_zone="Composite / Moderate")
    assert "executive_summary" in res
    assert "explanations" in res
    assert len(res["explanations"]) == 5

    pillars = [e["pillar"] for e in res["explanations"]]
    assert "Orientation" in pillars
    assert "Walls & Mass" in pillars
    assert "Roof & Insulation" in pillars
    assert "Windows & Shading" in pillars
    assert "Lifecycle Economics" in pillars

    for exp in res["explanations"]:
        assert len(exp["explanation"]) > 20
        assert "icon" in exp
