"""
material_recommender.py — Multi-Criteria Material Recommendation Engine for Shelter-AI.
Selects and ranks envelope material pairings (Wall + Roof + Insulation + Glazing)
based on Regional Climate Zone, Budget constraints, Availability, and Thermo-physical performance.
"""

from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from engine.materials import get_materials_catalog, calculate_assembly_u_value, calculate_material_carbon_and_cost


def recommend_materials(
    climate_zone: str = "Composite / Moderate",
    budget_level: str = "medium",  # "low", "medium", "high"
    max_budget_inr: Optional[float] = None,
    priority_low_carbon: bool = False,
) -> Dict[str, Any]:
    """
    Ranks material assembly combinations (Wall, Roof, Insulation, Glazing) based on:
    - Thermal conductivity & assembly U-value suitability
    - Volumetric heat capacity / thermal mass
    - Local availability score
    - Upfront unit cost (₹/m²) & embodied carbon footprint
    """
    df_mat = get_materials_catalog()
    if df_mat.empty:
        return {"ranked_assemblies": [], "best_assembly": None}

    walls = df_mat[df_mat["category"] == "Wall"].to_dict(orient="records")
    roofs = df_mat[df_mat["category"] == "Roof"].to_dict(orient="records")
    insulations = df_mat[df_mat["category"] == "Insulation"].to_dict(orient="records")
    glazings = df_mat[df_mat["category"] == "Glazing"].to_dict(orient="records")

    candidates = []

    for w in walls:
        for r in roofs:
            for g in glazings:
                for ins in [None] + insulations:
                    ins_id = ins["id"] if ins else None
                    ins_thick = 5.0 if ins else 0.0

                    # 1. Thermal Assembly Calculations
                    w_calc = calculate_assembly_u_value(w["id"], thickness_cm=20.0, ins_mat_id=None, ins_thickness_cm=0.0)
                    r_calc = calculate_assembly_u_value(r["id"], thickness_cm=10.0, ins_mat_id=ins_id, ins_thickness_cm=ins_thick)

                    u_wall = w_calc["u_value_w_m2k"]
                    u_roof = r_calc["u_value_w_m2k"]
                    thermal_mass = w_calc["thermal_mass_kj_m2k"]

                    # 2. Cost & Carbon
                    w_cost = calculate_material_carbon_and_cost(w["id"], 20.0, area_m2=50.0)
                    r_cost = calculate_material_carbon_and_cost(r["id"], 10.0, area_m2=24.0)
                    g_cost = calculate_material_carbon_and_cost(g["id"], 1.0, area_m2=8.0)
                    i_cost = calculate_material_carbon_and_cost(ins_id, ins_thick, area_m2=74.0) if ins else {"total_cost_inr": 0.0, "embodied_carbon_kgco2": 0.0}

                    total_mat_cost = w_cost["total_cost_inr"] + r_cost["total_cost_inr"] + g_cost["total_cost_inr"] + i_cost["total_cost_inr"]
                    total_carbon = w_cost["embodied_carbon_kgco2"] + r_cost["embodied_carbon_kgco2"] + g_cost["embodied_carbon_kgco2"] + i_cost["embodied_carbon_kgco2"]

                    # 3. Multi-Criteria Scoring (0 - 100)
                    # A. Thermal Score
                    if "Arid" in climate_zone or "Composite" in climate_zone:
                        # High thermal mass + low U-roof favored
                        thermal_score = min(40.0, (thermal_mass / 300.0) * 20.0) + min(20.0, max(0.0, (2.5 - u_roof) * 8.0))
                    elif "Humid" in climate_zone:
                        # Low U-roof + lightweight breathable walls favored
                        thermal_score = min(30.0, max(0.0, (2.5 - u_roof) * 12.0)) + (15.0 if "bamboo" in w["id"] or "eps" in w["id"] else 5.0)
                    else:  # Cold
                        # Ultra low U-values favored
                        thermal_score = min(30.0, max(0.0, (2.0 - u_wall) * 15.0)) + min(30.0, max(0.0, (2.0 - u_roof) * 15.0))

                    # B. Cost & Budget Score
                    if budget_level == "low":
                        cost_score = max(0.0, (1.0 - (total_mat_cost / 120000.0)) * 40.0)
                    elif budget_level == "high":
                        cost_score = 30.0  # budget not a limiting factor
                    else:
                        cost_score = max(0.0, (1.0 - (total_mat_cost / 160000.0)) * 30.0)

                    # C. Availability & Carbon Score
                    avail_score = (float(w.get("availability_score", 8.0)) + float(r.get("availability_score", 8.0))) * 1.0
                    carbon_score = max(0.0, (1.0 - (total_carbon / 3000.0)) * 20.0) if priority_low_carbon else 10.0

                    composite_score = round(thermal_score + cost_score + avail_score + carbon_score, 1)

                    candidates.append({
                        "wall_mat_id": w["id"],
                        "wall_name": w["name"],
                        "roof_mat_id": r["id"],
                        "roof_name": r["name"],
                        "insulation_mat_id": ins_id,
                        "insulation_name": ins["name"] if ins else "None (Uninsulated)",
                        "glazing_mat_id": g["id"],
                        "glazing_name": g["name"],
                        "u_wall": u_wall,
                        "u_roof": u_roof,
                        "thermal_mass_kj_m2k": thermal_mass,
                        "estimated_materials_cost_inr": round(total_mat_cost, 2),
                        "embodied_carbon_kg": round(total_carbon, 1),
                        "composite_suitability_score": composite_score,
                    })

    # Sort descending by composite score
    candidates.sort(key=lambda x: x["composite_suitability_score"], reverse=True)

    # Top recommendations
    ranked = candidates[:8]
    best = ranked[0] if ranked else None

    return {
        "climate_zone": climate_zone,
        "budget_level": budget_level,
        "best_assembly": best,
        "top_ranked_assemblies": ranked,
        "recommendation_summary": (
            f"Recommended combination for {climate_zone}: {best['wall_name']} with {best['roof_name']} "
            f"and {best['insulation_name']} (Composite Score: {best['composite_suitability_score']}/100)."
        ) if best else "No materials found",
    }
