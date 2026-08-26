"""
materials.py — Materials intelligence and envelope thermo-physical assembly engine.
Calculates thermal resistance (R-value), U-value, volumetric heat capacity (thermal mass),
embodied carbon, and construction cost for building envelope layers.
"""

import os
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd

MATERIALS_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "materials.csv")


def get_materials_catalog() -> pd.DataFrame:
    """Loads and standardizes the envelope materials catalog from CSV."""
    if os.path.exists(MATERIALS_CSV):
        df = pd.read_csv(MATERIALS_CSV)
        # Normalize column aliases
        col_map = {
            "thermal_conductivity": "thermal_cond_w_mk",
            "density": "density_kg_m3",
            "specific_heat": "specific_heat_j_kgk",
            "cost_per_m2": "unit_cost_inr_m2",
        }
        for old_col, new_col in col_map.items():
            if old_col in df.columns and new_col not in df.columns:
                df[new_col] = df[old_col]
            elif new_col in df.columns and old_col not in df.columns:
                df[old_col] = df[new_col]
        return df
    return pd.DataFrame()


def get_material_by_id(mat_id: str) -> Dict[str, Any]:
    """Retrieves physical and economic properties for a single material by ID."""
    df = get_materials_catalog()
    if not df.empty:
        mat = df[df["id"] == mat_id]
        if not mat.empty:
            row = mat.iloc[0].to_dict()
            # Ensure required float keys exist
            k = float(row.get("thermal_cond_w_mk", row.get("thermal_conductivity", 0.77)))
            rho = float(row.get("density_kg_m3", row.get("density", 1800.0)))
            cp = float(row.get("specific_heat_j_kgk", row.get("specific_heat", 840.0)))
            cost = float(row.get("unit_cost_inr_m2", row.get("cost_per_m2", 1200.0)))
            carbon = float(row.get("embodied_carbon_kgco2_kg", 0.24))

            return {
                "id": str(row.get("id", mat_id)),
                "name": str(row.get("name", mat_id)),
                "category": str(row.get("category", "Wall")),
                "thermal_cond_w_mk": k,
                "thermal_conductivity": k,
                "density_kg_m3": rho,
                "density": rho,
                "specific_heat_j_kgk": cp,
                "specific_heat": cp,
                "unit_cost_inr_m2": cost,
                "cost_per_m2": cost,
                "embodied_carbon_kgco2_kg": carbon,
                "thickness_options": str(row.get("thickness_options", "10;15;20")),
                "availability_score": float(row.get("availability_score", 8.5)),
                "description": str(row.get("description", "")),
            }

    # Fallback default
    return {
        "id": mat_id,
        "name": mat_id.replace("_", " ").title(),
        "category": "Wall",
        "thermal_cond_w_mk": 0.77,
        "thermal_conductivity": 0.77,
        "density_kg_m3": 1800.0,
        "density": 1800.0,
        "specific_heat_j_kgk": 840.0,
        "specific_heat": 840.0,
        "embodied_carbon_kgco2_kg": 0.24,
        "unit_cost_inr_m2": 1200.0,
        "cost_per_m2": 1200.0,
        "thickness_options": "10;15;20",
        "availability_score": 8.0,
        "description": "Standard envelope material",
    }


def calculate_assembly_u_value(
    core_mat_id: str,
    thickness_cm: float,
    ins_mat_id: Optional[str] = None,
    ins_thickness_cm: float = 0.0,
) -> Dict[str, Any]:
    """
    Calculates overall heat transfer coefficient (U-value in W/m²K),
    total thermal resistance (R-value in m²K/W), and effective thermal mass (kJ/m²K).
    R_total = R_si + (d_core / k_core) + (d_ins / k_ins) + R_se
    R_si = 0.13 m²K/W (interior air film), R_se = 0.04 m²K/W (exterior air film)
    """
    core_mat = get_material_by_id(core_mat_id)
    d1 = max(0.01, float(thickness_cm)) / 100.0
    k1 = max(0.001, float(core_mat["thermal_cond_w_mk"]))
    r1 = d1 / k1

    thermal_mass1 = (core_mat["density_kg_m3"] * core_mat["specific_heat_j_kgk"] * d1) / 1000.0  # kJ/m²K

    r_ins = 0.0
    thermal_mass2 = 0.0
    if ins_mat_id and ins_thickness_cm > 0:
        ins_mat = get_material_by_id(ins_mat_id)
        d2 = float(ins_thickness_cm) / 100.0
        k2 = max(0.001, float(ins_mat["thermal_cond_w_mk"]))
        r_ins = d2 / k2
        thermal_mass2 = (ins_mat["density_kg_m3"] * ins_mat["specific_heat_j_kgk"] * d2) / 1000.0

    r_si = 0.13
    r_se = 0.04
    r_total = r_si + r1 + r_ins + r_se
    u_value = 1.0 / max(0.05, r_total)
    total_thermal_mass = thermal_mass1 + thermal_mass2

    return {
        "u_value_w_m2k": round(u_value, 4),
        "r_value_m2k_w": round(r_total, 4),
        "thermal_mass_kj_m2k": round(total_thermal_mass, 2),
    }


def calculate_material_carbon_and_cost(
    mat_id: str,
    thickness_cm: float,
    area_m2: float,
) -> Dict[str, Any]:
    """Calculates mass, embodied carbon (kg CO₂), and material cost (INR)."""
    mat = get_material_by_id(mat_id)
    thickness_m = float(thickness_cm) / 100.0
    volume_m3 = float(area_m2) * thickness_m
    mass_kg = volume_m3 * float(mat["density_kg_m3"])

    embodied_carbon_kg = mass_kg * float(mat["embodied_carbon_kgco2_kg"])
    unit_cost = float(mat["unit_cost_inr_m2"])
    thickness_factor = (thickness_cm / 15.0) if mat["category"] == "Wall" else 1.0
    total_cost_inr = area_m2 * unit_cost * max(0.5, thickness_factor)

    return {
        "mass_kg": round(mass_kg, 1),
        "embodied_carbon_kgco2": round(embodied_carbon_kg, 1),
        "total_cost_inr": round(total_cost_inr, 2),
    }
