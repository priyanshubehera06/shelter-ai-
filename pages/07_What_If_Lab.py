import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from engine.geometry import ShelterGeometry
from engine.thermal import compare_thermal_scenarios
from engine.climate import get_climate_profile
from engine.materials import get_materials_catalog
from engine.location_widget import render_location_sidebar_widget

st.set_page_config(page_title="Shelter-AI — What-If Sensitivity Lab", page_icon="🔄", layout="wide")

st.title("🔄 What-If Sensitivity & Scenario Lab")
st.caption("Change envelope parameters, roofing assemblies, insulation thickness, or orientations and see the immediate difference in indoor conditions")

render_location_sidebar_widget()

climate_records = get_climate_profile(month=5)
df_mat = get_materials_catalog()
roof_opts = df_mat[df_mat["category"] == "Roof"]["id"].tolist() if not df_mat.empty else ["roof_cgi_sheet", "roof_cgi_insulated", "roof_concrete_slab"]
wall_opts = df_mat[df_mat["category"] == "Wall"]["id"].tolist() if not df_mat.empty else ["brick_standard", "cseb_interlocking"]

geom = ShelterGeometry(length_m=6.0, width_m=4.0, height_m=2.8)

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔴 BASELINE DESIGN")
    base_wall = st.selectbox("Baseline Wall", wall_opts, index=0, key="w_base")
    base_roof = st.selectbox("Baseline Roof", roof_opts, index=0, key="r_base")
    base_ins = st.checkbox("Add Baseline Insulation", value=False, key="i_base_chk")
    base_ins_id = "insulation_rockwool" if base_ins else None
    base_ins_thick = st.slider("Baseline Insulation (cm)", 0.0, 10.0, 0.0, 0.5, key="i_base_sl")

with col2:
    st.subheader("🟢 MODIFIED SCENARIO")
    mod_wall = st.selectbox("Modified Wall", wall_opts, index=min(1, len(wall_opts)-1), key="w_mod")
    mod_roof = st.selectbox("Modified Roof", roof_opts, index=min(1, len(roof_opts)-1), key="r_mod")
    mod_ins = st.checkbox("Add Modified Insulation", value=True, key="i_mod_chk")
    mod_ins_id = "insulation_rockwool" if mod_ins else None
    mod_ins_thick = st.slider("Modified Insulation (cm)", 0.0, 10.0, 5.0, 0.5, key="i_mod_sl")

base_cfg = {
    "wall_mat_id": base_wall,
    "wall_thickness_cm": 20.0,
    "roof_mat_id": base_roof,
    "glazing_mat_id": "glazing_single",
    "insulation_mat_id": base_ins_id,
    "insulation_thickness_cm": base_ins_thick,
}

mod_cfg = {
    "wall_mat_id": mod_wall,
    "wall_thickness_cm": 20.0,
    "roof_mat_id": mod_roof,
    "glazing_mat_id": "glazing_single",
    "insulation_mat_id": mod_ins_id,
    "insulation_thickness_cm": mod_ins_thick,
}

comp_res = compare_thermal_scenarios(geom, base_cfg, mod_cfg, climate_records=climate_records)

m1, m2, m3 = st.columns(3)
m1.metric("Peak Temp Reduction", f"{comp_res['peak_temperature_drop_c']:+.1f} °C")
m2.metric("Average Temp Reduction", f"{comp_res['avg_temperature_drop_c']:+.1f} °C")
m3.metric("Overheating Hours Avoided (>30°C)", f"{max(0, comp_res['discomfort_hours_reduced'])} hrs")

st.success(comp_res["summary_statement"])

fig_comp = go.Figure()
hours_arr = [f"{h:02d}:00" for h in range(24)]
fig_comp.add_trace(go.Scatter(x=hours_arr, y=comp_res["baseline_simulation"]["t_indoor"], name=f"Baseline ({base_roof})", line=dict(color="#e74c3c", width=3)))
fig_comp.add_trace(go.Scatter(x=hours_arr, y=comp_res["modified_simulation"]["t_indoor"], name=f"Modified ({mod_roof})", line=dict(color="#2ecc71", width=3)))
fig_comp.add_trace(go.Scatter(x=hours_arr, y=comp_res["baseline_simulation"]["t_outdoor"], name="Outdoor Ambient", line=dict(color="#95a5a6", width=2, dash="dot")))
fig_comp.update_layout(title="Baseline vs. Modified Indoor Temperature Trajectory", template="plotly_dark", margin=dict(l=20, r=20, t=40, b=20))
st.plotly_chart(fig_comp, use_container_width=True)

if st.button("➡️ Proceed to Final Recommended Results", use_container_width=True):
    st.switch_page("pages/08_Results.py")
