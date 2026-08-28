"""
design_service.py — Service adapter interfacing with engine.geometry and baseline design presets.
"""

import os
import json
from typing import List, Optional, Dict, Any
from engine.geometry import ShelterGeometry
from engine.materials import calculate_assembly_u_value, get_material_by_id
from backend.schemas.design import GeometryParams, MaterialSelection, ShelterDesign, StructuralMetrics

PRESETS_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "sample_designs.json")


def get_default_designs() -> List[ShelterDesign]:
    """Retrieves baseline shelter designs from sample_designs.json."""
    designs = []
    if os.path.exists(PRESETS_FILE):
        try:
            with open(PRESETS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                for item in data.get("baseline_designs", []):
                    dims = item.get("dimensions", {})
                    designs.append(ShelterDesign(
                        id=item.get("id"),
                        name=item.get("name", "Baseline Shelter"),
                        archetype=item.get("archetype", "Humanitarian"),
                        geometry=GeometryParams(
                            length_m=float(dims.get("length_m", 6.0)),
                            width_m=float(dims.get("width_m", 4.0)),
                            height_m=float(dims.get("height_m", 2.8)),
                            roof_type=str(item.get("roof_type", "pitched")),
                            roof_pitch_deg=float(item.get("roof_pitch_deg", 15.0)),
                            wall_thickness_cm=float(item.get("wall_thickness_cm", 20.0)),
                            wwr_pct=float(item.get("wwr_pct", 15.0)),
                            overhang_m=float(item.get("overhang_m", 0.6)),
                            orientation_deg=float(item.get("orientation_deg", 0.0))
                        ),
                        materials=MaterialSelection(
                            wall_mat_id=str(item.get("wall_mat_id", "cseb_interlocking")),
                            wall_thickness_cm=float(item.get("wall_thickness_cm", 20.0)),
                            roof_mat_id=str(item.get("roof_mat_id", "roof_cgi_insulated")),
                            insulation_mat_id=item.get("insulation_mat_id"),
                            insulation_thickness_cm=float(item.get("insulation_thickness_cm", 0.0) or 0.0),
                            glazing_mat_id=str(item.get("glazing_mat_id", "glazing_single"))
                        ),
                        occupants=4,
                        location_id="sambalpur"
                    ))
        except Exception as e:
            pass
            
    if not designs:
        designs.append(ShelterDesign(
            id="design_default",
            name="Standard Climate-Resilient Shelter",
            archetype="Transitional Resilient",
            geometry=GeometryParams(),
            materials=MaterialSelection(),
            occupants=4,
            location_id="sambalpur"
        ))
        
    return designs


def calculate_structural_summary(geom_params: GeometryParams, mat_sel: MaterialSelection, occupants: int = 4) -> StructuralMetrics:
    """Calculates all architectural and envelope metrics via engine.geometry."""
    geom = ShelterGeometry(
        length_m=geom_params.length_m,
        width_m=geom_params.width_m,
        height_m=geom_params.height_m,
        roof_type=geom_params.roof_type,
        roof_pitch_deg=geom_params.roof_pitch_deg,
        wall_thickness_cm=geom_params.wall_thickness_cm,
        wwr_pct=geom_params.wwr_pct,
        overhang_m=geom_params.overhang_m,
        orientation_deg=geom_params.orientation_deg,
        door_width_m=geom_params.door_width_m,
        door_height_m=geom_params.door_height_m,
        door_count=geom_params.door_count
    )
    
    u_wall_res = calculate_assembly_u_value(
        core_mat_id=mat_sel.wall_mat_id,
        thickness_cm=mat_sel.wall_thickness_cm,
        ins_mat_id=mat_sel.insulation_mat_id,
        ins_thickness_cm=mat_sel.insulation_thickness_cm
    )
    
    # Roof U-value calculation
    u_roof_res = calculate_assembly_u_value(
        core_mat_id=mat_sel.roof_mat_id,
        thickness_cm=10.0,
        ins_mat_id=mat_sel.insulation_mat_id,
        ins_thickness_cm=mat_sel.insulation_thickness_cm
    )
    
    return StructuralMetrics(
        floor_area_m2=round(geom.floor_area(), 2),
        gross_volume_m3=round(geom.volume(), 2),
        gross_wall_area_m2=round(geom.gross_wall_area(), 2),
        net_wall_area_m2=round(geom.net_wall_area(), 2),
        window_area_m2=round(geom.window_area(), 2),
        door_area_m2=round(geom.door_area(), 2),
        roof_area_m2=round(geom.roof_area(), 2),
        surface_to_volume_ratio=round(geom.surface_to_volume_ratio(), 3),
        roof_peak_height_m=round(geom.height + geom.roof_height_delta(), 2),
        area_per_person_m2=round(geom.floor_area() / max(1, occupants), 2),
        wall_u_value_w_m2k=round(u_wall_res["u_value_w_m2k"], 3),
        roof_u_value_w_m2k=round(u_roof_res["u_value_w_m2k"], 3)
    )
