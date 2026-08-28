# ShelterAI Feature Upgrade Plan: Climate-Resilient Shelter Decision Support Platform

## 1. Executive Overview & Existing Architecture Analysis

### 1.1 Existing Architecture
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Three.js / React Three Fiber (`@react-three/fiber`, `@react-three/drei`) + Zustand state store + Lucide icons.
- **Backend API**: FastAPI (Python 3.13) with modular REST routers under `/api/*` and `/` endpoints.
- **Engineering Engine**: Core physics and mathematical modeling:
  - `climate.py` & `climate_intelligence.py`: IMD / EPW climate processing, degree-days, radiation, diurnal ranges.
  - `geometry.py`: 3D parametric envelope, surface area, volume, aspect ratio, WWR, overhang shading geometry.
  - `materials.py`: Thermo-physical properties (conductivity, density, specific heat, U-value, thermal mass, embodied carbon, ₹ cost).
  - `thermal.py`: RC transient heat transfer model, solar heat gain, ventilation air changes, internal gains, sol-air temp.
  - `comfort.py`: ASHRAE 55 PMV/PPD, adaptive comfort (IMAC-R / EN 16798), heat index, diurnal comfort hours.
  - `energy.py`: Annual sensible/latent cooling & heating loads, peak kW sizing, operational electricity bills.
  - `cost.py`: CapEx envelope material takeoffs, labor factor, 30-year life-cycle cost (LCC), embodied carbon footprint.
  - `optimizer.py`: Multi-objective NSGA-II / Pareto optimization exploring non-dominated design candidate frontiers.
  - `resilience.py`: Thermal inertia, passive survivability under heat extremes, storm/cyclone envelope resistance.
  - `digital_twin.py`: Real-time 3D configuration generator, sun angle vector calculations, surface thermal tinting.
- **Data Layers**: `data/materials.csv`, `data/design_rules.json`, `data/sample_designs.json`, `data/climate/`.

### 1.2 Identified Integration Points & Extension Strategy
1. **Material & Construction Recommender**: Upgrade `engine/material_recommender.py` and create dedicated `engine/recommendation/` package with specialized scoring for walls, roofs, floors, windows, doors, insulation, shading, and construction methods.
2. **Design Simulator**: Enhance `ShelterDesignLabPage.tsx` and create full live interactive scenario mode with two-way sync to the 3D Digital Twin and instantaneous simulation triggering.
3. **Disaster & Migrant Shelter Mode**: Introduce high-density modular shelter archetypes (Emergency Pods, Elevated Flood Shelters, Cyclonic Core Shelters, Migrant Dormitories) with occupancy/area allocation, modular layouts, and hazard-specific mitigation strategies.
4. **Cost vs Comfort Dashboard**: Add interactive Pareto frontier scatter charts, Utopia distance metrics, budget-to-comfort sliders, and detailed engineering tradeoff explanations.
5. **Policy & Compliance Checker**: Build `data/regulations/` database and `engine/compliance/` engine screening projects against Eco-Niwas Samhita (ENS), ECBC, NBC 2016, and State Energy Conservation Building Codes across Indian States.
6. **State-Wise Thermal Vulnerability Index (TVI)**: Build a transparent, normalized composite index (Heat exposure, thermal extremes, humidity burden, cooling demand, adaptive capacity) across Indian States & UTs with documented data sources (IMD, BEE, Census, NDMA).

---

## 2. Upgraded System Architecture

```
                    SHELTERAI PLATFORM
                            │
               LOCATION & STATE SELECTION
                            │
      ┌─────────────────────┼─────────────────────┐
      ↓                     ↓                     ↓
Climate Intelligence    Thermal TVI (0-100)   State Policy DB
(IMD / Epw / Solar)   (Exposure/Sensitivity) (ENS/ECBC/NBC/State)
      │                     │                     │
      └─────────────────────┼─────────────────────┘
                            ↓
                    SHELTER ARCHETYPE
          (Standard / Disaster Relief / Migrant)
                            ↓
             INTERACTIVE DESIGN SIMULATOR
                            ↓
          ┌─────────────────┼─────────────────┐
          ↓                 ↓                 ↓
     Materials          Geometry        Construction
   (Walls/Roofs/     (L/W/H/Pitch/     (Modular/Prefab/
    Glazing/Insul)    Overhang/WWR)     Rapid Assembly)
          │                 │                 │
          └─────────────────┼─────────────────┘
                            ↓
              3D DIGITAL TWIN (WebGL / R3F)
          (Solar Shading, Heatmap, Ventilation)
                            ↓
             PHYSICS THERMAL SIMULATION (RC)
                            ↓
      ┌─────────────────────┼─────────────────────┐
      ↓                     ↓                     ↓
Comfort Engine            Energy Engine        Cost & Carbon
(PMV / Adaptive)        (Annual kWh/Peak)   (CapEx / Life-Cycle)
      │                     │                     │
      └─────────────────────┼─────────────────────┘
                            ↓
               COST ↔ COMFORT TRADEOFF
                  (Pareto Frontier)
                            ↓
              ENGINEERING RECOMMENDATION
                            ↓
               POLICY COMPLIANCE AUDIT
             (PASS / REVIEW / FAIL / N/V)
                            ↓
              FINAL REPORT & PDF EXPORT
```

---

## 3. Module Breakdown & Implementation Details

### Module 1: Material + Construction Recommendation Engine
- **Files**:
  - `engine/recommendation/climate_rules.py`: Climate-specific boundary limits, target U-values, solar reflectance, thermal mass requirements.
  - `engine/recommendation/material_recommender.py`: Multi-factor evaluator for individual assemblies and envelopes.
  - `engine/recommendation/construction_recommender.py`: Assembly method selection (Prefab panel, CSEB mortarless, Light-gauge steel, Bamboo truss, Modular container).
  - `engine/recommendation/recommendation_scoring.py`: Weighted multi-criteria scoring (`thermal`, `cost`, `climate`, `constructability`, `resilience`, `availability`).
- **REST Endpoints**:
  - `POST /api/recommendations/run`
  - `GET /api/recommendations/systems`

### Module 2: Design Simulator & Scenario Design Mode
- **Capabilities**:
  - Seamless real-time updates for length, width, height, number of floors, roof geometry (pitched, flat, monoslope, butterfly, hipped), orientation (0–360°), window wall ratio (WWR), overhang projection, door dimensions, and envelope materials.
  - Live side-by-side Baseline vs. Modified Design sensitivity simulator.
  - Zero full-page reloads, separate triggers for instant 3D rendering vs on-demand physics simulation.

### Module 3: Disaster & Migrant Shelter Mode
- **Disaster Modes**:
  - `Heatwave`: Cool roof high SRI, cross-ventilation sizing, night purging, thermal mass optimization.
  - `Flood`: Plinth elevation (stilt/raised floor 0.5–1.5m), water-resistant CSEB / fiber cement / steel framing, quick-drain porch.
  - `Cyclone`: Aerodynamic hipped roof (25–30° pitch), reinforced overhang connections, storm shutter protection.
  - `Earthquake`: Lightweight ductile envelope, symmetrical regular geometry, reinforced bracing.
  - `Extreme Rainfall`: Steep roof slope (>30°), wide overhangs (>0.8m), moisture barrier membranes.
- **Migrant & Humanitarian Temporary Housing**:
  - Standardized modular pods (Module A, B, C, D) configured for single workers or multi-family clusters.
  - Area per person budgeting (3.5 – 5.5 m²/person), shared cross-ventilation corridors, rapid disassembly.

### Module 4: Cost vs Comfort Trade-off Dashboard & Pareto Frontier
- **Interactive Visualizations**:
  - Scatter plot: Total Cost (₹) vs Comfort Score (0–100) with dynamic Pareto frontier contour.
  - Interactive weights slider: Cost vs Comfort vs Energy vs Resilience.
  - Highlighting for `Best Balanced`, `Best Comfort`, `Lowest Cost`, `Lowest Energy`.
  - Concrete explainable delta rationale (e.g. "+₹35,000 for AAC + Rockwool yields +14% annual comfort hours").

### Module 5: State-Specific Policy & Compliance Checker
- **Data & Schemas**:
  - `data/regulations/central/ens_2021.json`, `ecbc_2017.json`, `nbc_2016.json`
  - `data/regulations/states/*.json` (Odisha, Rajasthan, Maharashtra, Karnataka, Gujarat, Tamil Nadu, West Bengal, UP, Assam, etc.)
- **Engine**:
  - `engine/compliance/compliance_engine.py`: Checks RETV (Residential Envelope Transmittance Value), Roof U-value, WWR limits, Natural Ventilation Potential, Daylighting Aperture, and Setbacks.
  - Output status: `PASS`, `REVIEW`, `FAIL`, `NOT_VERIFIED`.

### Module 6: India State-Wise Thermal Vulnerability Index (TVI)
- **Methodology & Transparent Formulation**:
  - $TVI = w_1 \cdot \text{HeatExposure} + w_2 \cdot \text{ThermalExtremes} + w_3 \cdot \text{HumidityStress} + w_4 \cdot \text{CoolingBurden} + w_5 \cdot \text{PopulationVuln} + w_6 \cdot \text{BuildingVuln} - w_7 \cdot \text{AdaptiveCapacity}$
  - Documented sources: IMD Climatological Normals, BEE Building Energy Data, Census of India Housing Stock, NDMA Heat Action Plans.
  - Full transparent breakdown UI + dynamic state rankings + direct feed into passive design priorities.

---

## 4. Verification & Quality Assurance Plan
- Automated backend unit tests for recommendation scoring, TVI normalization, compliance rule evaluation, and simulation consistency.
- Full TypeScript compilation and production bundle build verification (`npm.cmd run build`).
- End-to-end user workflow test cases across varied Indian climate zones (Sambalpur, Jodhpur, Chennai, Shillong, Delhi).
