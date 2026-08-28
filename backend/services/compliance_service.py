"""
compliance_service.py — Service layer bridging API requests to the Compliance Engine.
"""

from typing import Dict, Any, Optional
from backend.schemas.compliance import ComplianceCheckRequest
from engine.compliance.compliance_engine import run_compliance_audit
from engine.compliance.state_rules import load_state_code


def evaluate_compliance(req: ComplianceCheckRequest) -> Dict[str, Any]:
    """Performs compliance check across National Codes and State Regulations."""
    design_params = {
        "geometry": req.geometry.model_dump(),
        "materials": req.materials.model_dump()
    }
    return run_compliance_audit(
        design_params=design_params,
        simulation_metrics=req.simulation_metrics,
        state_name=req.state_name,
        building_type=req.building_type
    )


def get_state_regulations(state_name: str) -> Optional[Dict[str, Any]]:
    """Fetches raw codified rules for a state."""
    return load_state_code(state_name)
