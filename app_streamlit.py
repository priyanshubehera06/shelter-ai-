"""
app_streamlit.py — Streamlit UI Entrypoint for SHELTER-AI Platform.
Intelligent Climate-Adaptive Shelter Design and Decision-Support Platform.
"""

import streamlit as st
import pandas as pd
from engine.location_widget import render_location_sidebar_widget, initialize_auto_location

st.set_page_config(
    page_title="SHELTER-AI — Intelligent Climate-Adaptive Shelter Platform",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize global auto-location and state
initialize_auto_location()
render_location_sidebar_widget()

st.title("🏡 SHELTER-AI")
st.markdown("### Intelligent Climate-Adaptive Shelter Design & Decision-Support Platform")
st.caption("Physics-based transient simulation, multi-objective optimization, and explainable generative engineering")

st.markdown("""
---
### 🗺️ Platform Workflow Architecture

Select a module from the **Sidebar Navigation** or click any stage below:
""")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div style="background:#1e272e;padding:12px;border-radius:8px;border-top:4px solid #1abc9c;min-height:160px;">
        <h4 style="color:#1abc9c;margin:0 0 6px 0;">01. Home & 02. Location</h4>
        <p style="font-size:12px;color:#bdc3c7;">
            • Target location selection<br/>
            • Live GPS geocoding<br/>
            • Climate CSV ingestion & validation
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📍 Open Location Setup", use_container_width=True):
        st.switch_page("pages/02_Location.py")

with col2:
    st.markdown("""
    <div style="background:#1e272e;padding:12px;border-radius:8px;border-top:4px solid #f39c12;min-height:160px;">
        <h4 style="color:#f39c12;margin:0 0 6px 0;">03. Climate & 04. Design</h4>
        <p style="font-size:12px;color:#bdc3c7;">
            • Diurnal microclimate analytics<br/>
            • Parametric geometry & orientation<br/>
            • Multi-layered material envelope
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🏛️ Open Design Lab", use_container_width=True):
        st.switch_page("pages/04_Shelter_Design.py")

with col3:
    st.markdown("""
    <div style="background:#1e272e;padding:12px;border-radius:8px;border-top:4px solid #e74c3c;min-height:160px;">
        <h4 style="color:#e74c3c;margin:0 0 6px 0;">05. Simulation & 06. Twin</h4>
        <p style="font-size:12px;color:#bdc3c7;">
            • 3R2C state-space thermal RC solver<br/>
            • Adaptive PMV / PPD comfort index<br/>
            • Interactive 3D Digital Twin model
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🔥 Open Thermal Sim", use_container_width=True):
        st.switch_page("pages/05_Thermal_Simulation.py")

with col4:
    st.markdown("""
    <div style="background:#1e272e;padding:12px;border-radius:8px;border-top:4px solid #9b59b6;min-height:160px;">
        <h4 style="color:#9b59b6;margin:0 0 6px 0;">07. Optimization & 08. Results</h4>
        <p style="font-size:12px;color:#bdc3c7;">
            • Genetic Pareto-optimal search<br/>
            • CapEx budget & carbon footprint<br/>
            • Comprehensive decision report
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("⚡ Open AI Optimizer", use_container_width=True):
        st.switch_page("pages/07_Optimization.py")
