import pytest
from engine.geometry import ShelterGeometry
from visualization.shelter_3d import create_plotly_3d_shelter, get_material_colors, calculate_surface_thermal_color
import numpy as np

def test_user_example_calculations():
    """
    Test calculations against the specification example:
    Input: Length: 6m, Width: 4m, Height: 3m, Window ratio: 20%, Orientation: 90°
    Output: Floor area: 24 m², Volume: 72 m³, Wall area: 60 m², Window area: 12 m², Roof area: 24 m²
    """
    geom = ShelterGeometry(
        length_m=6.0,
        width_m=4.0,
        height_m=3.0,
        roof_type="flat",
        roof_pitch_deg=0.0,
        wwr_pct=20.0,
        overhang_m=0.0,
        orientation_deg=90.0
    )
    
    assert geom.floor_area() == 24.0
    assert geom.volume() == 72.0
    assert geom.gross_wall_area() == 60.0
    assert geom.window_area() == 12.0
    assert geom.roof_area() == 24.0
    assert geom.surface_to_volume_ratio() == pytest.approx((60.0 + 24.0) / 72.0, 0.01)
    assert geom.orientation == 90.0

def test_geometry_openings_and_ratios():
    geom = ShelterGeometry(
        length_m=6.0,
        width_m=4.0,
        height_m=2.8,
        door_width_m=0.9,
        door_height_m=2.1,
        door_count=1,
        wwr_pct=15.0
    )
    assert geom.door_area() == pytest.approx(0.9 * 2.1, 0.01)
    assert geom.ventilation_area() > 0.0
    assert geom.total_openings_area() > geom.window_area()
    assert geom.net_wall_area() < geom.gross_wall_area()
    assert 0.0 < geom.opening_to_wall_ratio() < 1.0

def test_generate_design_variants():
    designs = ShelterGeometry.generate_design_variants(target_floor_area_m2=24.0)
    assert len(designs) >= 3
    assert designs[0].floor_area() == pytest.approx(24.0, 0.5)
    # Check that variants have varied dimensions
    dim_strings = [d.dimensions_str() for d in designs]
    assert len(set(dim_strings)) == len(dim_strings)

def test_geometry_from_occupants():
    geom = ShelterGeometry.from_occupants(occupants=4, standard_m2_per_person=3.5)
    assert geom.floor_area() >= 14.0
    assert geom.length > geom.width
    assert geom.volume() > 30.0

def test_roof_types():
    geom_pitched = ShelterGeometry(length_m=6, width_m=4, height_m=2.8, roof_type="pitched", roof_pitch_deg=15.0)
    assert geom_pitched.roof_height_delta() > 0.3
    
    geom_monoslope = ShelterGeometry(length_m=6, width_m=4, height_m=2.8, roof_type="monoslope", roof_pitch_deg=15.0)
    assert geom_monoslope.roof_height_delta() > 0.5
    
    geom_flat = ShelterGeometry(length_m=6, width_m=4, height_m=2.8, roof_type="flat", roof_pitch_deg=0.0)
    assert geom_flat.roof_height_delta() == 0.15

def test_plotly_3d_architectural_view():
    geom = ShelterGeometry(length_m=6, width_m=4, height_m=2.8, roof_type="pitched", roof_pitch_deg=15.0, wwr_pct=15.0)
    fig = create_plotly_3d_shelter(geom, wall_mat="cseb_interlocking", roof_mat="roof_cgi_insulated", view_mode="architectural", hour_of_day=12)
    assert len(fig.data) >= 8

def test_plotly_3d_thermal_heatmap_view():
    geom = ShelterGeometry(length_m=6, width_m=4, height_m=2.8, roof_type="monoslope", roof_pitch_deg=12.0)
    fig = create_plotly_3d_shelter(geom, wall_mat="eps_sandwich", roof_mat="roof_concrete_slab", view_mode="thermal_heatmap", hour_of_day=14, solar_ghi=950.0)
    assert len(fig.data) >= 8

def test_surface_thermal_color():
    color, temp = calculate_surface_thermal_color(np.array([0, 0, 1]), np.array([0, 0, 1]), base_temp=30.0, max_ghi=900.0)
    assert "rgb" in color
    assert temp >= 30.0
