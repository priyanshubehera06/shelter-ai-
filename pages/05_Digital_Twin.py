"""
05_Digital_Twin.py — Interactive Parametric Climate-Aware 3D Digital Twin for Shelter-AI.
Seamlessly connects physical shelter geometry, envelope materials, NOAA solar astronomy,
and transient RC thermal simulation outputs into a unified 3D engineering decision dashboard.
"""

import streamlit as st
import numpy as np
import pandas as pd

from engine.geometry import ShelterGeometry
from engine.materials import get_material_by_id, calculate_assembly_u_value
from engine.climate import get_climate_profile
from engine.thermal import simulate_shelter_thermal_dynamics
from engine.comfort import calculate_pmv_fanger, get_comfort_category
from engine.location_widget import render_location_sidebar_widget
from visualization.shelter_3d import (
    create_pyvista_3d_shelter,
    render_pyvista_3d_shelter,
    set_pyvista_camera_preset,
    calculate_solar_position,
    get_material_colors,
    get_camera_preset_dict,
)

st.set_page_config(
    page_title="Shelter-AI — 3D Digital Twin",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏢 Parametric 3D Climate-Aware Digital Twin")
st.caption("Interactive multi-physics building digital twin with astronomical solar tracking, envelope materials, and structural telemetry")

render_location_sidebar_widget()

# ==============================================================================
# 1. RETRIEVE OR INITIALIZE ACTIVE DESIGN & CLIMATE STATE
# ==============================================================================
geo_data = st.session_state.get("auto_geo_data", {})
lat = float(geo_data.get("lat", 21.4669))
lon = float(geo_data.get("lon", 83.9812))
loc_name = geo_data.get("location_name", "Selected Region")
climate_records = geo_data.get("climate_records") or get_climate_profile(month=5)

# Load active shelter design from session state (or provide robust baseline default)
current_design = st.session_state.get("current_design", {
    "length_m": 6.0,
    "width_m": 4.0,
    "height_m": 2.8,
    "roof_type": "pitched",
    "roof_pitch_deg": 15.0,
    "wall_mat_id": "cseb_interlocking",
    "wall_thickness_cm": 20.0,
    "roof_mat_id": "roof_cgi_insulated",
    "insulation_mat_id": "insulation_rockwool",
    "insulation_thickness_cm": 5.0,
    "glazing_mat_id": "glazing_single",
    "wwr_pct": 15.0,
    "overhang_m": 0.6,
    "orientation_deg": 0.0,
    "occupants": 4
})

geom = ShelterGeometry(
    length_m=current_design.get("length_m", 6.0),
    width_m=current_design.get("width_m", 4.0),
    height_m=current_design.get("height_m", 2.8),
    roof_type=current_design.get("roof_type", "pitched"),
    roof_pitch_deg=current_design.get("roof_pitch_deg", 15.0),
    wall_thickness_cm=current_design.get("wall_thickness_cm", 20.0),
    wwr_pct=current_design.get("wwr_pct", 15.0),
    overhang_m=current_design.get("overhang_m", 0.6),
    orientation_deg=current_design.get("orientation_deg", 0.0)
)

wall_mat_id = current_design.get("wall_mat_id", "cseb_interlocking")
roof_mat_id = current_design.get("roof_mat_id", "roof_cgi_insulated")
ins_mat_id = current_design.get("insulation_mat_id", "insulation_rockwool")
ins_thick_cm = current_design.get("insulation_thickness_cm", 5.0)
occupants = current_design.get("occupants", 4)

# Run or retrieve transient 24-hour thermal simulation
sim_results = simulate_shelter_thermal_dynamics(
    geometry=geom,
    wall_mat_id=wall_mat_id,
    wall_thickness_cm=current_design.get("wall_thickness_cm", 20.0),
    roof_mat_id=roof_mat_id,
    glazing_mat_id=current_design.get("glazing_mat_id", "glazing_single"),
    insulation_mat_id=ins_mat_id,
    insulation_thickness_cm=ins_thick_cm,
    climate_records=climate_records,
    occupants=occupants
)

# ==============================================================================
# 2. DIGITAL TWIN TOP CONTROLS (VIEW MODES & SIMULATION TIME)
# ==============================================================================
ctrl_col1, ctrl_col2 = st.columns([1.6, 1.4])

with ctrl_col1:
    view_mode_labels = [
        "🏢 Architectural Model",
        "☀️ Solar & Shading Analysis",
        "🌡️ Modeled Thermal Sol-Air Load",
        "💨 Passive Ventilation (Conceptual)",
        "🧩 Exploded Structural Assembly"
    ]
    mode_map = {
        "🏢 Architectural Model": "architectural",
        "☀️ Solar & Shading Analysis": "solar_shading",
        "🌡️ Modeled Thermal Sol-Air Load": "thermal_heatmap",
        "💨 Passive Ventilation (Conceptual)": "ventilation",
        "🧩 Exploded Structural Assembly": "exploded"
    }
    
    selected_mode_label = st.selectbox(
        "🎯 Select Engineering 3D View Mode:",
        view_mode_labels,
        index=0,
        help="Switch between Architectural, Solar Shading, Sol-Air Thermal Heatmap, Ventilation, and Exploded assembly."
    )
    active_mode = mode_map[selected_mode_label]

with ctrl_col2:
    # 24-Hour Simulation Time Slider with quick presets
    t_c1, t_c2 = st.columns([2.2, 1.2])
    with t_c1:
        sim_hour = st.slider("🕒 Simulation Time of Day (24-Hr Cycle):", 0, 23, 12, 1, format="%02d:00")
    with t_c2:
        st.write("")
        if st.button("☀️ Solar Noon (12:00)", use_container_width=True):
            sim_hour = 12

exploded_offset = 0.8 if active_mode == "exploded" else 0.0

# Extract hourly climate metrics at current simulation time
hour_idx = min(23, max(0, int(sim_hour)))
curr_t_out = climate_records[hour_idx]["dry_bulb_temp_c"] if hour_idx < len(climate_records) else 34.0
curr_rh = climate_records[hour_idx]["relative_humidity_pct"] if hour_idx < len(climate_records) else 50.0
curr_ghi = climate_records[hour_idx]["solar_ghi_w_m2"] if hour_idx < len(climate_records) else 850.0
curr_wind = climate_records[hour_idx].get("wind_speed_m_s", 3.2)
curr_wind_dir = climate_records[hour_idx].get("wind_direction_deg", 225.0)

# Calculate Solar Position
sol_alt, sol_az, is_day = calculate_solar_position(lat, lon, day_of_year=135, hour_of_day=sim_hour)

# ==============================================================================
# 3. MAIN DASHBOARD: 3D DIGITAL TWIN + TELEMETRY HUD
# ==============================================================================
left_col, right_col = st.columns([1.75, 1.0])

with left_col:
    # Camera Presets Bar
    cam_c1, cam_c2, cam_c3, cam_c4, cam_c5 = st.columns(5)
    if "selected_cam_preset" not in st.session_state:
        st.session_state["selected_cam_preset"] = "Isometric"
        
    if cam_c1.button("📐 Isometric", use_container_width=True):
        st.session_state["selected_cam_preset"] = "Isometric"
    if cam_c2.button("🏠 Front (South)", use_container_width=True):
        st.session_state["selected_cam_preset"] = "Front (South)"
    if cam_c3.button("↔️ Side (East)", use_container_width=True):
        st.session_state["selected_cam_preset"] = "Side (East)"
    if cam_c4.button("🔝 Top (Plan)", use_container_width=True):
        st.session_state["selected_cam_preset"] = "Top (Plan)"
    if cam_c5.button("🧭 North", use_container_width=True):
        st.session_state["selected_cam_preset"] = "North Elevation"

    # Component Visibility Filter Controls
    with st.expander("🛠️ Component Visibility & Rendering Options", expanded=False):
        c_v1, c_v2, c_v3, c_v4 = st.columns(4)
        vis_roof = c_v1.checkbox("Roof Assembly", value=True)
        vis_walls = c_v2.checkbox("Walls & Openings", value=True)
        vis_win = c_v3.checkbox("Glazing Panes", value=True)
        vis_door = c_v4.checkbox("Entrance Door", value=True)
        vis_shading = c_v1.checkbox("Overhang Shading", value=True)
        vis_ground = c_v2.checkbox("Ground & Grid", value=True)
        vis_comp = c_v3.checkbox("3D Compass", value=True)
        vis_sun = c_v4.checkbox("Solar Path & Sun", value=True)

    component_vis = {
        "roof": vis_roof,
        "walls": vis_walls,
        "windows": vis_win,
        "door": vis_door,
        "shading": vis_shading,
        "ground": vis_ground,
        "compass": vis_comp,
        "sun_path": vis_sun,
        "shadow": True,
    }

    # Build and Render Parametric 3D PyVista Digital Twin
    plotter = create_pyvista_3d_shelter(
        geometry=geom,
        wall_mat=wall_mat_id,
        roof_mat=roof_mat_id,
        view_mode=active_mode,
        hour_of_day=sim_hour,
        solar_ghi=curr_ghi,
        occupants=occupants,
        show_interior=True,
        latitude=lat,
        longitude=lon,
        wind_speed=curr_wind,
        wind_direction_deg=curr_wind_dir,
        sim_results=sim_results,
        exploded_offset=exploded_offset,
        component_visibility=component_vis
    )
    
    # Apply Camera Preset
    set_pyvista_camera_preset(plotter, st.session_state["selected_cam_preset"], geom)
    
    # Render interactive 3D WebGL Digital Twin
    render_pyvista_3d_shelter(plotter, height=580)
    
    # View mode contextual explanation banner
    if active_mode == "solar_shading":
        st.info(f"☀️ **Solar & Shading Analysis:** Sun Altitude = **{sol_alt:.1f}°**, Sun Azimuth = **{sol_az:.1f}°** (Clockwise from North). Ground shadow footprint updates dynamically based on roof ridge and wall geometry.")
    elif active_mode == "thermal_heatmap":
        st.info(f"🌡️ **Modeled Thermal Sol-Air Load:** Surface colors depict real-time Sol-Air temperatures derived from $T_{{\\text{{out}}}} + (\\alpha \\cdot GHI / h_o)$ across envelope orientations.")
    elif active_mode == "ventilation":
        st.info(f"💨 **Conceptual Passive Ventilation:** Ambient wind speed **{curr_wind:.1f} m/s** entering from **{curr_wind_dir:.0f}°** azimuth. Streamlines illustrate natural cross-ventilation through envelope openings.")
    elif active_mode == "exploded":
        st.info("🧩 **Exploded Assembly:** Vertical layer separation showing foundation slab, structural walls, and roof envelope layers.")

with right_col:
    # --------------------------------------------------------------------------
    # HUD TABBED TELEMETRY PANELS
    # --------------------------------------------------------------------------
    tab_specs, tab_climate, tab_thermal, tab_inspect = st.tabs([
        "📐 Specs", "🌤️ Climate", "🌡️ Thermal", "🔍 Inspector"
    ])
    
    with tab_specs:
        st.markdown("#### 📐 Current Design Specifications")
        st.markdown(f"""
        - **Dimensions ($L \\times W \\times H$):** `{geom.length:.1f}m × {geom.width:.1f}m × {geom.height:.1f}m`
        - **Usable Floor Area:** `{geom.floor_area():.1f} m²` (`{geom.floor_area()/max(1,occupants):.1f} m²/person`)
        - **Internal Air Volume:** `{geom.volume():.1f} m³`
        - **Surface-to-Volume Ratio:** `{geom.surface_to_volume_ratio():.3f} m⁻¹` (Thermal Compactness)
        - **Orientation:** `{geom.orientation:.0f}° from North`
        - **Roof Assembly:** `{geom.roof_type.title()} ({geom.roof_pitch:.1f}° pitch, {geom.overhang:.1f}m overhang)`
        - **Glazing Ratio (WWR):** `{geom.wwr*100:.0f}%` (`{geom.glazing_area():.1f} m²` glazed area)
        - **Occupancy Capacity:** `{occupants} People` (Sphere Humanitarian Standard)
        """)
        
        u_wall_res = calculate_assembly_u_value(wall_mat_id, current_design.get("wall_thickness_cm", 20.0))
        st.markdown("---")
        st.metric("Wall Assembly U-Value", f"{u_wall_res['u_value_w_m2k']:.3f} W/m²K")
        st.metric("Roof Assembly U-Value", f"{sim_results['u_roof']:.3f} W/m²K")

    with tab_climate:
        st.markdown(f"#### 🌤️ Live Micro-Climate ({loc_name})")
        st.caption(f"Time: **{sim_hour:02d}:00** | Lat: **{lat:.2f}°**, Lon: **{lon:.2f}°**")
        
        mc1, mc2 = st.columns(2)
        mc1.metric("Outdoor Temp", f"{curr_t_out:.1f} °C")
        mc2.metric("Solar GHI", f"{curr_ghi:.0f} W/m²")
        
        mc3, mc4 = st.columns(2)
        mc3.metric("Relative Humidity", f"{curr_rh:.0f} %")
        mc4.metric("Wind Speed", f"{curr_wind:.1f} m/s", f"{curr_wind_dir:.0f}° Azimuth")
        
        st.markdown("---")
        st.markdown(f"""
        - **Solar Altitude:** `{sol_alt:.1f}°` above horizon
        - **Solar Azimuth:** `{sol_az:.1f}°` (Clockwise from True North)
        - **Daylight Status:** `{'☀️ Direct Sunlight' if is_day else '🌙 Night Time'}`
        """)

    with tab_thermal:
        st.markdown("#### 🌡️ Modeled Thermal Performance")
        curr_t_in = sim_results["t_indoor"][hour_idx]
        curr_t_sa = sim_results["t_sol_air"][hour_idx]
        pmv_val, ppd_val = calculate_pmv_fanger(curr_t_in, curr_rh)
        comfort_cat, cat_color = get_comfort_category(pmv_val)
        
        th1, th2 = st.columns(2)
        th1.metric("Indoor Temp", f"{curr_t_in:.1f} °C", f"{curr_t_in - curr_t_out:+.1f} °C vs Ambient")
        th2.metric("Sol-Air Envelope", f"{curr_t_sa:.1f} °C")
        
        st.markdown(f"""
        - **Thermal Damping Factor:** `{sim_results['damping_factor']:.3f}` (Lower = Superior Thermal Mass)
        - **Thermal Lag:** `{sim_results['time_lag_hours']} Hours` delay in peak heat transfer
        - **24-Hour Peak Indoor:** `{sim_results['max_t_indoor']:.1f} °C` (vs `{sim_results['max_t_outdoor']:.1f} °C` Outdoor)
        - **Overheating Hours (>30°C):** `{sim_results['hours_above_threshold']} hrs/day`
        """)
        
        st.markdown(f"""
        <div style="background:#1e272e;padding:8px 12px;border-radius:6px;border-left:4px solid {cat_color};margin-top:6px;">
            <b>Fanger PMV Index:</b> {pmv_val:+.2f} ({comfort_cat})<br/>
            <b>Predicted Dissatisfied (PPD):</b> {ppd_val:.1f}%
        </div>
        """, unsafe_allow_html=True)

    with tab_inspect:
        st.markdown("#### 🔍 Envelope Component Inspector")
        inspect_target = st.selectbox("Inspect Component:", ["Roof Assembly", "Wall Assembly", "Glazed Openings", "Shading Eaves", "Foundation Slab"])
        
        if "Roof" in inspect_target:
            r_info = get_material_by_id(roof_mat_id)
            st.markdown(f"""
            - **Component:** Roof Envelope Assembly
            - **Material:** `{r_info['name']}`
            - **Total Area:** `{geom.roof_area():.1f} m²` (including overhang eaves)
            - **U-Value:** `{sim_results['u_roof']:.3f} W/m²K`
            - **Insulation:** `{ins_thick_cm:.1f} cm {ins_mat_id or 'None'}`
            - **Current Heat Flux ($Q_{{\\text{{roof}}}}$):** `{sim_results['q_roof'][hour_idx]:+.0f} Watts`
            """)
        elif "Wall" in inspect_target:
            w_info = get_material_by_id(wall_mat_id)
            st.markdown(f"""
            - **Component:** Opaque Vertical Walls
            - **Material:** `{w_info['name']}`
            - **Net Surface Area:** `{geom.net_wall_area():.1f} m²`
            - **Gross Surface Area:** `{geom.gross_wall_area():.1f} m²`
            - **Wall Thickness:** `{current_design.get('wall_thickness_cm', 20.0):.1f} cm`
            - **U-Value:** `{sim_results['u_wall']:.3f} W/m²K`
            - **Current Heat Flux ($Q_{{\\text{{wall}}}}$):** `{sim_results['q_wall'][hour_idx]:+.0f} Watts`
            """)
        elif "Glazing" in inspect_target:
            st.markdown(f"""
            - **Component:** Window Glazing & Openings
            - **Glazing Type:** `{current_design.get('glazing_mat_id', 'glazing_single').replace('_',' ').title()}`
            - **Window-to-Wall Ratio:** `{geom.wwr*100:.0f}%`
            - **Total Glazed Area:** `{geom.glazing_area():.1f} m²`
            - **U-Value:** `{sim_results['u_glazing']:.2f} W/m²K`
            - **Solar Gain ($Q_{{\\text{{solar}}}}$):** `{sim_results['q_solar'][hour_idx]:+.0f} Watts`
            """)
        elif "Shading" in inspect_target:
            st.markdown(f"""
            - **Component:** Roof & Window Overhang Shading
            - **Overhang Projection:** `{geom.overhang:.2f} m`
            - **Solar Shading Factor:** `{geom.shading_factor(solar_elevation_deg=sol_alt):.2f}` (fraction shaded at {sol_alt:.0f}° solar altitude)
            """)
        else:
            st.markdown(f"""
            - **Component:** Ground Foundation Concrete Slab
            - **Footprint Area:** `{geom.floor_area():.1f} m²`
            - **Perimeter:** `{geom.footprint_perimeter():.1f} m`
            - **Slab Thickness:** `0.22 m Concrete`
            """)

# ==============================================================================
# 4. BOTTOM NAVIGATION & WORKFLOW CONTINUATION
# ==============================================================================
st.markdown("---")
nav_c1, nav_c2, nav_c3 = st.columns([1, 1, 1])

with nav_c1:
    if st.button("⬅️ Modify in Parametric Design Lab", use_container_width=True):
        st.switch_page("pages/04_Design_Lab.py")
with nav_c2:
    if st.button("🔄 Test Sensitivity in What-If Lab", use_container_width=True):
        st.switch_page("pages/07_What_If_Lab.py")
with nav_c3:
    if st.button("🎯 Run Multi-Objective Pareto Optimization", use_container_width=True):
        st.switch_page("pages/06_Optimization.py")
