# SHELTER-AI — Climate-Resilient Shelter Decision Support Platform

> **Platform Mission:** *"Software Based Model Development for Design of Area Specific Shelter for Thermal Comfort Maintenance."*

SHELTER-AI is a physics-informed, multi-physics building design and decision-support platform. It synthesizes meteorological intelligence, state-specific thermal vulnerability indices, energy building codes, and evolutionary optimization to engineer climate-resilient, affordable, and low-carbon shelters across Indian climatic zones.

---

## 🏛️ High-Level System Architecture

```
                    SHELTER-AI FULL-STACK PLATFORM

┌────────────────────────────────────────────────────────────────────────┐
│                   REACT + TYPESCRIPT + VITE (SPA)                      │
│                                                                        │
│  01. Platform Overview         02. Location & Climate                  │
│  03. State Thermal TVI         04. Parametric Design Simulator         │
│  05. Material Recommender      06. 3D Digital Twin Viewport            │
│  07. Cost vs Comfort Pareto    08. Disaster & Migrant Mode             │
│  09. Policy & Compliance       10. What-If Sensitivity Lab             │
│  11. Multi-Objective Search    12. Certified Results & XAI             │
│                                                                        │
│          Three.js / React Three Fiber / @react-three/drei              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                           REST API (JSON & PDF)
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         FASTAPI REST BACKEND                           │
│                                                                        │
│  /api/climate             /api/thermal-vulnerability                   │
│  /api/recommendations     /api/compliance                              │
│  /api/designs             /api/materials                               │
│  /api/simulation          /api/optimization                            │
│  /api/digital-twin        /api/results                                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    PYTHON PHYSICS & CAD ENGINES                        │
│                                                                        │
│  • recommendation/      • compliance/         • tvi/                   │
│  • geometry.py          • climate.py          • materials.py           │
│  • thermal.py           • comfort.py          • energy.py              │
│  • cost.py              • optimizer.py        • resilience.py          │
│  • explainability.py    • digital_twin.py     • scoring.py             │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                 DATA REGISTRY & REGULATORY DATABASE                    │
│                                                                        │
│  • data/tvi/state_vulnerability_data.json                              │
│  • data/tvi/sources_registry.json                                      │
│  • data/regulations/central/ (ENS 2021, ECBC 2017, NBC 2016)           │
│  • data/regulations/states/ (OD, RJ, MH, KA, GJ, TN, WB, UP, AS, KL)   │
│  • data/materials.csv                                                  │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Six Major Core Engineering Modules

### 1. Material + Construction Recommendation Engine
- Evaluates envelope assemblies (Wall, Roof, Floor, Windows, Doors, Insulation, Shading, and Overhangs) using transparent multi-factor scoring:
  $$\text{Score} = w_{\text{thermal}} \cdot \text{Thermal} + w_{\text{cost}} \cdot \text{Cost} + w_{\text{resilience}} \cdot \text{Resilience} + w_{\text{construct}} \cdot \text{Constructability} + w_{\text{avail}} \cdot \text{Availability}$$
- Recommends rapid assembly methods (Mortarless Interlocking CSEB, Light-Gauge Steel Prefab, Confined Masonry, Elevated Bamboo Composite, Rapid Disaster Pods).

### 2. Interactive Design Simulator & Real-Time Twin
- Instantaneous 3D geometry updates without full-page reloads for length, width, floor count, roof types (pitched, monoslope, hipped, flat), orientation (0–360°), and window-to-wall ratios.
- On-demand execution of 24-hour RC thermal dynamics, ASHRAE 55 PMV comfort compliance, and live baseline vs. modified sensitivity comparisons.

### 3. Disaster & Migrant Shelter Mode
- Dedicated hazard configurations for **Heatwaves**, **Floods**, **Cyclones**, **Earthquakes**, and **Extreme Monsoons**.
- Modular humanitarian worker dormitories configured in repeatable pods (Modules A, B, C, D) complying with Sphere Standard area budgeting (3.5–5.0 m²/person).

### 4. Cost vs. Comfort Trade-Off Dashboard
- Interactive scatter plot mapping total CapEx (₹ Lakh) against Human Comfort Score (0–100).
- Visualizes the non-dominated Pareto Frontier and Utopia distance minimums with an interactive "What Matters Most?" preference slider.

### 5. State-Specific Policy & Compliance Checker
- Screens shelter parameters against **Eco-Niwas Samhita (ENS 2021)**, **ECBC 2017 / ECSBC 2024**, **National Building Code (NBC 2016)**, and State Building Byelaws across Indian States.
- Categorizes rules into `PASS`, `REVIEW`, `FAIL`, and `NOT_VERIFIED` with clause citations and remediation guidance.

### 6. India State-Wise Thermal Vulnerability Index (TVI)
- A transparent 0–100 composite index synthesizing Heat Exposure, Extreme Heatwave Days, Wet-Bulb Heat Stress, Cooling Energy Burden, Housing Stock Vulnerability, and Adaptive Infrastructure Capacity.
- Full provenance registry citing IMD Climatological Tables, BEE, Census of India, NDMA, and MoHFW.

---

## 🚀 Quickstart & Local Development

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 2. Backend Setup & Run (FastAPI)
```bash
# 1. Install Python requirements
pip install -r requirements.txt

# 2. Run the FastAPI development server
uvicorn backend.main:app --reload --port 8000
```
- **API Documentation (Swagger UI):** [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check:** [http://localhost:8000/api/health](http://localhost:8000/api/health)

### 3. Frontend Setup & Run (React + Vite)
```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start Vite development server
npm run dev
```
- **Web Application URL:** [http://localhost:5173](http://localhost:5173)

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | `GET` | Health check & engine status verification |
| `/api/climate/locations` | `GET` | Cataloged Indian meteorological stations |
| `/api/climate/analyze/{location_id}` | `GET` | 24-hr diurnal weather profile & psychrometrics |
| `/api/thermal-vulnerability` | `GET` | State-wise Thermal Vulnerability Index (TVI) and rankings |
| `/api/thermal-vulnerability/{state}` | `GET` | Single-state TVI breakdown and passive design priorities |
| `/api/recommendations/run` | `POST` | Multi-factor material and construction recommendations |
| `/api/compliance/check` | `POST` | Regulatory screening against ENS, ECBC, NBC, and state byelaws |
| `/api/compliance/regulations/{state}` | `GET` | State-specific building regulation document |
| `/api/simulation/run` | `POST` | 24-hr transient RC thermal simulation, comfort, and energy |
| `/api/simulation/what-if` | `POST` | Baseline vs modified retrofit sensitivity comparator |
| `/api/optimization/run` | `POST` | NSGA-II multi-objective Pareto search |
| `/api/digital-twin/config` | `POST` | 3D geometry coordinates, solar vectors, and sol-air fields |
| `/api/results/explain` | `POST` | Explainable AI engineering rationale narratives |
| `/api/results/pdf` | `POST` | Certified PDF engineering report export |

---

## 🧪 Testing & Verification

Run the full pytest test suite covering physics, optimization, TVI, compliance, and API routes:
```bash
python -m pytest tests/ backend/tests/
```

Run frontend production build verification:
```bash
cd frontend && npm run build
```

---

## ⚖️ Scientific & Regulatory Disclaimers

1. **Compliance Screening:** ShelterAI provides preliminary design and energy compliance screening based on published central codes and state building byelaws. It is not a substitute for formal approval by the competent municipal authority or structural certification by licensed professionals.
2. **Thermal Vulnerability Index:** The ShelterAI Thermal Vulnerability Index is a research/decision-support indicator constructed from documented Indian climatological, energy, and housing datasets. It is not an official Government of India vulnerability ranking.
