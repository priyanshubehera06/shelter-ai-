import pytest
from engine.geolocation import (
    get_ip_location,
    fetch_live_climate_profile,
    classify_climate_zone,
    recommend_shelter_preset,
    auto_detect_location_and_data
)
from engine.climate import get_climate_profile

def test_ip_location():
    loc = get_ip_location()
    assert loc is not None
    assert "lat" in loc
    assert "lon" in loc
    assert "city" in loc

def test_live_climate_fetch():
    records = fetch_live_climate_profile(20.27, 85.83)
    if records:
        assert len(records) == 24
        assert "dry_bulb_temp_c" in records[0]
        assert "relative_humidity_pct" in records[0]
        assert "solar_ghi_w_m2" in records[0]

def test_climate_classification():
    records_hot_arid = [{"dry_bulb_temp_c": 40.0, "relative_humidity_pct": 30.0, "solar_ghi_w_m2": 800, "wind_speed_m_s": 3} for _ in range(24)]
    assert classify_climate_zone(records_hot_arid) == "Hot & Arid"

    records_cold = [{"dry_bulb_temp_c": 5.0, "relative_humidity_pct": 40.0, "solar_ghi_w_m2": 400, "wind_speed_m_s": 3} for _ in range(24)]
    assert classify_climate_zone(records_cold) == "Cold & High-Altitude"

def test_shelter_presets():
    preset = recommend_shelter_preset("Hot & Arid")
    assert preset["wall"] == "cseb_interlocking"
    assert preset["thickness"] == 25.0

def test_full_auto_detect():
    data = auto_detect_location_and_data()
    assert data["status"] == "success"
    assert "location_name" in data
    assert len(data["climate_records"]) == 24

def test_climate_profile_auto_integration():
    data = auto_detect_location_and_data()
    # Test fallback & current_location handling
    records = get_climate_profile("current_location", month=5)
    assert len(records) == 24

def test_major_indian_cities():
    from engine.geolocation import MAJOR_INDIAN_CITIES
    assert len(MAJOR_INDIAN_CITIES) >= 30
    assert "Mumbai, Maharashtra (Hot & Humid)" in MAJOR_INDIAN_CITIES
    assert "Bengaluru, Karnataka (Temperate)" in MAJOR_INDIAN_CITIES

    records_mumbai = get_climate_profile("Mumbai, Maharashtra (Hot & Humid)", month=5)
    assert len(records_mumbai) == 24

def test_city_state_ut_search():
    from engine.geolocation import get_location_options
    
    # Search by state name
    kerala_opts = get_location_options("Kerala")
    assert any("Kochi" in opt or "Thiruvananthapuram" in opt for opt in kerala_opts)

    # Search by Union Territory
    ut_opts = get_location_options("Ladakh")
    assert any("Leh" in opt or "Kargil" in opt for opt in ut_opts)

    # Search by City name
    jaipur_opts = get_location_options("Jaipur")
    assert any("Jaipur" in opt for opt in jaipur_opts)
