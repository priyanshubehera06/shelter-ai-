-- SQLite Database Schema for Shelter-AI

CREATE TABLE IF NOT EXISTS materials (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    density_kg_m3 REAL NOT NULL,
    thermal_cond_w_mk REAL NOT NULL,
    specific_heat_j_kgk REAL NOT NULL,
    embodied_carbon_kgco2_kg REAL NOT NULL,
    unit_cost_inr_m2 REAL NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS climate_locations (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    region_type TEXT NOT NULL,
    t_max_summer REAL NOT NULL,
    t_min_winter REAL NOT NULL,
    rh_avg_pct REAL NOT NULL,
    solar_irradiance_peak REAL NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS shelter_designs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    length_m REAL NOT NULL,
    width_m REAL NOT NULL,
    height_m REAL NOT NULL,
    wall_material_id TEXT NOT NULL,
    wall_thickness_cm REAL NOT NULL,
    roof_material_id TEXT NOT NULL,
    glazing_material_id TEXT NOT NULL,
    wwr_pct REAL NOT NULL,
    overhang_m REAL NOT NULL,
    orientation_deg REAL NOT NULL,
    total_cost_inr REAL,
    embodied_carbon_kg REAL,
    pmv_score REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(wall_material_id) REFERENCES materials(id),
    FOREIGN KEY(roof_material_id) REFERENCES materials(id),
    FOREIGN KEY(glazing_material_id) REFERENCES materials(id)
);

CREATE TABLE IF NOT EXISTS optimization_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location_id TEXT NOT NULL,
    weights_json TEXT NOT NULL,
    best_design_json TEXT NOT NULL,
    pareto_front_json TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
