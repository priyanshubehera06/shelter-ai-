"""
compliance.py — REST API endpoints for Building Code and Regulatory Compliance Checks.
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.compliance import (
    ComplianceCheckRequest,
    ComplianceCheckResponse
)
from backend.services.compliance_service import evaluate_compliance, get_state_regulations

router = APIRouter(prefix="/compliance", tags=["Compliance & Policy"])


@router.post("/check", response_model=ComplianceCheckResponse)
def check_compliance(req: ComplianceCheckRequest):
    """
    Screens shelter design parameters against National Codes (ENS 2021, ECBC 2017, NBC 2016)
    and State Building Byelaws, returning PASS, REVIEW, FAIL, and NOT_VERIFIED statuses.
    """
    try:
        return evaluate_compliance(req)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance screening error: {str(e)}")


@router.get("/regulations/{state_name}")
def get_regulations_by_state(state_name: str):
    """Retrieves verified state building regulations and climate adaptations for a given state."""
    data = get_state_regulations(state_name)
    if not data:
        raise HTTPException(status_code=404, detail=f"No verified state regulation document found for {state_name}")
    return data
