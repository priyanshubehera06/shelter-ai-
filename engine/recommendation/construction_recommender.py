"""
construction_recommender.py — Construction System & Assembly Method Recommendation Engine.
Evaluates speed, constructability, disaster resistance, labor complexity, and climate suitability.
"""

from typing import Dict, List, Optional, Any
from engine.recommendation.recommendation_scoring import calculate_composite_score, DEFAULT_WEIGHTS

CONSTRUCTION_SYSTEMS = [
    {
        "id": "cseb_interlocking_mortarless",
        "name": "Interlocking CSEB (Mortarless Compressed Stabilized Earth Block)",
        "archetype": "Masonry Eco-Block",
        "deployment_speed_days": 10,
        "labor_skill": "Low to Moderate (Semi-skilled)",
        "embodied_carbon": "Ultra-Low (0.04 kg CO2/kg)",
        "thermal_inertia": "High",
        "hazard_suitability": ["Heatwave", "Drought", "Moderate Seismic"],
        "base_cost_inr_m2": 650,
        "description": "Tongue-and-groove compressed earth blocks locked with minimal grout, ideal for local earth sourcing and high thermal lag in rural/semi-urban regions."
    },
    {
        "id": "light_gauge_steel_prefab",
        "name": "Light Gauge Steel Frame (LGSF) Prefab Panelized Assembly",
        "archetype": "Rapid Modular Prefab",
        "deployment_speed_days": 3,
        "labor_skill": "Moderate (Dry assembly crew)",
        "embodied_carbon": "Medium",
        "thermal_inertia": "Low (Requires Cavity Insulation)",
        "hazard_suitability": ["Earthquake (Zone IV/V)", "Cyclone", "Emergency Disaster Relief"],
        "base_cost_inr_m2": 1800,
        "description": "Galvanized cold-formed steel framing panels erected rapidly on site with dry insulated wall boards, offering extreme ductile seismic resistance."
    },
    {
        "id": "reinforced_confined_masonry",
        "name": "Confined Masonry with Reinforced Concrete Tie-Columns & Bands",
        "archetype": "Permanent Engineered Masonry",
        "deployment_speed_days": 21,
        "labor_skill": "Standard Masonry Craftsmen",
        "embodied_carbon": "Medium-High",
        "thermal_inertia": "Very High",
        "hazard_suitability": ["Cyclone", "Flood", "Heatwave", "Earthquake"],
        "base_cost_inr_m2": 1400,
        "description": "Unreinforced brick/block masonry walls bounded on all 4 sides by cast-in-place concrete tie-columns and tie-beams for maximum multi-hazard endurance."
    },
    {
        "id": "elevated_bamboo_composite",
        "name": "Treated Structural Bamboo Truss on Elevated Concrete/Timber Stilts",
        "archetype": "Vernacular Bio-Composite",
        "deployment_speed_days": 5,
        "labor_skill": "Vernacular / Local Carpentry",
        "embodied_carbon": "Negative / Carbon Sink",
        "thermal_inertia": "Low (High Natural Aeration)",
        "hazard_suitability": ["Flood", "Extreme Rain", "Humid Heat", "Earthquake"],
        "base_cost_inr_m2": 550,
        "description": "Borax-treated bamboo post-and-beam frame on stilts with woven composite cladding, optimized for wetlands, coastal high-water tables, and flood plains."
    },
    {
        "id": "modular_container_pod",
        "name": "Modular Rapid-Deployment Insulated Disaster Relief Pod",
        "archetype": "Emergency Pod",
        "deployment_speed_days": 1,
        "labor_skill": "Crane / Forklift Placement",
        "embodied_carbon": "Medium-Low (Reused structural shell)",
        "thermal_inertia": "Moderate (Internal Rockwool lining)",
        "hazard_suitability": ["Post-Disaster Immediate Relief", "Migrant Transit Camp", "Emergency Clinic"],
        "base_cost_inr_m2": 2100,
        "description": "Pre-outfitted flatpack or ISO-dimensioned pod with pre-installed electricals, insulated panels, and adjustable screw-jack footings."
    }
]


def recommend_construction_method(
    climate_zone: str = "Composite",
    shelter_type: str = "Standard Residential",
    disaster_mode: Optional[str] = None,
    rapid_deployment_needed: bool = False,
    budget_level: str = "medium",
    weights: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Ranks construction assembly systems based on deployment speed, disaster resilience,
    thermal performance, and cost constraints.
    """
    w_config = weights or DEFAULT_WEIGHTS
    candidates = []

    for sys in CONSTRUCTION_SYSTEMS:
        # 1. Thermal score
        if "Dry" in climate_zone or "Composite" in climate_zone:
            thermal_score = 90.0 if sys["thermal_inertia"] in ["High", "Very High"] else 65.0
        elif "Humid" in climate_zone:
            thermal_score = 92.0 if "Bamboo" in sys["name"] or "Modular" in sys["name"] else 75.0
        else:
            thermal_score = 80.0

        # 2. Cost score
        cost_score = max(20.0, min(100.0, 100.0 - (sys["base_cost_inr_m2"] / 2500.0) * 70.0))
        if budget_level == "low":
            cost_score = max(10.0, min(100.0, 100.0 - (sys["base_cost_inr_m2"] / 1000.0) * 80.0))

        # 3. Resilience score
        resilience_score = 75.0
        if disaster_mode:
            matched_hazards = [h for h in sys["hazard_suitability"] if disaster_mode.lower() in h.lower()]
            if matched_hazards:
                resilience_score = 96.0
            else:
                resilience_score = 55.0

        # 4. Constructability & Speed
        constructability_score = 80.0
        if rapid_deployment_needed or disaster_mode or "Disaster" in shelter_type or "Migrant" in shelter_type:
            if sys["deployment_speed_days"] <= 3:
                constructability_score = 98.0
            elif sys["deployment_speed_days"] <= 7:
                constructability_score = 85.0
            else:
                constructability_score = 50.0

        avail_score = 85.0

        composite = calculate_composite_score(
            thermal_score, cost_score, resilience_score, constructability_score, avail_score, w_config
        )

        candidates.append({
            "system_id": sys["id"],
            "name": sys["name"],
            "archetype": sys["archetype"],
            "deployment_speed_days": sys["deployment_speed_days"],
            "labor_skill": sys["labor_skill"],
            "embodied_carbon": sys["embodied_carbon"],
            "thermal_inertia": sys["thermal_inertia"],
            "base_cost_inr_m2": sys["base_cost_inr_m2"],
            "description": sys["description"],
            "score": composite,
            "sub_scores": {
                "thermal_suitability": round(thermal_score, 1),
                "cost_suitability": round(cost_score, 1),
                "disaster_resilience": round(resilience_score, 1),
                "constructability_speed": round(constructability_score, 1)
            }
        })

    candidates.sort(key=lambda x: x["score"], reverse=True)
    best = candidates[0]

    return {
        "best_construction_method": best,
        "ranked_methods": candidates,
        "recommendation_summary": (
            f"Recommended construction method: {best['name']} with estimated assembly time of "
            f"{best['deployment_speed_days']} days (Composite Score: {best['score']}/100)."
        )
    }
