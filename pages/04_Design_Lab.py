import streamlit as st
import pandas as pd
import numpy as np
from engine.geometry import ShelterGeometry
from engine.materials import get_materials_catalog, calculate_assembly_u_value
from engine.location_widget import render_location_sidebar_widget, render_location_selectbox
from visualization.shelter_3d import create_pyvista_3d_shelter, render_pyvista_3d_shelter

st.set_page_config(page_title="Shelter-AI — Design Lab", page_icon="🏗️", layout="wide")

st.title("🏗️ Parametric Shelter Design Lab")
st.caption("Define functional shelter requirements, spatial dimensions, material assemblies, and generate passive heuristics")

render_location_sidebar_widget()

# Initialize from session state if available
saved_design = st.session_state.get("current_design", {})
def_l = saved_design.get("length_m", 6.0)
def_w = saved_design.get("width_m", 4.0)
def_h = saved_design.get("height_m", 2.8)
def_roof_type = saved_design.get("roof_type", "pitched")
def_roof_pitch = saved_design.get("roof_pitch_deg", 15.0)
def_wall_mat = saved_design.get("wall_mat_id", "cseb_interlocking")
def_roof_mat = saved_design.get("roof_mat_id", "roof_cgi_insulated")
def_wall_thick = saved_design.get("wall_thickness_cm", 20.0)
def_wwr = saved_design.get("wwr_pct", 15.0)
def_overhang = saved_design.get("overhang_m", 0.6)
def_orientation = saved_design.get("orientation_deg", 0.0)
def_occupants = saved_design.get("occupants", 4)

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("1. Spatial Dimensions & Humanitarian Occupancy")
    occupants = st.slider("Target Occupants (Sphere 3.5m²/person standard)", 1, 12, int(def_occupants), 1)
    auto_size = st.checkbox("⚡ Auto-Size Footprint from Occupants", value=False)
    
    if auto_size:
        geom_auto = ShelterGeometry.from_occupants(occupants=occupants)
        length_m = st.slider("Length (m)", 3.0, 14.0, float(geom_auto.length), 0.5)
        width_m = st.slider("Width (m)", 2.5, 10.0, float(geom_auto.width), 0.5)
    else:
        length_m = st.slider("Length (m)", 3.0, 14.0, float(def_l), 0.5)
        width_m = st.slider("Width (m)", 2.5, 10.0, float(def_w), 0.5)
        
    height_m = st.slider("Ceiling Height (m)", 2.4, 4.5, float(def_h), 0.1)
    
    roof_idx = 0 if def_roof_type == "pitched" else (1 if def_roof_type == "monoslope" else 2)
    roof_type_label = st.selectbox("Roof Form", ["Pitched (Gable)", "Monoslope (Shed)", "Flat Slab"], index=roof_idx)
    roof_type_id = "pitched" if "Pitched" in roof_type_label else ("monoslope" if "Monoslope" in roof_type_label else "flat")
    roof_pitch_deg = st.slider("Roof Pitch (°)", 5.0, 45.0, float(def_roof_pitch), 2.5) if roof_type_id != "flat" else 0.0

with col2:
    st.subheader("2. Envelope Materials & Passive Parameters")
    df_mat = get_materials_catalog()
    wall_opts = df_mat[df_mat["category"] == "Wall"]["id"].tolist() if not df_mat.empty else ["cseb_interlocking"]
    roof_opts = df_mat[df_mat["category"] == "Roof"]["id"].tolist() if not df_mat.empty else ["roof_cgi_insulated"]
    
    w_idx = wall_opts.index(def_wall_mat) if def_wall_mat in wall_opts else 0
    r_idx = roof_opts.index(def_roof_mat) if def_roof_mat in roof_opts else 0
    
    wall_mat_id = st.selectbox("Wall Material", wall_opts, index=w_idx)
    wall_thickness_cm = st.slider("Wall Thickness (cm)", 10.0, 40.0, float(def_wall_thick), 2.5)
    
    roof_mat_id = st.selectbox("Roof Assembly", roof_opts, index=r_idx)
    ins_check = st.checkbox("Add Continuous Insulation Layer", value=True)
    ins_mat_id = "insulation_rockwool" if ins_check else None
    ins_thick_cm = st.slider("Insulation Thickness (cm)", 1.0, 10.0, 5.0, 0.5) if ins_check else 0.0
    
    wwr_pct = st.slider("Window-to-Wall Ratio (WWR %)", 5.0, 40.0, float(def_wwr), 1.0)
    overhang_m = st.slider("Overhang Shading Eave Depth (m)", 0.0, 1.5, float(def_overhang), 0.1)
    orientation_deg = st.slider("Orientation (° from North)", 0.0, 360.0, float(def_orientation), 15.0)

geom = ShelterGeometry(
    length_m=length_m, width_m=width_m, height_m=height_m,
    roof_type=roof_type_id, roof_pitch_deg=roof_pitch_deg,
    wall_thickness_cm=wall_thickness_cm, wwr_pct=wwr_pct,
    overhang_m=overhang_m, orientation_deg=orientation_deg
)

# Store persistent current design state
st.session_state["current_design"] = {
    "length_m": length_m,
    "width_m": width_m,
    "height_m": height_m,
    "roof_type": roof_type_id,
    "roof_pitch_deg": roof_pitch_deg,
    "wall_mat_id": wall_mat_id,
    "wall_thickness_cm": wall_thickness_cm,
    "roof_mat_id": roof_mat_id,
    "insulation_mat_id": ins_mat_id,
    "insulation_thickness_cm": ins_thick_cm,
    "glazing_mat_id": "glazing_single",
    "wwr_pct": wwr_pct,
    "overhang_m": overhang_m,
    "orientation_deg": orientation_deg,
    "occupants": occupants
}
st.session_state["geometry"] = geom

u_calc = calculate_assembly_u_value(wall_mat_id, wall_thickness_cm, ins_mat_id, ins_thick_cm)

st.markdown("---")
st.subheader("📐 Calculated Structural Summary")

s1, s2, s3, s4 = st.columns(4)
s1.metric("Usable Floor Area", f"{geom.floor_area()} m²", f"{geom.floor_area()/occupants:.1f} m²/person")
s2.metric("Gross Internal Volume", f"{geom.volume()} m³")
s3.metric("Surface/Volume Ratio", f"{geom.surface_to_volume_ratio():.3f} m⁻¹")
s4.metric("Wall Assembly U-Value", f"{u_calc['u_value_w_m2k']:.3f} W/m²K")

st.markdown("---")
st.subheader("🏢 Live 3D Parametric Blueprint Preview")
st.caption("3D model responds instantly to all dimension, roof, WWR, and orientation changes above.")

plotter_preview = create_pyvista_3d_shelter(
    geometry=geom,
    wall_mat=wall_mat_id,
    roof_mat=roof_mat_id,
    view_mode="architectural",
    hour_of_day=12.0,
    occupants=occupants,
    show_interior=True
)
render_pyvista_3d_shelter(plotter_preview, height=520)

if st.button("➡️ Proceed to 3D Digital Twin (Full Analysis & Thermal Heatmaps)", use_container_width=True):
    st.switch_page("pages/05_Digital_Twin.py")
