# SHELTER-AI — Intelligent Climate-Adaptive Shelter Platform

> **Platform Mission:** *"Software Based Model Development for Design of Area Specific Shelter for Thermal Comfort Maintenance."*

SHELTER-AI is a physics-informed, multi-physics building design and decision-support platform. It analyzes local meteorological conditions and generates optimized, climate-responsive shelter designs based on parametric geometry, envelope materials, thermal mass, astronomical solar tracking, natural ventilation, ASHRAE 55 PMV comfort, operational HVAC energy, construction CapEx, and multi-objective evolutionary optimization.

---

## 🏛️ System Architecture

```
                    SHELTER-AI FULL-STACK PLATFORM

┌────────────────────────────────────────────────────────────────────────┐
│                   REACT + TYPESCRIPT + VITE (SPA)                      │
│                                                                        │
│  01. Overview         02. Location Setup     03. Climate Intelligence │
│  04. Design Lab       05. 3D Digital Twin    06. Optimization (NSGA-II)│
│  07. What-If Lab      08. Results & XAI Audit                          │
│                                                                        │
│          Three.js / React Three Fiber / @react-three/drei              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                           REST API (JSON & PDF)
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         FASTAPI REST BACKEND                           │
│                                                                        │
│  /api/climate         /api/designs           /api/materials            │
│  /api/simulation      /api/optimization      /api/digital-twin         │
│  /api/results         /api/health                                      │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                    PYTHON PHYSICS & CAD ENGINE                         │
│                     (Engine Source of Truth)                           │
│                                                                        │
│  • geometry.py         • climate.py           • materials.py           │
│  • thermal.py          • comfort.py           • energy.py              │
│  • cost.py             • optimizer.py         • scoring.py             │
│  • explainability.py   • extreme_analysis.py  • geolocation.py         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         DATA & METEOROLOGY                             │
│                                                                        │
│  • data/materials.csv  • data/sample_designs.json • database/shelter.db│
└────────────────────────────────────────────────────────────────────────┘
```

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

# 2. Start the Vite development server
npm run dev
```
- **Web Application URL:** [http://localhost:5173](http://localhost:5173)

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | `GET` | Health check & engine status verification |
| `/api/climate/locations` | `GET` | List all cataloged Indian meteorological stations |
| `/api/climate/analyze/{location_id}` | `GET` | 24-hr diurnal weather profile, extreme scenarios, and psychrometrics |
| `/api/materials` | `GET` | Envelope catalog (CSEB, brick, AAC, sandwich panels, thatch, CGI) |
| `/api/materials/u-value` | `POST` | Layered assembly $U$-value, $R$-value, and thermal mass computation |
| `/api/designs` | `GET` | Baseline pre-configured shelter archetypes |
| `/api/designs/metrics` | `POST` | Parametric geometric and surface envelope metrics |
| `/api/simulation/run` | `POST` | 24-hr transient RC thermal simulation, PMV comfort, energy & cost |
| `/api/simulation/what-if` | `POST` | Side-by-side baseline vs modified retrofit comparator |
| `/api/optimization/run` | `POST` | NSGA-II multi-objective Pareto search (Comfort vs Cost vs Carbon) |
| `/api/digital-twin/config` | `POST` | 3D bounding geometry, NOAA solar trajectory & Sol-Air scalar fields |
| `/api/results/explain` | `POST` | Transparent Explainable AI rationale narratives |
| `/api/results/pdf` | `POST` | Downloadable certified PDF engineering audit report |

---

## 🌐 3D Digital Twin Architecture (React Three Fiber)

1. **Hardware-Accelerated WebGL Rendering**: Driven by React Three Fiber and Three.js with soft shadows, PBR roughness/metalness materials, and OrbitControls.
2. **Astronomical Solar Tracking**: NOAA solar altitude and azimuth calculations place directional sunlight and diurnal spline trajectory arcs precisely matching local coordinates and time of day.
3. **Multi-Physics View Modes**:
   - **Architectural**: Realistic textures and finishes.
   - **Solar & Shading**: Directional solar beams and overhang shading projections.
   - **Thermal Heatmap**: Sol-Air scalar temperature gradients ($T_{\text{out}} + \alpha \cdot GHI / h_o$).
   - **Passive Ventilation**: Streamline airflow tubes through envelope openings.
   - **Exploded Assembly**: Parametric vertical layer separation for plinth, walls, and roof.
4. **Camera Presets**: `Isometric`, `Front (South)`, `Side (East)`, `Top (Plan)`, `North Elevation`.

---

## 🧪 Testing

Run both the engine test suite and FastAPI API integration tests:
```bash
python -m pytest tests/ backend/tests/
```
All **75 tests** pass with 100% numerical consistency.
