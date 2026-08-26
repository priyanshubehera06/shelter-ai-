"""
app.py — Main Entrypoint for SHELTER-AI Platform.
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
            • Diurnal heat wave analytics<br/>
            • Passive architectural heuristics<br/>
            • Parametric geometry & materials
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🏗️ Open Design Lab", use_container_width=True):
        st.switch_page("pages/04_Design_Lab.py")

with col3:
    st.markdown("""
    <div style="background:#1e272e;padding:12px;border-radius:8px;border-top:4px solid #3498db;min-height:160px;">
        <h4 style="color:#3498db;margin:0 0 6px 0;">05. Twin & 06. Optimize</h4>
        <p style="font-size:12px;color:#bdc3c7;">
            • 3D parametric digital twin<br/>
            • 24-hr Sol-Air thermal heatmaps<br/>
            • NSGA-II Pareto optimization
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🎯 Open Optimization", use_container_width=True):
        st.switch_page("pages/06_Optimization.py")

with col4:
    st.markdown("""
    <div style="background:#1e272e;padding:12px;border-radius:8px;border-top:4px solid #e74c3c;min-height:160px;">
        <h4 style="color:#e74c3c;margin:0 0 6px 0;">07. What-If & 08. Results</h4>
        <p style="font-size:12px;color:#bdc3c7;">
            • Interactive scenario comparator<br/>
            • Top 4 recommended designs<br/>
            • Certified engineering report export
        </p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🏆 View Final Results", use_container_width=True):
        st.switch_page("pages/08_Results.py")

st.markdown("---")
st.info("💡 **Tip:** Use the sidebar on the left to navigate directly across all 8 specialized analytical engineering pages.")