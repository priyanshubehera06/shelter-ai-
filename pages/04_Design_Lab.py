import streamlit as st
import pandas as pd
import numpy as np
from engine.geometry import ShelterGeometry
from engine.materials import get_materials_catalog, calculate_assembly_u_value
from engine.location_widget import render_location_sidebar_widget, render_location_selectbox

st.set_page_config(page_title="Shelter-AI — Design Lab", page_icon="🏗️", layout="wide")

st.title("🏗️ Parametric Shelter Design Lab")
st.caption("Define functional shelter requirements, spatial dimensions, material assemblies, and generate passive heuristics")

render_location_sidebar_widget()

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("1. Spatial Dimensions & Humanitarian Occupancy")
    occupants = st.slider("Target Occupants (Sphere 3.5m²/person standard)", 1, 12, 4, 1)
    auto_size = st.checkbox("⚡ Auto-Size Footprint from Occupants", value=False)
    
    if auto_size:
        geom_auto = ShelterGeometry.from_occupants(occupants=occupants)
        length_m = st.slider("Length (m)", 3.0, 14.0, float(geom_auto.length), 0.5)
        width_m = st.slider("Width (m)", 2.5, 10.0, float(geom_auto.width), 0.5)
    else:
        length_m = st.slider("Length (m)", 3.0, 14.0, 6.0, 0.5)
        width_m = st.slider("Width (m)", 2.5, 10.0, 4.0, 0.5)
        
    height_m = st.slider("Ceiling Height (m)", 2.4, 4.5, 2.8, 0.1)
    
    roof_type_label = st.selectbox("Roof Form", ["Pitched (Gable)", "Monoslope (Shed)", "Flat Slab"], index=0)
    roof_type_id = "pitched" if "Pitched" in roof_type_label else ("monoslope" if "Monoslope" in roof_type_label else "flat")
    roof_pitch_deg = st.slider("Roof Pitch (°)", 5.0, 45.0, 15.0, 2.5) if roof_type_id != "flat" else 0.0

with col2:
    st.subheader("2. Envelope Materials & Passive Parameters")
    df_mat = get_materials_catalog()
    wall_opts = df_mat[df_mat["category"] == "Wall"]["id"].tolist() if not df_mat.empty else ["cseb_interlocking"]
    roof_opts = df_mat[df_mat["category"] == "Roof"]["id"].tolist() if not df_mat.empty else ["roof_cgi_insulated"]
    
    wall_mat_id = st.selectbox("Wall Material", wall_opts, index=0)
    wall_thickness_cm = st.slider("Wall Thickness (cm)", 10.0, 40.0, 20.0, 2.5)
    
    roof_mat_id = st.selectbox("Roof Assembly", roof_opts, index=0)
    ins_check = st.checkbox("Add Continuous Insulation Layer", value=True)
    ins_mat_id = "insulation_rockwool" if ins_check else None
    ins_thick_cm = st.slider("Insulation Thickness (cm)", 1.0, 10.0, 5.0, 0.5) if ins_check else 0.0
    
    wwr_pct = st.slider("Window-to-Wall Ratio (WWR %)", 5.0, 40.0, 15.0, 1.0)
    overhang_m = st.slider("Overhang Shading Eave Depth (m)", 0.0, 1.5, 0.6, 0.1)
    orientation_deg = st.slider("Orientation (° from North)", 0.0, 360.0, 0.0, 15.0)

geom = ShelterGeometry(
    length_m=length_m, width_m=width_m, height_m=height_m,
    roof_type=roof_type_id, roof_pitch_deg=roof_pitch_deg,
    wall_thickness_cm=wall_thickness_cm, wwr_pct=wwr_pct,
    overhang_m=overhang_m, orientation_deg=orientation_deg
)

u_calc = calculate_assembly_u_value(wall_mat_id, wall_thickness_cm, ins_mat_id, ins_thick_cm)

st.markdown("---")
st.subheader("📐 Calculated Structural Summary")

s1, s2, s3, s4 = st.columns(4)
s1.metric("Usable Floor Area", f"{geom.floor_area()} m²", f"{geom.floor_area()/occupants:.1f} m²/person")
s2.metric("Gross Internal Volume", f"{geom.volume()} m³")
s3.metric("Surface/Volume Ratio", f"{geom.surface_to_volume_ratio():.3f} m⁻¹")
s4.metric("Wall Assembly U-Value", f"{u_calc['u_value_w_m2k']:.3f} W/m²K")

if st.button("➡️ Proceed to 3D Digital Twin", use_container_width=True):
    st.switch_page("pages/05_Digital_Twin.py")
