import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from engine.climate import load_climate_dataset, calculate_psychrometrics, calculate_degree_days
from engine.location_widget import render_location_sidebar_widget, render_location_selectbox

st.set_page_config(page_title="Shelter-AI — Climate Intelligence", page_icon="🌤️", layout="wide")

st.title("🌤️ Climate Intelligence & Micro-Climate Diagnostics")
st.caption("Historical analysis, extreme climate scenarios, diurnal heat waves, and passive architectural insights")

render_location_sidebar_widget()

df = load_climate_dataset()

# Climate Analytics Summary
t_mean = df["temperature"].mean()
t_max = df["temperature"].max()
t_min = df["temperature"].min()
hot_hours = int((df["temperature"] > 35.0).sum())
cold_hours = int((df["temperature"] < 15.0).sum())
high_solar_hours = int((df["solar_radiation"] > 700.0).sum())

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Annual Mean Temp", f"{t_mean:.1f} °C")
m2.metric("Peak Extreme Temp", f"{t_max:.1f} °C")
m3.metric("Min Winter Temp", f"{t_min:.1f} °C")
m4.metric("Hot Hours (>35°C)", f"{hot_hours} hrs")
m5.metric("Peak Solar Hours", f"{high_solar_hours} hrs")

st.markdown("---")

tab1, tab2, tab3 = st.tabs([
    "📈 Historical Diurnal & Solar Trends",
    "🌡️ Extreme Heat Stress Scenarios",
    "💡 Actionable Passive Design Insights"
])

with tab1:
    fig_temp = px.line(df.iloc[:720], x="datetime", y="temperature", title="30-Day Hourly Temperature Profile (°C)")
    fig_temp.update_traces(line_color="#e74c3c")
    fig_temp.update_layout(template="plotly_dark")
    st.plotly_chart(fig_temp, use_container_width=True)

    fig_solar = px.area(df.iloc[:720], x="datetime", y="solar_radiation", title="Solar Radiation (GHI W/m²)")
    fig_solar.update_traces(line_color="#f1c40f")
    fig_solar.update_layout(template="plotly_dark")
    st.plotly_chart(fig_solar, use_container_width=True)

with tab2:
    st.subheader("🔥 Extreme Climate Risk Scenarios")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.error("🔥 **EXTREME_HOT Scenario**: Peak $44.5^\\circ\\text{C}$ with severe $1050\\text{ W/m}^2$ solar flux.")
    with c2:
        st.warning("☀️ **NORMAL Scenario**: Diurnal swing $26^\\circ\\text{C} \\rightarrow 38^\\circ\\text{C}$.")
    with c3:
        st.info("❄️ **EXTREME_COLD Scenario**: Minimum $-2.0^\\circ\\text{C}$ with overcast skies.")

with tab3:
    st.subheader("🧠 Structured Climate Insights & Recommendations")
    st.markdown("""
    - 💡 **High Afternoon Solar Irradiation**: Critical thermal risk from roof surface. *Action: Mandate minimum 50mm continuous roof insulation.*
    - 💡 **Diurnal Temperature Swing ($>12^\\circ\\text{C}$)**: Strong thermal lag potential. *Action: High thermal mass walls (CSEB / Masonry) recommended.*
    - 💡 **Evening Wind Currents ($>3.5\\text{ m/s}$)**: High natural ventilation efficacy. *Action: Position operable cross-ventilation louvers on North-South facades.*
    """)

if st.button("➡️ Proceed to Parametric Design Lab", use_container_width=True):
    st.switch_page("pages/04_Design_Lab.py")
