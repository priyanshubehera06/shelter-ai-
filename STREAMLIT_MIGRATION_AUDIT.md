# SHELTER-AI — Streamlit Migration Audit

This audit document details every Streamlit file, import, UI element, session state mechanism, cache, and dependency across the Shelter-AI codebase, mapping each item to its production-ready pure React + Vite + TypeScript frontend and FastAPI backend counterpart.

---

## 1. Streamlit Files Inventory & Disposition

| Streamlit File | Path | Role / Original Purpose | Disposition | React / FastAPI Equivalent |
|---|---|---|---|---|
| `app_streamlit.py` | `shelter-ai/app_streamlit.py` | Streamlit top-level entry point & navigation hub | **DELETE** | `frontend/src/App.tsx`, `frontend/src/pages/HomePage.tsx` |
| `01_Home.py` | `shelter-ai/pages/01_Home.py` | Streamlit landing & workflow pipeline page | **DELETE** | `frontend/src/pages/HomePage.tsx` |
| `02_Location.py` | `shelter-ai/pages/02_Location.py` | Location picker, live GPS, climate dataset viewer | **DELETE** | `frontend/src/pages/LocationClimatePage.tsx` |
| `03_Climate_Intelligence.py` | `shelter-ai/pages/03_Climate_Intelligence.py` | Diurnal climate analysis & solar graphs | **DELETE** | `frontend/src/pages/LocationClimatePage.tsx` + `frontend/src/components/charts/` |
| `04_Design_Lab.py` | `shelter-ai/pages/04_Design_Lab.py` | Parametric dimensions & envelope materials | **DELETE** | `frontend/src/pages/ShelterDesignLabPage.tsx` |
| `05_Digital_Twin.py` | `shelter-ai/pages/05_Digital_Twin.py` | 3D visualizer & thermal telemetry HUD | **DELETE** | `frontend/src/pages/DigitalTwinPage.tsx` + `frontend/src/digitalTwin/ShelterCanvas.tsx` |
| `06_Optimization.py` | `shelter-ai/pages/06_Optimization.py` | Pareto multi-objective genetic optimization | **DELETE** | `frontend/src/pages/OptimizationPage.tsx` |
| `07_What_If_Lab.py` | `shelter-ai/pages/07_What_If_Lab.py` | Scenario sensitivity & comparative simulation | **DELETE** | `frontend/src/pages/WhatIfLabPage.tsx` |
| `08_Results.py` | `shelter-ai/pages/08_Results.py` | Recommended designs, explainability & PDF export | **DELETE** | `frontend/src/pages/ResultsPage.tsx` |
| `location_widget.py` | `shelter-ai/engine/location_widget.py` | Streamlit sidebar location selector & GPS button | **DELETE** | `frontend/src/components/location/LocationSelector.tsx` |
| `shelter_3d.py` | `shelter-ai/visualization/shelter_3d.py` | PyVista/VTK WebGL renderer for Streamlit | **CLEAN/REF`** (Remove Streamlit imports/components) | `frontend/src/digitalTwin/` (Three.js / React Three Fiber) |
| `climate.py` | `shelter-ai/engine/climate.py` | Line 182 Streamlit session state check | **CLEAN** (Remove `st.session_state` check) | `backend/services/climate_service.py` / `engine/climate.py` |

---

## 2. Streamlit Imports & Dependencies

### Python Dependencies:
- `requirements-dev.txt`: contains `streamlit>=1.30.0` $\rightarrow$ **REMOVE**.
- `requirements.txt`: clean (contains only `fastapi`, `uvicorn`, `pydantic`, `numpy`, `pandas`, `scipy`, `requests`, `httpx`, `python-multipart`).
- `pyproject.toml`: clean (only core backend dependencies).

### Streamlit Imports to Remove:
- `import streamlit as st`
- `import streamlit.components.v1 as components`
- `from engine.location_widget import render_location_sidebar_widget`

---

## 3. UI Component Mapping (Streamlit $\rightarrow$ React + Vite)

| Streamlit Component / Hook | React + Vite + TypeScript Replacement | Implementation Location |
|---|---|---|
| `st.title()`, `st.header()`, `st.subheader()` | Tailwind styled semantic typography `<h1>`, `<h2>`, `<h3>` | `frontend/src/pages/*` |
| `st.button()` | React `<button>` / Lucide icon buttons | `frontend/src/components/common/*` |
| `st.selectbox()`, `st.radio()` | Controlled `<select>`, custom pill-selector, radio components | `frontend/src/pages/ShelterDesignLabPage.tsx` |
| `st.slider()`, `st.number_input()` | Controlled `<input type="range">` with direct state binds | `frontend/src/pages/ShelterDesignLabPage.tsx` |
| `st.tabs()` | React Tab Switcher with tab state | `frontend/src/pages/DigitalTwinPage.tsx` |
| `st.metric()` | React Metric Card components with deltas & badges | `frontend/src/components/common/MetricCard.tsx` |
| `st.plotly_chart()` | Recharts (`ResponsiveContainer`, `LineChart`, `AreaChart`, `BarChart`) | `frontend/src/components/charts/*` |
| `st.dataframe()` | Responsive HTML5 table with Tailwind grid styling | `frontend/src/pages/LocationClimatePage.tsx` |
| `st.spinner()` | Tailwind spinner / Lucide `<Loader2 className="animate-spin" />` | `frontend/src/components/common/LoadingSpinner.tsx` |
| `st.download_button()` | Axios blob response trigger or direct browser download | `frontend/src/pages/ResultsPage.tsx` |
| `st.switch_page()` | React Router `useNavigate()` / `<NavLink to="...">` | `frontend/src/components/layout/Navbar.tsx` |
| `st.sidebar` | Collapsible / persistent responsive AppLayout Sidebar | `frontend/src/components/layout/AppLayout.tsx` |
| PyVista 3D Renderer | **Three.js + React Three Fiber + React Three Drei** | `frontend/src/digitalTwin/ShelterCanvas.tsx` |

---

## 4. State Management & Caching Migration

| Streamlit Mechanism | Production React / FastAPI Equivalent | Location |
|---|---|---|
| `st.session_state["current_design"]` | Zustand Store (`useShelterStore`) | `frontend/src/store/useShelterStore.ts` |
| `st.session_state["auto_geo_data"]` | Zustand Store + TanStack React Query | `frontend/src/store/useLocationStore.ts` |
| `st.session_state["opt_results"]` | Zustand Store (`useOptimizationStore`) | `frontend/src/store/useOptimizationStore.ts` |
| `@st.cache_data` for Open-Meteo | FastAPI in-memory / TTL caching service | `backend/services/climate_service.py` |
| `@st.cache_resource` | FastAPI lifespan startup handlers | `backend/main.py` |

---

## 5. Deployment Architecture Migration

- **Old (Legacy):** `streamlit run app_streamlit.py`
- **New (100% Pure Architecture):**
  - **Frontend:** Pure React 18 + TypeScript + Vite deployed on **Vercel** (`frontend/`)
  - **Backend:** FastAPI + Uvicorn + Python Physics Engine deployed on **Render / Railway / Container** (`backend.main:app`)
  - **Communication:** Standard REST JSON / HTTPS endpoints (`/api/v1/*`)
