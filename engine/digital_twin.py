"""
digital_twin.py — High-Fidelity 3D Parametric Digital Twin Engine for Shelter-AI.
Generates architectural mesh geometry, computes dynamic directional Sol-Air thermal heatmaps,
solar incident angles, and creates interactive Plotly 3D representations.
"""

from typing import Dict, List, Optional, Any, Tuple
import math
import numpy as np
import plotly.graph_objects as go
from engine.geometry import ShelterGeometry


def calculate_sol_air_facet_temperatures(
    t_outdoor: float,
    solar_ghi: float,
    hour_of_day: int = 14,
    wall_absorptivity: float = 0.70,
    roof_absorptivity: float = 0.85,
    h_outdoor: float = 22.7,  # Exterior convection coefficient W/m²K
) -> Dict[str, float]:
    """
    Computes Sol-Air temperatures for each building facade based on solar altitude and azimuth.
    T_sol_air = T_out + (alpha * I_surface) / h_o - (epsilon * delta_R) / h_o
    """
    # Solar altitude angle (approximate diurnal sine)
    sun_alt_rad = max(0.0, math.sin((hour_of_day - 6) * math.pi / 12.0)) if 6 <= hour_of_day <= 18 else 0.0

    # Direct incident radiation approximations by orientation
    # East peak: 08:00 - 10:00; South peak: 12:00 - 14:00; West peak: 15:00 - 17:00; North: diffuse only
    i_roof = solar_ghi * (0.95 * sun_alt_rad + 0.05) if sun_alt_rad > 0 else 0.0

    if 6 <= hour_of_day < 11:
        i_east = solar_ghi * 0.75
        i_west = solar_ghi * 0.10
        i_south = solar_ghi * 0.35
        i_north = solar_ghi * 0.10
    elif 11 <= hour_of_day <= 14:
        i_east = solar_ghi * 0.25
        i_west = solar_ghi * 0.25
        i_south = solar_ghi * 0.70
        i_north = solar_ghi * 0.10
    elif 14 < hour_of_day <= 18:
        i_east = solar_ghi * 0.10
        i_west = solar_ghi * 0.80
        i_south = solar_ghi * 0.40
        i_north = solar_ghi * 0.10
    else:
        i_east = i_west = i_south = i_north = 0.0

    t_roof_sol = t_outdoor + (roof_absorptivity * i_roof) / h_outdoor - 4.0
    t_south_sol = t_outdoor + (wall_absorptivity * i_south) / h_outdoor
    t_north_sol = t_outdoor + (wall_absorptivity * i_north) / h_outdoor
    t_east_sol = t_outdoor + (wall_absorptivity * i_east) / h_outdoor
    t_west_sol = t_outdoor + (wall_absorptivity * i_west) / h_outdoor

    return {
        "Roof": round(max(t_outdoor, t_roof_sol), 1),
        "South_Wall": round(max(t_outdoor, t_south_sol), 1),
        "North_Wall": round(max(t_outdoor, t_north_sol), 1),
        "East_Wall": round(max(t_outdoor, t_east_sol), 1),
        "West_Wall": round(max(t_outdoor, t_west_sol), 1),
        "Floor": round(t_outdoor - 2.0, 1),
    }


def generate_3d_digital_twin_model(
    geometry: ShelterGeometry,
    wall_mat_id: str = "cseb_interlocking",
    roof_mat_id: str = "roof_cgi_insulated",
    view_mode: str = "architectural",  # "architectural" or "thermal_heatmap"
    hour_of_day: int = 14,
    solar_ghi: float = 850.0,
    t_outdoor: float = 36.0,
    occupants: int = 4,
) -> Dict[str, Any]:
    """
    Generates structured mesh data, thermal surface temperatures, and Plotly 3D visual figure.
    """
    sol_air_temps = calculate_sol_air_facet_temperatures(
        t_outdoor=t_outdoor,
        solar_ghi=solar_ghi,
        hour_of_day=hour_of_day,
    )

    L = geometry.length
    W = geometry.width
    H = geometry.height
    overhang = geometry.overhang
    roof_type = geometry.roof_type

    fig = go.Figure()

    # Color definitions
    wall_colors = {
        "cseb_interlocking": "#c0392b",
        "brick_standard": "#d35400",
        "ceb_standard": "#b9770e",
        "stone_masonry": "#7f8c8d",
        "bamboo_composite": "#27ae60",
        "aac_block": "#bdc3c7",
        "eps_sandwich": "#ecf0f1",
    }
    base_wall_color = wall_colors.get(wall_mat_id, "#bdc3c7")

    # Helper function for surface color in thermal mode
    def get_thermal_color(temp_c: float) -> str:
        # Colormap from cool (22°C blue) to moderate (32°C green/orange) to hot (50°C red)
        if temp_c < 25.0:
            return "#3498db"
        elif temp_c < 32.0:
            return "#2ecc71"
        elif temp_c < 40.0:
            return "#f39c12"
        elif temp_c < 48.0:
            return "#e67e22"
        else:
            return "#e74c3c"

    # 1. Floor Slab
    x_floor = [0, L, L, 0, 0]
    y_floor = [0, 0, W, W, 0]
    z_floor = [0, 0, 0, 0, 0]
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, W, W], z=[0, 0, 0, 0],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color="#7f8c8d" if view_mode == "architectural" else get_thermal_color(sol_air_temps["Floor"]),
        opacity=0.9, name="Floor Slab"
    ))

    # 2. South Wall (y = 0)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[0, 0, 0, 0], z=[0, 0, H, H],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color=base_wall_color if view_mode == "architectural" else get_thermal_color(sol_air_temps["South_Wall"]),
        opacity=0.85, name=f"South Facade ({sol_air_temps['South_Wall']}°C)"
    ))

    # 3. North Wall (y = W)
    fig.add_trace(go.Mesh3d(
        x=[0, L, L, 0], y=[W, W, W, W], z=[0, 0, H, H],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color=base_wall_color if view_mode == "architectural" else get_thermal_color(sol_air_temps["North_Wall"]),
        opacity=0.85, name=f"North Facade ({sol_air_temps['North_Wall']}°C)"
    ))

    # 4. East Wall (x = L)
    fig.add_trace(go.Mesh3d(
        x=[L, L, L, L], y=[0, W, W, 0], z=[0, 0, H, H],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color=base_wall_color if view_mode == "architectural" else get_thermal_color(sol_air_temps["East_Wall"]),
        opacity=0.85, name=f"East Facade ({sol_air_temps['East_Wall']}°C)"
    ))

    # 5. West Wall (x = 0)
    fig.add_trace(go.Mesh3d(
        x=[0, 0, 0, 0], y=[0, W, W, 0], z=[0, 0, H, H],
        i=[0, 0], j=[1, 2], k=[2, 3],
        color=base_wall_color if view_mode == "architectural" else get_thermal_color(sol_air_temps["West_Wall"]),
        opacity=0.85, name=f"West Facade ({sol_air_temps['West_Wall']}°C)"
    ))

    # 6. Roof Assembly (Pitched gable or flat)
    roof_color = "#34495e" if "cgi" in roof_mat_id else ("#95a5a6" if "concrete" in roof_mat_id else "#b7950b")
    h_ridge = H + (W / 2.0) * math.tan(math.radians(geometry.roof_pitch)) if roof_type == "pitched" else H

    if roof_type == "pitched":
        # Pitch 1 (South half)
        fig.add_trace(go.Mesh3d(
            x=[-overhang, L + overhang, L + overhang, -overhang],
            y=[-overhang, -overhang, W / 2.0, W / 2.0],
            z=[H, H, h_ridge, h_ridge],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color=roof_color if view_mode == "architectural" else get_thermal_color(sol_air_temps["Roof"]),
            opacity=0.9, name=f"Roof South Pitch ({sol_air_temps['Roof']}°C)"
        ))
        # Pitch 2 (North half)
        fig.add_trace(go.Mesh3d(
            x=[-overhang, L + overhang, L + overhang, -overhang],
            y=[W / 2.0, W / 2.0, W + overhang, W + overhang],
            z=[h_ridge, h_ridge, H, H],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color=roof_color if view_mode == "architectural" else get_thermal_color(sol_air_temps["Roof"]),
            opacity=0.9, name=f"Roof North Pitch ({sol_air_temps['Roof']}°C)"
        ))
    else:
        # Flat slab
        fig.add_trace(go.Mesh3d(
            x=[-overhang, L + overhang, L + overhang, -overhang],
            y=[-overhang, -overhang, W + overhang, W + overhang],
            z=[H, H, H, H],
            i=[0, 0], j=[1, 2], k=[2, 3],
            color=roof_color if view_mode == "architectural" else get_thermal_color(sol_air_temps["Roof"]),
            opacity=0.9, name=f"Flat Roof ({sol_air_temps['Roof']}°C)"
        ))

    # Layout styling
    fig.update_layout(
        scene=dict(
            xaxis=dict(title="Length (m)", showbackground=False),
            yaxis=dict(title="Width (m)", showbackground=False),
            zaxis=dict(title="Height (m)", showbackground=False),
            aspectratio=dict(x=L / max(L, W, H), y=W / max(L, W, H), z=H / max(L, W, H)),
        ),
        margin=dict(l=10, r=10, t=30, b=10),
        template="plotly_dark",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    return {
        "figure": fig,
        "sol_air_temperatures": sol_air_temps,
        "h_ridge": h_ridge,
        "overhang_m": overhang,
        "total_exposed_area_m2": geometry.exposed_surface_area(),
    }
