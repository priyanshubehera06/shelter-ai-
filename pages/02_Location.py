"""
02_Location.py — Target Location Selection, Live Geocoding & Climate Dataset Ingestion for Shelter-AI.
"""

import streamlit as st
import pandas as pd
from engine.climate import load_climate_dataset, validate_climate_data
from engine.location_widget import render_location_sidebar_widget, render_location_selectbox

st.set_page_config(page_title="Shelter-AI — Location & Climate Setup", page_icon="📍", layout="wide")

st.title("📍 Location & Climate Data Setup")
st.caption("Select your target location, acquire live/historical weather data, or upload custom climate files")

render_location_sidebar_widget()

col1, col2 = st.columns([1.2, 1])

with col1:
    st.subheader("1. Target City & Climate Zone Classification")
    loc_id, loc_name = render_location_selectbox(label="Select City or Region (Indian Catalog / Live GPS)", sidebar=False, key="page2_city_dropdown")
    
    geo_data = st.session_state.get("auto_geo_data", {})
    if geo_data:
        zone = geo_data.get("climate_zone", "Composite")
        zone_color = "#3498db" if "Cold" in zone else ("#e74c3c" if "Arid" in zone else "#2ecc71")
        
        st.markdown(f"""
        <div style="background:#1e272e;padding:14px;border-radius:8px;border-left:5px solid {zone_color};margin-top:10px;">
            <h4 style="margin:0 0 6px 0;color:#1abc9c;">📍 Active Target: {geo_data.get('location_name')}</h4>
            <p style="margin:0;font-size:13px;color:#bdc3c7;">Coordinates: <b>Lat {geo_data.get('lat', 20.0):.2f}°, Lon {geo_data.get('lon', 78.0):.2f}°</b> | Source: <b>{geo_data.get('source')}</b></p>
            <h3 style="margin:8px 0 0 0;color:{zone_color};">🌤️ Climate Zone: {zone}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        summary = geo_data.get("summary", {})
        if summary:
            st.markdown("---")
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Peak Summer Temp", f"{summary.get('t_max', 38.0)} °C")
            m2.metric("Min Winter Temp", f"{summary.get('t_min', 18.0)} °C")
            m3.metric("Average Humidity", f"{summary.get('rh_avg', 55)} %")
            m4.metric("Peak Solar GHI", f"{summary.get('ghi_peak', 900)} W/m²")

with col2:
    st.subheader("2. Climate Data Source & Ingestion")
    data_source = st.radio("Climate Data Ingestion Mode:", ["Standard Built-In / Live Stream", "Upload Custom CSV Dataset"], horizontal=True)
    
    uploaded_file = None
    if "Upload" in data_source:
        uploaded_file = st.file_uploader("Upload Climate CSV (datetime, temp, humidity, solar, wind)", type=["csv"])
        if uploaded_file:
            try:
                raw_df = pd.read_csv(uploaded_file)
                is_valid, msgs = validate_climate_data(raw_df)
                if is_valid:
                    st.success("✅ Custom climate dataset uploaded and validated successfully!")
                else:
                    st.error(f"❌ Validation issues: {'; '.join(msgs)}")
            except Exception as e:
                st.error(f"Error reading file: {e}")

df_climate = load_climate_dataset(uploaded_file=uploaded_file)

st.markdown("---")
st.subheader("📊 Standardized Climate Data Preview")

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Records", f"{len(df_climate):,} hours")
m2.metric("Mean Annual Temp", f"{df_climate['temperature'].mean():.1f} °C")
m3.metric("Max Recorded Temp", f"{df_climate['temperature'].max():.1f} °C")
m4.metric("Average RH", f"{df_climate['humidity'].mean():.0f} %")

st.dataframe(df_climate.head(100), use_container_width=True)

if st.button("➡️ Proceed to Climate Intelligence Diagnostics", use_container_width=True):
    st.switch_page("pages/03_Climate_Intelligence.py")
