import pytest
import pandas as pd
from engine.climate import (
    load_climate_dataset,
    validate_climate_data,
    standardize_climate_dataframe,
    get_climate_profile,
    calculate_psychrometrics,
    calculate_degree_days,
)


def test_load_sample_climate_dataset():
    df = load_climate_dataset()
    assert not df.empty
    assert len(df) >= 24
    for col in ["datetime", "temperature", "humidity", "solar_radiation", "wind_speed", "wind_direction"]:
        assert col in df.columns


def test_validate_climate_data():
    df = load_climate_dataset()
    is_valid, errors = validate_climate_data(df)
    assert is_valid
    assert len(errors) == 0


def test_validate_invalid_climate_data():
    invalid_df = pd.DataFrame({"temperature": [150.0, -100.0]})
    is_valid, errors = validate_climate_data(invalid_df)
    assert not is_valid
    assert len(errors) > 0


def test_get_climate_profile():
    records = get_climate_profile("sample_location", month=5)
    assert len(records) == 24
    for r in records:
        assert "dry_bulb_temp_c" in r
        assert "relative_humidity_pct" in r
        assert "solar_ghi_w_m2" in r


def test_psychrometrics():
    p = calculate_psychrometrics(t_db=30.0, rh=50.0)
    assert "dew_point_c" in p
    assert "wet_bulb_c" in p
    assert "enthalpy_kj_kg" in p
    assert p["dew_point_c"] < 30.0
    assert p["wet_bulb_c"] < 30.0
