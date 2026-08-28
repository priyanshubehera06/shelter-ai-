"""
compliance.py — Pydantic Schemas for Policy & Regulatory Compliance Screening.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from backend.schemas.design import GeometryParams, MaterialSelection


class ComplianceCheckRequest(BaseModel):
    state_name: str = Field(default="Odisha", description="Target Indian state or union territory")
    building_type: str = Field(default="Residential / Transitional Shelter", description="Building typology")
    geometry: GeometryParams
    materials: MaterialSelection
    simulation_metrics: Optional[Dict[str, Any]] = None


class ComplianceRuleResult(BaseModel):
    id: str
    jurisdiction: str
    code_name: str
    category: str
    clause: str
    requirement: str
    actual_value: Any
    required_threshold: str
    status: str  # "PASS", "REVIEW", "FAIL", "NOT_VERIFIED"
    reason: str
    remediation: str
    source: str
    source_url: str
    last_verified: str


class ComplianceCheckResponse(BaseModel):
    state: str
    building_type: str
    overall_status: str
    summary: Dict[str, int]
    results: List[ComplianceRuleResult]
    disclaimer: str
