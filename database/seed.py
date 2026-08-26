import os
import sqlite3
import pandas as pd

DB_PATH = os.path.join(os.path.dirname(__file__), "shelter.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")
MATERIALS_CSV = os.path.join(os.path.dirname(__file__), "..", "data", "materials.csv")

def seed_database():
    print(f"Initializing database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Execute Schema
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)

    # Seed Materials from CSV
    if os.path.exists(MATERIALS_CSV):
        df_materials = pd.read_csv(MATERIALS_CSV)
        for _, row in df_materials.iterrows():
            cursor.execute("""
                INSERT OR REPLACE INTO materials 
                (id, name, category, density_kg_m3, thermal_cond_w_mk, specific_heat_j_kgk, embodied_carbon_kgco2_kg, unit_cost_inr_m2, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                row["id"], row["name"], row["category"],
                float(row["density_kg_m3"]), float(row["thermal_cond_w_mk"]),
                float(row["specific_heat_j_kgk"]), float(row["embodied_carbon_kgco2_kg"]),
                float(row["unit_cost_inr_m2"]), row.get("description", "")
            ))
        print(f"Loaded {len(df_materials)} materials into database.")

    # Seed Climate Locations
    climate_presets = [
        ("sambalpur", "Sambalpur, Odisha", "Composite / Hot & Humid", 43.5, 12.1, 78.0, 950.0, "Hot dry summers with intense monsoons and mild winters."),
        ("barmer", "Barmer, Rajasthan", "Hot & Arid", 45.0, 8.0, 35.0, 1050.0, "Extreme diurnal temperature range with high direct solar irradiation."),
        ("puri", "Puri, Odisha", "Hot & Humid Coastal", 35.0, 22.0, 84.0, 850.0, "Coastal tropical environment requiring high natural cross-ventilation."),
        ("leh", "Leh, Ladakh", "Cold & High Altitude", 22.0, -15.0, 38.0, 980.0, "Extreme winter freezing requiring high thermal insulation envelope.")
    ]

    for loc in climate_presets:
        cursor.execute("""
            INSERT OR REPLACE INTO climate_locations 
            (id, name, region_type, t_max_summer, t_min_winter, rh_avg_pct, solar_irradiance_peak, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, loc)
    print("Loaded climate locations into database.")

    # Seed Baseline Presets
    presets = [
        ("Disaster Relief Rapid Shelter", 6.0, 4.0, 2.8, "eps_sandwich", 10.0, "roof_cgi_insulated", "glazing_polycarb", 15.0, 0.6, 180.0, 75000.0, 420.0, 0.15),
        ("Eco Earth Block Shelter", 6.0, 5.0, 3.0, "cseb_interlocking", 23.0, "roof_bamboo_thatch", "glazing_single", 20.0, 0.8, 0.0, 92000.0, 180.0, 0.05),
        ("High-Performance Thermal Shelter", 7.0, 5.0, 3.0, "aac_block", 20.0, "roof_concrete_slab", "glazing_double", 25.0, 1.0, 90.0, 145000.0, 650.0, -0.10)
    ]

    for p in presets:
        cursor.execute("""
            INSERT OR REPLACE INTO shelter_designs 
            (name, length_m, width_m, height_m, wall_material_id, wall_thickness_cm, roof_material_id, glazing_material_id, wwr_pct, overhang_m, orientation_deg, total_cost_inr, embodied_carbon_kg, pmv_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, p)

    conn.commit()
    conn.close()
    print("Database seeding completed successfully.")

if __name__ == "__main__":
    seed_database()
