import pytest
from engine.geometry import ShelterGeometry
from engine.cost import calculate_shelter_cost_and_carbon


def test_cost_itemized_breakdown():
    geom = ShelterGeometry(
        length_m=6.0,
        width_m=4.0,
        height_m=2.8,
        door_width_m=0.9,
        door_height_m=2.1,
        door_count=1,
        overhang_m=0.6
    )
    res = calculate_shelter_cost_and_carbon(
        geometry=geom,
        wall_mat_id="cseb_interlocking",
        wall_thickness_cm=20.0,
        roof_mat_id="roof_cgi_insulated",
        glazing_mat_id="glazing_double",
        insulation_mat_id="insulation_rockwool",
        insulation_thickness_cm=5.0
    )
    
    assert res["wall_cost_inr"] > 0.0
    assert res["roof_cost_inr"] > 0.0
    assert res["window_cost_inr"] > 0.0
    assert res["door_cost_inr"] > 0.0
    assert res["insulation_cost_inr"] > 0.0
    assert res["shading_cost_inr"] > 0.0
    assert res["labor_cost_inr"] > 0.0
    assert res["total_construction_cost_inr"] > res["materials_subtotal_inr"]
    assert res["total_embodied_carbon_kgco2"] > 0.0
    assert len(res["boq"]) >= 7


def test_cost_without_insulation():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8)
    res = calculate_shelter_cost_and_carbon(
        geometry=geom,
        wall_mat_id="brick_standard",
        wall_thickness_cm=20.0,
        roof_mat_id="roof_cgi_sheet",
        insulation_mat_id=None,
        insulation_thickness_cm=0.0
    )
    assert res["insulation_cost_inr"] == 0.0
    assert res["total_construction_cost_inr"] > 0.0
