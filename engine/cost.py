"""
cost.py — Construction CapEx, Life Cycle Costing (LCC), and Embodied Carbon Engine for Shelter-AI.
Calculates component itemized costs (walls, roof, windows, doors, insulation, shading, labor),
total estimated construction cost, and operational energy lifecycle expenses.
"""

from typing import Dict, List, Optional, Any
import pandas as pd
from engine.materials import calculate_material_carbon_and_cost
from engine.geometry import ShelterGeometry


def calculate_shelter_cost_and_carbon(
    geometry: ShelterGeometry,
    wall_mat_id: str = "brick_standard",
    wall_thickness_cm: float = 20.0,
    roof_mat_id: str = "roof_cgi_insulated",
    glazing_mat_id: str = "glazing_single",
    insulation_mat_id: Optional[str] = None,
    insulation_thickness_cm: float = 0.0,
    door_unit_cost_inr: float = 3500.0,
    shading_cost_per_m_inr: float = 450.0,
    elec_rate_inr_kwh: float = 7.50,
    annual_kwh: float = 1200.0,
) -> Dict[str, Any]:
    """
    Calculates detailed itemized Bill of Quantities (BOQ), CapEx construction cost,
    embodied carbon (kg CO₂), and 20-year Life Cycle Cost (LCC).
    """
    net_wall_area = geometry.net_wall_area()
    roof_area = geometry.roof_area()
    window_area = geometry.window_area()
    door_area = geometry.door_area()
    floor_area = geometry.floor_area()
    perimeter = geometry.footprint_perimeter()
    overhang = geometry.overhang

    # 1. Wall Envelope
    wall_res = calculate_material_carbon_and_cost(wall_mat_id, wall_thickness_cm, net_wall_area)
    wall_cost = wall_res["total_cost_inr"]

    # 2. Continuous Insulation Layer
    ins_cost = 0.0
    ins_carbon = 0.0
    if insulation_mat_id and insulation_thickness_cm > 0:
        ins_res = calculate_material_carbon_and_cost(insulation_mat_id, insulation_thickness_cm, net_wall_area + roof_area)
        ins_cost = ins_res["total_cost_inr"]
        ins_carbon = ins_res["embodied_carbon_kgco2"]

    # 3. Roofing Assembly (nominal 10cm slab or sheet equivalent)
    roof_res = calculate_material_carbon_and_cost(roof_mat_id, 10.0, roof_area)
    roof_cost = roof_res["total_cost_inr"]

    # 4. Glazing Windows (nominal 1cm glass equivalent)
    glazing_res = calculate_material_carbon_and_cost(glazing_mat_id, 1.0, window_area)
    window_cost = glazing_res["total_cost_inr"]

    # 5. Doors and Access Hardware
    door_cost = float(geometry.door_count if geometry.door_count > 0 else 1) * door_unit_cost_inr
    door_carbon = float(geometry.door_count if geometry.door_count > 0 else 1) * 25.0  # ~25 kg CO2 per timber/composite door

    # 6. Overhang Shading Eaves & Brackets
    shading_cost = perimeter * overhang * shading_cost_per_m_inr if overhang > 0 else 0.0
    shading_carbon = perimeter * overhang * 4.5  # ~4.5 kg CO2/m²

    # 7. Subfloor Base (Concrete screed or compacted earth)
    floor_res = calculate_material_carbon_and_cost("floor_concrete_screed", 10.0, floor_area)
    floor_cost = floor_res["total_cost_inr"]

    # Subtotal Material Cost
    materials_subtotal = wall_cost + ins_cost + roof_cost + window_cost + door_cost + shading_cost + floor_cost

    # Structural Framework & Hardware (~15% of materials)
    structural_frame_cost = materials_subtotal * 0.15

    # Construction Labor & Assembly (~25% of materials)
    labor_cost = materials_subtotal * 0.25

    # Total CapEx Construction Cost
    total_capex = materials_subtotal + structural_frame_cost + labor_cost

    # Total Embodied Carbon (kg CO₂)
    total_carbon = (
        wall_res["embodied_carbon_kgco2"]
        + ins_carbon
        + roof_res["embodied_carbon_kgco2"]
        + glazing_res["embodied_carbon_kgco2"]
        + door_carbon
        + shading_carbon
        + floor_res["embodied_carbon_kgco2"]
    )
    carbon_intensity_kg_m2 = total_carbon / max(1.0, floor_area)

    # 20-Year Operational Energy Life Cycle Cost (NPV at 5% discount rate)
    annual_opex = annual_kwh * elec_rate_inr_kwh
    npv_factor_20yr = sum(1.0 / (1.05 ** t) for t in range(1, 21))  # ~12.46
    opex_20yr_npv = annual_opex * npv_factor_20yr
    total_lcc = total_capex + opex_20yr_npv

    # Cost Breakdown dictionary
    cost_breakdown = {
        "Wall Envelope": round(wall_cost, 2),
        "Roofing System": round(roof_cost, 2),
        "Glazing Windows": round(window_cost, 2),
        "Doors & Access": round(door_cost, 2),
        "Thermal Insulation": round(ins_cost, 2),
        "Overhang Shading": round(shading_cost, 2),
        "Subfloor Base": round(floor_cost, 2),
        "Structural Hardware": round(structural_frame_cost, 2),
        "Construction Labor": round(labor_cost, 2),
    }

    # Itemized Bill of Quantities (BOQ)
    boq = [
        {"component": "Wall Envelope", "material_id": wall_mat_id, "quantity": f"{net_wall_area:.1f} m²", "thickness_cm": wall_thickness_cm, "cost_inr": round(wall_cost, 2), "carbon_kgco2": round(wall_res["embodied_carbon_kgco2"], 1)},
        {"component": "Roofing System", "material_id": roof_mat_id, "quantity": f"{roof_area:.1f} m²", "thickness_cm": 10.0, "cost_inr": round(roof_cost, 2), "carbon_kgco2": round(roof_res["embodied_carbon_kgco2"], 1)},
        {"component": "Glazing Windows", "material_id": glazing_mat_id, "quantity": f"{window_area:.1f} m²", "thickness_cm": 1.0, "cost_inr": round(window_cost, 2), "carbon_kgco2": round(glazing_res["embodied_carbon_kgco2"], 1)},
        {"component": "Doors & Access", "material_id": "door_timber_composite", "quantity": f"{geometry.door_count or 1} unit(s)", "thickness_cm": 3.5, "cost_inr": round(door_cost, 2), "carbon_kgco2": round(door_carbon, 1)},
        {"component": "Thermal Insulation", "material_id": insulation_mat_id or "None", "quantity": f"{net_wall_area + roof_area:.1f} m²" if insulation_mat_id else "0 m²", "thickness_cm": insulation_thickness_cm, "cost_inr": round(ins_cost, 2), "carbon_kgco2": round(ins_carbon, 1)},
        {"component": "Overhang Shading", "material_id": "shading_louvers", "quantity": f"{overhang:.1f} m depth", "thickness_cm": 0.0, "cost_inr": round(shading_cost, 2), "carbon_kgco2": round(shading_carbon, 1)},
        {"component": "Subfloor Base", "material_id": "floor_concrete_screed", "quantity": f"{floor_area:.1f} m²", "thickness_cm": 10.0, "cost_inr": round(floor_cost, 2), "carbon_kgco2": round(floor_res["embodied_carbon_kgco2"], 1)},
        {"component": "Structural Hardware", "material_id": "frame_anchors_trusses", "quantity": "Assembly", "thickness_cm": 0.0, "cost_inr": round(structural_frame_cost, 2), "carbon_kgco2": 45.0},
        {"component": "Construction Labor", "material_id": "on_site_assembly", "quantity": "Labor days", "thickness_cm": 0.0, "cost_inr": round(labor_cost, 2), "carbon_kgco2": 0.0},
    ]

    return {
        "wall_cost_inr": round(wall_cost, 2),
        "roof_cost_inr": round(roof_cost, 2),
        "window_cost_inr": round(window_cost, 2),
        "door_cost_inr": round(door_cost, 2),
        "insulation_cost_inr": round(ins_cost, 2),
        "shading_cost_inr": round(shading_cost, 2),
        "floor_cost_inr": round(floor_cost, 2),
        "labor_cost_inr": round(labor_cost, 2),
        "structural_frame_inr": round(structural_frame_cost, 2),
        "materials_subtotal_inr": round(materials_subtotal, 2),
        "material_cost_subtotal_inr": round(materials_subtotal, 2),
        "capex_inr": round(total_capex, 2),
        "total_construction_cost_inr": round(total_capex, 2),
        "cost_per_m2_inr": round(total_capex / max(1.0, floor_area), 2),
        "annual_opex_inr": round(annual_opex, 2),
        "opex_20yr_npv_inr": round(opex_20yr_npv, 2),
        "total_lcc_inr": round(total_lcc, 2),
        "total_embodied_carbon_kgco2": round(total_carbon, 1),
        "carbon_intensity_kg_m2": round(carbon_intensity_kg_m2, 1),
        "cost_breakdown": cost_breakdown,
        "boq": boq,
    }
