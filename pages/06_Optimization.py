import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from engine.optimizer import run_pareto_optimization
from engine.climate import get_climate_profile
from engine.location_widget import render_location_sidebar_widget

st.set_page_config(page_title="Shelter-AI — Multi-Objective Optimization", page_icon="🎯", layout="wide")

st.title("🎯 Multi-Objective Pareto Optimization (NSGA-II)")
st.caption("Simultaneously optimizes Thermal Comfort (Maximize), Operational Energy Demand (Minimize), and CapEx Construction Cost (Minimize)")

render_location_sidebar_widget()

climate_records = get_climate_profile(month=5)

st.sidebar.header("Optimization Objective Weights")
w_comfort = st.sidebar.slider("Weight: Thermal Comfort", 0.0, 1.0, 0.4, 0.05)
w_cost = st.sidebar.slider("Weight: Construction CapEx", 0.0, 1.0, 0.3, 0.05)
w_carbon = st.sidebar.slider("Weight: Embodied Carbon / Energy", 0.0, 1.0, 0.3, 0.05)

if st.button("🚀 Run Pareto Multi-Objective Search", use_container_width=True):
    with st.spinner("Evaluating multi-objective design space across transient thermal cycles..."):
        opt_res = run_pareto_optimization(
            climate_records=climate_records,
            w_comfort=w_comfort,
            w_cost=w_cost,
            w_carbon=w_carbon,
            population_size=30
        )
        st.session_state["opt_results"] = opt_res
        st.success(f"Discovered **{len(opt_res['pareto_front'])}** non-dominated Pareto-optimal shelter design solutions!")

if "opt_results" in st.session_state:
    res = st.session_state["opt_results"]
    df_all = pd.DataFrame([
        {
            "Cost (INR ₹)": item["cost_inr"],
            "Embodied Carbon (kg)": item["carbon_kg"],
            "PMV Discomfort Error": item["discomfort_pmv"],
            "Avg Indoor Temp (°C)": item["avg_indoor_temp"],
            "Wall Material": item["candidate"]["wall_mat_id"],
            "Roof Material": item["candidate"]["roof_mat_id"],
            "Is Pareto Optimal": "🏆 Non-Dominated (Pareto Front)" if item.get("is_pareto") else "Candidate Design"
        }
        for item in res["all_candidates"]
    ])
    
    fig_pareto = px.scatter_3d(
        df_all,
        x="Cost (INR ₹)",
        y="Embodied Carbon (kg)",
        z="PMV Discomfort Error",
        color="Is Pareto Optimal",
        hover_data=["Wall Material", "Roof Material", "Avg Indoor Temp (°C)"],
        title="3D Pareto Optimal Design Space (Cost vs Carbon vs Discomfort)"
    )
    fig_pareto.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=40, b=10))
    st.plotly_chart(fig_pareto, use_container_width=True)

if st.button("➡️ Proceed to What-If Sensitivity Lab", use_container_width=True):
    st.switch_page("pages/07_What_If_Lab.py")
