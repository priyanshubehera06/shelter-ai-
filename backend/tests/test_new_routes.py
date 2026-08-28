"""
test_new_routes.py — Integration tests for newly registered FastAPI routes:
/api/recommendations, /api/compliance, and /api/thermal-vulnerability.
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_api_tvi_all():
    res = client.get("/api/thermal-vulnerability")
    assert res.status_code == 200
    data = res.json()
    assert "states_ranked" in data
    assert len(data["states_ranked"]) > 0


def test_api_tvi_single_state():
    res = client.get("/api/thermal-vulnerability/Odisha")
    assert res.status_code == 200
    data = res.json()
    assert data["state_name"] == "Odisha"
    assert "variables" in data
    assert "tvi_score" in data


def test_api_recommendations_run():
    payload = {
        "climate_zone": "Composite",
        "state_code": "OD",
        "budget_level": "medium",
        "shelter_type": "Standard Residential",
        "disaster_mode": None
    }
    res = client.post("/api/recommendations/run", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "material_recommendations" in data
    assert len(data["material_recommendations"]) >= 6
    assert "construction_recommendation" in data


def test_api_compliance_check():
    payload = {
        "state_name": "Odisha",
        "building_type": "Residential / Transitional Shelter",
        "geometry": {
            "length_m": 6.0,
            "width_m": 4.0,
            "height_m": 2.8,
            "roof_type": "pitched",
            "roof_pitch_deg": 15.0,
            "wall_thickness_cm": 20.0,
            "wwr_pct": 15.0,
            "overhang_m": 0.6,
            "orientation_deg": 0.0,
            "door_width_m": 0.9,
            "door_height_m": 2.1,
            "door_count": 1
        },
        "materials": {
            "wall_mat_id": "cseb_interlocking",
            "wall_thickness_cm": 20.0,
            "roof_mat_id": "roof_cgi_insulated",
            "insulation_mat_id": "insulation_rockwool",
            "insulation_thickness_cm": 5.0,
            "glazing_mat_id": "glazing_single"
        }
    }
    res = client.post("/api/compliance/check", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "overall_status" in data
    assert "results" in data
    assert len(data["results"]) > 0
