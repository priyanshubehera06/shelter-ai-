"""
location_widget.py — Unified Location Selection, Browser GPS, and Live Climate Synchronizer for Shelter-AI.
Ensures single-source-of-truth real-time synchronization of target cities, coordinates, climate zone classification,
and micro-climate profiles across all platform pages without conflicting resets.
"""

from typing import Dict, List, Optional, Any, Tuple
import streamlit as st
import streamlit.components.v1 as components
from engine.geolocation import (
    auto_detect_location_and_data,
    MAJOR_INDIAN_CITIES,
    classify_climate_zone,
    recommend_shelter_preset,
    fetch_live_climate_profile,
)


def render_gps_button():
    """Render an HTML5 browser geolocation button."""
    html_code = """
    <div style="font-family: sans-serif; text-align: center; margin-top: 5px;">
        <button id="gps-btn" onclick="getLocation()" style="
            background: linear-gradient(135deg, #16a085, #1abc9c);
            color: white; border: none; padding: 8px 14px;
            border-radius: 6px; font-weight: 600; font-size: 13px;
            cursor: pointer; width: 100%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2); transition: all 0.3s ease;">
            🎯 Use Precise Browser GPS Location
        </button>
        <div id="gps-status" style="font-size: 11px; color: #bdc3c7; margin-top: 4px;"></div>
    </div>
    <script>
    function getLocation() {
        var status = document.getElementById("gps-status");
        var btn = document.getElementById("gps-btn");
        if (navigator.geolocation) {
            status.innerText = "Requesting GPS coordinates...";
            btn.disabled = true; btn.style.opacity = "0.7";
            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    var lat = pos.coords.latitude;
                    var lon = pos.coords.longitude;
                    status.innerText = "GPS acquired! Updating...";
                    var url = new URL(window.parent.location.href);
                    url.searchParams.set("lat", lat);
                    url.searchParams.set("lon", lon);
                    url.searchParams.set("gps_triggered", "true");
                    window.parent.location.href = url.href;
                },
                function(err) {
                    status.innerText = "GPS Error: " + err.message + ". Falling back to IP.";
                    btn.disabled = false; btn.style.opacity = "1";
                },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 0 }
            );
        } else {
            status.innerText = "Geolocation not supported.";
        }
    }
    </script>
    """
    components.html(html_code, height=65)


def get_city_geo_data(city_key: str) -> Dict[str, Any]:
    """Builds complete geo_data profile for a specific Indian city key."""
    if city_key not in MAJOR_INDIAN_CITIES:
        return auto_detect_location_and_data()

    info = MAJOR_INDIAN_CITIES[city_key]
    lat = float(info["lat"])
    lon = float(info["lon"])
    city = info.get("city", city_key.split(",")[0])
    state = info.get("state", "")
    zone = info.get("zone", "Composite")

    # Try fetching live/interpolated records for this city
    records = fetch_live_climate_profile(lat, lon)
    if not records:
        from engine.climate import get_climate_profile
        records = get_climate_profile("sambalpur", month=5)

    temps = [r["dry_bulb_temp_c"] for r in records]
    rhs = [r["relative_humidity_pct"] for r in records]
    ghis = [r["solar_ghi_w_m2"] for r in records]
    winds = [r["wind_speed_m_s"] for r in records]

    # Adjust temperature range based on zone
    if "Cold" in zone:
        temps = [t - 18.0 for t in temps]
        for r, t in zip(records, temps):
            r["dry_bulb_temp_c"] = round(t, 1)
            r["temperature"] = round(t, 1)
    elif "Arid" in zone:
        temps = [t + 4.0 for t in temps]
        rhs = [max(15.0, h - 25.0) for h in rhs]
        for r, t, h in zip(records, temps, rhs):
            r["dry_bulb_temp_c"] = round(t, 1)
            r["temperature"] = round(t, 1)
            r["relative_humidity_pct"] = round(h, 1)
            r["humidity"] = round(h, 1)
    elif "Humid" in zone:
        rhs = [min(95.0, h + 20.0) for h in rhs]
        for r, h in zip(records, rhs):
            r["relative_humidity_pct"] = round(h, 1)
            r["humidity"] = round(h, 1)

    preset = recommend_shelter_preset(zone)
    loc_display = f"{city}" + (f", {state}" if state else "")

    return {
        "status": "success",
        "location_name": loc_display,
        "city": city,
        "region": state,
        "country": "India",
        "lat": lat,
        "lon": lon,
        "source": "Indian Cities Catalog",
        "climate_zone": zone,
        "climate_records": records,
        "summary": {
            "t_max": round(max(temps), 1),
            "t_min": round(min(temps), 1),
            "t_avg": round(sum(temps) / len(temps), 1),
            "rh_avg": round(sum(rhs) / len(rhs), 0),
            "ghi_peak": round(max(ghis), 1),
            "wind_avg": round(sum(winds) / len(winds), 1),
        },
        "recommended_preset": preset,
    }


def set_active_location(chosen_key: str):
    """Sets the active location and updates auto_geo_data immediately."""
    st.session_state["global_selected_location"] = chosen_key
    if chosen_key == "__current__":
        if "base_live_geo" not in st.session_state:
            st.session_state["base_live_geo"] = auto_detect_location_and_data()
        st.session_state["auto_geo_data"] = st.session_state["base_live_geo"]
    else:
        st.session_state["auto_geo_data"] = get_city_geo_data(chosen_key)


def initialize_auto_location() -> Dict[str, Any]:
    """Populates session state with geolocated climate data once per session."""
    params = st.query_params
    custom_lat = params.get("lat")
    custom_lon = params.get("lon")

    if "base_live_geo" not in st.session_state or custom_lat or custom_lon:
        if custom_lat and custom_lon:
            try:
                st.session_state["base_live_geo"] = auto_detect_location_and_data(
                    float(custom_lat), float(custom_lon)
                )
            except Exception:
                st.session_state["base_live_geo"] = auto_detect_location_and_data()
        else:
            st.session_state["base_live_geo"] = auto_detect_location_and_data()

    if "auto_geo_data" not in st.session_state:
        current_choice = st.session_state.get("global_selected_location", "__current__")
        set_active_location(current_choice)

    return st.session_state["auto_geo_data"]


def _build_all_options(live_label: str) -> Tuple[List[str], Dict[str, str]]:
    """Returns (keys_list, display_map) for the selectbox."""
    all_keys = ["__current__"] + list(MAJOR_INDIAN_CITIES.keys())
    display_map = {"__current__": live_label}
    for key, info in MAJOR_INDIAN_CITIES.items():
        city = info.get("city", key.replace("_", " ").title())
        state = info.get("state", "")
        zone = info.get("zone", "")
        display_map[key] = f"{city} — {state} ({zone})"
    return all_keys, display_map


def _on_location_select_change(widget_key: str):
    """Callback when any selectbox changes."""
    selected_val = st.session_state.get(widget_key)
    if selected_val:
        set_active_location(selected_val)


def render_location_selectbox(label="🏙️ Select City / Region", sidebar=False, key="location_select") -> Tuple[str, str]:
    """
    Renders a searchable selectbox of all major Indian cities.
    Synchronizes across all widgets via global_selected_location and on_change callback.
    """
    initialize_auto_location()
    base_live = st.session_state.get("base_live_geo", {})
    live_label = f"📍 Current Location: {base_live.get('location_name', 'Live Weather')} (Live GPS/IP)"

    all_keys, display_map = _build_all_options(live_label)

    # Determine default index from global_selected_location
    active_key = st.session_state.get("global_selected_location", "__current__")
    default_idx = all_keys.index(active_key) if active_key in all_keys else 0

    widget = st.sidebar.selectbox if sidebar else st.selectbox

    chosen_key = widget(
        label,
        options=all_keys,
        format_func=lambda k: display_map.get(k, k),
        index=default_idx,
        key=key,
        on_change=_on_location_select_change,
        args=(key,),
        help="Type to search by city name, state, or climate zone"
    )

    # If key was loaded without on_change firing yet, sync state
    if st.session_state.get("global_selected_location") != chosen_key:
        set_active_location(chosen_key)

    if chosen_key == "__current__":
        return "current_location", live_label
    return chosen_key, display_map.get(chosen_key, chosen_key)


def render_location_sidebar_widget():
    """
    Renders the full location sidebar:
    - Searchable city selectbox
    - Detected location & Climate Zone card
    - Auto-detect IP & GPS buttons
    """
    st.sidebar.markdown("### 📍 Location & Climate Zone")

    # Render the selectbox directly inside sidebar
    render_location_selectbox(label="🏙️ Target Region / City", sidebar=True, key="sidebar_city_select")

    geo_data = st.session_state.get("auto_geo_data", initialize_auto_location())

    col_btn1, col_btn2 = st.sidebar.columns(2)
    with col_btn1:
        if st.sidebar.button("🔄 Reset to Live IP", use_container_width=True):
            with st.spinner("Detecting..."):
                st.session_state["base_live_geo"] = auto_detect_location_and_data()
                set_active_location("__current__")
                st.rerun()
    with col_btn2:
        if st.sidebar.button("⚡ Apply Presets", use_container_width=True):
            preset = geo_data["recommended_preset"]
            st.session_state["preset_wall"] = preset["wall"]
            st.session_state["preset_roof"] = preset["roof"]
            st.session_state["preset_thickness"] = preset["thickness"]
            st.sidebar.success("✅ Preset applied!")
            st.rerun()

    render_gps_button()

    # Location & Climate Zone info card
    summary = geo_data.get("summary", {})
    preset = geo_data.get("recommended_preset", {})
    zone = geo_data.get("climate_zone", "Composite")
    zone_color = "#3498db" if "Cold" in zone else ("#e74c3c" if "Arid" in zone else "#2ecc71")

    st.sidebar.markdown(f"""
    <div style="background:#1e272e;padding:10px 14px;border-radius:8px;
                border-left:5px solid {zone_color};margin:8px 0;">
        <div style="font-size:13px;font-weight:700;color:#1abc9c;">
            📍 {geo_data.get('location_name')}</div>
        <div style="font-size:11px;color:#bdc3c7;">
            Source: <b>{geo_data.get('source')}</b>
            (Lat: {geo_data.get('lat', 20.0):.2f}, Lon: {geo_data.get('lon', 78.0):.2f})</div>
        <div style="font-size:13px;margin-top:5px;color:#f39c12;font-weight:700;">
            🌤️ Climate Zone: <span style="color:{zone_color};">{zone}</span></div>
        <div style="font-size:11px;color:#ecf0f1;margin-top:3px;">
            🌡️ <b>{summary.get('t_min', 18)}°C – {summary.get('t_max', 38)}°C</b> &nbsp;|&nbsp;
            RH: <b>{summary.get('rh_avg', 50)}%</b><br/>
            ☀️ GHI: <b>{summary.get('ghi_peak', 900)} W/m²</b> &nbsp;|&nbsp;
            Wind: <b>{summary.get('wind_avg', 3.0)} m/s</b>
        </div>
        <div style="font-size:11px;color:#2ecc71;margin-top:4px;">
            💡 Recommended: <b>{preset.get('wall', 'cseb_interlocking').replace('_',' ').title()}</b> ({preset.get('thickness', 20)}cm)
        </div>
    </div>
    """, unsafe_allow_html=True)


def get_location_options(search_query=None):
    """Legacy helper for backward compatibility."""
    geo_data = initialize_auto_location()
    live_label = f"📍 Current Location: {geo_data['location_name']} (Live Weather)"
    all_keys = list(MAJOR_INDIAN_CITIES.keys())
    return [live_label] + all_keys
