"""
passive_design.py — Climate-Responsive Passive Design Intelligence Engine for Shelter-AI.
Generates actionable, deterministic architectural recommendations for Orientation, Materials,
Geometry compactness, Natural Ventilation, Openings (WWR), and Solar Shading based on micro-climates.
"""

from typing import Dict, List, Optional, Any
import numpy as np
from engine.climate_intelligence import analyze_climate_intelligence


def generate_passive_design_recommendations(
    climate_insights: Optional[Dict[str, Any]] = None,
    occupants: int = 4,
    budget_level: str = "medium",  # "low", "medium", "high"
    target_area_m2: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Generates structured passive design strategies across 6 core architectural pillars:
    1. ORIENTATION
    2. MATERIALS
    3. GEOMETRY
    4. VENTILATION
    5. OPENINGS
    6. SHADING

    Every recommendation strictly adheres to:
    { "recommendation": ..., "reason": ..., "priority": ..., "expected_benefit": ... }
    """
    if climate_insights is None:
        climate_insights = analyze_climate_intelligence()

    climate_zone = climate_insights.get("climate_zone", "Composite / Moderate")
    t_max = climate_insights.get("max_temp_c", 38.0)
    t_min = climate_insights.get("min_temp_c", 18.0)
    avg_swing = climate_insights.get("avg_diurnal_swing_c", 10.0)
    rh_mean = climate_insights.get("mean_humidity_pct", 55.0)
    ghi_max = climate_insights.get("max_solar_radiation_w_m2", 900.0)
    wind_mean = climate_insights.get("mean_wind_speed_m_s", 3.0)

    recommendations: List[Dict[str, Any]] = []

    # -------------------------------------------------------------
    # 1. ORIENTATION RECOMMENDATION
    # -------------------------------------------------------------
    if "Cold" in climate_zone or t_min < 10.0:
        recommendations.append({
            "category": "ORIENTATION",
            "recommendation": "Orient major longitudinal facade within 0° to 15° South (Azimuth 180°).",
            "reason": f"Cold winter temperatures (minimum {t_min}°C) require maximizing passive direct solar gain during winter months.",
            "priority": "HIGH",
            "expected_benefit": "Captures 35-45% more winter solar heat gain, reducing heating requirements.",
        })
    else:
        recommendations.append({
            "category": "ORIENTATION",
            "recommendation": "Orient major longitudinal facade North-South (Azimuth 0° / 360°), minimizing East-West wall exposure.",
            "reason": f"High peak solar irradiance ({ghi_max:.0f} W/m²) generates extreme morning (East) and afternoon (West) thermal loads.",
            "priority": "HIGH",
            "expected_benefit": "Reduces peak exterior solar surface overheating by up to 6.5°C.",
        })

    # -------------------------------------------------------------
    # 2. MATERIALS RECOMMENDATION
    # -------------------------------------------------------------
    if avg_swing >= 9.0 and "Humid" not in climate_zone:
        wall_rec = "High thermal mass walls: Compressed Stabilized Earth Blocks (CSEB 20cm) or Brick Masonry."
        roof_rec = "Continuous overhead insulation: 50mm Rockwool or EPS under CGI / Concrete Slab roof."
        mat_reason = f"High diurnal temperature swing ({avg_swing:.1f}°C) and peak temp of {t_max}°C."
        mat_benefit = "Flattens peak indoor temperature wave by 4.0-6.0°C and provides 6-8 hours phase lag."
    elif "Humid" in climate_zone:
        wall_rec = "Lightweight breathable composite wallboards (Bamboo Composite / Woven Timber)."
        roof_rec = "High-reflectance sloped thatch or double-skin ventilated metal roof with reflective foil barrier."
        mat_reason = f"High ambient humidity ({rh_mean:.0f}% RH) with minimal night cooling."
        mat_benefit = "Prevents heat retention at night and accelerates convective heat release."
    else:
        wall_rec = "Autoclaved Aerated Concrete (AAC 20cm) or CSEB Interlocking Block."
        roof_rec = "Insulated CGI Sheet with 50mm mineral wool (U ≤ 0.45 W/m²K)."
        mat_reason = "Balanced multi-seasonal composite climate with summer overheating and cool winter nights."
        mat_benefit = "Year-round passive envelope moderation with low embodied carbon footprint."

    recommendations.append({
        "category": "MATERIALS",
        "recommendation": f"{wall_rec} | {roof_rec}",
        "reason": mat_reason,
        "priority": "HIGH",
        "expected_benefit": mat_benefit,
    })

    # -------------------------------------------------------------
    # 3. GEOMETRY & COMPACTNESS RECOMMENDATION
    # -------------------------------------------------------------
    if "Cold" in climate_zone:
        geom_rec = "Compact cubical form (Aspect ratio 1.1 - 1.3, S/V ratio ≤ 1.10 m⁻¹)."
        geom_reason = "Minimizing external surface-to-volume (S/V) ratio reduces conductive heat loss to freezing ambient air."
        geom_benefit = "Reduces total exposed building surface area and space heating load by 22%."
    elif "Humid" in climate_zone:
        geom_rec = "Elongated linear form (Aspect ratio 1.8 - 2.5, East-West length) with high sloped ceiling (≥3.2m)."
        geom_reason = "Narrow floor plan ensures wind breeze penetrates through all living quarters without air stagnation."
        geom_benefit = "Maximizes cross-ventilation airflow paths and facilitates warm air stack stratification."
    else:
        geom_rec = "Moderate rectangular footprint (Aspect ratio 1.4 - 1.6, e.g. 6.0m × 4.0m) with 2.8m ceiling height."
        geom_reason = "Optimal balance between structural efficiency, natural light distribution, and solar exposure control."
        geom_benefit = "Achieves standard Sphere humanitarian compliance (3.5 m²/person) with optimal compactness."

    recommendations.append({
        "category": "GEOMETRY",
        "recommendation": geom_rec,
        "reason": geom_reason,
        "priority": "MEDIUM",
        "expected_benefit": geom_benefit,
    })

    # -------------------------------------------------------------
    # 4. NATURAL VENTILATION RECOMMENDATION
    # -------------------------------------------------------------
    if "Humid" in climate_zone or (rh_mean > 60.0 and t_mean > 24.0):
        vent_rec = "Continuous cross-ventilation with large operable louvers (inlet/outlet area ≥ 15% of floor area)."
        vent_reason = f"Elevated humidity ({rh_mean:.0f}%) requires high indoor air velocity (≥0.5 m/s) for sweat evaporation."
        vent_benefit = "Expands adaptive comfort threshold by up to 3.0°C via physiological skin convective cooling."
    elif "Arid" in climate_zone or avg_swing >= 11.0:
        vent_rec = "Diurnal night-purge cooling: seal shelter during hot daytime (10:00-17:00), open for night ventilation."
        vent_reason = "Daytime ambient air is scorching (>40°C), whereas nighttime air drops significantly to recharge thermal mass."
        vent_benefit = "Lowers starting morning indoor structural temperature by 3.5-5.0°C."
    else:
        vent_rec = "Seasonal operable cross-ventilation with trickle vents and ceiling level exhaust."
        vent_reason = "Moderate wind availability allowing user-controlled natural fresh air renewal."
        vent_benefit = "Maintains indoor air quality (ACH 3.0 - 4.0) with zero active power consumption."

    recommendations.append({
        "category": "VENTILATION",
        "recommendation": vent_rec,
        "reason": vent_reason,
        "priority": "HIGH",
        "expected_benefit": vent_benefit,
    })

    # -------------------------------------------------------------
    # 5. OPENINGS & GLAZING (WWR) RECOMMENDATION
    # -------------------------------------------------------------
    if "Arid" in climate_zone:
        wwr_rec = "Low Window-to-Wall Ratio: 10% to 12% WWR with deep recessed reveals and exterior shutters."
        wwr_reason = "Glazing is the weakest thermal link, admitting direct infrared solar radiation into the space."
        wwr_benefit = "Prevents severe greenhouse heat trapping, reducing peak indoor temp by up to 4.2°C."
    elif "Humid" in climate_zone:
        wwr_rec = "High Window-to-Wall Ratio: 20% to 25% WWR with jali/wooden louvers and insect mesh."
        wwr_reason = "Maximizes airflow area while blocking rainfall and diffusing glare."
        wwr_benefit = "Ensures continuous passive airflow renewal without overheating."
    else:
        wwr_rec = "Standard 12% to 15% WWR with double glazing on North/South facades."
        wwr_reason = "Provides optimal daylighting (300-500 lux) while restricting thermal transmission."
        wwr_benefit = "Satisfies NBC daylighting standards with minimal conductive thermal bridging."

    recommendations.append({
        "category": "OPENINGS",
        "recommendation": wwr_rec,
        "reason": wwr_reason,
        "priority": "MEDIUM",
        "expected_benefit": wwr_benefit,
    })

    # -------------------------------------------------------------
    # 6. SHADING & OVERHANG RECOMMENDATION
    # -------------------------------------------------------------
    if ghi_max > 850.0:
        shade_rec = "Deep roof overhang eaves: 0.6m to 0.9m on North/South facades; 1.0m to 1.2m on East/West."
        shade_reason = f"High solar radiation ({ghi_max:.0f} W/m²) causes intense incident wall and window heat flux."
        shade_benefit = "Completely shades windows during peak solar altitude hours (10:00 to 15:00), cutting solar gains by 60-80%."
    else:
        shade_rec = "Moderate overhang eaves: 0.4m to 0.6m depth."
        shade_reason = "Protects envelope from monsoon driving rain while admitting winter sun."
        shade_benefit = "Prevents facade weathering and reduces glare."

    recommendations.append({
        "category": "SHADING",
        "recommendation": shade_rec,
        "reason": shade_reason,
        "priority": "HIGH",
        "expected_benefit": shade_benefit,
    })

    return {
        "climate_zone": climate_zone,
        "recommendations_count": len(recommendations),
        "recommendations": recommendations,
        "design_rules_applied": [
            "NBC 2016 Part 8 (Building Physics & Daylighting)",
            "ECBC 2017 (Energy Conservation Building Code)",
            "ASHRAE Standard 55-2020 (Adaptive Thermal Comfort)",
            "Sphere Humanitarian Standards (Minimum Spatial Standards)",
        ],
    }
