import urllib.request
import json
import datetime

MAJOR_INDIAN_CITIES = {
    # --- UNION TERRITORIES ---
    "New Delhi, Delhi (UT - Composite)": {"lat": 28.6139, "lon": 77.2090, "city": "New Delhi", "state": "Delhi", "type": "Union Territory", "zone": "Composite"},
    "Chandigarh, Chandigarh (UT - Composite)": {"lat": 30.7333, "lon": 76.7794, "city": "Chandigarh", "state": "Chandigarh", "type": "Union Territory", "zone": "Composite"},
    "Srinagar, Jammu & Kashmir (UT - Cold)": {"lat": 34.0837, "lon": 74.7973, "city": "Srinagar", "state": "Jammu & Kashmir", "type": "Union Territory", "zone": "Cold & High-Altitude"},
    "Jammu, Jammu & Kashmir (UT - Subtropical)": {"lat": 32.7266, "lon": 74.8570, "city": "Jammu", "state": "Jammu & Kashmir", "type": "Union Territory", "zone": "Composite"},
    "Leh, Ladakh (UT - Cold & High-Altitude)": {"lat": 34.1526, "lon": 77.5771, "city": "Leh", "state": "Ladakh", "type": "Union Territory", "zone": "Cold & High-Altitude"},
    "Kargil, Ladakh (UT - Cold)": {"lat": 34.5539, "lon": 76.1349, "city": "Kargil", "state": "Ladakh", "type": "Union Territory", "zone": "Cold & High-Altitude"},
    "Puducherry, Puducherry (UT - Hot & Humid)": {"lat": 11.9416, "lon": 79.8083, "city": "Puducherry", "state": "Puducherry", "type": "Union Territory", "zone": "Hot & Humid"},
    "Port Blair, Andaman & Nicobar (UT - Tropical)": {"lat": 11.6234, "lon": 92.7265, "city": "Port Blair", "state": "Andaman and Nicobar Islands", "type": "Union Territory", "zone": "Hot & Humid"},
    "Daman, Dadra & Nagar Haveli & Daman & Diu (UT)": {"lat": 20.3974, "lon": 72.8328, "city": "Daman", "state": "Dadra and Nagar Haveli and Daman and Diu", "type": "Union Territory", "zone": "Hot & Humid"},
    "Kavaratti, Lakshadweep (UT - Tropical)": {"lat": 10.5669, "lon": 72.6420, "city": "Kavaratti", "state": "Lakshadweep", "type": "Union Territory", "zone": "Hot & Humid"},

    # --- STATES ---
    # Andhra Pradesh
    "Visakhapatnam, Andhra Pradesh (Hot & Humid)": {"lat": 17.6868, "lon": 83.2185, "city": "Visakhapatnam", "state": "Andhra Pradesh", "type": "State", "zone": "Hot & Humid"},
    "Vijayawada, Andhra Pradesh (Hot & Humid)": {"lat": 16.5062, "lon": 80.6480, "city": "Vijayawada", "state": "Andhra Pradesh", "type": "State", "zone": "Hot & Humid"},
    "Tirupati, Andhra Pradesh (Hot & Semi-Arid)": {"lat": 13.6288, "lon": 79.4192, "city": "Tirupati", "state": "Andhra Pradesh", "type": "State", "zone": "Hot & Arid"},

    # Arunachal Pradesh
    "Itanagar, Arunachal Pradesh (Temperate / Mountain)": {"lat": 27.0844, "lon": 93.6053, "city": "Itanagar", "state": "Arunachal Pradesh", "type": "State", "zone": "Cold & High-Altitude"},

    # Assam
    "Guwahati, Assam (Warm & Humid)": {"lat": 26.1445, "lon": 91.7362, "city": "Guwahati", "state": "Assam", "type": "State", "zone": "Warm & Humid"},
    "Silchar, Assam (Warm & Humid)": {"lat": 24.8333, "lon": 92.7789, "city": "Silchar", "state": "Assam", "type": "State", "zone": "Warm & Humid"},
    "Dibrugarh, Assam (Warm & Humid)": {"lat": 27.4728, "lon": 94.9120, "city": "Dibrugarh", "state": "Assam", "type": "State", "zone": "Warm & Humid"},

    # Bihar
    "Patna, Bihar (Composite)": {"lat": 25.5941, "lon": 85.1376, "city": "Patna", "state": "Bihar", "type": "State", "zone": "Composite"},
    "Gaya, Bihar (Hot & Arid)": {"lat": 24.7955, "lon": 85.0002, "city": "Gaya", "state": "Bihar", "type": "State", "zone": "Hot & Arid"},
    "Muzaffarpur, Bihar (Composite)": {"lat": 26.1209, "lon": 85.3647, "city": "Muzaffarpur", "state": "Bihar", "type": "State", "zone": "Composite"},

    # Chhattisgarh
    "Raipur, Chhattisgarh (Composite)": {"lat": 21.2514, "lon": 81.6296, "city": "Raipur", "state": "Chhattisgarh", "type": "State", "zone": "Composite"},
    "Bilaspur, Chhattisgarh (Composite)": {"lat": 22.0797, "lon": 82.1391, "city": "Bilaspur", "state": "Chhattisgarh", "type": "State", "zone": "Composite"},

    # Goa
    "Panaji, Goa (Hot & Humid)": {"lat": 15.4909, "lon": 73.8278, "city": "Panaji", "state": "Goa", "type": "State", "zone": "Hot & Humid"},
    "Margao, Goa (Hot & Humid)": {"lat": 15.2736, "lon": 73.9581, "city": "Margao", "state": "Goa", "type": "State", "zone": "Hot & Humid"},

    # Gujarat
    "Ahmedabad, Gujarat (Hot & Arid)": {"lat": 23.0225, "lon": 72.5714, "city": "Ahmedabad", "state": "Gujarat", "type": "State", "zone": "Hot & Arid"},
    "Surat, Gujarat (Hot & Humid)": {"lat": 21.1702, "lon": 72.8311, "city": "Surat", "state": "Gujarat", "type": "State", "zone": "Hot & Humid"},
    "Vadodara, Gujarat (Hot & Arid)": {"lat": 22.3072, "lon": 73.1812, "city": "Vadodara", "state": "Gujarat", "type": "State", "zone": "Hot & Arid"},
    "Rajkot, Gujarat (Hot & Arid)": {"lat": 22.3039, "lon": 70.8022, "city": "Rajkot", "state": "Gujarat", "type": "State", "zone": "Hot & Arid"},

    # Haryana
    "Gurugram, Haryana (Composite / Extreme)": {"lat": 28.4595, "lon": 77.0266, "city": "Gurugram", "state": "Haryana", "type": "State", "zone": "Composite"},
    "Faridabad, Haryana (Composite)": {"lat": 28.4089, "lon": 77.3178, "city": "Faridabad", "state": "Haryana", "type": "State", "zone": "Composite"},

    # Himachal Pradesh
    "Shimla, Himachal Pradesh (Cold & Mountain)": {"lat": 31.1048, "lon": 77.1734, "city": "Shimla", "state": "Himachal Pradesh", "type": "State", "zone": "Cold & High-Altitude"},
    "Dharamshala, Himachal Pradesh (Cold)": {"lat": 32.2190, "lon": 76.3234, "city": "Dharamshala", "state": "Himachal Pradesh", "type": "State", "zone": "Cold & High-Altitude"},
    "Manali, Himachal Pradesh (Cold & Alpine)": {"lat": 32.2432, "lon": 77.1892, "city": "Manali", "state": "Himachal Pradesh", "type": "State", "zone": "Cold & High-Altitude"},

    # Jharkhand
    "Ranchi, Jharkhand (Composite)": {"lat": 23.3441, "lon": 85.3096, "city": "Ranchi", "state": "Jharkhand", "type": "State", "zone": "Composite"},
    "Jamshedpur, Jharkhand (Composite)": {"lat": 22.8046, "lon": 86.2029, "city": "Jamshedpur", "state": "Jharkhand", "type": "State", "zone": "Composite"},

    # Karnataka
    "Bengaluru, Karnataka (Temperate)": {"lat": 12.9716, "lon": 77.5946, "city": "Bengaluru", "state": "Karnataka", "type": "State", "zone": "Temperate"},
    "Mysuru, Karnataka (Temperate)": {"lat": 12.2958, "lon": 76.6394, "city": "Mysuru", "state": "Karnataka", "type": "State", "zone": "Temperate"},
    "Mangaluru, Karnataka (Hot & Humid)": {"lat": 12.9141, "lon": 74.8560, "city": "Mangaluru", "state": "Karnataka", "type": "State", "zone": "Hot & Humid"},

    # Kerala
    "Thiruvananthapuram, Kerala (Hot & Humid)": {"lat": 8.5241, "lon": 76.9366, "city": "Thiruvananthapuram", "state": "Kerala", "type": "State", "zone": "Hot & Humid"},
    "Kochi, Kerala (Hot & Humid)": {"lat": 9.9312, "lon": 76.2673, "city": "Kochi", "state": "Kerala", "type": "State", "zone": "Hot & Humid"},
    "Kozhikode, Kerala (Hot & Humid)": {"lat": 11.2588, "lon": 75.7804, "city": "Kozhikode", "state": "Kerala", "type": "State", "zone": "Hot & Humid"},

    # Madhya Pradesh
    "Bhopal, Madhya Pradesh (Composite)": {"lat": 23.2599, "lon": 77.4126, "city": "Bhopal", "state": "Madhya Pradesh", "type": "State", "zone": "Composite"},
    "Indore, Madhya Pradesh (Composite)": {"lat": 22.7196, "lon": 75.8577, "city": "Indore", "state": "Madhya Pradesh", "type": "State", "zone": "Composite"},
    "Gwalior, Madhya Pradesh (Hot & Arid)": {"lat": 26.2183, "lon": 78.1828, "city": "Gwalior", "state": "Madhya Pradesh", "type": "State", "zone": "Hot & Arid"},

    # Maharashtra
    "Mumbai, Maharashtra (Hot & Humid)": {"lat": 19.0760, "lon": 72.8777, "city": "Mumbai", "state": "Maharashtra", "type": "State", "zone": "Hot & Humid"},
    "Pune, Maharashtra (Warm & Semi-Arid)": {"lat": 18.5204, "lon": 73.8567, "city": "Pune", "state": "Maharashtra", "type": "State", "zone": "Warm & Semi-Arid"},
    "Nagpur, Maharashtra (Hot & Arid)": {"lat": 21.1458, "lon": 79.0882, "city": "Nagpur", "state": "Maharashtra", "type": "State", "zone": "Hot & Arid"},
    "Nashik, Maharashtra (Warm & Semi-Arid)": {"lat": 19.9975, "lon": 73.7898, "city": "Nashik", "state": "Maharashtra", "type": "State", "zone": "Warm & Semi-Arid"},

    # Manipur
    "Imphal, Manipur (Temperate)": {"lat": 24.8170, "lon": 93.9368, "city": "Imphal", "state": "Manipur", "type": "State", "zone": "Temperate"},

    # Meghalaya
    "Shillong, Meghalaya (Cold & Mountain)": {"lat": 25.5788, "lon": 91.8933, "city": "Shillong", "state": "Meghalaya", "type": "State", "zone": "Cold & High-Altitude"},

    # Mizoram
    "Aizawl, Mizoram (Temperate)": {"lat": 23.7271, "lon": 92.7176, "city": "Aizawl", "state": "Mizoram", "type": "State", "zone": "Temperate"},

    # Nagaland
    "Kohima, Nagaland (Temperate)": {"lat": 25.6751, "lon": 94.1086, "city": "Kohima", "state": "Nagaland", "type": "State", "zone": "Temperate"},

    # Odisha
    "Bhubaneswar, Odisha (Hot & Humid)": {"lat": 20.2961, "lon": 85.8245, "city": "Bhubaneswar", "state": "Odisha", "type": "State", "zone": "Hot & Humid"},
    "Puri, Odisha (Hot & Humid)": {"lat": 19.8135, "lon": 85.8312, "city": "Puri", "state": "Odisha", "type": "State", "zone": "Hot & Humid"},
    "Sambalpur, Odisha (Composite)": {"lat": 21.4669, "lon": 83.9812, "city": "Sambalpur", "state": "Odisha", "type": "State", "zone": "Composite"},
    "Cuttack, Odisha (Hot & Humid)": {"lat": 20.4625, "lon": 85.8828, "city": "Cuttack", "state": "Odisha", "type": "State", "zone": "Hot & Humid"},
    "Rourkela, Odisha (Composite)": {"lat": 22.2604, "lon": 84.8536, "city": "Rourkela", "state": "Odisha", "type": "State", "zone": "Composite"},

    # Punjab
    "Ludhiana, Punjab (Composite / Semi-Arid)": {"lat": 30.9010, "lon": 75.8573, "city": "Ludhiana", "state": "Punjab", "type": "State", "zone": "Composite"},
    "Amritsar, Punjab (Composite)": {"lat": 31.6340, "lon": 74.8723, "city": "Amritsar", "state": "Punjab", "type": "State", "zone": "Composite"},

    # Rajasthan
    "Jaipur, Rajasthan (Hot & Arid)": {"lat": 26.9124, "lon": 75.7873, "city": "Jaipur", "state": "Rajasthan", "type": "State", "zone": "Hot & Arid"},
    "Barmer, Rajasthan (Hot & Arid)": {"lat": 25.7532, "lon": 71.4181, "city": "Barmer", "state": "Rajasthan", "type": "State", "zone": "Hot & Arid"},
    "Jodhpur, Rajasthan (Hot & Arid)": {"lat": 26.2389, "lon": 73.0243, "city": "Jodhpur", "state": "Rajasthan", "type": "State", "zone": "Hot & Arid"},
    "Jaisalmer, Rajasthan (Hot & Arid)": {"lat": 26.9157, "lon": 70.9083, "city": "Jaisalmer", "state": "Rajasthan", "type": "State", "zone": "Hot & Arid"},
    "Udaipur, Rajasthan (Hot & Arid)": {"lat": 24.5854, "lon": 73.7125, "city": "Udaipur", "state": "Rajasthan", "type": "State", "zone": "Hot & Arid"},

    # Sikkim
    "Gangtok, Sikkim (Cold & Mountain)": {"lat": 27.3389, "lon": 88.6065, "city": "Gangtok", "state": "Sikkim", "type": "State", "zone": "Cold & High-Altitude"},

    # Tamil Nadu
    "Chennai, Tamil Nadu (Hot & Humid)": {"lat": 13.0827, "lon": 80.2707, "city": "Chennai", "state": "Tamil Nadu", "type": "State", "zone": "Hot & Humid"},
    "Coimbatore, Tamil Nadu (Warm & Semi-Arid)": {"lat": 11.0168, "lon": 76.9558, "city": "Coimbatore", "state": "Tamil Nadu", "type": "State", "zone": "Warm & Humid"},
    "Madurai, Tamil Nadu (Hot & Arid)": {"lat": 9.9252, "lon": 78.1198, "city": "Madurai", "state": "Tamil Nadu", "type": "State", "zone": "Hot & Arid"},

    # Telangana
    "Hyderabad, Telangana (Hot & Semi-Arid)": {"lat": 17.3850, "lon": 78.4867, "city": "Hyderabad", "state": "Telangana", "type": "State", "zone": "Hot & Semi-Arid"},
    "Warangal, Telangana (Hot & Arid)": {"lat": 17.9689, "lon": 79.5941, "city": "Warangal", "state": "Telangana", "type": "State", "zone": "Hot & Arid"},

    # Tripura
    "Agartala, Tripura (Warm & Humid)": {"lat": 23.8315, "lon": 91.2868, "city": "Agartala", "state": "Tripura", "type": "State", "zone": "Warm & Humid"},

    # Uttar Pradesh
    "Lucknow, Uttar Pradesh (Composite)": {"lat": 26.8467, "lon": 80.9462, "city": "Lucknow", "state": "Uttar Pradesh", "type": "State", "zone": "Composite"},
    "Varanasi, Uttar Pradesh (Composite)": {"lat": 25.3176, "lon": 82.9739, "city": "Varanasi", "state": "Uttar Pradesh", "type": "State", "zone": "Composite"},
    "Agra, Uttar Pradesh (Composite)": {"lat": 27.1767, "lon": 78.0081, "city": "Agra", "state": "Uttar Pradesh", "type": "State", "zone": "Composite"},
    "Kanpur, Uttar Pradesh (Composite)": {"lat": 26.4499, "lon": 80.3319, "city": "Kanpur", "state": "Uttar Pradesh", "type": "State", "zone": "Composite"},
    "Noida, Uttar Pradesh (Composite)": {"lat": 28.5355, "lon": 77.3910, "city": "Noida", "state": "Uttar Pradesh", "type": "State", "zone": "Composite"},

    # Uttarakhand
    "Dehradun, Uttarakhand (Temperate)": {"lat": 30.3165, "lon": 78.0322, "city": "Dehradun", "state": "Uttarakhand", "type": "State", "zone": "Temperate"},
    "Haridwar, Uttarakhand (Composite)": {"lat": 29.9457, "lon": 78.1642, "city": "Haridwar", "state": "Uttarakhand", "type": "State", "zone": "Composite"},
    "Nainital, Uttarakhand (Cold & Mountain)": {"lat": 29.3919, "lon": 79.4542, "city": "Nainital", "state": "Uttarakhand", "type": "State", "zone": "Cold & High-Altitude"},

    # West Bengal
    "Kolkata, West Bengal (Hot & Humid)": {"lat": 22.5726, "lon": 88.3639, "city": "Kolkata", "state": "West Bengal", "type": "State", "zone": "Hot & Humid"},
    "Siliguri, West Bengal (Warm & Humid)": {"lat": 26.7271, "lon": 88.3953, "city": "Siliguri", "state": "West Bengal", "type": "State", "zone": "Warm & Humid"}
}

def get_city_climate_profile(city_name_key):
    """
    Look up lat/lon for any major Indian city and fetch its live weather profile.
    """
    for key, info in MAJOR_INDIAN_CITIES.items():
        if city_name_key == key or city_name_key.lower() in key.lower() or key.lower() in city_name_key.lower():
            lat = info["lat"]
            lon = info["lon"]
            records = fetch_live_climate_profile(lat, lon)
            if records:
                return records
    return None

def get_ip_location():
    """
    Auto-detect location using IP Geolocation APIs with fallback options.
    """
    apis = [
        "http://ip-api.com/json/",
        "https://ipapi.co/json/"
    ]
    
    for api_url in apis:
        try:
            req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=4) as response:
                data = json.loads(response.read().decode())
                
                # ip-api.com format
                if data.get("status") == "success":
                    return {
                        "city": data.get("city", "Unknown City"),
                        "region": data.get("regionName", data.get("region", "")),
                        "country": data.get("country", "India"),
                        "lat": float(data.get("lat")),
                        "lon": float(data.get("lon")),
                        "source": "IP Geolocation"
                    }
                
                # ipapi.co format
                if "latitude" in data and "longitude" in data:
                    return {
                        "city": data.get("city", "Unknown City"),
                        "region": data.get("region", ""),
                        "country": data.get("country_name", "India"),
                        "lat": float(data.get("latitude")),
                        "lon": float(data.get("longitude")),
                        "source": "IP Geolocation"
                    }
        except Exception:
            continue
            
    # Fallback to default coordinates (Sambalpur, Odisha) if offline/unreachable
    return {
        "city": "Sambalpur",
        "region": "Odisha",
        "country": "India",
        "lat": 21.4669,
        "lon": 83.9812,
        "source": "Fallback Preset"
    }

def reverse_geocode(lat, lon):
    """
    Reverse geocode lat/lon coordinates to get City, Region, Country using Open-Meteo or OpenStreetMap.
    """
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/get?latitude={lat}&longitude={lon}"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            if "name" in data:
                return {
                    "city": data.get("name"),
                    "region": data.get("admin1", ""),
                    "country": data.get("country", "")
                }
    except Exception:
        pass
        
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
        req = urllib.request.Request(url, headers={'User-Agent': 'Shelter-AI Engine/1.0'})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            addr = data.get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or "Detected Location"
            region = addr.get("state") or ""
            country = addr.get("country") or ""
            return {"city": city, "region": region, "country": country}
    except Exception:
        pass

    return {"city": f"Location ({lat:.2f}, {lon:.2f})", "region": "", "country": ""}

def fetch_live_climate_profile(lat, lon):
    """
    Fetch real-time 24-hour hourly weather forecast/current data from Open-Meteo API.
    """
    now = datetime.datetime.now()
    month = now.month
    day = now.day
    
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,relative_humidity_2m,shortwave_radiation,wind_speed_10m&forecast_days=1"
    
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            hourly = data.get("hourly", {})
            
            temps = hourly.get("temperature_2m", [])
            rhs = hourly.get("relative_humidity_pct", hourly.get("relative_humidity_2m", []))
            ghis = hourly.get("shortwave_radiation", [])
            winds = hourly.get("wind_speed_10m", [])
            
            if len(temps) >= 24:
                records = []
                for h in range(24):
                    t = float(temps[h])
                    r = float(rhs[h]) if h < len(rhs) else 50.0
                    g = max(0.0, float(ghis[h])) if h < len(ghis) else 0.0
                    w = float(winds[h]) if h < len(winds) else 2.5
                    
                    records.append({
                        "month": month,
                        "day": day,
                        "hour": h,
                        "dry_bulb_temp_c": round(t, 2),
                        "relative_humidity_pct": round(r, 1),
                        "solar_ghi_w_m2": round(g, 1),
                        "direct_normal_irradiance_w_m2": round(g * 1.1, 1),
                        "wind_speed_m_s": round(w, 1)
                    })
                return records
    except Exception as e:
        print("Live weather fetch error:", e)
        
    return None

def classify_climate_zone(records):
    """
    Classifies climate zone based on 24-hour temperature, humidity, and solar GHI metrics.
    """
    if not records:
        return "Composite / Moderate"
        
    temps = [r["dry_bulb_temp_c"] for r in records]
    rhs = [r["relative_humidity_pct"] for r in records]
    
    t_max = max(temps)
    t_min = min(temps)
    t_avg = sum(temps) / len(temps)
    rh_avg = sum(rhs) / len(rhs)
    
    if t_avg < 15.0 or t_min < 5.0:
        return "Cold & High-Altitude"
    elif t_max >= 36.0 and rh_avg <= 45.0:
        return "Hot & Arid"
    elif t_max >= 30.0 and rh_avg >= 70.0:
        return "Hot & Humid"
    elif t_avg >= 26.0 and rh_avg >= 60.0:
        return "Warm & Humid"
    else:
        return "Composite / Tropical"

def recommend_shelter_preset(climate_zone):
    """
    Returns optimal material and geometric envelope preset for detected climate zone.
    """
    presets = {
        "Cold & High-Altitude": {
            "wall": "aac_block",
            "roof": "roof_concrete_slab",
            "thickness": 25.0,
            "wwr": 20.0,
            "overhang": 0.4,
            "description": "High thermal insulation (AAC concrete + concrete slab) with tight envelope to retain heat."
        },
        "Hot & Arid": {
            "wall": "cseb_interlocking",
            "roof": "roof_concrete_slab",
            "thickness": 25.0,
            "wwr": 12.0,
            "overhang": 0.8,
            "description": "High thermal mass (CEB block) to damp extreme diurnal temperature swings with deep overhangs."
        },
        "Hot & Humid": {
            "wall": "eps_sandwich",
            "roof": "roof_bamboo_thatch",
            "thickness": 12.0,
            "wwr": 25.0,
            "overhang": 1.0,
            "description": "Lightweight envelope with maximum cross-ventilation (WWR 25%) and rain/sun overhangs."
        },
        "Warm & Humid": {
            "wall": "bamboo_composite",
            "roof": "roof_bamboo_thatch",
            "thickness": 15.0,
            "wwr": 20.0,
            "overhang": 0.8,
            "description": "Eco-friendly breathable wall with high natural airflow and solar shading."
        },
        "Composite / Tropical": {
            "wall": "cseb_interlocking",
            "roof": "roof_cgi_insulated",
            "thickness": 20.0,
            "wwr": 15.0,
            "overhang": 0.6,
            "description": "Balanced thermal mass with insulated roofing for variable seasonal climate."
        }
    }
    return presets.get(climate_zone, presets["Composite / Tropical"])

def auto_detect_location_and_data(custom_lat=None, custom_lon=None):
    """
    Complete pipeline: Detect location, fetch live weather data, classify climate zone, and recommend design.
    """
    if custom_lat is not None and custom_lon is not None:
        geo_info = reverse_geocode(custom_lat, custom_lon)
        lat, lon = float(custom_lat), float(custom_lon)
        city = geo_info.get("city", f"Location ({lat:.2f}, {lon:.2f})")
        region = geo_info.get("region", "")
        country = geo_info.get("country", "")
        source = "GPS Geolocation"
    else:
        ip_info = get_ip_location()
        city = ip_info["city"]
        region = ip_info["region"]
        country = ip_info["country"]
        lat = ip_info["lat"]
        lon = ip_info["lon"]
        source = ip_info["source"]
        
    records = fetch_live_climate_profile(lat, lon)
    
    if not records:
        # Fallback synthetic profile if live API fails
        from engine.climate import get_climate_profile
        records = get_climate_profile("sambalpur", month=5)
        
    temps = [r["dry_bulb_temp_c"] for r in records]
    rhs = [r["relative_humidity_pct"] for r in records]
    ghis = [r["solar_ghi_w_m2"] for r in records]
    winds = [r["wind_speed_m_s"] for r in records]
    
    climate_zone = classify_climate_zone(records)
    recommended_preset = recommend_shelter_preset(climate_zone)
    
    loc_display = f"{city}" + (f", {region}" if region else "") + (f" ({country})" if country else "")
    
    return {
        "status": "success",
        "location_name": loc_display,
        "city": city,
        "region": region,
        "country": country,
        "lat": lat,
        "lon": lon,
        "source": source,
        "climate_zone": climate_zone,
        "climate_records": records,
        "summary": {
            "t_max": round(max(temps), 1),
            "t_min": round(min(temps), 1),
            "t_avg": round(sum(temps)/len(temps), 1),
            "rh_avg": round(sum(rhs)/len(rhs), 0),
            "ghi_peak": round(max(ghis), 1),
            "wind_avg": round(sum(winds)/len(winds), 1)
        },
        "recommended_preset": recommended_preset
    }
