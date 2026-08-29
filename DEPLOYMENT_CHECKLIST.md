# ShelterAI — Production Deployment Checklist & Operations Runbook

**Architecture Target**: Vercel (Frontend React SPA) + Render (Backend FastAPI Python Service)  
**Primary Region Context**: High-Altitude Cold Region (Ladakh) & Multi-Zone Indian Meteorological Catalog

---

## 1. Pre-Deployment Readiness Matrix

| Status | Verification Item | Specification / Verification Method | Result |
|:---:|---|---|:---:|
| ✅ | **Frontend TypeScript Compilation** | `npm run build` in `frontend/` executes `tsc && vite build` | Passed (0 TS errors) |
| ✅ | **Frontend Production Bundle** | Outputs clean minified assets to `frontend/dist/` | Verified (`dist/index.html`) |
| ✅ | **FastAPI Core Startup** | `uvicorn backend.main:app --host 0.0.0.0 --port 8000` | Passed (< 0.2s start) |
| ✅ | **Fast Health Endpoint** | `GET /health` returns `{"status": "ok"}` in < 2ms | Verified |
| ✅ | **Root Status Endpoint** | `GET /` returns `{"name": "ShelterAI API", "status": "running"}` | Verified |
| ✅ | **CORS Configuration** | Dynamic origin resolution + Vercel regex preview support | Configured |
| ✅ | **Open-Meteo Integration** | 24-hr live forecast, reverse geocoding & fallback handling | Verified |
| ✅ | **Stateless Backend** | In-memory physics simulation & transient RC solver | 0 disk writes required |
| ✅ | **No Secrets in Repo** | Comprehensive git search for tokens, keys, credentials | Clean |
| ✅ | **No Hardcoded Absolute Paths** | Relative POSIX paths across 3D models and data | Clean |

---

## 2. Step-by-Step GitHub Setup

1. **Commit & Push Code**:
   ```bash
   git add .
   git commit -m "feat(deploy): production hardening for Vercel and Render deployment"
   git push origin main
   ```
2. **Verify Repository Structure**:
   - `frontend/`: Contains `package.json`, `vite.config.ts`, `vercel.json`, `src/`
   - `backend/`: Contains `main.py`, `requirements.txt`, `api/`, `services/`
   - `engine/`: Contains `thermal.py`, `solar.py`, `climate.py`, `materials.py`, `optimizer.py`, etc.
   - `data/`: Contains read-only `climate/` and `tvi/` datasets

---

## 3. Step-by-Step Render Backend Deployment

1. **Create Web Service on Render**:
   - Navigate to [Render Dashboard](https://dashboard.render.com/) -> **New** -> **Web Service**.
   - Connect your GitHub repository: `shelter-ai`.
2. **Configure Service Settings**:
   - **Name**: `shelterai-api` (or preferred name)
   - **Region**: Singapore / Frankfurt / Oregon (nearest to user traffic)
   - **Branch**: `main`
   - **Root Directory**: `.` (leave as repository root so `engine/` and `backend/` are top-level)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free or Starter
3. **Configure Environment Variables in Render**:
   - `ENVIRONMENT`: `production`
   - `FRONTEND_ORIGIN`: `https://shelterai.vercel.app` (Update with your actual Vercel domain)
4. **Health Check Path**:
   - Set Health Check Path to `/health`
5. **Deploy**:
   - Click **Create Web Service**.
   - Note the assigned live URL: `https://shelterai-api.onrender.com`

---

## 4. Step-by-Step Vercel Frontend Deployment

1. **Create Project on Vercel**:
   - Navigate to [Vercel Dashboard](https://vercel.com/dashboard) -> **Add New...** -> **Project**.
   - Import your GitHub repository: `shelter-ai`.
2. **Configure Project Settings**:
   - **Framework Preset**: `Vite`
   - **Root Directory**: Click **Edit** and select `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
3. **Configure Environment Variables in Vercel**:
   - `VITE_API_BASE_URL`: `https://shelterai-api.onrender.com` (Your live Render backend URL)
4. **Deploy**:
   - Click **Deploy**.
   - Once deployed, copy your production domain: `https://<your-project-name>.vercel.app`.
5. **Update Render CORS**:
   - Return to the Render dashboard -> Environment tab -> update `FRONTEND_ORIGIN` with your exact Vercel domain.

---

## 5. End-to-End Verification Runbook

### A. Backend Verification
1. **Health Check**:
   ```bash
   curl -i https://YOUR-RENDER-SERVICE.onrender.com/health
   ```
   *Expected*: HTTP 200 `{"status":"ok"}`
2. **Root Discovery**:
   ```bash
   curl -i https://YOUR-RENDER-SERVICE.onrender.com/
   ```
   *Expected*: HTTP 200 `{"name":"ShelterAI API","status":"running"}`
3. **Climate Locations**:
   ```bash
   curl -i https://YOUR-RENDER-SERVICE.onrender.com/api/climate/locations
   ```
   *Expected*: HTTP 200 JSON array of Indian meteorological stations including Leh, Ladakh.
4. **Ladakh Climate Intelligence**:
   ```bash
   curl -i "https://YOUR-RENDER-SERVICE.onrender.com/api/climate/analyze/leh_ladakh?month=1"
   ```
   *Expected*: HTTP 200 with 24-hr sub-zero diurnal profile and solar irradiance.

### B. Frontend Verification
1. **Direct Deep Link Navigation**:
   - Test navigating directly to:
     - `https://YOUR-VERCEL-DOMAIN/climate`
     - `https://YOUR-VERCEL-DOMAIN/design`
     - `https://YOUR-VERCEL-DOMAIN/materials`
     - `https://YOUR-VERCEL-DOMAIN/simulate`
     - `https://YOUR-VERCEL-DOMAIN/compare`
     - `https://YOUR-VERCEL-DOMAIN/optimize`
     - `https://YOUR-VERCEL-DOMAIN/results`
   - *Expected*: Loads pages directly without 404 or routing failures.
2. **Real-Time Climate Workflow (Ladakh)**:
   - Go to `/climate`, select **Leh, Ladakh**.
   - Check temperature diurnal curve, peak GHI, and relative humidity.
3. **3D Digital Twin**:
   - Go to `/simulate`, verify 3D shelter renders, geometry updates on slider movement, materials update shading.
4. **Thermal Simulation & Comfort**:
   - Execute simulation for Ladakh cold envelope (AAC block / Rockwool insulation).
   - Verify indoor temperature curve, solar heat gain, heat loss breakdown, PMV/PPD thermal comfort.
5. **NSGA-II Optimization**:
   - Go to `/optimize`, run evolutionary Pareto solver.
   - Verify Pareto frontier generation (Thermal Comfort vs CapEx vs Embodied Carbon).

---

## 6. Troubleshooting Guide

| Issue | Root Cause | Solution |
|---|---|---|
| **CORS Error on Vercel** | Backend origin mismatch | Set `FRONTEND_ORIGIN` on Render to match the exact Vercel domain (e.g. `https://shelterai.vercel.app`). Preview deployments are automatically whitelisted via `*.vercel.app` regex. |
| **API 404 on Render** | Missing `/api` prefix | Backend registers routes under both `/api/*` and `/*`. Verify `VITE_API_BASE_URL` on Vercel is set to `https://<render-url>`. |
| **Spin-up Delay on Render Free Tier** | Container spin-down after 15m inactivity | Normal behavior on Render free tier (takes ~30-50s to cold start). The frontend displays a friendly loading indicator. |
| **Open-Meteo Rate Limiting or Down** | Upstream weather API temporarily unreachable | Backend returns `CLIMATE_DATA_UNAVAILABLE`. Frontend enables **Manual Profile** or **Historical EPW** mode instantly. |
| **Vercel Deep-link 404** | Missing SPA rewrite rule | Verified `frontend/vercel.json` contains `rewrites: [{"source": "/(.*)", "destination": "/index.html"}]`. |
