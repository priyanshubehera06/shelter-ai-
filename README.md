# ShelterAI — Climate-Resilient Passive Thermal Engineering Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![Three.js](https://img.shields.io/badge/Three.js-r128%20%2F%20R3F-black.svg)](https://threejs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)
[![Tests](https://img.shields.io/badge/Tests-88%2F88%20Passed-brightgreen.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**ShelterAI** is a physics-informed, multi-physics building design and decision-support platform engineered for climate-resilient, affordable, and low-carbon shelters. It synthesizes meteorological intelligence, state-specific thermal vulnerability indices (TVI), energy building codes (Eco-Niwas Samhita 2021, ECBC 2017, NBC 2016), and evolutionary multi-objective optimization (NSGA-II) to deliver optimized passive thermal shelter designs.

---

## 🏛️ System Architecture

```
                                 SHELTER-AI FULL-STACK PLATFORM

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              REACT + TYPESCRIPT + VITE (SPA)                                │
│                                                                                             │
│  01. Certified Workflow Dashboard           02. Target Location & Climate                   │
│  03. Parametric Shelter Design Lab          04. Materials & Construction Layers             │
│  05. Multi-Physics Simulation & 3D Twin     06. Comparative Thermal Design (What-If)        │
│  07. Pareto Optimization (NSGA-II)          08. Decision Matrix & Scientific Audit          │
│                                                                                             │
│               Three.js / React Three Fiber / @react-three/drei / TailwindCSS                │
└──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │
                                      REST API (JSON & PDF)
                                               │
┌──────────────────────────────────────────────▼──────────────────────────────────────────────┐
│                                    FASTAPI REST BACKEND                                     │
│                                                                                             │
│  /api/climate             /api/thermal-vulnerability        /api/recommendations            │
│  /api/compliance          /api/designs                      /api/materials                  │
│  /api/simulation          /api/optimization                 /api/digital-twin               │
│  /api/results/explain     /api/results/pdf                  /api/simulation/export-ansys    │
└──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │
┌──────────────────────────────────────────────▼──────────────────────────────────────────────┐
│                                PYTHON PHYSICS & CAD ENGINES                                 │
│                                                                                             │
│  • engine/thermal.py          (24-hr Transient Energy Balance ODE Solver)                   │
│  • engine/solar.py            (NOAA Solar Position, Incidence Angle & Solar Flux)           │
│  • engine/geometry.py         (Parametric CAD Shell, Envelope Area & S/V Volume)            │
│  • engine/materials.py        (PBR Database, ISO 6946 Composite U-Values & Embodied Carbon) │
│  • engine/comfort.py          (Fanger PMV/PPD & ASHRAE 55 Adaptive Comfort Hours)           │
│  • engine/optimizer.py        (NSGA-II Genetic Pareto Search & MCDA Scoring)                │
│  • engine/ansys_export.py     (PyANSYS Fluent 3D CHT Scripts & APDL Thermal Macros)         │
│  • engine/explainability.py   (5-Pillar Climate-Aware Explainable AI Audits)                │
│  • reports/report_generator.py(Certified Engineering PDF Generation)                       │
└──────────────────────────────────────────────┬──────────────────────────────────────────────┘
                                               │
┌──────────────────────────────────────────────▼──────────────────────────────────────────────┐
│                             DATA REGISTRY & REGULATORY DATABASE                             │
│                                                                                             │
│  • data/tvi/state_vulnerability_data.json                                                   │
│  • data/regulations/central/ (ENS 2021, ECBC 2017, NBC 2016)                                │
│  • data/regulations/states/  (OD, RJ, MH, KA, GJ, TN, WB, UP, AS, KL)                       │
│  • data/climate/             (IMD Station Normals & Solar Radiation Datasets)               │
└─────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🌟 Key Platform Capabilities

### 1. 🌡️ First-Principles Transient Thermal Energy Solver
Simulates 24-hour time-dependent thermal response using lumped-capacitance heat balance differential equations:
$$\rho \cdot V \cdot C_p \frac{dT_{\text{in}}}{dt} = Q_{\text{solar}}(t) - Q_{\text{cond}}(t) - Q_{\text{conv}}(t) - Q_{\text{rad}}(t) - Q_{\text{inf}}(t) + Q_{\text{internal}}(t)$$
- Solves for internal air temperature, envelope sol-air surface temperatures, thermal mass storage/release, and diurnal damping factors.
- Evaluates human comfort via Fanger PMV/PPD (ISO 7730) and ASHRAE 55 Adaptive Comfort standards.

### 2. 🎮 Interactive 3D WebGL Digital Twin (Three.js / React Three Fiber)
- **Parametric Morphing**: Live real-time dimensional updates for Length, Width, Height, Roof Pitch ($0\text{--}45^\circ$), Overhangs, and Orientation ($0\text{--}360^\circ$).
- **5 Visualization Modes**: Architectural, Solar & Shading, Thermal Heatmap, Passive Ventilation Streamlines, and Exploded Assembly.
- **Top-Right CAD Control Bar**: Instant camera presets (Isometric, Front South, Side East, Top Plan, North Elevation).
- **Fullscreen Studio Mode**: Expands the 3D twin across the display with collapsible live CAD controls and real-time geometry telemetry HUD.

### 3. 🧬 Evolutionary Multi-Objective Optimization (NSGA-II)
- Searches non-dominated Pareto frontiers balancing:
  1. **Thermal Discomfort Hours** ($\min \int |T_{\text{in}} - T_{\text{comf}}| dt$)
  2. **Capital Construction Cost** ($\min \text{CapEx}$)
  3. **Embodied Carbon Footprint** ($\min \text{kgCO}_2/\text{m}^2$)
- Provides interactive Utopia distance minimum selection and automated top candidate recommendations (Balanced, Peak Comfort, Lowest Cost, Ultra-Low Carbon).

### 4. 📋 Building Code Compliance & Thermal Vulnerability Index (TVI)
- Automated rule screening against **Eco-Niwas Samhita (ENS 2021)**, **ECBC 2017 / ECSBC 2024**, **National Building Code (NBC 2016)**, and State Building Byelaws across Indian States.
- Transparent 0–100 State-Wise Thermal Vulnerability Index (TVI) ranking states by climate exposure, housing vulnerability, and adaptive infrastructure capacity.

### 5. 📑 Certified Reports & CFD Export
- **Certified PDF Audit Reports**: Generates downloadable PDF engineering reports with spatial dimensions, diurnal temperature charts, compliance metrics, and life-cycle cost audits.
- **PyANSYS / Fluent & APDL Export**: Generates executable Python scripts for `ansys-fluent-core` (3D Conjugate Heat Transfer and Solar Ray Tracing) and MAPDL macros for finite-element thermal diffusion analysis.

---

## 📂 Repository Structure

```
shelter-ai/
├── backend/                    # FastAPI Application
│   ├── api/routes/             # Modular API endpoints (climate, simulation, compliance, etc.)
│   ├── schemas/                # Pydantic v2 data models & request/response contracts
│   ├── services/               # Service orchestration layer
│   └── tests/                  # Backend pytest test suite
├── engine/                     # Physics, Simulation, and Optimization Engines
│   ├── thermal.py              # 24-hr transient lumped-capacitance ODE solver
│   ├── solar.py                # Astronomical solar position & irradiance calculations
│   ├── geometry.py             # Parametric CAD shell & spatial envelope calculations
│   ├── materials.py            # Material database, thermal conductivity & carbon intensities
│   ├── comfort.py              # Fanger PMV/PPD & ASHRAE 55 Adaptive Comfort
│   ├── optimizer.py            # NSGA-II genetic optimization algorithm
│   ├── ansys_export.py         # PyANSYS Fluent & APDL macro generator
│   └── explainability.py       # 5-Pillar XAI engineering audit generator
├── frontend/                   # Modern React + TypeScript + Vite Web Application
│   ├── src/
│   │   ├── api/                # Axios API client & typed endpoints
│   │   ├── components/         # Reusable UI primitives, cards, charts, and navigation
│   │   ├── digitalTwin/        # Three.js / React Three Fiber 3D scene & parametric meshes
│   │   ├── pages/              # 8 Workflow Screens (Home, Climate, Design, Materials, etc.)
│   │   └── store/              # Global Zustand reactive state store
├── data/                       # Climatological normals, TVI datasets, and building regulations
├── reports/                    # FPDF2 certified PDF report generation templates
├── tests/                      # Python unit & integration test suites
├── requirements.txt            # Python dependencies
└── README.md                   # Platform documentation
```

---

## 🚀 Quickstart & Installation

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** and **npm**

### 1. Clone Repository
```bash
git clone https://github.com/your-org/shelter-ai.git
cd shelter-ai
```

### 2. Backend Setup (FastAPI)
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI backend server (port 8000)
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```
- **Interactive Swagger Docs:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **Health Check:** [http://127.0.0.1:8000/api/health](http://127.0.0.1:8000/api/health)

### 3. Frontend Setup (React + Vite)
```bash
# In a separate terminal:
cd frontend

# Install Node dependencies
npm install

# Start Vite development server (port 5173)
npm run dev
```
- **Web Application URL:** [http://127.0.0.1:5173](http://127.0.0.1:5173)

---

## 📡 REST API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | `GET` | System health check and engine readiness |
| `/api/climate/locations` | `GET` | Catalog of Indian meteorological stations & climate profiles |
| `/api/climate/analyze/{location_id}` | `GET` | 24-hr diurnal meteorological profile & psychrometrics |
| `/api/thermal-vulnerability` | `GET` | State-wise Thermal Vulnerability Index (TVI) and rankings |
| `/api/recommendations/run` | `POST` | Multi-factor material & construction recommendations |
| `/api/compliance/check` | `POST` | Regulatory screening against ENS 2021, ECBC 2017, and NBC 2016 |
| `/api/simulation/run` | `POST` | 24-hr transient RC thermal simulation & hourly telemetry |
| `/api/simulation/what-if` | `POST` | Side-by-side sensitivity comparison (Baseline vs. Retrofit) |
| `/api/simulation/export-ansys` | `POST` | Generates PyANSYS Fluent scripts (`.py`) & APDL macros (`.mac`) |
| `/api/optimization/run` | `POST` | NSGA-II multi-objective Pareto search |
| `/api/digital-twin/config` | `POST` | 3D geometry coordinates, solar vectors, and sol-air fields |
| `/api/results/explain` | `POST` | 5-Pillar Explainable AI engineering audit |
| `/api/results/pdf` | `POST` | Generates downloadable certified engineering PDF report |

---

## 🧪 Testing & Verification

### Run Python Test Suite (88 Tests)
```bash
python -m pytest
```

### Run Frontend Production Build
```bash
cd frontend
npm run build
```

---

## ⚖️ Scientific & Regulatory References

1. **ASHRAE Standard 55-2020**: *Thermal Environmental Conditions for Human Occupancy*.
2. **Bureau of Energy Efficiency (BEE)**: *Eco-Niwas Samhita (ENS) 2021 & Energy Conservation Building Code (ECBC) 2017*.
3. **Bureau of Indian Standards (BIS)**: *National Building Code of India (NBC 2016), SP 7*.
4. **India Meteorological Department (IMD)**: *Climatological Normals & Diurnal Solar Radiation Tables*.
5. **ISO 7730:2005**: *Moderate thermal environments — Determination of the PMV and PPD indices*.
6. **ISO 6946:2017**: *Building components and building elements — Thermal resistance and thermal transmittance*.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.
