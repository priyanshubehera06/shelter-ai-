# Deployment Fix Plan: Decoupling PyVista from FastAPI Backend

## 1. Root Cause Analysis
During production startup on Vercel, the application fails with `500 INTERNAL_SERVER_ERROR (FUNCTION_INVOCATION_FAILED)` due to:
```
ModuleNotFoundError: No module named 'pyvista'
```
This occurs because:
1. `backend/main.py` imports `backend/api/router.py`.
2. `backend/api/router.py` includes `backend/api/routes/digital_twin.py`.
3. `backend/api/routes/digital_twin.py` imports `backend/services/digital_twin_service.py`.
4. `backend/services/digital_twin_service.py` was importing mathematical calculation utilities (`calculate_solar_position`, `get_solar_vector`, `calculate_surface_thermal_color`) from `visualization/shelter_3d.py`.
5. `visualization/shelter_3d.py` contained a top-level un-guarded `import pyvista as pv`.
6. Since PyVista is a heavy C++/OpenGL desktop rendering library not present in the lean serverless environment, the top-level import crashes during the FastAPI route registration phase.

---

## 2. Import Dependency Chain

```
[Vercel Serverless Invocation / uvicorn app:app]
    │
    ▼
backend/main.py
    │
    ▼
backend/api/router.py
    │
    ▼
backend/api/routes/digital_twin.py
    │
    ▼
backend/services/digital_twin_service.py
    │  (OLD DEPENDENCY PATH - BROKEN)
    ├──❌ from visualization.shelter_3d import ... ──► import pyvista as pv (CRASH)
    │
    │  (NEW REFACTORED PATH - CLEAN & DECOUPLED)
    └──✅ from engine.solar import calculate_solar_position, get_solar_vector, calculate_surface_thermal_color
```

---

## 3. Files Affected
1. **`engine/solar.py`** [NEW]: Extracts pure NOAA solar calculation logic, unit vector projection, and Sol-Air heat-flux surface color mapping.
2. **`backend/services/digital_twin_service.py`**: Changes import source from `visualization.shelter_3d` to `engine.solar`.
3. **`visualization/shelter_3d.py`**: Refactored to import shared logic from `engine.solar`, with lazy/safe imports for PyVista so it remains isolated for offline/legacy Streamlit tools.
4. **`tests/test_3d_geometry.py`**: Updated to test calculation functions from `engine.solar` and `visualization.shelter_3d` without hard PyVista crash.
5. **`requirements.txt`**: Confirmed clean production dependencies (FastAPI, Pydantic, NumPy, Pandas, SciPy, Requests, HTTPX).

---

## 4. PyVista-Dependent vs FastAPI-Required Functionality

| Function / Component | Requires PyVista? | Destination Module | Consumed By |
|---|---|---|---|
| `calculate_solar_position()` | ❌ No (Pure Math/NOAA) | `engine/solar.py` | FastAPI `digital_twin_service`, React Three Fiber |
| `get_solar_vector()` | ❌ No (NumPy) | `engine/solar.py` | FastAPI `digital_twin_service`, React Three Fiber |
| `calculate_surface_thermal_color()` | ❌ No (NumPy / RGB Hex) | `engine/solar.py` | FastAPI `digital_twin_service`, React Three Fiber |
| `create_pyvista_3d_shelter()` | ✅ Yes (VTK / PolyData) | `visualization/shelter_3d.py` | Legacy Streamlit (Isolated) |
| `render_pyvista_3d_shelter()` | ✅ Yes (WebGL Trame) | `visualization/shelter_3d.py` | Legacy Streamlit (Isolated) |

---

## 5. Frontend & Browser 3D Rendering Responsibility
The interactive 3D Digital Twin is rendered entirely on the client side using:
- **React Three Fiber (`@react-three/fiber`)**
- **Three.js (`three`)**
- **React Three Drei (`@react-three/drei`)**
- **PBR Materials & Dynamic GLB Models**

The FastAPI backend is responsible strictly for providing JSON metadata, solar telemetry, and component thermal values. It does not perform server-side 3D rendering.

---

## 6. Testing & Validation Plan
1. **FastAPI Import Test**:
   `python -c "from backend.main import app; print('FastAPI import OK')"` must succeed with 0 errors without PyVista.
2. **Solar Engine Test**:
   `python -c "from engine.solar import calculate_solar_position, get_solar_vector, calculate_surface_thermal_color; print('Solar engine OK')"`
3. **Digital Twin Service Test**:
   `python -c "from backend.services.digital_twin_service import get_digital_twin_config; print('Digital Twin service OK')"`
4. **Full Pytest Suite**:
   `python -m pytest tests/ backend/tests/` (75+ tests passing).
5. **Frontend Production Build**:
   `npm run build` in `frontend/` (0 TypeScript / bundling errors).
