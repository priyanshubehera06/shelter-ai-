"""
material_service.py — Service adapter interfacing with engine.materials.
"""

from typing import List, Optional, Dict, Any
from engine.materials import get_materials_catalog, get_material_by_id, calculate_assembly_u_value
from backend.schemas.material import MaterialItem, AssemblyUValueRequest, AssemblyUValueResponse

# Visual texture & styling mappings for 3D Digital Twin Materials
MATERIAL_VISUAL_MAP = {
    "cseb_interlocking": {"color_hex": "#b58d6b", "roughness": 0.90, "metalness": 0.0},
    "brick_standard": {"color_hex": "#a34839", "roughness": 0.85, "metalness": 0.0},
    "aac_block": {"color_hex": "#dcdde1", "roughness": 0.95, "metalness": 0.0},
    "eps_sandwich": {"color_hex": "#ecf0f1", "roughness": 0.35, "metalness": 0.4},
    "bamboo_composite": {"color_hex": "#c8b075", "roughness": 0.70, "metalness": 0.0},
    "roof_cgi_sheet": {"color_hex": "#7f8c8d", "roughness": 0.30, "metalness": 0.85},
    "roof_cgi_insulated": {"color_hex": "#34495e", "roughness": 0.40, "metalness": 0.70},
    "roof_concrete_slab": {"color_hex": "#95a5a6", "roughness": 0.90, "metalness": 0.05},
    "roof_bamboo_thatch": {"color_hex": "#8d704b", "roughness": 0.95, "metalness": 0.0},
    "roof_bipv_solar": {"color_hex": "#1b1464", "roughness": 0.15, "metalness": 0.95},
    "glazing_single": {"color_hex": "#81ecec", "roughness": 0.10, "metalness": 0.90},
    "glazing_double": {"color_hex": "#74b9ff", "roughness": 0.10, "metalness": 0.90},
    "glazing_low_e": {"color_hex": "#0984e3", "roughness": 0.10, "metalness": 0.90},
    "glazing_polycarb": {"color_hex": "#a29bfe", "roughness": 0.20, "metalness": 0.50},
    "insulation_rockwool": {"color_hex": "#f5cd79", "roughness": 0.95, "metalness": 0.0},
    "insulation_eps": {"color_hex": "#ffffff", "roughness": 0.90, "metalness": 0.0},
    "insulation_aerogel": {"color_hex": "#dff9fb", "roughness": 0.80, "metalness": 0.0},
}


def get_all_materials() -> List[MaterialItem]:
    """Loads all envelope materials from catalog and decorates with 3D visual metadata."""
    df = get_materials_catalog()
    items = []
    for _, row in df.iterrows():
        mid = str(row["id"])
        vis = MATERIAL_VISUAL_MAP.get(mid, {"color_hex": "#95a5a6", "roughness": 0.8, "metalness": 0.1})
        items.append(MaterialItem(
            id=mid,
            name=str(row["name"]),
            category=str(row["category"]),
            thermal_cond_w_mk=float(row.get("thermal_cond_w_mk", 0.77)),
            density_kg_m3=float(row.get("density_kg_m3", 1800.0)),
            specific_heat_j_kgk=float(row.get("specific_heat_j_kgk", 840.0)),
            embodied_carbon_kgco2_kg=float(row.get("embodied_carbon_kgco2_kg", 0.24)),
            unit_cost_inr_m2=float(row.get("unit_cost_inr_m2", 1200.0)),
            thickness_options=str(row.get("thickness_options", "10;15;20")),
            availability_score=float(row.get("availability_score", 8.0)),
            description=str(row.get("description", "")),
            color_hex=vis.get("color_hex", "#95a5a6"),
            roughness=vis.get("roughness", 0.8),
            metalness=vis.get("metalness", 0.1),
        ))
    return items


def get_material(material_id: str) -> Optional[MaterialItem]:
    """Retrieves a single material by ID."""
    raw = get_material_by_id(material_id)
    if raw:
        vis = MATERIAL_VISUAL_MAP.get(material_id, {"color_hex": "#95a5a6", "roughness": 0.8, "metalness": 0.1})
        return MaterialItem(
            id=raw["id"],
            name=raw["name"],
            category=raw["category"],
            thermal_cond_w_mk=float(raw["thermal_cond_w_mk"]),
            density_kg_m3=float(raw["density_kg_m3"]),
            specific_heat_j_kgk=float(raw["specific_heat_j_kgk"]),
            embodied_carbon_kgco2_kg=float(raw["embodied_carbon_kgco2_kg"]),
            unit_cost_inr_m2=float(raw["unit_cost_inr_m2"]),
            thickness_options=str(raw.get("thickness_options", "10;15;20")),
            availability_score=float(raw.get("availability_score", 8.0)),
            description=str(raw.get("description", "")),
            color_hex=vis.get("color_hex", "#95a5a6"),
            roughness=vis.get("roughness", 0.8),
            metalness=vis.get("metalness", 0.1),
        )
    return None


def calculate_u_value(req: AssemblyUValueRequest) -> AssemblyUValueResponse:
    """Calculates thermal U-value and assembly properties via engine.materials."""
    res = calculate_assembly_u_value(
        core_mat_id=req.core_mat_id,
        thickness_cm=req.thickness_cm,
        ins_mat_id=req.ins_mat_id,
        ins_thickness_cm=req.ins_thickness_cm
    )
    return AssemblyUValueResponse(
        core_mat_id=res["core_mat_id"],
        core_name=res["core_name"],
        thickness_cm=res["core_thickness_cm"],
        ins_mat_id=res["ins_mat_id"],
        ins_name=res["ins_name"],
        ins_thickness_cm=res["ins_thickness_cm"],
        total_thickness_m=res["total_thickness_m"],
        r_value_m2k_w=res["r_value_m2k_w"],
        u_value_w_m2k=res["u_value_w_m2k"],
        thermal_mass_kj_m2k=res["thermal_mass_kj_m2k"],
        total_unit_cost_inr_m2=res["total_unit_cost_inr_m2"],
        total_embodied_carbon_kgco2_m2=res["total_embodied_carbon_kgco2_m2"]
    )
