import pytest
from engine.geometry import ShelterGeometry


def test_geometry_math_standards():
    geom = ShelterGeometry(
        length_m=6.0,
        width_m=4.0,
        height_m=3.0,
        roof_type="flat",
        roof_pitch_deg=0.0,
        wwr_pct=20.0,
        overhang_m=0.0,
        orientation_deg=90.0,
    )
    assert geom.floor_area() == 24.0
    assert geom.gross_wall_area() == 60.0
    assert geom.window_area() == 12.0
    assert geom.roof_area() == 24.0
    assert geom.volume() == 72.0
    assert geom.surface_to_volume_ratio() == pytest.approx(84.0 / 72.0, 0.01)


def test_geometry_from_occupants():
    geom = ShelterGeometry.from_occupants(occupants=4, standard_m2_per_person=3.5)
    assert geom.floor_area() >= 14.0
    assert geom.volume() > 30.0


def test_generate_design_variants():
    designs = ShelterGeometry.generate_design_variants(target_floor_area_m2=24.0)
    assert len(designs) == 3
    assert designs[0].length == 6.0 and designs[0].width == 4.0
    assert designs[1].length == 8.0 and designs[1].width == 3.0
    assert designs[2].length == 6.0 and designs[2].width == 5.0
