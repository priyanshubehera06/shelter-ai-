# PROJECT_REFACTOR_PLAN: Core Thermal Engineering Focus & UI Simplification

## 1. Primary Focus & Scope
ShelterAI is a **Clean, Scientifically Credible Passive Thermal Shelter Design and Simulation Platform**.
- **Primary Showcase**: **Ladakh High-Altitude Cold Climate**
- **Core Engineering Challenge**: Capture solar radiation during sub-zero sunny daytime ($1900\text{--}2100\ \text{kWh/m}^2/\text{yr}$, $7.9\ \text{hrs}$ sunshine) and retain stored thermal energy across extreme sub-zero nights ($-15^\circ\text{C}$ to $-25^\circ\text{C}$).

---

## 2. Clean 8-Step Navigation Architecture

```
1. HOME       → Clean Hero, Process Flow, Ladakh Case Study Quick-Launch
2. CLIMATE    → Location (Default: Leh Ladakh), Data Modes (Live Open-Meteo, Historical, Manual)
3. DESIGN     → Parametric Sizing, 0-360° South Solar Compass, Openings, Thermal Mass
4. MATERIALS  → Thermophysical Catalog, Side-by-Side Comparison, Composite Multi-Layer Builder
5. SIMULATE   → Central 3D Digital Twin + Live Physics Simulation + 24-Hr Thermal Curves + Heat Flows
6. COMPARE    → Design A (Baseline Uninsulated) vs. Design B (Optimized Passive Trombe)
7. OPTIMIZE   → Multi-Objective Pareto Search (Comfort, Heat Loss, Energy, Cost)
8. RESULTS    → Certified Thermal Decision Report with "Why?" Physics Justification & Export
```

---

## 3. Removal of Extraneous Modules & Routes
- ❌ **Removed from Navigation & Primary UI**:
  - `ThermalVulnerabilityPage` (`/tvi` state ranking and vulnerability maps)
  - `DisasterShelterPage` (`/disaster-mode` multi-hazard flood/cyclone systems)
  - `PolicyCompliancePage` (`/compliance` large state legal screening)
  - `ClimateIntelligencePage` (merged into unified `ClimatePage`)
  - Any conversational AI / text-to-CAD generators / non-shelter archetypes.

---

## 4. Engineering Data Flow
```
CLIMATE DATA (Open-Meteo / Historical / Manual)
        ↓
SOLAR ENERGY ENGINE (engine/solar.py: NOAA Position, Facade Radiation, Q_solar)
        ↓
SHELTER GEOMETRY & TRUE-SOUTH ORIENTATION (engine/geometry.py)
        ↓
COMPOSITE MULTI-LAYER ENVELOPE & THERMAL MASS (engine/materials.py)
        ↓
TIME-DEPENDENT TRANSIENT RC HEAT BALANCE (engine/thermal.py)
        ↓
INDOOR TEMPERATURE & HOURLY COMPONENT HEAT FLOWS
        ↓
DESIGN A vs B COMPARISON & PARETO OPTIMIZATION (engine/optimizer.py)
        ↓
3D DIGITAL TWIN & CERTIFIED AUDIT REPORT
```
