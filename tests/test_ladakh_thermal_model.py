"""
test_ladakh_thermal_model.py — Rigorous unit tests for high-altitude cold climate (Ladakh) thermal dynamics,
NOAA solar surface incidence angles, directional fenestration heat gain, composite envelope U-values,
and time-dependent day/night heat balance.
"""

import pytest
import numpy as np
from engine.geometry import ShelterGeometry
from engine.solar import (
    calculate_solar_position,
    calculate_surface_incidence_angle,
    calculate_incident_radiation_on_surface,
    calculate_fenestration_solar_gain
)
from engine.materials import (
    calculate_assembly_u_value,
    calculate_composite_assembly_u_value,
    get_material_by_id
)
from engine.thermal import (
    simulate_shelter_thermal_dynamics,
    compare_thermal_scenarios
)
from engine.tvi.tvi_engine import calculate_state_tvi


def test_ladakh_solar_position_and_incidence_angle():
    """Verify NOAA solar geometry for Leh, Ladakh (34.15°N, 77.58°E) in winter (January)."""
    # At noon in winter, sun is in the South (azimuth ~ 180°) with low altitude (~32°)
    alt, az, is_day = calculate_solar_position(lat_deg=34.1526, lon_deg=77.5771, day_of_year=15, hour_of_day=12.0)
    assert is_day is True
    assert 25.0 <= alt <= 40.0
    assert 160.0 <= az <= 200.0

    # True South vertical wall (tilt=90°, az=180°) should have high incidence cos(theta) (low angle theta)
    theta_south = calculate_surface_incidence_angle(
        solar_alt_deg=alt,
        solar_az_deg=az,
        surface_tilt_deg=90.0,
        surface_az_deg=180.0
    )
    assert theta_south < 45.0  # High solar capture

    # North vertical wall (tilt=90°, az=0°) should receive zero beam radiation (theta ~ 90°)
    theta_north = calculate_surface_incidence_angle(
        solar_alt_deg=alt,
        solar_az_deg=az,
        surface_tilt_deg=90.0,
        surface_az_deg=0.0
    )
    assert theta_north >= 85.0


def test_fenestration_solar_heat_gain():
    """Verify directional solar heat gain through South-facing double glazing in winter Ladakh."""
    # Peak winter GHI ~ 800 W/m²
    incident_south = calculate_incident_radiation_on_surface(
        ghi_w_m2=800.0,
        solar_alt_deg=32.0,
        solar_az_deg=180.0,
        surface_tilt_deg=90.0,
        surface_az_deg=180.0
    )
    assert incident_south > 600.0  # Vertical South facade captures strong direct beam

    # Double low-e window (area = 5 m², SHGC = 0.45)
    q_sol = calculate_fenestration_solar_gain(
        glazed_area_m2=5.0,
        shgc=0.45,
        incident_radiation_w_m2=incident_south
    )
    assert q_sol > 1300.0  # Generates over 1.3 kW of passive solar heat gain at noon


def test_composite_multi_layer_assembly():
    """Verify U-value and thermal mass for high-altitude multi-layer wall assembly."""
    # Layered: Exterior Plaster (2cm) + Sheep Wool (7.5cm) + Trombe Earth Mass (30cm) + Timber (2cm)
    layers = [
        {"material_id": "mud_thatch_wall", "thickness_cm": 2.0},
        {"material_id": "insulation_sheep_wool", "thickness_cm": 7.5},
        {"material_id": "trombe_wall_mass", "thickness_cm": 30.0},
        {"material_id": "bamboo_composite", "thickness_cm": 2.0}
    ]
    res = calculate_composite_assembly_u_value(layers)
    assert res["u_value_w_m2k"] < 0.50  # Super-insulated envelope
    assert res["thermal_mass_kj_m2k"] > 400.0  # Massive diurnal storage
    assert res["total_thickness_cm"] == 41.5


def test_ladakh_winter_transient_thermal_simulation():
    """Verify 24-hour simulation with cold ambient (-15°C night, +2°C day, 850 W/m² solar)."""
    geom = ShelterGeometry(
        length_m=7.0,
        width_m=5.0,
        height_m=2.8,
        roof_type="pitched",
        roof_pitch_deg=20.0,
        wall_thickness_cm=30.0,
        wwr_pct=20.0,
        overhang_m=0.5,
        orientation_deg=180.0  # South-facing
    )

    # Synthetic extreme winter Ladakh diurnal records
    hours = np.arange(24)
    t_out = -6.5 + 8.5 * np.sin((hours - 8) * np.pi / 12.0)  # Tmin = -15°C, Tmax = +2°C
    ghi = np.maximum(0.0, 850.0 * np.sin((hours - 6) * np.pi / 12.0))
    ghi[(hours < 6) | (hours > 18)] = 0.0

    climate_recs = []
    for h in range(24):
        climate_recs.append({
            "month": 1,
            "day": 15,
            "hour": h,
            "dry_bulb_temp_c": float(t_out[h]),
            "relative_humidity_pct": 35.0,
            "solar_ghi_w_m2": float(ghi[h]),
            "wind_speed_m_s": 3.5
        })

    sim = simulate_shelter_thermal_dynamics(
        geometry=geom,
        wall_mat_id="trombe_wall_mass",
        wall_thickness_cm=30.0,
        roof_mat_id="roof_insulated_timber_deck",
        glazing_mat_id="glazing_double",
        insulation_mat_id="insulation_sheep_wool",
        insulation_thickness_cm=7.5,
        climate_records=climate_recs,
        thermal_mass_level="high",
        lat_deg=34.1526,
        lon_deg=77.5771,
        day_of_year=15
    )

    # Assert daytime solar capture significantly lifts the shelter temperature (~15°C above outdoor ambient)
    assert sim["max_t_indoor"] > 6.0  # Compared to peak outdoor +2°C and mean -6.5°C
    # Assert thermal mass and insulation retain heat ~15°C warmer than the -15°C nighttime extreme
    assert sim["min_t_indoor"] > -2.0  # Maintained well above outdoor sub-zero extreme (-15°C)
    # Assert solar capture metrics are populated
    assert sim["total_daily_solar_captured_kwh"] > 5.0
    assert sim["total_daily_heat_loss_kwh"] > 3.0
    assert len(sim["q_wall_watts"]) == 24
    assert len(sim["q_roof_watts"]) == 24
    assert len(sim["q_solar_watts"]) == 24


def test_tvi_ladakh_cold_and_solar_dimensions():
    """Verify that Ladakh TVI evaluates high Cold Vulnerability and High Solar Potential."""
    tvi = calculate_state_tvi("Ladakh")
    assert tvi is not None
    assert tvi["state_name"] == "Ladakh"
    assert tvi["cold_vulnerability_score"] >= 80.0
    assert tvi["solar_potential_score"] >= 85.0
    assert "South-facing solar aperture" in tvi["passive_priorities"][0]
