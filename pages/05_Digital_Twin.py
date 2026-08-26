import streamlit as st
from engine.geometry import ShelterGeometry
from visualization.shelter_3d import create_plotly_3d_shelter
from engine.climate import get_climate_profile
from engine.location_widget import render_location_sidebar_widget

st.set_page_config(page_title="Shelter-AI — 3D Digital Twin", page_icon="🏢", layout="wide")

st.title("🏢 Parametric 3D Digital Twin")
st.caption("Interactive architectural building twin with diurnal solar tracking, material textures, and thermal sol-air surface heatmaps")

render_location_sidebar_widget()

climate_records = get_climate_profile(month=5)

c1, c2, c3 = st.columns([1.5, 1.5, 1])
with c1:
    view_mode_label = st.radio("3D Display Mode:", ["🏢 Architectural Material Textures", "🌡️ Sol-Air Thermal Surface Heatmap"], horizontal=True)
    mode_key = "thermal_heatmap" if "Thermal" in view_mode_label else "architectural"
with c2:
    sim_hour = st.slider("🕒 Solar Trajectory Hour (0-23)", 0, 23, 12, 1, format="%d:00")
    current_ghi = climate_records[sim_hour]["solar_ghi_w_m2"] if sim_hour < len(climate_records) else 850.0
with c3:
    show_interior = st.checkbox("Show Occupancy Layout", value=True)
    st.caption(f"☀️ Solar GHI: **{current_ghi:.0f} W/m²**")

geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8, roof_type="pitched", roof_pitch_deg=15.0, wwr_pct=15.0, overhang_m=0.6)

fig_3d = create_plotly_3d_shelter(
    geometry=geom,
    wall_mat="cseb_interlocking",
    roof_mat="roof_cgi_insulated",
    view_mode=mode_key,
    hour_of_day=sim_hour,
    solar_ghi=current_ghi,
    occupants=4,
    show_interior=show_interior
)

st.plotly_chart(fig_3d, use_container_width=True)

if st.button("➡️ Proceed to Multi-Objective Optimization", use_container_width=True):
    st.switch_page("pages/06_Optimization.py")
