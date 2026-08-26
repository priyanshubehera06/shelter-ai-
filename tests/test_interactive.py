import pytest
from engine.geometry import ShelterGeometry
from engine.digital_twin import calculate_sol_air_facet_temperatures, generate_3d_digital_twin_model
from engine.scenario import compare_what_if_scenarios


def test_sol_air_facet_temperatures():
    temps = calculate_sol_air_facet_temperatures(t_outdoor=35.0, solar_ghi=900.0, hour_of_day=14)
    assert "Roof" in temps
    assert "South_Wall" in temps
    assert "East_Wall" in temps
    assert "West_Wall" in temps
    assert temps["Roof"] >= 35.0
    assert temps["West_Wall"] >= 35.0


def test_generate_3d_digital_twin_model():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8, roof_type="pitched", overhang_m=0.6)
    twin = generate_3d_digital_twin_model(geometry=geom, wall_mat_id="cseb_interlocking", view_mode="thermal_heatmap")
    assert "figure" in twin
    assert "sol_air_temperatures" in twin
    assert twin["overhang_m"] == 0.6
    assert twin["total_exposed_area_m2"] > 0.0


def test_compare_what_if_scenarios():
    geom_base = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8)
    geom_mod = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8, overhang_m=0.6)
    
    cfg_base = {"wall_mat_id": "brick_standard", "roof_mat_id": "roof_cgi_sheet"}
    cfg_mod = {"wall_mat_id": "cseb_interlocking", "roof_mat_id": "roof_cgi_insulated", "insulation_mat_id": "insulation_rockwool", "insulation_thickness_cm": 5.0}

    comp = compare_what_if_scenarios(geom_base, cfg_base, geom_mod, cfg_mod)
    assert "peak_temperature_drop_c" in comp
    assert "annual_energy_saved_kwh" in comp
    assert "energy_savings_pct" in comp
    assert "summary_text" in comp
    assert "figure" in comp
    assert isinstance(comp["energy_savings_pct"], (float, int))
