import streamlit as st

st.set_page_config(
    page_title="Shelter-AI — Intelligent Climate-Adaptive Shelter Platform",
    page_icon="🏡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏡 SHELTER-AI")
st.markdown("### Intelligent Climate-Adaptive Shelter Design & Decision-Support Platform")
st.caption("Physics-based transient simulation, multi-objective optimization, and explainable generative engineering")

st.markdown("""
---
#### 🔄 Core Platform Workflow Pipeline
""")

col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("""
    **1. 📍 Location & Climate Intelligence**
    - High-resolution climate parsing & extreme weather analysis
    - Diurnal temperature cycles, solar irradiation, and psychrometrics
    - Real-time GPS and fallback climate datasets
    """)
with col2:
    st.markdown("""
    **2. 🏠 Passive Design & Digital Twin**
    - Passive architectural heuristics (orientation, shading, thermal mass)
    - 3D interactive mesh blueprint & envelope U-values
    - Multi-application evaluation (Humans, Livestock, Agricultural Storage)
    """)
with col3:
    st.markdown("""
    **3. ⚡ Multi-Objective Optimization & Explainability**
    - Transient lumped RC thermal simulation (Hourly heat flux balance)
    - NSGA-II / Pareto optimization (Comfort vs Energy vs Cost)
    - Explainable AI recommendations & PDF engineering reports
    """)

st.markdown("---")

c_btn1, c_btn2, c_btn3 = st.columns(3)
with c_btn1:
    if st.button("📍 Start with Location & Climate (Page 02)", use_container_width=True):
        st.switch_page("pages/02_Location.py")
with c_btn2:
    if st.button("🏗️ Open Parametric Design Lab (Page 04)", use_container_width=True):
        st.switch_page("pages/04_Design_Lab.py")
with c_btn3:
    if st.button("🎯 Run Pareto Optimization (Page 06)", use_container_width=True):
        st.switch_page("pages/06_Optimization.py")
