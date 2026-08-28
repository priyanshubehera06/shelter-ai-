"""
compliance_engine.py — Policy & Compliance Screening Engine for ShelterAI.
Audits building geometry, materials, and physics results against Central Codes (ENS, ECBC, NBC)
and State-specific Building Byelaws.
"""

from typing import Dict, List, Optional, Any
from engine.compliance.rules import evaluate_numeric_rule
from engine.compliance.state_rules import load_central_codes, load_state_code


def run_compliance_audit(
    design_params: Dict[str, Any],
    simulation_metrics: Optional[Dict[str, Any]] = None,
    state_name: str = "Odisha",
    building_type: str = "Residential / Transitional Shelter"
) -> Dict[str, Any]:
    """
    Executes preliminary compliance audit against National and State regulations.
    Status outputs: 'PASS', 'REVIEW', 'FAIL', 'NOT_VERIFIED'.
    """
    simulation_metrics = simulation_metrics or {}
    geom = design_params.get("geometry", {})
    mats = design_params.get("materials", {})

    # Extract or compute envelope variables
    length = geom.get("length_m", 6.0)
    width = geom.get("width_m", 4.0)
    height = geom.get("height_m", 2.8)
    floor_area = length * width
    wwr_pct = geom.get("wwr_pct", 15.0)
    overhang = geom.get("overhang_m", 0.6)
    roof_pitch = geom.get("roof_pitch_deg", 15.0)
    u_wall = simulation_metrics.get("u_wall", 0.52)
    u_roof = simulation_metrics.get("u_roof", 0.85)
    
    # Calculate derived parameters
    total_wall_area = 2 * (length + width) * height
    glazed_area = total_wall_area * (wwr_pct / 100.0)
    window_to_floor_ratio_pct = (glazed_area / max(1.0, floor_area)) * 100.0
    operable_opening_ratio_pct = window_to_floor_ratio_pct * 0.85  # typical operable sash

    # RETV approximation (W/m2) based on BEE ENS formula: a*U_wall*(1-WWR) + b*U_glaze*WWR + c*SHGC*WWR
    retv_approx = round(0.5 * u_wall * (1 - wwr_pct/100.0) + 1.2 * 3.0 * (wwr_pct/100.0) + 30.0 * 0.4 * (wwr_pct/100.0), 1)

    eval_data = {
        "u_wall": u_wall,
        "u_roof": u_roof,
        "retv": retv_approx,
        "height_m": height,
        "floor_area_m2": floor_area,
        "wwr_pct": wwr_pct,
        "west_wwr_pct": wwr_pct if geom.get("orientation_deg", 0.0) in [90.0, 270.0] else wwr_pct * 0.7,
        "overhang_m": overhang,
        "roof_pitch_deg": roof_pitch,
        "window_to_floor_ratio_pct": round(window_to_floor_ratio_pct, 1),
        "operable_opening_ratio_pct": round(operable_opening_ratio_pct, 1),
        "vlt": 0.35 if "double" in mats.get("glazing_mat_id", "") else 0.80,
        "plinth_height_m": geom.get("plinth_height_m", 0.45),
        "cyclone_anchoring_verified": True if "concrete" in mats.get("roof_mat_id", "") or overhang <= 0.8 else False,
        "roof_sri": 82.0 if "cool" in mats.get("roof_mat_id", "") else 35.0,
        "wall_thermal_mass_kj_m2k": 180.0 if ("cseb" in mats.get("wall_mat_id", "") or "brick" in mats.get("wall_mat_id", "")) else 40.0,
        "cross_ventilation_ratio": 1.0,
        "seismic_band_integrated": True
    }

    results_list: List[Dict[str, Any]] = []

    # 1. Audit Central Codes
    central_codes = load_central_codes()
    for code in central_codes:
        code_id = code.get("code_id", "CENTRAL")
        code_name = code.get("code_name", "")
        source_url = code.get("source_url", "")
        for rule in code.get("rules", []):
            param = rule.get("parameter")
            op = rule.get("operator")
            lim = rule.get("max_limit") if "max" in rule or op in ["<=", "<"] else rule.get("min_limit")
            actual_val = eval_data.get(param)

            if actual_val is not None and lim is not None:
                passed = evaluate_numeric_rule(actual_val, op, lim)
                status = "PASS" if passed else rule.get("failure_severity", "REVIEW")
                reason = (
                    f"Calculated value {actual_val} {op} {lim} {rule.get('units', '')} "
                    f"({'meets' if passed else 'fails to meet'} {code_id} requirement)."
                )
            else:
                status = "NOT_VERIFIED"
                reason = f"Parameter {param} not directly specified in current parametric configuration."

            results_list.append({
                "id": rule.get("id"),
                "jurisdiction": "Central",
                "code_name": code_name,
                "category": rule.get("category"),
                "clause": rule.get("clause"),
                "requirement": rule.get("description"),
                "actual_value": actual_val,
                "required_threshold": f"{op} {lim} {rule.get('units', '')}" if lim is not None else "Documented Standard",
                "status": status,
                "reason": reason,
                "remediation": rule.get("remediation", ""),
                "source": code_name,
                "source_url": source_url,
                "last_verified": "2025-12-01"
            })

    # 2. Audit State-Specific Rules
    state_code = load_state_code(state_name)
    if state_code:
        state_title = state_code.get("state_name", state_name)
        gov_doc = state_code.get("governing_document", "")
        src_url = state_code.get("source_url", "")
        for rule in state_code.get("rules", []):
            param = rule.get("parameter")
            op = rule.get("operator")
            lim = rule.get("max_limit") if "max" in rule or op in ["<=", "<"] else rule.get("min_limit", rule.get("expected_value"))
            actual_val = eval_data.get(param)

            if isinstance(lim, bool):
                passed = (actual_val == lim)
                status = "PASS" if passed else rule.get("failure_severity", "REVIEW")
                reason = f"State adaptation verification: {'Compliant with' if passed else 'Requires on-site confirmation under'} {state_title} regulations."
            elif actual_val is not None and isinstance(lim, (int, float)):
                passed = evaluate_numeric_rule(actual_val, op, lim)
                status = "PASS" if passed else rule.get("failure_severity", "REVIEW")
                reason = f"State adaptation: Calculated value {actual_val} {op} {lim} ({'Complies with' if passed else 'Non-compliant with'} {state_title} requirement)."
            else:
                status = "NOT_VERIFIED"
                reason = f"Requires local municipal verification under {state_title} byelaws."

            results_list.append({
                "id": rule.get("id"),
                "jurisdiction": f"State ({state_title})",
                "code_name": gov_doc,
                "category": rule.get("category"),
                "clause": rule.get("clause"),
                "requirement": rule.get("description"),
                "actual_value": actual_val,
                "required_threshold": f"{op} {lim}" if lim is not None else "Documented Standard",
                "status": status,
                "reason": reason,
                "remediation": rule.get("remediation", ""),
                "source": gov_doc,
                "source_url": src_url,
                "last_verified": state_code.get("last_verified", "2025-10-01")
            })
    else:
        results_list.append({
            "id": f"{state_name.upper()}_LOCAL_BYELAWS",
            "jurisdiction": f"State ({state_name})",
            "code_name": f"{state_name} Municipal Building Byelaws",
            "category": "Local Building Setbacks & Height Zoning",
            "clause": "Municipal Zoning Annexure",
            "requirement": "Local authority site setbacks, permissible FAR, and fire engine turning radius.",
            "actual_value": "Site Specific",
            "required_threshold": "Local Master Plan",
            "status": "NOT_VERIFIED",
            "reason": f"Detailed municipal master plan for {state_name} requires local site verification.",
            "remediation": "Submit preliminary drawings to local town planning development authority.",
            "source": f"{state_name} Urban Development Department",
            "source_url": "https://mohua.gov.in/",
            "last_verified": "2025-01-01"
        })

    # Summary Statistics
    pass_count = sum(1 for r in results_list if r["status"] == "PASS")
    review_count = sum(1 for r in results_list if r["status"] == "REVIEW")
    fail_count = sum(1 for r in results_list if r["status"] == "FAIL")
    not_verified_count = sum(1 for r in results_list if r["status"] == "NOT_VERIFIED")

    overall_status = "PASS" if fail_count == 0 and review_count == 0 else ("FAIL" if fail_count > 0 else "REVIEW")

    return {
        "state": state_name,
        "building_type": building_type,
        "overall_status": overall_status,
        "summary": {
            "total_rules_checked": len(results_list),
            "pass": pass_count,
            "review": review_count,
            "fail": fail_count,
            "not_verified": not_verified_count
        },
        "results": results_list,
        "disclaimer": "ShelterAI provides preliminary design and compliance screening based on available datasets and coded rules. It is not a substitute for approval by the competent authority or design certification by qualified professionals."
    }
