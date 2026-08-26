import numpy as np
import pandas as pd
import plotly.graph_objects as go
from engine.geometry import ShelterGeometry

def get_material_colors(wall_mat, roof_mat):
    """
    Map envelope material identifiers to realistic 3D mesh HEX colors.
    """
    w_lower = str(wall_mat).lower()
    r_lower = str(roof_mat).lower()

    # Wall colors
    if "cseb" in w_lower or "ceb" in w_lower or "earth" in w_lower:
        wall_color = "#d35400"  # Terracotta / Earth red-orange
        wall_name = "Compressed Earth Block (CSEB)"
    elif "eps" in w_lower or "sandwich" in w_lower:
        wall_color = "#bdc3c7"  # Metallic Light Silver
        wall_name = "EPS Sandwich Panel"
    elif "aac" in w_lower or "aerated" in w_lower or "concrete" in w_lower:
        wall_color = "#ecf0f1"  # Clean Off-White Concrete
        wall_name = "AAC Aerated Concrete"
    elif "bamboo" in w_lower:
        wall_color = "#f39c12"  # Golden Bamboo Timber
        wall_name = "Bamboo Composite"
    elif "brick" in w_lower:
        wall_color = "#c0392b"  # Deep Burnt Brick Red
        wall_name = "Brick Masonry"
    else:
        wall_color = "#16a085"  # Teal default
        wall_name = str(wall_mat).replace("_", " ").title()

    # Roof colors
    if "cgi" in r_lower or "metal" in r_lower or "sheet" in r_lower:
        roof_color = "#2980b9"  # Slate / Corrugated Blue
        roof_name = "Insulated CGI Sheet Roof"
    elif "bamboo" in r_lower or "thatch" in r_lower:
        roof_color = "#b9770e"  # Organic Bamboo Thatch Brown
        roof_name = "Bamboo Thatch Roof"
    elif "concrete" in r_lower or "slab" in r_lower:
        roof_color = "#34495e"  # Dark Slate Concrete Slab
        roof_name = "RCC Concrete Slab"
    elif "solar" in r_lower or "pv" in r_lower:
        roof_color = "#1a252f"  # Midnight Blue Solar PV
        roof_name = "Integrated Solar PV Roof"
    else:
        roof_color = "#e67e22"
        roof_name = str(roof_mat).replace("_", " ").title()

    return wall_color, roof_color, wall_name, roof_name

def calculate_surface_thermal_color(normal_vector, sun_vector, base_temp=30.0, max_ghi=850.0):
    """
    Computes Sol-Air temperature color gradient (Cool Blue -> Amber -> Hot Red)
    based on solar incident angle cos(theta).
    """
    cos_theta = max(0.0, float(np.dot(normal_vector, sun_vector)))
    sol_air_t = base_temp + (cos_theta * (max_ghi / 30.0))  # approx sol-air rise
    
    # Normalize sol_air_t between 20°C and 55°C
    norm = np.clip((sol_air_t - 20.0) / 35.0, 0.0, 1.0)
    
    # Interpolate from Navy Blue (0.0) -> Yellow-Orange (0.5) -> Crimson Red (1.0)
    if norm < 0.5:
        t = norm * 2.0
        r = int(41 + t * (243 - 41))
        g = int(128 + t * (156 - 128))
        b = int(185 - t * (185 - 18))
    else:
        t = (norm - 0.5) * 2.0
        r = int(243 + t * (231 - 243))
        g = int(156 - t * (156 - 76))
        b = int(18 + t * (60 - 18))
        
    return f"rgb({r},{g},{b})", round(sol_air_t, 1)

def create_plotly_3d_shelter(
    geometry: ShelterGeometry, 
    wall_mat="cseb_interlocking", 
    roof_mat="roof_cgi_insulated",
    view_mode="architectural",
    hour_of_day=12,
    solar_ghi=850.0,
    occupants=4,
    show_interior=True
):
    """
    Renders high-realism, dynamic 3D Parametric Architectural Shelter Model with:
    - Dynamic dimensions ($L \times W \times H$)
    - Multi-roof types (Gable Pitched, Monoslope / Shed, Flat Slab)
    - Foundation concrete slab
    - Window glazing & architectural entrance door
    - Corner structural support posts
    - Interactive 24-Hour Solar Vector & Sun Path
    - Sol-Air Thermal Surface Heatmap overlay mode
    - Interior occupancy spatial zones & furniture layout
    - Blueprint dimension callout lines
    """
    L = geometry.length
    W = geometry.width
    H = geometry.height
    pitch = geometry.roof_pitch
    roof_type = geometry.roof_type
    overhang = geometry.overhang
    wwr = geometry.wwr
    orientation = geometry.orientation
    
    wall_color, roof_color, wall_label, roof_label = get_material_colors(wall_mat, roof_mat)

    # Compute solar position vector based on hour_of_day and orientation
    # Hour 6 = East sunrise, Hour 12 = Solar Noon, Hour 18 = West sunset
    hour_clamped = max(0, min(23, int(hour_of_day)))
    is_daytime = 6 <= hour_clamped <= 18
    
    if is_daytime:
        solar_hour_angle = (hour_clamped - 12) * 15.0  # degrees from noon
        sol_altitude_deg = max(5.0, 90.0 - abs(solar_hour_angle * 1.1))
        sol_azimuth_deg = (orientation + solar_hour_angle) % 360.0
    else:
        sol_altitude_deg = 0.0
        sol_azimuth_deg = orientation

    rad_alt = np.radians(sol_altitude_deg)
    rad_az = np.radians(sol_azimuth_deg)
    
    sun_dir = np.array([
        np.cos(rad_alt) * np.cos(rad_az),
        np.cos(rad_alt) * np.sin(rad_az),
        np.sin(rad_alt) if is_daytime else 0.1
    ])
    sun_dir = sun_dir / (np.linalg.norm(sun_dir) or 1.0)

    fig = go.Figure()

    # 1. FOUNDATION CONCRETE SLAB
    slab_margin = 0.35
    sx = [-slab_margin, L + slab_margin, L + slab_margin, -slab_margin,  -slab_margin, L + slab_margin, L + slab_margin, -slab_margin]
    sy = [-slab_margin, -slab_margin, W + slab_margin, W + slab_margin,  -slab_margin, -slab_margin, W + slab_margin, W + slab_margin]
    sz = [-0.22, -0.22, -0.22, -0.22,  0.0, 0.0, 0.0, 0.0]
    
    si = [0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5]
    sj = [1, 4, 2, 5, 3, 6, 0, 7, 5, 7, 6, 7]
    sk = [4, 5, 5, 6, 6, 7, 7, 4, 6, 6, 7, 4]

    fig.add_trace(go.Mesh3d(
        x=sx, y=sy, z=sz, i=si, j=sj, k=sk,
        color="#5d6d7e", opacity=0.9, name="Foundation Concrete Slab", showscale=False
    ))

    # Compute wall thermal colors if in heatmap mode
    if view_mode == "thermal_heatmap" and is_daytime:
        c_front, t_front = calculate_surface_thermal_color(np.array([0, -1, 0]), sun_dir, max_ghi=solar_ghi)
        c_back, t_back = calculate_surface_thermal_color(np.array([0, 1, 0]), sun_dir, max_ghi=solar_ghi)
        c_left, t_left = calculate_surface_thermal_color(np.array([-1, 0, 0]), sun_dir, max_ghi=solar_ghi)
        c_right, t_right = calculate_surface_thermal_color(np.array([1, 0, 0]), sun_dir, max_ghi=solar_ghi)
        c_roof, t_roof = calculate_surface_thermal_color(np.array([0, 0, 1]), sun_dir, max_ghi=solar_ghi)
        
        wall_front_c, wall_back_c = c_front, c_back
        wall_left_c, wall_right_c = c_left, c_right
        roof_surface_c = c_roof
    else:
        wall_front_c = wall_back_c = wall_left_c = wall_right_c = wall_color
        roof_surface_c = roof_color

    # 2. ENVELOPE WALLS
    # Front Wall (y = 0)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, 0, 0], z=[0, 0, H, H],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color=wall_front_c, opacity=0.92, name=f"Front Wall ({wall_label})", showscale=False
    ))
    # Back Wall (y = W)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[W, W, W, W], z=[0, 0, H, H],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color=wall_back_c, opacity=0.92, name="Back Wall", showscale=False
    ))
    # Left Wall (x = 0)
    fig.add_trace(go.Mesh3d(
        x=[0, 0, 0, 0], y=[0, W, W, 0], z=[0, 0, H, H],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color=wall_left_c, opacity=0.92, name="Left Wall", showscale=False
    ))
    # Right Wall (x = L)
    fig.add_trace(go.Mesh3d(
        x=[L, L, L, L], y=[0, W, W, 0], z=[0, 0, H, H],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color=wall_right_c, opacity=0.92, name="Right Wall", showscale=False
    ))

    # 3. WINDOW GLAZING PANES & ARCHITECTURAL ENTRANCE DOOR
    if wwr > 0.02:
        win_w = max(0.8, L * 0.45 * min(1.0, wwr * 3.2))
        win_h = max(0.8, H * 0.38)
        wx_start = min(L - win_w - 0.3, max(0.6, (L - win_w) / 2.0 + 0.3))
        wx_end = wx_start + win_w
        wz_start = H * 0.32
        wz_end = wz_start + win_h
        
        fig.add_trace(go.Mesh3d(
            x=[wx_start, wx_end, wx_end, wx_start],
            y=[-0.02, -0.02, -0.02, -0.02],
            z=[wz_start, wz_start, wz_end, wz_end],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color="#38ef7d" if view_mode == "architectural" else "#3498db",
            opacity=0.75, name=f"Glazed Window ({wwr*100:.0f}% WWR)", showscale=False
        ))
        # Window Frame Border
        fig.add_trace(go.Scatter3d(
            x=[wx_start, wx_end, wx_end, wx_start, wx_start],
            y=[-0.02, -0.02, -0.02, -0.02, -0.02],
            z=[wz_start, wz_start, wz_end, wz_end, wz_start],
            mode="lines", line=dict(color="#117a65", width=4), showlegend=False
        ))

    # Entrance Door on Front Facade
    door_w = min(1.0, max(0.7, L * 0.18))
    door_x0 = 0.3
    door_x1 = door_x0 + door_w
    door_z1 = min(H * 0.78, 2.15)
    
    fig.add_trace(go.Mesh3d(
        x=[door_x0, door_x1, door_x1, door_x0],
        y=[-0.03, -0.03, -0.03, -0.03],
        z=[0, 0, door_z1, door_z1],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color="#4a235a", opacity=0.95, name="Main Entrance Door", showscale=False
    ))
    fig.add_trace(go.Scatter3d(
        x=[door_x0, door_x1, door_x1, door_x0, door_x0],
        y=[-0.03, -0.03, -0.03, -0.03, -0.03],
        z=[0, 0, door_z1, door_z1, 0],
        mode="lines", line=dict(color="#1a001a", width=4), showlegend=False
    ))

    # 4. DYNAMIC ROOF ASSEMBLY BASED ON ROOF TYPE
    oh = overhang
    rx0, rx1 = -oh, L + oh
    ry0, ry2 = -oh, W + oh

    if roof_type == "pitched":
        # Double-slope gable roof
        roof_delta = (W / 2.0) * np.tan(np.radians(pitch))
        roof_apex_h = H + max(0.3, roof_delta)
        ry1 = W / 2.0
        
        # Left Slope
        fig.add_trace(go.Mesh3d(
            x=[rx0, rx1, rx1, rx0],
            y=[ry0, ry0, ry1, ry1],
            z=[H, H, roof_apex_h, roof_apex_h],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color=roof_surface_c, opacity=0.95, name=f"Roof: {roof_label}", showscale=False
        ))
        # Right Slope
        fig.add_trace(go.Mesh3d(
            x=[rx0, rx1, rx1, rx0],
            y=[ry1, ry1, ry2, ry2],
            z=[roof_apex_h, roof_apex_h, H, H],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color=roof_surface_c, opacity=0.95, name="Roof Slope Right", showscale=False
        ))
        # Front Triangular Gable Wall
        fig.add_trace(go.Mesh3d(
            x=[0, L/2.0, L], y=[0, 0, 0], z=[H, roof_apex_h, H],
            i=[0], j=[1], k=[2], color=wall_front_c, opacity=0.92, showlegend=False
        ))
        # Back Triangular Gable Wall
        fig.add_trace(go.Mesh3d(
            x=[0, L/2.0, L], y=[W, W, W], z=[H, roof_apex_h, H],
            i=[0], j=[1], k=[2], color=wall_back_c, opacity=0.92, showlegend=False
        ))
        roof_top_z = roof_apex_h

    elif roof_type == "monoslope":
        # Single-slope shed roof rising from Front to Back
        roof_delta = W * np.tan(np.radians(pitch))
        roof_top_z = H + max(0.3, roof_delta)
        
        fig.add_trace(go.Mesh3d(
            x=[rx0, rx1, rx1, rx0],
            y=[ry0, ry0, ry2, ry2],
            z=[H, H, roof_top_z, roof_top_z],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color=roof_surface_c, opacity=0.95, name=f"Monoslope Roof ({roof_label})", showscale=False
        ))
        # Side Gable triangles
        fig.add_trace(go.Mesh3d(
            x=[0, 0, 0], y=[0, W, W], z=[H, H, roof_top_z],
            i=[0], j=[1], k=[2], color=wall_left_c, opacity=0.92, showlegend=False
        ))
        fig.add_trace(go.Mesh3d(
            x=[L, L, L], y=[0, W, W], z=[H, H, roof_top_z],
            i=[0], j=[1], k=[2], color=wall_right_c, opacity=0.92, showlegend=False
        ))
    else:
        # Flat Overhang Slab
        roof_top_z = H + 0.18
        fig.add_trace(go.Mesh3d(
            x=[rx0, rx1, rx1, rx0],
            y=[ry0, ry0, ry2, ry2],
            z=[H+0.05, H+0.05, roof_top_z, roof_top_z],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color=roof_surface_c, opacity=0.95, name=f"Flat Roof Slab ({roof_label})", showscale=False
        ))

    # 5. CORNER STRUCTURAL POSTS
    posts_x = [0, L, L, 0]
    posts_y = [0, 0, W, W]
    for px, py in zip(posts_x, posts_y):
        fig.add_trace(go.Scatter3d(
            x=[px, px], y=[py, py], z=[0, H],
            mode="lines", line=dict(color="#1a252f", width=7), showlegend=False
        ))

    # 6. INTERIOR OCCUPANCY SPATIAL ZONES
    if show_interior and occupants > 0:
        occ_count = min(12, int(occupants))
        grid_cols = max(1, int(np.ceil(np.sqrt(occ_count))))
        grid_rows = int(np.ceil(occ_count / grid_cols))
        
        spacing_x = (L - 1.2) / max(1, grid_cols)
        spacing_y = (W - 1.0) / max(1, grid_rows)
        
        bed_xs, bed_ys, bed_zs = [], [], []
        for idx in range(occ_count):
            r = idx // grid_cols
            c = idx % grid_cols
            bx = 0.8 + c * spacing_x
            by = 0.6 + r * spacing_y
            bed_xs.append(bx)
            bed_ys.append(by)
            bed_zs.append(0.2)
            
        fig.add_trace(go.Scatter3d(
            x=bed_xs, y=bed_ys, z=bed_zs,
            mode="markers+text",
            marker=dict(size=8, color="#2ecc71", symbol="diamond"),
            text=[f"P{i+1}" for i in range(occ_count)],
            textposition="top center",
            name=f"Occupant Zones ({occ_count} Ppl)"
        ))

    # 7. 24-HOUR SOLAR VECTOR & DYNAMIC SUN POSITION
    sun_dist = max(L, W) * 1.35
    sun_x = L / 2.0 + sun_dist * sun_dir[0]
    sun_y = W / 2.0 + sun_dist * sun_dir[1]
    sun_z = roof_top_z + sun_dist * sun_dir[2]

    if is_daytime:
        # Sunbeam ray targeting roof center
        fig.add_trace(go.Scatter3d(
            x=[sun_x, L / 2.0], y=[sun_y, W / 2.0], z=[sun_z, roof_top_z],
            mode="lines", name=f"Sun Ray ({solar_ghi:.0f} W/m²)",
            line=dict(color="#f39c12", width=5, dash="dot")
        ))
        # Glowing Sun sphere
        fig.add_trace(go.Scatter3d(
            x=[sun_x], y=[sun_y], z=[sun_z],
            mode="markers+text", name=f"Sun Position ({hour_clamped}:00)",
            marker=dict(size=14, color="#f1c40f", symbol="circle"),
            text=[f"☀️ {hour_clamped}:00 ({sol_altitude_deg:.0f}° Alt)"],
            textposition="top center"
        ))

    # Diurnal Sun Trajectory Arc
    arc_hours = np.linspace(6, 18, 25)
    arc_xs, arc_ys, arc_zs = [], [], []
    for h in arc_hours:
        ha = (h - 12) * 15.0
        alt = max(5.0, 90.0 - abs(ha * 1.1))
        az = (orientation + ha) % 360.0
        dx = np.cos(np.radians(alt)) * np.cos(np.radians(az))
        dy = np.cos(np.radians(alt)) * np.sin(np.radians(az))
        dz = np.sin(np.radians(alt))
        arc_xs.append(L/2.0 + sun_dist * dx)
        arc_ys.append(W/2.0 + sun_dist * dy)
        arc_zs.append(roof_top_z + sun_dist * dz)

    fig.add_trace(go.Scatter3d(
        x=arc_xs, y=arc_ys, z=arc_zs,
        mode="lines", name="Diurnal Sun Arc (6h-18h)",
        line=dict(color="#f39c12", width=3, dash="dash")
    ))

    # 8. BLUEPRINT DIMENSION ANNOTATIONS
    fig.add_trace(go.Scatter3d(
        x=[0, L], y=[-0.6, -0.6], z=[0, 0],
        mode="lines+text", name="Dimensions",
        line=dict(color="#e74c3c", width=4),
        text=["", f"Length: {L:.1f}m"], textposition="bottom center", showlegend=False
    ))
    fig.add_trace(go.Scatter3d(
        x=[-0.6, -0.6], y=[0, W], z=[0, 0],
        mode="lines+text",
        line=dict(color="#e74c3c", width=4),
        text=["", f"Width: {W:.1f}m"], textposition="bottom center", showlegend=False
    ))
    fig.add_trace(go.Scatter3d(
        x=[-0.6, -0.6], y=[-0.6, -0.6], z=[0, H],
        mode="lines+text",
        line=dict(color="#e74c3c", width=4),
        text=["", f"Height: {H:.1f}m"], textposition="top center", showlegend=False
    ))

    # 9. LAYOUT & CAMERA VIEWPORT
    mode_title = "🌡️ Thermal Sol-Air Heatmap" if view_mode == "thermal_heatmap" else "🏢 Architectural Model"
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Length X (m)", gridcolor="#333", backgroundcolor="#111827", zerolinecolor="#555"),
            yaxis=dict(title="Width Y (m)", gridcolor="#333", backgroundcolor="#111827", zerolinecolor="#555"),
            zaxis=dict(title="Height Z (m)", gridcolor="#333", backgroundcolor="#111827", zerolinecolor="#555"),
            camera=dict(
                eye=dict(x=1.75, y=-1.75, z=1.35),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            aspectmode="data"
        ),
        title=dict(
            text=f"{mode_title} | {L}m × {W}m × {H}m (Floor: {geometry.floor_area()}m² | Vol: {geometry.volume()}m³)",
            font=dict(size=15, color="#2ecc71")
        ),
        margin=dict(l=10, r=10, t=40, b=10),
        template="plotly_dark",
        legend=dict(x=0.02, y=0.98, bgcolor="rgba(0,0,0,0.65)")
    )

    return fig
