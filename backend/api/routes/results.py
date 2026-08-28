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
    geom = ShelterGeometry(
        length_m=design.geometry.length_m,
        width_m=design.geometry.width_m,
        height_m=design.geometry.height_m,
        roof_type=design.geometry.roof_type,
        roof_pitch_deg=design.geometry.roof_pitch_deg,
        wall_thickness_cm=design.geometry.wall_thickness_cm,
        wwr_pct=design.geometry.wwr_pct,
        overhang_m=design.geometry.overhang_m,
        orientation_deg=design.geometry.orientation_deg
    )
    
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
    
    explanation = generate_design_explanation(design_dict, climate_zone="Composite")
    return {"explanation": explanation}


@router.post("/pdf")
def export_pdf_report(design: ShelterDesign):
    """Generates downloadable certified PDF engineering audit report."""
    try:
        pdf_bytes = generate_pdf_report(
            design_id=design.id or "design_custom",
            design_name=design.name,
            location_id=design.location_id or "sambalpur",
            design_dict={
                "geometry": design.geometry.model_dump(),
                "materials": design.materials.model_dump(),
                "occupants": design.occupants
            }
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=ShelterAI_Certified_Report_{design.name.replace(' ', '_')}.pdf"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation error: {str(e)}")
