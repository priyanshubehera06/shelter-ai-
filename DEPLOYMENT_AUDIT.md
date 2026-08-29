# ShelterAI — Comprehensive Deployment Audit

**Date**: August 2026  
**Audited Target**: React (Vite + TypeScript) on Vercel & FastAPI (Python) on Render  
**Platform Domain**: Climate-Responsive Passive Thermal Shelter Design, Simulation & Optimization Platform (Primary Focus: High-Altitude Cold Region Ladakh)

---

## 1. Current Architecture Overview

```
                      +-----------------------------+
                      |         Web Client          |
                      |   (Desktop / Tablet / Mob)  |
                      +--------------+--------------+
                                     |
                                HTTPS (SPA)
                                     v
                      +-----------------------------+
                      |     Vercel Frontend CDN     |
                      |   React 18 + TypeScript     |
                      |   Vite + Three.js / R3F     |
                      |   Tailwind CSS + Zustand    |
                      +--------------+--------------+
                                     |
                          HTTPS REST API Requests
                                     v
                      +-----------------------------+
                      |   Render Web Service (PaaS) |
                      |    FastAPI Python 3.10+     |
                      |   Uvicorn ASGI Server       |
                      +--------------+--------------+
                                     |
         +---------------------------+---------------------------+
         |                           |                           |
         v                           v                           v
+------------------+       +-------------------+       +-------------------+
| Climate Service  |       |  Thermal & Solar  |       | Multi-Objective   |
| Open-Meteo Live  |       | Transient Physics |       | NSGA-II Optimizer |
| IMD/EPW Datasets |       | RC Network Model  |       | Pareto Frontiers  |
+------------------+       +-------------------+       +-------------------+
```

### Architectural Breakdown:
- **Frontend Root**: `frontend/`
- **Backend Root**: `backend/` (with core physics engine in `engine/` and catalog data in `data/`)
- **Package Management**:
  - Frontend: `package.json`, `package-lock.json`
  - Backend: `requirements.txt`, `backend/requirements.txt`, `pyproject.toml`
- **Entry Points**:
  - Frontend: `frontend/index.html` -> `frontend/src/main.tsx` -> `frontend/src/App.tsx`
  - Backend: `backend.main:app` (FastAPI instance in `backend/main.py`)

---

## 2. Frontend Startup & Build Pipeline

- **Local Dev Server**: `npm run dev` (Runs Vite on `http://localhost:5173`)
- **Production Build Command**: `npm run build` (Executes `tsc && vite build`)
- **Build Output Target**: `dist/` (Standard Vite output directory)
- **Asset Processing**: Three.js procedural geometries (walls, roofs, glazing, foundations, shading louvers) and CSS bundle minification.
- **Routing**: React Router v7 SPA routing with HTML5 history pushState (`/climate`, `/design`, `/materials`, `/simulate`, `/compare`, `/optimize`, `/results`).

---

## 3. Backend Startup & ASGI Specification

- **Entry Point Module**: `backend.main:app`
- **Local Dev Startup**: `uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000`
- **Production Startup**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
- **Concurrency & Event Loop**: Asynchronous FastAPI endpoints with underlying NumPy / SciPy transient thermal matrix solvers and multi-threaded request processing.

---

## 4. Required Environment Variables

### Frontend (Vercel):
| Variable | Development Default | Production Target (Render API) | Description |
|---|---|---|---|
| `VITE_API_BASE_URL` | `http://localhost:8000` | `https://shelterai-api.onrender.com` | Base URL for FastAPI REST endpoints |

### Backend (Render):
| Variable | Development Default | Production Target | Description |
|---|---|---|---|
| `FRONTEND_ORIGIN` | `http://localhost:5173` | `https://shelterai.vercel.app` | Vercel production frontend origin for CORS whitelist |
| `CORS_ORIGINS` | `["*"]` | (Comma-separated Vercel origins) | Additional allowed CORS origins |
| `ENVIRONMENT` | `development` | `production` | Deployment environment mode |
| `PORT` | `8000` | Assigned by Render (`$PORT`) | Network port for Uvicorn ASGI listener |
| `HOST` | `0.0.0.0` | `0.0.0.0` | Network binding interface |

---

## 5. External APIs & Telemetry

1. **Open-Meteo Live Forecast API**:
   - URL: `https://api.open-meteo.com/v1/forecast`
   - Purpose: Fetch 24-hour real-time telemetry (Dry-bulb temperature, relative humidity, shortwave solar GHI, wind velocity).
   - Parameters: `latitude`, `longitude`, `hourly=temperature_2m,relative_humidity_2m,shortwave_radiation,wind_speed_10m`.
   - Timeout: 5.0 seconds.
2. **Open-Meteo Geocoding / OpenStreetMap Nominatim**:
   - URL: `https://geocoding-api.open-meteo.com/v1/get` & `https://nominatim.openstreetmap.org/reverse`
   - Purpose: Reverse geocode GPS coordinates to Indian administrative regions and cities.
   - Timeout: 4.0 seconds.
3. **IP Geolocation Services** (`ipwho.is`, `ip-api.com`, `freeipapi.com`, `ipapi.co`):
   - Purpose: Automatic IP-to-city resolution with resilient cascading fallbacks.

---

## 6. Local Filesystem & Data Dependencies

- **Data Files**:
  - `data/climate/sample_location.csv`: Standardized 8,760-hour typical meteorological dataset.
  - `data/tvi/sources_registry.json`: State and UT meteorological normals and thermal vulnerability criteria.
- **Filesystem Nature**:
  - Read-only packaged static datasets. No stateful file persistence is required or expected across container restarts.
  - Report exports (PDF / PyANSYS Fluent scripts / APDL input decks) are streamed dynamically as in-memory HTTP byte buffers (`Response(content=..., media_type=...)`), ensuring 100% stateless serverless/container compatibility.

---

## 7. Deployment Risks & Mitigations

| Risk Identified | Potential Impact | Implemented Mitigation |
|---|---|---|
| Hardcoded API URLs | Frontend fails to connect to backend on Vercel | Centralized `src/lib/api.ts` and `src/api/client.ts` reading `VITE_API_BASE_URL` with automatic fallback. |
| CORS Origin Rejection | Browser blocks API calls from Vercel to Render | Dynamic CORS middleware supporting `FRONTEND_ORIGIN` + regex whitelist for Vercel preview domains (`https://.*\.vercel\.app`). |
| Port Binding Hardcoding | Render container crashes on startup | Read `$PORT` dynamically from environment with `0.0.0.0` host interface. |
| Open-Meteo Outage / Network Glitch | Live climate fails, simulation halted | Explicit `CLIMATE_DATA_UNAVAILABLE` status flag + automatic option for User Manual Diurnal Curve or packaged Historical EPW datasets. |
| SPA Deep Link 404s on Vercel | Direct URL navigation to `/simulate` yields 404 | `vercel.json` rewrites all non-asset routes to `/index.html`. |
| Unhandled Exceptions Leaking Stack Traces | Security vulnerability / poor UX | Global FastAPI exception handler returning structured `{ "error": { "code": "...", "message": "..." } }`. |

---

## 8. Vercel Deployment Requirements

1. **Framework Preset**: `Vite`
2. **Root Directory**: `frontend` (or repository root with root configuration)
3. **Build Command**: `npm run build`
4. **Output Directory**: `dist`
5. **Environment Variable**: `VITE_API_BASE_URL=https://<your-render-app>.onrender.com`
6. **SPA Routing**: `vercel.json` rewrite rule routing `/(.*)` to `/index.html`.

---

## 9. Render Deployment Requirements

1. **Service Type**: Web Service
2. **Environment**: `Python 3`
3. **Build Command**: `pip install -r requirements.txt`
4. **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
5. **Health Check Path**: `/health` (Responds `{ "status": "ok" }` in < 2ms)
6. **Environment Variables**:
   - `FRONTEND_ORIGIN=https://<your-vercel-app>.vercel.app`
   - `ENVIRONMENT=production`

---

## 10. Required Architectural Changes Implemented

1. Standardize Fast `/health` (`{"status": "ok"}`) and Root `/` (`{"name": "ShelterAI API", "status": "running"}`) endpoints.
2. Dynamic environment-aware CORS configuration handling production Vercel domains and preview deployments.
3. Central API client `frontend/src/lib/api.ts` standardizing all backend interactions with configurable timeouts and robust error handling.
4. TypeScript environment definitions for `VITE_API_BASE_URL` via `frontend/src/vite-env.d.ts`.
5. Support for direct `/optimize` routing alongside `/optimization`.
6. Complete clean requirements definition in `requirements.txt` and `backend/requirements.txt`.
7. Hardened `.gitignore` and `.env.example` templates.
