# ShelterAI — Climate-Responsive Passive Thermal Engineering Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB.svg)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-3178C6.svg)](https://www.typescriptlang.org/)
[![Three.js](https://img.shields.io/badge/Three.js-R3F-black.svg)](https://threejs.org/)
[![Vite](https://img.shields.io/badge/Vite-6.0-646CFF.svg)](https://vitejs.dev/)
[![Tests](https://img.shields.io/badge/Tests-90%2F90%20Passed-brightgreen.svg)]()
[![Deployment](https://img.shields.io/badge/Deploy-Vercel%20%2B%20Render-black.svg)]()

**ShelterAI** is a physics-informed, climate-responsive building design, simulation, and optimization platform. Focused primarily on high-altitude extreme cold regions such as **Ladakh** as well as diverse Indian climate zones, ShelterAI enables engineers, architects, and disaster relief planners to evaluate passive solar heat gain, thermal mass insulation, envelope conduction losses, indoor diurnal temperatures, thermal comfort (Fanger PMV/PPD & ASHRAE 55 Adaptive Comfort), and multi-objective Pareto optimization (NSGA-II).

---

## 🏛️ Production Architecture

```
                    USER BROWSER
                         │
                         ▼
                 ┌───────────────┐
                 │    VERCEL     │
                 │               │
                 │  React 18     │
                 │  TypeScript   │
                 │  Vite + R3F   │
                 │  Three.js     │
                 └───────┬───────┘
                         │
                         │ HTTPS (REST API)
                         │
                         ▼
                 ┌───────────────┐
                 │    RENDER     │
                 │               │
                 │  FastAPI      │
                 │  Python 3.10+ │
                 │  Uvicorn      │
                 └───────┬───────┘
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ▼              ▼              ▼
   ┌─────────────┐┌─────────────┐┌─────────────┐
   │   Climate   ││   Thermal   ││ Evolutionary│
   │   Service   ││   Physics   ││  Optimizer  │
   │ (Open-Meteo)││  (3R2C RC)  ││  (NSGA-II)  │
   └─────────────┘└─────────────┘└─────────────┘
```

---

## 🚀 Local Development

### 1. Backend (FastAPI + Python)

From the repository root:

```bash
# 1. Create and activate a clean virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start FastAPI development server
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be live at `http://localhost:8000`.  
- Interactive API Docs (Swagger): `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Frontend (React + Vite + TypeScript)

In a new terminal:

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start Vite dev server
npm run dev
```

The frontend SPA will be live at `http://localhost:5173`.

---

## ⚙️ Environment Variables

### Frontend (`frontend/.env`)
| Variable | Default (Local) | Production Example (Vercel) | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | `https://shelterai-api.onrender.com` | Base URL of deployed FastAPI backend |

### Backend (`backend/.env` or Render Environment)
| Variable | Default (Local) | Production Example (Render) | Description |
|---|---|---|---|
| `ENVIRONMENT` | `development` | `production` | Deployment mode |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | `https://shelterai.vercel.app` | Vercel production frontend origin for CORS |
| `CORS_ORIGINS` | `*` (dev only) | `https://shelterai.vercel.app` | Comma-separated allowed origins |
| `PORT` | `8000` | `$PORT` (assigned by Render) | Listening port for Uvicorn |
| `HOST` | `0.0.0.0` | `0.0.0.0` | Binding network interface |

---

## ☀️ Real-Time Climate API & Telemetry

ShelterAI integrates seamlessly with the **Open-Meteo API** to provide live meteorological streams and historical TMY datasets:
- **Diurnal Profiles**: 24-hour hourly dry-bulb temperature ($T_{out}$), relative humidity ($RH$), Global Horizontal Irradiance ($GHI$), and wind velocity.
- **Fail-Safe Operation**: If external telemetry is temporarily unavailable, the system flags `CLIMATE_DATA_UNAVAILABLE` and offers instant fallbacks to **Manual Diurnal Specification** or **Packaged Historical EPW datasets (Leh, Ladakh / Delhi / Sambalpur)** without halting simulations.

---

## 🌐 Vercel Frontend Deployment

1. Import the repository on [Vercel](https://vercel.com).
2. Set **Root Directory** to `frontend`.
3. Framework Preset: `Vite`.
4. Build Command: `npm run build` (Output Directory: `dist`).
5. Add Environment Variable:
   ```
   VITE_API_BASE_URL = https://your-render-backend.onrender.com
   ```
6. Click **Deploy**.
7. Single-page navigation (`/climate`, `/design`, `/materials`, `/simulate`, `/compare`, `/optimize`, `/results`) is automatically handled by `frontend/vercel.json`.

---

## 🛠️ Render Backend Deployment

1. Create a new **Web Service** on [Render](https://render.com).
2. Connect your GitHub repository.
3. Configure settings:
   - **Root Directory**: `.` (leave as root)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
4. Add Environment Variables:
   ```
   ENVIRONMENT = production
   FRONTEND_ORIGIN = https://your-vercel-app.vercel.app
   ```
5. Click **Create Web Service**.

---

## 🔌 API Endpoints Summary

| Endpoint | Method | Description |
|---|:---:|---|
| `/health` | `GET` | Ultra-fast health check (`{"status": "ok"}`) |
| `/` | `GET` | API root discovery |
| `/api/climate/locations` | `GET` | Indian meteorological station catalog |
| `/api/climate/ip-location` | `GET` | IP / GPS location resolver |
| `/api/climate/analyze/{loc_id}` | `GET` | 24-hr diurnal weather cycle & solar analysis |
| `/api/materials` | `GET` | Certified thermal building materials database |
| `/api/designs` | `GET` | Parametric shelter archetype presets |
| `/api/simulation/run` | `POST` | 24-hr transient RC thermal & comfort simulation |
| `/api/simulation/what-if` | `POST` | Side-by-side design comparison solver |
| `/api/optimization/run` | `POST` | NSGA-II Multi-Objective Evolutionary Optimizer |
| `/api/digital-twin/config` | `POST` | 3D Digital Twin geometry & NOAA solar vector |
| `/api/results/pdf` | `POST` | In-memory dynamic PDF audit export |
| `/api/simulation/export-ansys` | `POST` | Dynamic PyANSYS Fluent & APDL decks |

---

## 🧪 Testing

Execute the comprehensive unit and integration test suite:

```bash
# Run all 90 backend and physics tests
python -m pytest

# Run frontend build check
cd frontend && npm run build
```

---

## 🚨 Troubleshooting

- **CORS Errors**: Ensure `FRONTEND_ORIGIN` on Render matches your exact Vercel URL (e.g. `https://shelterai.vercel.app`). Preview branches on `*.vercel.app` are automatically supported.
- **Render Cold Start**: The free tier of Render spins down containers after 15 minutes of inactivity. Initial request may take ~30s while waking up.
- **Vercel 404 on Refresh**: Ensure `frontend/vercel.json` rewrite rule is active.
