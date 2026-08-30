"""
shelter_3d.py — Parametric 3D Climate-Aware Digital Twin Engine for Shelter-AI.
Standalone 3D geometric mesh builder and solar/thermal visualization.

Features:
- Parametric structural geometry (Length, Width, Height, Wall Thickness, Orientation)
- Roof systems (Gable Pitched, Monoslope Shed, Hipped, Flat Slab) with variable pitch & overhang eaves
- Openings (Parametric glazed panes, frames, entrance door, structural corner posts)
- Engineering coordinate system & compact 3D Cardinal Compass (North indicator)
- Astronomical solar positioning (NOAA solar altitude & azimuth from lat/lon/day/time)
- Dynamic ground shadow footprint projection
- Multi-mode engineering visualization:
    1. Architectural Digital Twin (Realistic materials, dimensions, structural components)
    2. Solar Exposure & Shading View (Incident solar beam, shadow footprint, shading factor)
    3. Modeled Thermal Load View (Sol-Air & component heat fluxes from thermal simulation)
    4. Conceptual Ventilation View (Wind streamlines & opening vectors from wind speed/direction)
    5. Exploded Structural View (Separated envelope layers: slab, walls, roof)
- Camera preset views (Isometric, Front, Side, Top/Plan, North Elevation)
"""

import math
import os
import tempfile
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import plotly.graph_objects as go

from engine.geometry import ShelterGeometry
from engine.solar import (
    calculate_solar_position,
    get_solar_vector,
    calculate_surface_thermal_color,
    MATERIAL_SPECS,
    get_material_colors
)

# Optional PyVista import for desktop / standalone offline visualizer
try:
    import pyvista as pv
    pv.OFF_SCREEN = True
except ImportError:
    pv = None


# ==============================================================================
# 3. 3D ROTATION & GEOMETRIC COORDINATE HELPERS
# ==============================================================================

def rotate_points_z(xs, ys, zs, angle_deg, cx, cy):
    if angle_deg % 360.0 == 0.0:
        return xs, ys, zs
    rad = math.radians(-angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    out_x, out_y, out_z = [], [], []
    for x, y, z in zip(xs, ys, zs):
        dx, dy = x - cx, y - cy
        out_x.append(cx + dx * cos_a - dy * sin_a)
        out_y.append(cy + dx * sin_a + dy * cos_a)
        out_z.append(z)
    return out_x, out_y, out_z


def rotate_mesh_z(mesh: pv.PolyData, angle_deg: float, cx: float, cy: float) -> pv.PolyData:
    if angle_deg % 360.0 == 0.0 or mesh.n_points == 0:
        return mesh
    m = mesh.copy()
    m.translate((-cx, -cy, 0.0), inplace=True)
    m.rotate_z(-angle_deg, inplace=True)
    m.translate((cx, cy, 0.0), inplace=True)
    return m


# ==============================================================================
# 4. PYVISTA PARAMETRIC SHELTER MESH BUILDERS
# ==============================================================================

def create_box_mesh(bounds: Tuple[float, float, float, float, float, float]) -> pv.PolyData:
    xmin, xmax, ymin, ymax, zmin, zmax = bounds
    if xmax <= xmin or ymax <= ymin or zmax <= zmin:
        return pv.PolyData()
    return pv.Box(bounds=(xmin, xmax, ymin, ymax, zmin, zmax)).triangulate()


def build_parametric_walls(geometry: ShelterGeometry, wall_thickness: float, wwr: float, door_w: float = 0.9, door_h: float = 2.1) -> Tuple[pv.PolyData, pv.PolyData, pv.PolyData, pv.PolyData]:
    L = geometry.length
    W = geometry.width
    H = geometry.height
    t = max(0.12, wall_thickness)
    
    wall_blocks = []
    win_blocks = []
    frame_blocks = []
    door_blocks = []
    
    door_cx = L / 2.0
    door_x0 = max(0.3, door_cx - door_w / 2.0)
    door_x1 = min(L - 0.3, door_cx + door_w / 2.0)
    
    # South Wall (Front)
    wall_blocks.append(create_box_mesh((0, door_x0, 0, t, 0, H)))
    wall_blocks.append(create_box_mesh((door_x1, L, 0, t, 0, H)))
    wall_blocks.append(create_box_mesh((door_x0, door_x1, 0, t, door_h, H)))
    door_blocks.append(create_box_mesh((door_x0 + 0.02, door_x1 - 0.02, t * 0.2, t * 0.8, 0.02, door_h - 0.02)))
    
    # North Wall (Back)
    if wwr > 0.05:
        win_w = min(1.5, L * 0.35 * (wwr / 0.15))
        win_h = min(1.2, H * 0.45)
        win_z0 = H * 0.35
        wx0 = L / 2.0 - win_w / 2.0
        wx1 = L / 2.0 + win_w / 2.0
        wall_blocks.append(create_box_mesh((0, wx0, W - t, W, 0, H)))
        wall_blocks.append(create_box_mesh((wx1, L, W - t, W, 0, H)))
        wall_blocks.append(create_box_mesh((wx0, wx1, W - t, W, 0, win_z0)))
        wall_blocks.append(create_box_mesh((wx0, wx1, W - t, W, win_z0 + win_h, H)))
        win_blocks.append(create_box_mesh((wx0 + 0.03, wx1 - 0.03, W - t * 0.6, W - t * 0.4, win_z0 + 0.03, win_z0 + win_h - 0.03)))
        frame_blocks.append(create_box_mesh((wx0, wx1, W - t * 0.8, W - t * 0.2, win_z0, win_z0 + win_h)))
    else:
        wall_blocks.append(create_box_mesh((0, L, W - t, W, 0, H)))
        
    # West Wall (Left)
    wall_blocks.append(create_box_mesh((0, t, t, W - t, 0, H)))
    # East Wall (Right)
    wall_blocks.append(create_box_mesh((L - t, L, t, W - t, 0, H)))
    
    def merge_all(blocks):
        valid = [b for b in blocks if b.n_points > 0]
        if not valid: return pv.PolyData()
        res = valid[0].copy()
        for b in valid[1:]:
            res = res.merge(b)
        return res

    return merge_all(wall_blocks), merge_all(door_blocks), merge_all(win_blocks), merge_all(frame_blocks)


def build_parametric_roof(geometry: ShelterGeometry, roof_thickness: float = 0.08) -> Tuple[pv.PolyData, pv.PolyData, float]:
    L = geometry.length
    W = geometry.width
    H = geometry.height
    pitch_deg = geometry.roof_pitch
    roof_type = geometry.roof_type.lower()
    overhang = geometry.overhang
    th = max(0.04, roof_thickness)
    
    e_x0 = -overhang
    e_x1 = L + overhang
    e_y0 = -overhang
    e_y1 = W + overhang
    
    rad = math.radians(pitch_deg)
    delta_h = geometry.roof_height_delta()
    peak_z = H + delta_h
    
    roof_blocks = []
    shading_blocks = []
    
    if roof_type == 'pitched' and pitch_deg > 0:
        ridge_y = W / 2.0
        eave_z = H - overhang * math.tan(rad)
        
        # South slope
        s_mesh = pv.PolyData(np.array([
            [e_x0, e_y0, eave_z],
            [e_x1, e_y0, eave_z],
            [e_x1, ridge_y, peak_z],
            [e_x0, ridge_y, peak_z]
        ]), faces=np.array([4, 0, 1, 2, 3])).extrude([0, 0, -th], capping=True)
        roof_blocks.append(s_mesh)
        
        # North slope
        n_mesh = pv.PolyData(np.array([
            [e_x0, ridge_y, peak_z],
            [e_x1, ridge_y, peak_z],
            [e_x1, e_y1, eave_z],
            [e_x0, e_y1, eave_z]
        ]), faces=np.array([4, 0, 1, 2, 3])).extrude([0, 0, -th], capping=True)
        roof_blocks.append(n_mesh)
        
        # Triangular Gable End Walls
        g_w = pv.PolyData(np.array([[0, 0, H], [0, W, H], [0, ridge_y, peak_z]]), faces=np.array([3, 0, 1, 2])).extrude([0.15, 0, 0], capping=True)
        g_e = pv.PolyData(np.array([[L, 0, H], [L, W, H], [L, ridge_y, peak_z]]), faces=np.array([3, 0, 2, 1])).extrude([-0.15, 0, 0], capping=True)
        roof_blocks.extend([g_w, g_e])
        
        if overhang > 0.1:
            shading_blocks.append(create_box_mesh((e_x0, e_x1, e_y0 - 0.04, e_y0, eave_z - 0.1, eave_z + 0.02)))
            shading_blocks.append(create_box_mesh((e_x0, e_x1, e_y1, e_y1 + 0.04, eave_z - 0.1, eave_z + 0.02)))
            
    elif roof_type == 'monoslope' and pitch_deg > 0:
        z_low = H - overhang * math.tan(rad)
        z_high = H + (W + overhang) * math.tan(rad)
        peak_z = z_high
        m_mesh = pv.PolyData(np.array([
            [e_x0, e_y0, z_low],
            [e_x1, e_y0, z_low],
            [e_x1, e_y1, z_high],
            [e_x0, e_y1, z_high]
        ]), faces=np.array([4, 0, 1, 2, 3])).extrude([0, 0, -th], capping=True)
        roof_blocks.append(m_mesh)
        
        side_w = pv.PolyData(np.array([[0, 0, H], [0, W, H], [0, W, H + W * math.tan(rad)], [0, 0, H]]), faces=np.array([4, 0, 1, 2, 3])).extrude([0.15, 0, 0], capping=True)
        side_e = pv.PolyData(np.array([[L, 0, H], [L, W, H], [L, W, H + W * math.tan(rad)], [L, 0, H]]), faces=np.array([4, 0, 3, 2, 1])).extrude([-0.15, 0, 0], capping=True)
        roof_blocks.extend([side_w, side_e])
    else:
        peak_z = H + 0.15
        roof_blocks.append(create_box_mesh((e_x0, e_x1, e_y0, e_y1, H, H + 0.15)))
        
    def merge_all(blocks):
        valid = [b for b in blocks if b.n_points > 0]
        if not valid: return pv.PolyData()
        res = valid[0].copy()
        for b in valid[1:]:
            res = res.merge(b)
        return res
        
    return merge_all(roof_blocks), merge_all(shading_blocks), peak_z


def build_ground_and_compass(L: float, W: float, cx: float, cy: float, radius: float = 12.0) -> Tuple[pv.PolyData, pv.PolyData, pv.PolyData]:
    ground = pv.Cylinder(center=(cx, cy, -0.06), direction=(0, 0, 1), radius=radius, height=0.10, resolution=64).triangulate()
    grid_lines = []
    step = 2.0
    for x in np.arange(cx - radius * 0.8, cx + radius * 0.8 + 0.1, step):
        y_max = math.sqrt(max(0.1, (radius * 0.85)**2 - (x - cx)**2))
        grid_lines.append(pv.Line((x, cy - y_max, -0.005), (x, cy + y_max, -0.005)))
    for y in np.arange(cy - radius * 0.8, cy + radius * 0.8 + 0.1, step):
        x_max = math.sqrt(max(0.1, (radius * 0.85)**2 - (y - cy)**2))
        grid_lines.append(pv.Line((cx - x_max, y, -0.005), (cx + x_max, y, -0.005)))
        
    grid_mesh = pv.PolyData()
    for gl in grid_lines:
        grid_mesh = grid_mesh.merge(gl)
        
    comp_x = cx - radius * 0.65
    comp_y = cy - radius * 0.65
    comp_z = 0.02
    
    ring = pv.Disc(center=(comp_x, comp_y, comp_z), inner=0.35, outer=0.65, r_res=2, c_res=32)
    n_arrow = pv.Arrow(start=(comp_x, comp_y, comp_z + 0.02), direction=(0, 1, 0), tip_length=0.4, tip_radius=0.12, shaft_radius=0.04, scale=1.0)
    e_arrow = pv.Arrow(start=(comp_x, comp_y, comp_z + 0.02), direction=(1, 0, 0), tip_length=0.4, tip_radius=0.10, shaft_radius=0.03, scale=0.8)
    compass_mesh = ring.merge(n_arrow).merge(e_arrow)
    
    return ground, grid_mesh, compass_mesh


def build_solar_path_and_sun(latitude: float, longitude: float, day_of_year: int, hour_of_day: float, cx: float, cy: float, peak_z: float, sun_dist: float = 12.0):
    sol_alt, sol_az, is_daylight = calculate_solar_position(latitude, longitude, day_of_year, hour_of_day)
    sun_dir = get_solar_vector(sol_alt, sol_az)
    sun_x = cx + sun_dist * sun_dir[0]
    sun_y = cy + sun_dist * sun_dir[1]
    sun_z = peak_z * 0.5 + sun_dist * max(0.05, sun_dir[2])
    sun_sphere = pv.Sphere(radius=0.42, center=(sun_x, sun_y, sun_z), theta_resolution=24, phi_resolution=24)
    
    arc_points = []
    for h_step in np.linspace(5.5, 18.5, 35):
        s_alt, s_az, _ = calculate_solar_position(latitude, longitude, day_of_year, h_step)
        if s_alt > 0.0:
            s_vec = get_solar_vector(s_alt, s_az)
            arc_points.append([cx + sun_dist * s_vec[0], cy + sun_dist * s_vec[1], peak_z * 0.5 + sun_dist * max(0.02, s_vec[2])])
            
    if len(arc_points) > 2:
        arc_spline = pv.Spline(np.array(arc_points), n_points=70)
        arc_tube = arc_spline.tube(radius=0.03)
    else:
        arc_tube = pv.PolyData()
        
    return sun_sphere, arc_tube, sun_dir, sol_alt, sol_az, is_daylight


def build_ground_shadow_projection(geometry: ShelterGeometry, sun_dir: np.ndarray, sol_alt: float, cx: float, cy: float, peak_z: float) -> pv.PolyData:
    if sol_alt < 4.0: return pv.PolyData()
    L, W, H = geometry.length, geometry.width, peak_z
    orientation = geometry.orientation
    tan_alt = max(0.08, math.tan(math.radians(sol_alt)))
    shd_len = H / tan_alt
    shd_dx = -sun_dir[0] * shd_len
    shd_dy = -sun_dir[1] * shd_len
    bx, by, _ = rotate_points_z([0, L, L, 0], [0, 0, W, W], [0, 0, 0, 0], orientation, cx, cy)
    pts = np.array([
        [bx[0], by[0], 0.005],
        [bx[1], by[1], 0.005],
        [bx[1] + shd_dx, by[1] + shd_dy, 0.005],
        [bx[2] + shd_dx, by[2] + shd_dy, 0.005],
        [bx[3] + shd_dx, by[3] + shd_dy, 0.005],
        [bx[0] + shd_dx, by[0] + shd_dy, 0.005],
    ])
    faces = np.array([3, 0, 1, 2, 3, 0, 2, 3, 3, 0, 3, 4, 3, 0, 4, 5])
    return pv.PolyData(pts, faces=faces)


# ==============================================================================
# 5. MAIN PYVISTA 3D DIGITAL TWIN SCENE GENERATOR
# ==============================================================================

def create_pyvista_3d_shelter(
    geometry: ShelterGeometry,
    wall_mat: str = 'cseb_interlocking',
    roof_mat: str = 'roof_cgi_insulated',
    view_mode: str = 'architectural',
    hour_of_day: float = 12.0,
    solar_ghi: float = 850.0,
    occupants: int = 4,
    show_interior: bool = True,
    latitude: float = 21.4669,
    longitude: float = 83.9812,
    day_of_year: int = 135,
    wind_speed: float = 3.5,
    wind_direction_deg: float = 225.0,
    sim_results: Optional[Dict[str, Any]] = None,
    exploded_offset: float = 0.0,
    component_visibility: Optional[Dict[str, bool]] = None
) -> pv.Plotter:
    L = geometry.length
    W = geometry.width
    H = geometry.height
    orientation = geometry.orientation
    wall_thick = geometry.wall_thickness
    wwr = geometry.wwr
    
    cx = L / 2.0
    cy = W / 2.0
    
    vis = {
        'roof': True, 'walls': True, 'windows': True, 'door': True,
        'shading': True, 'ground': True, 'compass': True, 'sun_path': True, 'shadow': True,
    }
    if component_visibility: vis.update(component_visibility)
        
    plotter = pv.Plotter(window_size=[960, 580], lighting='none')
    plotter.set_background('#0a0f18', top='#141f2e')
    
    wall_mesh, door_mesh, win_mesh, frame_mesh = build_parametric_walls(geometry=geometry, wall_thickness=wall_thick, wwr=wwr)
    roof_mesh, shading_mesh, peak_z = build_parametric_roof(geometry=geometry, roof_thickness=0.08)
    slab_mesh = create_box_mesh((-0.08, L + 0.08, -0.08, W + 0.08, -0.15, 0.0))
    
    sun_dist = max(12.0, max(L, W) * 2.2)
    sun_mesh, arc_tube, sun_dir, sol_alt, sol_az, is_day = build_solar_path_and_sun(
        latitude, longitude, day_of_year, hour_of_day, cx, cy, peak_z, sun_dist=sun_dist
    )
    
    if is_day and sol_alt > 0.5:
        sun_light = pv.Light(
            position=(cx + sun_dist * sun_dir[0], cy + sun_dist * sun_dir[1], peak_z * 0.5 + sun_dist * sun_dir[2]),
            focal_point=(cx, cy, H * 0.5), color='#fff8e7', intensity=0.95, positional=True
        )
        plotter.add_light(sun_light)
        
    ambient_light = pv.Light(position=(cx, cy, peak_z + 10.0), focal_point=(cx, cy, 0), color='#c8d6e5', intensity=0.45, positional=False)
    plotter.add_light(ambient_light)
    fill_light = pv.Light(position=(cx - 8.0, cy - 8.0, 4.0), focal_point=(cx, cy, H * 0.5), color='#7f8c8d', intensity=0.25, positional=True)
    plotter.add_light(fill_light)
    
    wall_hex, roof_hex, wall_name, roof_name = get_material_colors(wall_mat, roof_mat)
    wall_spec = MATERIAL_SPECS.get(str(wall_mat).lower(), {})
    roof_spec = MATERIAL_SPECS.get(str(roof_mat).lower(), {})
    
    wall_z_off = exploded_offset * 0.4
    roof_z_off = exploded_offset * 1.0
    
    wall_mesh_r = rotate_mesh_z(wall_mesh, orientation, cx, cy)
    door_mesh_r = rotate_mesh_z(door_mesh, orientation, cx, cy)
    win_mesh_r = rotate_mesh_z(win_mesh, orientation, cx, cy)
    frame_mesh_r = rotate_mesh_z(frame_mesh, orientation, cx, cy)
    roof_mesh_r = rotate_mesh_z(roof_mesh, orientation, cx, cy)
    shading_mesh_r = rotate_mesh_z(shading_mesh, orientation, cx, cy)
    slab_mesh_r = rotate_mesh_z(slab_mesh, orientation, cx, cy)
    
    if wall_z_off > 0:
        for m in [wall_mesh_r, door_mesh_r, win_mesh_r, frame_mesh_r]:
            if m.n_points > 0: m.translate((0, 0, wall_z_off), inplace=True)
    if roof_z_off > 0:
        for m in [roof_mesh_r, shading_mesh_r]:
            if m.n_points > 0: m.translate((0, 0, roof_z_off), inplace=True)
            
    if view_mode == 'thermal_heatmap':
        base_t = 30.0
        if sim_results and 't_indoor' in sim_results:
            h_idx = max(0, min(23, int(hour_of_day)))
            base_t = sim_results['t_indoor'][h_idx]
        wall_render_color, _ = calculate_surface_thermal_color(
            normal_vector=np.array([math.cos(math.radians(orientation)), math.sin(math.radians(orientation)), 0]),
            sun_vector=sun_dir, base_temp=base_t, max_ghi=solar_ghi
        )
        roof_render_color, _ = calculate_surface_thermal_color(
            normal_vector=np.array([0, 0, 1]), sun_vector=sun_dir, base_temp=base_t + 2.0, max_ghi=solar_ghi
        )
    else:
        wall_render_color = wall_hex
        roof_render_color = roof_hex
        
    if vis.get('walls', True) and slab_mesh_r.n_points > 0:
        plotter.add_mesh(slab_mesh_r, color='#2c3e50', smooth_shading=True, ambient=0.25, diffuse=0.85, specular=0.1)
    if vis.get('walls', True) and wall_mesh_r.n_points > 0:
        plotter.add_mesh(wall_mesh_r, color=wall_render_color, smooth_shading=True, ambient=wall_spec.get('ambient', 0.30), diffuse=wall_spec.get('diffuse', 0.85), specular=wall_spec.get('specular', 0.10))
    if vis.get('roof', True) and roof_mesh_r.n_points > 0:
        plotter.add_mesh(roof_mesh_r, color=roof_render_color, smooth_shading=True, ambient=roof_spec.get('ambient', 0.25), diffuse=roof_spec.get('diffuse', 0.75), specular=roof_spec.get('specular', 0.35))
    if vis.get('shading', True) and shading_mesh_r.n_points > 0:
        plotter.add_mesh(shading_mesh_r, color='#1abc9c', smooth_shading=True, ambient=0.3, diffuse=0.8, specular=0.2)
    if vis.get('door', True) and door_mesh_r.n_points > 0:
        plotter.add_mesh(door_mesh_r, color='#5d4037', smooth_shading=True, ambient=0.3, diffuse=0.85, specular=0.2)
    if vis.get('windows', True) and win_mesh_r.n_points > 0:
        plotter.add_mesh(win_mesh_r, color='#38bdf8', opacity=0.65, smooth_shading=True, ambient=0.4, diffuse=0.6, specular=0.9)
    if vis.get('windows', True) and frame_mesh_r.n_points > 0:
        plotter.add_mesh(frame_mesh_r, color='#1e293b', smooth_shading=True, ambient=0.3, diffuse=0.7, specular=0.3)
        
    ground_rad = max(10.0, max(L, W) * 1.6)
    ground_disc, ground_grid, compass_mesh = build_ground_and_compass(L, W, cx, cy, radius=ground_rad)
    if vis.get('ground', True):
        plotter.add_mesh(ground_disc, color='#0f172a', smooth_shading=True, ambient=0.35, diffuse=0.65, specular=0.05)
        if ground_grid.n_points > 0:
            plotter.add_mesh(ground_grid, color='#1e293b', line_width=1.5, opacity=0.6)
    if vis.get('compass', True) and compass_mesh.n_points > 0:
        plotter.add_mesh(compass_mesh, color='#e74c3c', smooth_shading=True, ambient=0.4, diffuse=0.8)
        
    if vis.get('sun_path', True):
        if is_day and sun_mesh.n_points > 0:
            plotter.add_mesh(sun_mesh, color='#f1c40f', ambient=1.0, diffuse=0.0, specular=0.0)
        if arc_tube.n_points > 0:
            plotter.add_mesh(arc_tube, color='#e67e22', opacity=0.75, ambient=0.6)
            
    if vis.get('shadow', True) and is_day and sol_alt > 5.0 and exploded_offset == 0.0:
        shadow_mesh = build_ground_shadow_projection(geometry, sun_dir, sol_alt, cx, cy, peak_z)
        if shadow_mesh.n_points > 0:
            plotter.add_mesh(shadow_mesh, color='#020617', opacity=0.70, smooth_shading=True)
            
    if view_mode == 'ventilation':
        w_rad = math.radians(wind_direction_deg)
        w_vec = np.array([math.sin(w_rad), math.cos(w_rad), 0.0])
        arrow_scale = max(1.5, min(4.5, wind_speed * 0.8))
        y_offsets = np.linspace(-W * 0.35, W * 0.35, 3)
        for dy in y_offsets:
            start_pt = np.array([cx - w_vec[0] * 5.0, cy + dy - w_vec[1] * 5.0, H * 0.45])
            mid_pt = np.array([cx, cy + dy * 0.5, H * 0.45])
            end_pt = np.array([cx + w_vec[0] * 5.0, cy + dy * 0.5 + w_vec[1] * 5.0, H * 0.45])
            stream_spline = pv.Spline(np.array([start_pt, mid_pt, end_pt]), n_points=30)
            plotter.add_mesh(stream_spline.tube(radius=0.06), color='#00e5ff', opacity=0.85, ambient=0.5)
            entry_arr = pv.Arrow(start=start_pt, direction=w_vec, scale=arrow_scale * 0.6)
            exit_arr = pv.Arrow(start=end_pt - w_vec * (arrow_scale * 0.6), direction=w_vec, scale=arrow_scale * 0.6)
            plotter.add_mesh(entry_arr, color='#00e5ff', ambient=0.6)
            plotter.add_mesh(exit_arr, color='#00b4d8', ambient=0.6)
    elif view_mode == 'solar_shading' and is_day:
        beam = pv.Line((cx + sun_dist * 0.9 * sun_dir[0], cy + sun_dist * 0.9 * sun_dir[1], peak_z * 0.5 + sun_dist * 0.9 * sun_dir[2]), (cx, cy, peak_z * 0.8))
        plotter.add_mesh(beam.tube(radius=0.04), color='#f39c12', opacity=0.85, ambient=0.8)
        
    plotter.camera_position = [(cx + max(L, W) * 2.2, cy - max(L, W) * 2.2, peak_z * 1.8), (cx, cy, H * 0.4), (0, 0, 1)]
    return plotter


# ==============================================================================
# 6. CAMERA PRESETS
# ==============================================================================

def set_pyvista_camera_preset(plotter: pv.Plotter, preset_name: str, geometry: ShelterGeometry):
    L, W, H = geometry.length, geometry.width, geometry.height
    cx, cy = L / 2.0, W / 2.0
    focal = (cx, cy, H * 0.4)
    dist = max(L, W) * 2.6
    
    if preset_name == 'Front (South)':
        plotter.camera_position = [(cx, cy - dist, H * 0.5), focal, (0, 0, 1)]
    elif preset_name == 'Side (East)':
        plotter.camera_position = [(cx + dist, cy, H * 0.5), focal, (0, 0, 1)]
    elif preset_name == 'Top (Plan)':
        plotter.camera_position = [(cx, cy, dist * 1.2), focal, (0, 1, 0)]
    elif preset_name == 'North Elevation':
        plotter.camera_position = [(cx, cy + dist, H * 0.5), focal, (0, 0, 1)]
    else:  # Isometric
        plotter.camera_position = [(cx + dist * 0.8, cy - dist * 0.8, H * 1.6), focal, (0, 0, 1)]


def get_camera_preset_dict(preset_name: str) -> Dict[str, Any]:
    presets = {
        'Isometric': dict(eye=dict(x=1.65, y=-1.65, z=1.25), center=dict(x=0, y=0, z=0), up=dict(x=0, y=0, z=1)),
        'Front (South)': dict(eye=dict(x=0.0, y=-2.5, z=0.4), center=dict(x=0, y=0, z=0), up=dict(x=0, y=0, z=1)),
        'Side (East)': dict(eye=dict(x=2.5, y=0.0, z=0.4), center=dict(x=0, y=0, z=0), up=dict(x=0, y=0, z=1)),
        'Top (Plan)': dict(eye=dict(x=0.0, y=0.0, z=3.0), center=dict(x=0, y=0, z=0), up=dict(x=0, y=1, z=0)),
        'North Elevation': dict(eye=dict(x=0.0, y=2.5, z=0.4), center=dict(x=0, y=0, z=0), up=dict(x=0, y=0, z=1)),
    }
    return presets.get(preset_name, presets['Isometric'])


# ==============================================================================
# 7. PYVISTA STANDALONE HTML EXPORTER
# ==============================================================================

def export_pyvista_3d_html(plotter: pv.Plotter) -> Optional[str]:
    """Exports PyVista 3D plotter scene to standalone interactive WebGL HTML string."""
    try:
        with tempfile.NamedTemporaryFile(suffix='.html', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        plotter.export_html(tmp_path)
        with open(tmp_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        try: os.remove(tmp_path)
        except Exception: pass
        return html_content
    except Exception:
        return None


# ==============================================================================
# 8. BACKWARD COMPATIBILITY: PLOTLY 3D GENERATOR
# ==============================================================================

def create_plotly_3d_shelter(
    geometry: ShelterGeometry,
    wall_mat: str = 'cseb_interlocking',
    roof_mat: str = 'roof_cgi_insulated',
    view_mode: str = 'architectural',
    hour_of_day: float = 12.0,
    solar_ghi: float = 850.0,
    occupants: int = 4,
    show_interior: bool = True,
    latitude: float = 21.4669,
    longitude: float = 83.9812,
    day_of_year: int = 135,
    wind_speed: float = 3.5,
    wind_direction_deg: float = 225.0,
    sim_results: Optional[Dict[str, Any]] = None,
    exploded_offset: float = 0.0
) -> go.Figure:
    L = geometry.length
    W = geometry.width
    H = geometry.height
    orientation = geometry.orientation
    cx = L / 2.0
    cy = W / 2.0
    
    sol_alt, sol_az, is_daytime = calculate_solar_position(latitude, longitude, day_of_year, hour_of_day)
    sun_dir = get_solar_vector(sol_alt, sol_az)
    wall_color, roof_color, wall_label, roof_label = get_material_colors(wall_mat, roof_mat)
    
    fig = go.Figure()
    margin = max(L, W) * 0.9
    gx = [-margin, L + margin, L + margin, -margin]
    gy = [-margin, -margin, W + margin, W + margin]
    gz = [-0.1, -0.1, -0.1, -0.1]
    fig.add_trace(go.Mesh3d(x=gx, y=gy, z=gz, i=[0, 0], j=[1, 2], k=[2, 3], color='#0f172a', opacity=0.9, name='Ground Plane'))
    
    wx = [0, L, L, 0, 0, L, L, 0]
    wy = [0, 0, W, W, 0, 0, W, W]
    wz = [0, 0, 0, 0, H, H, H, H]
    r_wx, r_wy, r_wz = rotate_points_z(wx, wy, wz, orientation, cx, cy)
    fig.add_trace(go.Mesh3d(
        x=r_wx, y=r_wy, z=r_wz,
        i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
        j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
        k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
        color=wall_color, opacity=0.85, name=f'Walls ({wall_label})'
    ))
    
    delta_h = geometry.roof_height_delta()
    roof_peak_z = H + delta_h
    overhang = geometry.overhang
    rx = [-overhang, L + overhang, L + overhang, -overhang, -overhang, L + overhang]
    ry = [-overhang, -overhang, W + overhang, W + overhang, cy, cy]
    rz = [H, H, H, H, roof_peak_z, roof_peak_z]
    r_rx, r_ry, r_rz = rotate_points_z(rx, ry, rz, orientation, cx, cy)
    
    fig.add_trace(go.Mesh3d(
        x=r_rx, y=r_ry, z=r_rz,
        i=[0, 1, 3, 2], j=[1, 5, 2, 4], k=[4, 4, 4, 5],
        color=roof_color, opacity=0.9, name=f'Roof ({roof_label})'
    ))
    
    sun_dist = max(L, W) * 2.0
    sun_x = cx + sun_dist * sun_dir[0]
    sun_y = cy + sun_dist * sun_dir[1]
    sun_z = roof_peak_z + sun_dist * max(0.05, sun_dir[2])
    
    if is_daytime:
        fig.add_trace(go.Scatter3d(
            x=[sun_x], y=[sun_y], z=[sun_z],
            mode='markers+text', name='Sun Position',
            marker=dict(size=12, color='#f1c40f')
        ))
        
    arc_xs, arc_ys, arc_zs = [], [], []
    for h_step in np.linspace(6.0, 18.0, 20):
        s_alt, s_az, _ = calculate_solar_position(latitude, longitude, day_of_year, h_step)
        if s_alt > 0.0:
            s_vec = get_solar_vector(s_alt, s_az)
            arc_xs.append(cx + sun_dist * s_vec[0])
            arc_ys.append(cy + sun_dist * s_vec[1])
            arc_zs.append(roof_peak_z + sun_dist * max(0.05, s_vec[2]))
            
    fig.add_trace(go.Scatter3d(
        x=arc_xs, y=arc_ys, z=arc_zs,
        mode='lines', name='Diurnal Solar Path',
        line=dict(color='#e67e22', width=3, dash='dash')
    ))
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False, title=''),
            camera=dict(eye=dict(x=1.65, y=-1.65, z=1.25)),
            aspectmode='data'
        ),
        margin=dict(l=5, r=5, t=25, b=5),
        template='plotly_dark'
    )
    return fig
