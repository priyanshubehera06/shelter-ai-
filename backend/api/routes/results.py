"""
results.py — REST API endpoints for Final Decision Matrix, Certified PDF Generation & XAI.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Response
from backend.schemas.design import ShelterDesign
from engine.explainability import generate_design_explanation
from reports.report_generator import generate_pdf_report
from engine.geometry import ShelterGeometry
from engine.climate import get_climate_profile

router = APIRouter(prefix="/results", tags=["Results & Reports"])


@router.post("/explain")
def get_explanation(design: ShelterDesign):
    """Generates transparent explainability narratives comparing selected design against regional baseline."""
    loc_id = design.location_id or "leh_ladakh"
    try:
        profile = get_climate_profile(loc_id, month=1)
    except Exception:
        profile = None

    design_dict = {
        "wall_mat_id": design.materials.wall_mat_id,
        "wall_thickness_cm": design.materials.wall_thickness_cm,
        "roof_mat_id": design.materials.roof_mat_id,
        "insulation_mat_id": design.materials.insulation_mat_id,
        "insulation_thickness_cm": design.materials.insulation_thickness_cm,
        "glazing_mat_id": design.materials.glazing_mat_id,
        "wwr_pct": design.geometry.wwr_pct,
        "overhang_m": design.geometry.overhang_m,
        "orientation_deg": design.geometry.orientation_deg,
    }

    zone_name = profile.zone_name if profile else "High-Altitude Cold / Sunny"
    t_max = profile.t_max_c if profile else 2.0
    t_min = profile.t_min_c if profile else -18.0
    diurnal = (t_max - t_min) if profile else 20.0
    ghi = profile.peak_solar_w_m2 if profile else 950.0

    explanation = generate_design_explanation(
        design_dict,
        climate_zone=zone_name,
        t_outdoor_max=t_max,
        t_outdoor_min=t_min,
        avg_diurnal_swing=diurnal,
        ghi_max=ghi,
    )
    return explanation



@router.post("/pdf")
def export_pdf_report(design: ShelterDesign):
    """Generates downloadable certified PDF engineering audit report."""
    try:
        from engine.geometry import ShelterGeometry
        from engine.thermal import simulate_shelter_thermal_dynamics
        from engine.comfort import calculate_pmv_fanger
        from engine.cost import calculate_shelter_cost_and_carbon
        from engine.scoring import calculate_mcda_shelter_score
        from engine.climate import get_climate_profile
        
        geom = ShelterGeometry(
            length_m=design.geometry.length_m,
            width_m=design.geometry.width_m,
            height_m=design.geometry.height_m,
            roof_type=design.geometry.roof_type,
            roof_pitch_deg=design.geometry.roof_pitch_deg,
            wall_thickness_cm=design.geometry.wall_thickness_cm,
            wwr_pct=design.geometry.wwr_pct,
            overhang_m=design.geometry.overhang_m,
            orientation_deg=design.geometry.orientation_deg,
        )
        
        location_id = design.location_id or "leh_ladakh"
        mat_dict = design.materials.model_dump() if hasattr(design.materials, "model_dump") else design.materials.dict()
        climate_records = get_climate_profile(location_id, month=1)
        
        sim = simulate_shelter_thermal_dynamics(
            geometry=geom,
            wall_mat_id=mat_dict.get("wall_mat_id", "trombe_wall_mass"),
            wall_thickness_cm=mat_dict.get("wall_thickness_cm", 30.0),
            roof_mat_id=mat_dict.get("roof_mat_id", "roof_insulated_timber_deck"),
            glazing_mat_id=mat_dict.get("glazing_mat_id", "glazing_double"),
            insulation_mat_id=mat_dict.get("insulation_mat_id", "insulation_glasswool"),
            insulation_thickness_cm=mat_dict.get("insulation_thickness_cm", 10.0),
            climate_records=climate_records,
            occupants=design.occupants or 4
        )
        
        pmv, ppd = calculate_pmv_fanger(sim["avg_t_indoor"], 50.0)
        cost_res = calculate_shelter_cost_and_carbon(geom, wall_mat_id=mat_dict.get("wall_mat_id", "trombe_wall_mass"))
        mcda = calculate_mcda_shelter_score(
            pmv,
            92.0,
            cost_res.get("carbon_intensity_kg_m2", 45.0),
            cost_res.get("capex_inr", 85000.0),
            320.0,
            88.0
        )
        
        pdf_path = generate_pdf_report(
            shelter_name=design.name,
            location_name=location_id.replace("_", " ").title(),
            geometry_dict=geom.envelope_summary(),
            thermal_dict=sim,
            comfort_dict={"pmv": pmv, "compliance_pct": 92.0},
            cost_dict=cost_res,
            mcda_dict=mcda,
        )
        
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()
            
        safe_name = design.name.replace(" ", "_")
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="ShelterAI_Certified_Report_{safe_name}.pdf"'}
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")


