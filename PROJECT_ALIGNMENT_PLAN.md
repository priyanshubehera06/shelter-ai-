# PROJECT_ALIGNMENT_PLAN: Area-Specific Passive Shelter Design Platform (Ladakh Focus)

## 1. Executive Mission & Engineering Purpose
**ShelterAI** is an engineering software platform for designing and evaluating area-specific passive shelters for thermal comfort and reduced external energy requirements.

- **Primary Benchmark Region**: **Ladakh (High-Altitude Cold Desert)**
- **Central Engineering Question**:
  > *"Given a location and its atmospheric conditions, what combination of shelter geometry, orientation, materials, thermal mass, openings, and passive design strategies can maintain a suitable indoor temperature with minimum external energy requirement?"*

---

## 2. Feature Scoping & Rationalization

### 2.1 Features to Maintain & Polish (Green & Yellow)
1. **Ladakh Thermal Simulation & Case Study**: Realistic winter sub-zero ambient conditions (-15°C to +2°C, 850 W/m² solar GHI, 7.9 hrs sunshine) demonstrating daytime solar gain vs. nighttime thermal loss.
2. **Solar Heat Gain Engine (`engine/solar.py`)**: NOAA astronomical positioning, surface incidence angles on tilted/oriented envelopes, fenestration solar gains, and Sol-Air temperatures.
3. **Component Heat Flow & Transient Thermal Model (`engine/thermal.py`)**: Time-dependent heat balance tracking $Q_{\text{solar}}, Q_{\text{wall}}, Q_{\text{roof}}, Q_{\text{floor}}, Q_{\text{window}}, Q_{\text{door}}, Q_{\text{vent}}, \pm Q_{\text{mass}}$, daytime peak, nighttime min, and sunset temperature drop.
4. **Material Engine & Comparison (`engine/materials.py`)**: Rigorous thermo-physical database ($k, \rho, C_p$, thickness, U-value, cost, embodied carbon) and side-by-side material comparison under identical climate.
5. **Composite Multi-Layer Assemblies**: Layered wall/roof builder ($Exterior \rightarrow Insulation \rightarrow Thermal Mass \rightarrow Interior Finish$).
6. **Thermal Mass Dynamics**: Low/Medium/High thermal mass core (Trombe wall, rammed earth, CSEB) damping diurnal swings and releasing stored solar heat at night.
7. **Openings & Fenestration Analysis**: Window area, WWR, glazing type (single, double low-E, triple argon), and nighttime shutter thermal resistance.
8. **Orientation Optimization**: 0°–360° rotation with South-facing (180°) solar collection optimization.
9. **Parametric Design Simulator**: Real-time 3D geometry response without page reload + on-demand physics execution.
10. **Cost vs. Comfort Pareto Frontier**: 2D trade-off scatter plot with non-dominated frontier and budget sliders.
11. **Design A vs. Design B Comparison**: Side-by-side delta metrics (Indoor temp, solar gain, heat loss, comfort, energy, cost).
12. **Emergency Cold-Region & Migrant Shelter Modes**: Rapid deployment high-insulation shelters and modular temporary pods using the unified thermal engine.
13. **Climate Thermal Risk Profile**: Dual-dimension Cold/Heating vs. Heat/Cooling vulnerability profiles with full data transparency.
14. **Simplified Policy & Energy Compliance**: Preliminary screening against Eco-Niwas Samhita (ENS 2021), ECBC, and NBC.
15. **3D Digital Twin (React Three Fiber)**: Realistic architectural model with Solar, Thermal Heatmap, Heat Flow Vectors, and Multi-Layer Envelope views.

### 2.2 Explicitly Excluded Functionality
- ❌ No conversational AI chatbots or assistant widgets.
- ❌ No arbitrary text-to-3D / generic architectural generation.
- ❌ No non-shelter archetypes (animal shelters, schools, clinics, warehouses, industrial generators).
- ❌ No smart-city or agriculture distractions.

---

## 3. Clean Navigation & Page Architecture

```
01. Home (Hero: Area-Specific Passive Shelter Design, Core Metrics, Workflow)
02. Climate Analysis & Thermal Risk (Atmospheric inputs, Ladakh profile, Risk factors)
03. Shelter Design Simulator (Geometry, Orientation, Openings, Thermal Mass, Live 3D Twin)
04. Materials & Construction (Database, Multi-Layer Builder, Side-by-Side Comparison)
05. 3D Digital Twin (Interactive 3D viewport, Solar path, Thermal gradients, Heat-flow vectors)
06. Design Comparison (Design A Baseline vs. Design B Optimized)
07. Optimization & Pareto Frontier (NSGA-II Multi-objective search, Cost vs. Comfort)
08. Results & Scientific Report (24-hr Thermal curve, Heat-flow breakdown, Methodology, Certified PDF)
```
