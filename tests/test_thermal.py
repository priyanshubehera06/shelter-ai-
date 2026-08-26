import sys
import os

try:
    import pytest
except ImportError:
    pytest = None

# Ensure engine modules are on Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from engine.materials import calculate_assembly_u_value, get_material_by_id
from engine.geometry import ShelterGeometry
from engine.thermal import (
    simulate_shelter_thermal_dynamics,
    calculate_internal_heat_gain,
    compare_thermal_scenarios,
)
from engine.comfort import calculate_pmv_fanger, get_comfort_category
from engine.cost import calculate_shelter_cost_and_carbon
from engine.optimizer import run_pareto_optimization
from engine.scoring import calculate_mcda_shelter_score
from engine.climate import get_climate_profile
from engine.energy import calculate_annual_energy_loads
from reports.report_generator import generate_pdf_report
from visualization.charts import plot_diurnal_trajectory, plot_mcda_radar
from visualization.shelter_3d import create_plotly_3d_shelter


def test_material_u_value():
    res = calculate_assembly_u_value("brick_standard", 20.0)
    assert "u_value_w_m2k" in res
    assert res["u_value_w_m2k"] > 0.0
    assert res["u_value_w_m2k"] < 5.0
    assert res["r_value_m2k_w"] > 0.0


def test_geometry_math():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=3.0, wwr_pct=20.0, overhang_m=0.5)
    assert geom.floor_area() == 24.0
    assert geom.gross_wall_area() == 60.0
    assert geom.glazing_area() == 12.0
    assert geom.net_wall_area() == 48.0
    assert geom.volume() > 72.0


def test_internal_heat_gain_archetypes():
    q_human = calculate_internal_heat_gain(occupancy_type="humans", occupants=4)
    assert q_human == 450.0  # 4 * 100 + 50

    q_livestock = calculate_internal_heat_gain(occupancy_type="livestock", livestock_count=2, livestock_type="cattle")
    assert q_livestock >= 800.0

    q_agri = calculate_internal_heat_gain(occupancy_type="agriculture")
    assert q_agri >= 150.0


def test_thermal_simulation():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8)
    sim = simulate_shelter_thermal_dynamics(
        geometry=geom,
        wall_mat_id="cseb_interlocking",
        wall_thickness_cm=20.0,
        roof_mat_id="roof_cgi_insulated",
        glazing_mat_id="glazing_single",
    )
    assert len(sim["hours"]) == 24
    assert len(sim["t_indoor"]) == 24
    assert len(sim["q_wall"]) == 24
    assert len(sim["q_roof"]) == 24
    assert len(sim["q_solar"]) == 24
    assert len(sim["q_vent"]) == 24
    assert "hourly_df" in sim
    assert sim["avg_t_indoor"] > -20.0 and sim["avg_t_indoor"] < 60.0


def test_compare_thermal_scenarios():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8)
    base_cfg = {"roof_mat_id": "roof_cgi_insulated", "insulation_mat_id": None, "insulation_thickness_cm": 0.0}
    mod_cfg = {"roof_mat_id": "roof_concrete_slab", "insulation_mat_id": "insulation_rockwool", "insulation_thickness_cm": 5.0}

    comp = compare_thermal_scenarios(geom, base_cfg, mod_cfg)
    assert "peak_temperature_drop_c" in comp
    assert "comparison_table" in comp
    assert len(comp["comparison_table"]) == 24


def test_pmv_comfort():
    pmv, ppd = calculate_pmv_fanger(ta=24.0, rh=50.0, vel=0.15)
    assert -3.0 <= pmv <= 3.0
    assert 5.0 <= ppd <= 100.0
    status, color = get_comfort_category(pmv)
    assert isinstance(status, str)


def test_human_comfort_evaluation():
    from engine.comfort import evaluate_human_comfort
    t_hourly = [24.0, 25.0, 26.0, 28.0, 31.0, 33.0, 31.0, 28.0, 25.0, 24.0] * 3
    res = evaluate_human_comfort(t_hourly[:24], rh_hourly=55.0)
    assert "comfort_score" in res
    assert 0 <= res["comfort_score"] <= 100
    assert "comfortable_hours_annual" in res
    assert res["comfortable_hours_annual"] + res["too_hot_hours_annual"] + res["too_cold_hours_annual"] == 8760


def test_livestock_comfort_evaluation():
    from engine.comfort import evaluate_livestock_comfort
    t_hourly = [15.0, 18.0, 20.0, 22.0, 24.0, 26.0, 25.0, 22.0, 18.0, 16.0] * 3
    cattle_res = evaluate_livestock_comfort(t_hourly[:24], rh_hourly=60.0, species="cattle")
    assert "thermal_suitability_pct" in cattle_res
    assert 0 <= cattle_res["thermal_suitability_pct"] <= 100
    assert "max_thi" in cattle_res


def test_agricultural_suitability_evaluation():
    from engine.comfort import evaluate_agricultural_suitability
    t_hourly = [20.0, 21.0, 22.0, 23.0, 22.0, 21.0, 20.0, 19.0, 20.0, 21.0] * 3
    mush_res = evaluate_agricultural_suitability(t_hourly[:24], rh_hourly=80.0, ach=4.0, application="mushroom_cultivation")
    assert "agricultural_suitability_pct" in mush_res
def test_multi_application_suitability():
    from engine.comfort import evaluate_multi_application_suitability
    t_hourly = [22.0, 24.0, 26.0, 28.0, 30.0, 29.0, 26.0, 24.0] * 3
    multi_res = evaluate_multi_application_suitability(t_hourly[:24], rh_hourly=55.0, ach=3.0)
    assert "scores_summary" in multi_res
    assert "Human" in multi_res["scores_summary"]
    assert "Cattle" in multi_res["scores_summary"]
    assert "Mushrooms" in multi_res["scores_summary"]
    assert len(multi_res["comparison_table"]) >= 3


def test_energy_hourly_and_annual_loads():
    from engine.energy import calculate_annual_energy_loads, calculate_hourly_hvac_loads
    t_hourly = [32.0, 34.0, 36.0, 38.0, 35.0, 31.0, 28.0, 26.0] * 3
    
    # Test hourly HVAC loads
    hvac_res = calculate_hourly_hvac_loads(t_hourly[:24], floor_area_m2=24.0, t_target_cool=26.0)
    assert len(hvac_res["cooling_thermal_kw"]) == 24
    assert hvac_res["peak_cooling_kw"] > 0.0
    assert hvac_res["daily_cooling_kwh"] > 0.0

    # Test annual energy loads
    ann_res = calculate_annual_energy_loads(t_hourly[:24], floor_area_m2=24.0, t_base_cool=26.0, t_base_heat=20.0)
    assert "annual_cooling_kwh" in ann_res
    assert "annual_heating_kwh" in ann_res
    assert "total_annual_kwh" in ann_res
    assert len(ann_res["monthly_cooling_kwh"]) == 12
    assert ann_res["total_annual_kwh"] > 0.0


def test_compare_design_energy():
    from engine.energy import compare_design_energy
    design_a = {"annual_cooling_kwh": 1450.0, "annual_heating_kwh": 100.0, "total_annual_kwh": 1550.0}
    design_b = {"annual_cooling_kwh": 2400.0, "annual_heating_kwh": 120.0, "total_annual_kwh": 2520.0}
    
    comp = compare_design_energy(design_a, design_b, label_a="Design A", label_b="Design B")
    assert comp["savings_kwh_yr"] == pytest.approx(970.0, 0.1)
    assert comp["cost_saved_inr_yr"] > 0.0
    assert len(comp["comparison_table"]) == 5


def test_cost_calculation():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8)
    cost_res = calculate_shelter_cost_and_carbon(
        geom,
        wall_mat_id="brick_standard",
        wall_thickness_cm=20.0,
        roof_mat_id="roof_cgi_insulated",
        glazing_mat_id="glazing_single",
    )
    assert cost_res["capex_inr"] > 0.0
    assert cost_res["total_embodied_carbon_kgco2"] > 0.0


def test_pareto_optimizer():
    opt_res = run_pareto_optimization(population_size=10)
    assert "best_candidate" in opt_res
    assert "pareto_front" in opt_res
    assert len(opt_res["all_candidates"]) == 10


def test_mcda_scoring():
    mcda = calculate_mcda_shelter_score(0.2, 85.0, 45.0, 75000.0, 250.0, 80.0)
    assert "overall_score" in mcda
    assert mcda["overall_score"] > 0.0


def test_pdf_generation():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8)
    sim = simulate_shelter_thermal_dynamics(geom)
    pmv, ppd = calculate_pmv_fanger(sim["avg_t_indoor"], 50.0)
    cost_res = calculate_shelter_cost_and_carbon(geom)
    mcda = calculate_mcda_shelter_score(pmv, 85.0, cost_res["carbon_intensity_kg_m2"], cost_res["capex_inr"], 250.0, 80.0)

    pdf_path = generate_pdf_report(
        shelter_name="Test Shelter",
        location_name="Sambalpur",
        geometry_dict=geom.envelope_summary(),
        thermal_dict=sim,
        comfort_dict={"pmv": pmv, "compliance_pct": 85.0},
        cost_dict=cost_res,
        mcda_dict=mcda,
    )
    assert os.path.exists(pdf_path)


def test_visualization():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8)
    fig_3d = create_plotly_3d_shelter(geom)
    assert fig_3d is not None
