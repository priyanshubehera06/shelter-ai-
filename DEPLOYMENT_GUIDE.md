# ShelterAI — Full-Stack Deployment Architecture Guide

```
┌────────────────────────────────────────────┐
│                 GitHub                     │
│               shelter-ai                   │
└─────────────────────┬──────────────────────┘
                      │
          ┌───────────┴───────────┐
          ↓                       ↓
      VERCEL                   RAILWAY
          │                       │
      React/TS                FastAPI
      Vite                    Python
          │                       │
          │                ┌──────┴───────┐
          │                ↓              ↓
          │             ENGINE        DATA
          │                │
          │        ┌───────┼────────┐
          │        ↓       ↓        ↓
          │     Thermal  Climate  Optimizer
          │
          ↓
    React Three Fiber
          │
    ┌─────┴───────────────┐
    ↓                     ↓
High-quality GLB      PBR Materials
Shelter Models        + Textures
```

---

## 1. Backend Deployment: Railway (FastAPI + Python Simulation Engine)

### Step 1: Connect Repository to Railway
1. Go to [railway.app](https://railway.app) and create a **New Project**.
2. Select **Deploy from GitHub repo** and pick `shelter-ai`.
3. Railway will automatically detect the [`Dockerfile`](file:///c:/Users/PRIYANSHU/Documents/SIH/shelter-ai/Dockerfile) and [`railway.json`](file:///c:/Users/PRIYANSHU/Documents/SIH/shelter-ai/railway.json).

### Step 2: Configure Environment Variables on Railway
In your Railway dashboard under **Variables**, set:
- `PORT`: `8000` (or leave default assigned by Railway)
- `PYTHONUNBUFFERED`: `1`

### Step 3: Generate Public Domain
Under **Settings** → **Networking**, click **Generate Domain** (e.g. `https://shelter-ai-backend.up.railway.app`).

### Verify Backend Health
```bash
curl https://shelter-ai-backend.up.railway.app/api/health
# Returns: {"status":"healthy","service":"ShelterAI API","version":"1.0.0"}
```

---

## 2. Frontend Deployment: Vercel (React + TypeScript + Vite + R3F)

### Step 1: Connect Repository to Vercel
1. Go to [vercel.com](https://vercel.com) and click **Add New** → **Project**.
2. Select the `shelter-ai` GitHub repository.
3. Set **Root Directory** to `frontend`.
4. The build settings are auto-configured by Vite:
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

### Step 2: Configure Environment Variables on Vercel
Under **Environment Variables**, set:
- `VITE_API_URL`: `https://shelter-ai-backend.up.railway.app/api`

### Step 3: Deploy
Click **Deploy**. Vercel will build the frontend and serve it with client-side SPA routing governed by [`frontend/vercel.json`](file:///c:/Users/PRIYANSHU/Documents/SIH/shelter-ai/frontend/vercel.json).

---

## 3. 3D Digital Twin Model & Assets Pipeline

- **Procedural PBR Model**: Built into React Three Fiber with dynamic parametric roof types (Gable, Monoslope, Hip, Flat), foundation plinth, layered exterior walls, transparent glazing panes, solid timber door, and solar louvers.
- **External GLB Support**: The [`ShelterModel`](file:///c:/Users/PRIYANSHU/Documents/SIH/shelter-ai/frontend/src/digitalTwin/models/ShelterModel.tsx) component supports custom GLB 3D shelter models by passing `glbUrl` with automatic shadow casting/receiving and fallback to the procedural model.
- **Astronomical Solar & Climate Trajectories**: Real-time NOAA solar tracking and 24-hr diurnal spline curves calculated from the backend climate intelligence engine.
