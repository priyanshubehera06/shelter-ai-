"""
climate_rules.py — Climate zone specific design parameters, targets, and boundary conditions
for climate-responsive shelter recommendation in India.
"""

from typing import Dict, Any, List

CLIMATE_ZONE_TARGETS: Dict[str, Dict[str, Any]] = {
    "Hot & Dry": {
        "target_max_u_wall": 0.44,
        "target_max_u_roof": 0.33,
        "recommended_thermal_mass": "High",
        "recommended_wwr_range": [10.0, 15.0],
        "recommended_overhang_m": 0.75,
        "recommended_ventilation": "Daytime sealed, night flush ventilation",
        "recommended_shading": "Deep external overhangs and vertical fins on East/West",
        "cooling_strategy": "Evaporative cooling, thermal mass lag, courtyard buffering",
        "key_mechanisms": [
            "High thermal inertia (damping factor >= 0.65) to delay diurnal heat wave",
            "Continuous roof insulation to block solar radiation (>800 W/m² peak)",
            "Minimal West-facing fenestration to eliminate direct solar infiltration"
        ]
    },
    "Warm & Humid": {
        "target_max_u_wall": 0.60,
        "target_max_u_roof": 0.35,
        "recommended_thermal_mass": "Low to Moderate",
        "recommended_wwr_range": [15.0, 25.0],
        "recommended_overhang_m": 0.90,
        "recommended_ventilation": "Continuous cross ventilation (air velocity 0.5 - 1.5 m/s)",
        "recommended_shading": "Continuous horizontal chajjas and operable ventilated louvers",
        "cooling_strategy": "Induced convective cooling, high air exchange, breathable envelope",
        "key_mechanisms": [
            "Maximizing operable openings (operable area >= 12.5% of floor area)",
            "Sloped high-pitch roof for rapid monsoon precipitation shedding",
            "Low thermal mass to avoid night-time radiative heat entrapment"
        ]
    },
    "Composite": {
        "target_max_u_wall": 0.44,
        "target_max_u_roof": 0.33,
        "recommended_thermal_mass": "High",
        "recommended_wwr_range": [12.0, 18.0],
        "recommended_overhang_m": 0.60,
        "recommended_ventilation": "Seasonal switchable (cross-vent in monsoon, night flush in summer, sealed in winter)",
        "recommended_shading": "Movable or seasonal shading pergolas",
        "cooling_strategy": "Dual-mode envelope with high summer thermal lag and winter passive solar gain",
        "key_mechanisms": [
            "Versatile envelope maintaining U-value < 0.44 W/m²K in peak summer & winter",
            "Reflective cool roof coating with under-deck thermal insulation",
            "Flexible operable windows for monsoon airflow"
        ]
    },
    "Moderate": {
        "target_max_u_wall": 0.75,
        "target_max_u_roof": 0.50,
        "recommended_thermal_mass": "Moderate",
        "recommended_wwr_range": [15.0, 22.0],
        "recommended_overhang_m": 0.50,
        "recommended_ventilation": "Daytime natural ventilation",
        "recommended_shading": "Standard horizontal overhangs",
        "cooling_strategy": "Direct passive solar gain and natural breeze capture",
        "key_mechanisms": [
            "Optimal daylight autonomy (VLT >= 0.30)",
            "Balanced natural ventilation throughout day"
        ]
    },
    "Cold": {
        "target_max_u_wall": 0.35,
        "target_max_u_roof": 0.25,
        "recommended_thermal_mass": "High",
        "recommended_wwr_range": [12.0, 20.0],
        "recommended_overhang_m": 0.30,
        "recommended_ventilation": "Controlled minimum fresh air (0.5 ACH) with heat recovery",
        "recommended_shading": "Unshaded South glazing for passive winter solar capture (Trombe wall)",
        "cooling_strategy": "Passive solar heat retention and high airtightness",
        "key_mechanisms": [
            "Extremely low envelope U-values (<0.35 W/m²K)",
            "Double/triple glazed argon-filled windows",
            "Direct solar heat collection via South-facing Trombe wall"
        ]
    }
}


def get_climate_targets(climate_zone: str) -> Dict[str, Any]:
    """Retrieve normalized targets matching the given climate zone string."""
    for key, val in CLIMATE_ZONE_TARGETS.items():
        if key.lower() in climate_zone.lower():
            return val
    return CLIMATE_ZONE_TARGETS["Composite"]
