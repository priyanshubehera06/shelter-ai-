import pytest
import numpy as np
from engine.geometry import ShelterGeometry
from visualization.shelter_3d import (
    create_plotly_3d_shelter,
    get_material_colors,
    calculate_surface_thermal_color,
    calculate_solar_position,
    get_solar_vector,
    get_camera_preset_dict,
    rotate_points_z
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
    
    geom_hipped = ShelterGeometry(length_m=6, width_m=4, height_m=2.8, roof_type="hipped", roof_pitch_deg=20.0)
    assert geom_hipped.roof_height_delta() > 0.5

    geom_flat = ShelterGeometry(length_m=6, width_m=4, height_m=2.8, roof_type="flat", roof_pitch_deg=0.0)
    assert geom_flat.roof_height_delta() == 0.15

def test_noaa_solar_astronomy():
    # Test solar position at noon
    alt_noon, az_noon, is_day_noon = calculate_solar_position(lat_deg=21.46, lon_deg=83.98, day_of_year=135, hour_of_day=12.0)
    assert alt_noon > 45.0
    assert is_day_noon is True
    
    # Test solar position at midnight
    alt_night, az_night, is_day_night = calculate_solar_position(lat_deg=21.46, lon_deg=83.98, day_of_year=135, hour_of_day=0.0)
    assert alt_night == 0.0
    assert is_day_night is False
    
    # Solar vector
    vec = get_solar_vector(alt_noon, az_noon)
    assert np.linalg.norm(vec) == pytest.approx(1.0, 1e-4)

def test_rotate_points():
    xs, ys, zs = [1.0, 0.0], [0.0, 1.0], [2.0, 2.0]
    rx, ry, rz = rotate_points_z(xs, ys, zs, angle_deg=90.0, cx=0.0, cy=0.0)
    assert len(rx) == 2
    assert rz == zs

def test_camera_presets():
    presets = ["Isometric", "Front (South)", "Side (East)", "Top (Plan)", "North Elevation"]
    for p in presets:
        cam = get_camera_preset_dict(p)
        assert "eye" in cam
        assert "center" in cam

def test_plotly_3d_all_view_modes():
    geom = ShelterGeometry(length_m=7.0, width_m=4.5, height_m=3.0, roof_type="pitched", roof_pitch_deg=18.0, wwr_pct=20.0, overhang_m=0.8, orientation_deg=45.0)
    modes = ["architectural", "solar_shading", "thermal_heatmap", "ventilation", "heat_flow", "exploded"]
    
    sim_dummy = {
        "q_roof": [250.0] * 24,
        "q_wall": [150.0] * 24,
        "q_solar": [120.0] * 24,
        "q_vent": [80.0] * 24,
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

def test_pyvista_3d_all_view_modes():
    from visualization.shelter_3d import (
        create_pyvista_3d_shelter,
        build_parametric_walls,
        build_parametric_roof,
        build_ground_and_compass,
        build_solar_path_and_sun,
        build_ground_shadow_projection,
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
