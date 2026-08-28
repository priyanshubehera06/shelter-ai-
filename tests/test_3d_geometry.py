import pytest
import numpy as np
from engine.geometry import ShelterGeometry
from engine.solar import (
    get_material_colors,
    calculate_surface_thermal_color,
    calculate_solar_position,
    get_solar_vector
)
from visualization.shelter_3d import (
    create_plotly_3d_shelter,
    get_camera_preset_dict,
    rotate_points_z,
    pv
)

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
        length_m=7.0,
        width_m=5.0,
        height_m=3.2,
        roof_type="pitched",
        roof_pitch_deg=20.0,
        wwr_pct=15.0,
        overhang_m=0.6,
        orientation_deg=45.0
    )
    
    expected_gross_wall = 2 * (7.0 + 5.0) * 3.2
    assert geom.gross_wall_area() == pytest.approx(expected_gross_wall)
    assert geom.window_area() == pytest.approx(expected_gross_wall * 0.15)
    assert geom.net_wall_area() == pytest.approx(expected_gross_wall * (1.0 - 0.15))
    assert geom.roof_area() > 35.0  # Roof slope area > footprint

def test_solar_position_noaa():
    # Solar noon summer in Sambalpur (lat: 21.46, lon: 83.98)
    alt, az, is_day = calculate_solar_position(21.46, 83.98, day_of_year=135, hour_of_day=12.0)
    assert is_day is True
    assert alt > 70.0  # High noon altitude
    assert 0.0 <= az <= 360.0
    
    # Night time
    alt_night, _, is_day_night = calculate_solar_position(21.46, 83.98, day_of_year=135, hour_of_day=2.0)
    assert is_day_night is False
    assert alt_night == 0.0

def test_solar_vector_normalization():
    vec = get_solar_vector(altitude_deg=45.0, azimuth_deg=180.0)
    assert len(vec) == 3
    assert np.linalg.norm(vec) == pytest.approx(1.0, 1e-5)
    assert vec[2] > 0.0  # Upwards component

def test_material_color_specs():
    w_col, r_col, w_name, r_name = get_material_colors("cseb_interlocking", "roof_cgi_insulated")
    assert w_col.startswith("#")
    assert r_col.startswith("#")
    assert "Compressed Earth" in w_name
    assert "Insulated" in r_name

def test_camera_presets():
    presets = ["Isometric", "Front (South)", "Side (East)", "Top (Plan)", "North Elevation"]
    for p in presets:
        cam = get_camera_preset_dict(p)
        assert "eye" in cam
        assert "center" in cam

def test_coordinate_rotation():
    xs, ys, zs = [1.0, 0.0], [0.0, 1.0], [0.0, 0.0]
    rx, ry, rz = rotate_points_z(xs, ys, zs, angle_deg=90.0, cx=0.0, cy=0.0)
    assert rx[0] == pytest.approx(0.0, 1e-4)
    assert ry[0] == pytest.approx(-1.0, 1e-4)
    assert rx[1] == pytest.approx(1.0, 1e-4)
    assert ry[1] == pytest.approx(0.0, 1e-4)

def test_plotly_3d_all_view_modes():
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=3.0, roof_type="pitched", roof_pitch_deg=20.0, wwr_pct=20.0, overhang_m=0.5, orientation_deg=0.0)
    modes = ["architectural", "solar_shading", "thermal_heatmap", "ventilation", "exploded"]
    
    sim_dummy = {
        "u_roof": 0.45,
        "u_wall": 0.65,
        "u_glazing": 2.8,
        "t_indoor": [28.0] * 24,
        "t_sol_air": [35.0] * 24,
    }
    
    for mode in modes:
        fig = create_plotly_3d_shelter(
            geom,
            wall_mat="cseb_interlocking",
            roof_mat="roof_cgi_insulated",
            view_mode=mode,
            hour_of_day=13,
            sim_results=sim_dummy,
            exploded_offset=0.8 if mode == "exploded" else 0.0
        )
        assert len(fig.data) >= 3

@pytest.mark.skipif(pv is None, reason="PyVista not installed in lean environment")
def test_pyvista_3d_all_view_modes():
    from visualization.shelter_3d import (
        create_pyvista_3d_shelter,
        build_parametric_walls,
        build_parametric_roof,
        build_ground_and_compass,
        build_solar_path_and_sun,
        set_pyvista_camera_preset
    )
    geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8, roof_type="pitched", roof_pitch_deg=15.0, wwr_pct=15.0, overhang_m=0.5, orientation_deg=30.0)
    
    # Test Wall meshes
    wall_mesh, door_mesh, win_mesh, frame_mesh = build_parametric_walls(geom, wall_thickness=0.20, wwr=0.15)
    assert wall_mesh.n_points > 0
    assert door_mesh.n_points > 0
    
    # Test Roof mesh
    roof_mesh, shading_mesh, peak_z = build_parametric_roof(geom, roof_thickness=0.08)
    assert roof_mesh.n_points > 0
    assert peak_z > geom.height
    
    # Test Ground and compass
    ground_disc, ground_grid, compass_mesh = build_ground_and_compass(6.0, 4.0, 3.0, 2.0, radius=10.0)
    assert ground_disc.n_points > 0
    assert compass_mesh.n_points > 0
    
    # Test Solar path & sun
    sun_mesh, arc_tube, sun_dir, sol_alt, sol_az, is_day = build_solar_path_and_sun(21.46, 83.98, 135, 12.0, 3.0, 2.0, peak_z)
    assert sun_mesh.n_points > 0
    assert arc_tube.n_points > 0
    assert is_day is True
    
    # Test all view modes
    modes = ["architectural", "solar_shading", "thermal_heatmap", "ventilation", "exploded"]
    for m in modes:
        plotter = create_pyvista_3d_shelter(geom, view_mode=m, hour_of_day=12.0)
        assert plotter is not None
        set_pyvista_camera_preset(plotter, "Isometric", geom)
        set_pyvista_camera_preset(plotter, "Front (South)", geom)

def test_surface_thermal_color():
    color, temp = calculate_surface_thermal_color(np.array([0, 0, 1]), np.array([0, 0, 1]), base_temp=30.0, max_ghi=900.0)
    assert color.startswith("#")
    assert len(color) == 7
    assert temp >= 30.0
