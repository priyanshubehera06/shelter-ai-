"""
test_api.py — Integration tests for FastAPI REST API endpoints.
"""

import pytest
from starlette.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    # Test Render health check path /health
    response_health = client.get("/health")
    assert response_health.status_code == 200
    data_health = response_health.json()
    assert data_health["status"] == "ok"

    # Test /api/health
    response_api = client.get("/api/health")
    assert response_api.status_code == 200
    data_api = response_api.json()
    assert data_api["status"] == "ok"
    assert "ShelterAI" in data_api["service"]

    # Test root endpoint /
    response_root = client.get("/")
    assert response_root.status_code == 200
    data_root = response_root.json()
    assert data_root["status"] == "running"
    assert "ShelterAI" in data_root["name"]


def test_locations_endpoint():
    response = client.get("/api/climate/locations")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 4
    assert any(loc["id"] == "sambalpur" for loc in data)


def test_climate_analysis_endpoint():
    response = client.get("/api/climate/analyze/sambalpur?month=5")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["hourly_records_24h"]) == 24
    assert data["summary"]["peak_summer_temp"] > 30.0


def test_materials_endpoint():
    response = client.get("/api/materials")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 8
    
    # Filter by category
    resp_wall = client.get("/api/materials?category=Wall")
    assert resp_wall.status_code == 200
    assert all(m["category"] == "Wall" for m in resp_wall.json())


def test_simulation_endpoint():
    payload = {
        "location_id": "sambalpur",
        "month": 5,
        "geometry": {
            "length_m": 6.0,
            "width_m": 4.0,
            "height_m": 2.8,
            "roof_type": "pitched",
            "roof_pitch_deg": 15.0,
            "wall_thickness_cm": 20.0,
            "wwr_pct": 15.0,
            "overhang_m": 0.6,
            "orientation_deg": 0.0
        },
        "materials": {
            "wall_mat_id": "cseb_interlocking",
            "wall_thickness_cm": 20.0,
            "roof_mat_id": "roof_cgi_insulated",
            "insulation_mat_id": "insulation_rockwool",
            "insulation_thickness_cm": 5.0,
            "glazing_mat_id": "glazing_single"
        },
        "occupants": 4
    }
    response = client.post("/api/simulation/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert len(data["hourly_results"]) == 24
    assert data["summary"]["comfort_score"] >= 0.0
    assert data["summary"]["total_capex_cost_inr"] > 0


def test_digital_twin_config_endpoint():
    payload = {
        "geometry": {
            "length_m": 6.0,
            "width_m": 4.0,
            "height_m": 2.8,
            "roof_type": "pitched",
            "roof_pitch_deg": 15.0,
            "wall_thickness_cm": 20.0,
            "wwr_pct": 15.0,
            "overhang_m": 0.6,
            "orientation_deg": 0.0
        },
        "materials": {
            "wall_mat_id": "cseb_interlocking",
            "wall_thickness_cm": 20.0,
            "roof_mat_id": "roof_cgi_insulated",
            "insulation_mat_id": "insulation_rockwool",
            "insulation_thickness_cm": 5.0,
            "glazing_mat_id": "glazing_single"
        },
        "hour_of_day": 13.0,
        "location_id": "sambalpur",
        "month": 5
    }
    response = client.post("/api/digital-twin/config", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "solar" in data
    assert "components" in data
    assert len(data["components"]) >= 5
    assert "camera_presets" in data


def test_designs_list_endpoint():
    response = client.get("/api/designs")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "geometry" in data[0]
    assert "materials" in data[0]


def test_optimization_endpoint():
    payload = {
        "location_id": "sambalpur",
        "month": 5,
        "w_comfort": 0.4,
        "w_cost": 0.3,
        "w_carbon": 0.3,
        "population_size": 15
    }
    response = client.post("/api/optimization/run", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "pareto_front" in data
    assert len(data["pareto_front"]) >= 1
    assert "top_4_designs" in data
