# SHELTER-AI — UI Upgrade Plan & Digital Twin Engineering Workspace Architecture

## 1. Executive Summary & Objective

Transform the current ShelterAI frontend into a dedicated, professional dark Digital Twin engineering workspace inspired by advanced building physics dashboards. The application serves as **"Software Based Model Development for Design of Area Specific Shelter for Thermal Comfort Maintenance"**, combining:
1. Top environmental & simulation controls bar (Location, Date, Time of Day slider, Season, Simulation trigger, Animation play/pause, Screenshot).
2. Left control sidebar (Design presets thumbnail grid, Building geometric parameter inspector with real-time editing, Material selectors with visual previews & palette modal).
3. Central immersive 3D Digital Twin viewport (High-precision architectural parametric model with detailed foundation plinth, walls with thickness and window/door recesses, realistic window frames & glass transparency, entrance door, porch, columns, steps, multi-variant roof types: Gable, Single Slope, Hip, Flat; physically based PBR materials; dynamic NOAA astronomical sun positioning; smooth diurnal spline arc; 3D cardinal compass with orientation alignment; view modes: Normal, Solar, Thermal Sol-Air Heatmap, Passive Ventilation, Heat Flow).
4. Right analytics & performance sidebar (Real-time micro-climate metrics, ASHRAE 55 PMV comfort, peak/mean indoor temperatures, HVAC energy, construction CapEx, resilience score, and modeled thermal load gradient legend).
5. Bottom multi-physics & camera control dock (View modes, simulation time player, camera view presets: Front, Side, Top, Isometric, Reset, and granular component visibility toggles).

---

## 2. Codebase Audit & Component Map

| Component Area | Current State | Planned Upgrade |
|---|---|---|
| **Digital Twin Workspace** | Standard card with 3D canvas on subpage | Full-screen multi-pane responsive layout: Top bar, Left sidebar (260px), Central 3D viewport (flex-1), Right analytics sidebar (280px), Bottom control dock |
| **Procedural Shelter Model** | Basic wall boxes & roof planes | Architectural procedural model (`ShelterModel.tsx`) with foundation plinth, layered exterior walls with openings, window frames, glass transparency, timber entrance door with frame & hardware, porch slab, structural columns, entrance steps, roof overhangs & fascia |
| **Roof System** | Pitched & monoslope | Parametric roof engine supporting **Single Slope (Monoslope)**, **Gable (Pitched)**, **Hip (4-slope)**, and **Flat Slab** with configurable slope, overhang, thickness, and material mapping |
| **PBR Material System** | Simple hex colors | Physically based `MeshStandardMaterial` library with roughness, metalness, normal/bump procedural details, texture repeat scaling, and fail-safe fallbacks |
| **Material Selection & Palette** | Basic dropdowns | Material cards with texture previews, modal palette selector across categories (*Wall, Roof, Floor, Glazing, Door*), real-time 3D preview and bi-directional sync to FastAPI simulation engine |
| **Solar & Astronomical Modeling** | NOAA vector mapped | Dynamic directional sunlight with soft shadows, 24-hr diurnal spline trajectory tube with time/alt/az annotations, and orientation-coupled compass |
| **Camera & Viewport** | OrbitControls basic | Smooth animated camera presets (`Isometric`, `Front`, `Side`, `Top`, `North Elevation`), HUD overlays, interactive gesture hints |
| **UI Design System** | Generic Tailwind | Dark engineering theme with design tokens (`--bg-main`, `--bg-panel`, `--border-subtle`, `--accent-green`, etc.), compact high-density metric rows, icon buttons with tooltips |
| **Backend Integration** | 8 FastAPI endpoints active | Fully integrated with `/api/climate`, `/api/materials`, `/api/designs`, `/api/simulation/run`, `/api/digital-twin/config`, `/api/results`, `/api/optimization/run` |

---

## 3. Component Hierarchy & File Structure

```
frontend/src/
├── digitalTwin/
│   ├── materials/
│   │   └── materialLibrary.ts         # PBR material definitions, textures, fallbacks
│   ├── models/
│   │   ├── ShelterModel.tsx           # Master architectural shelter assembly
│   │   ├── FoundationMesh.tsx         # Foundation plinth & steps
│   │   ├── PorchMesh.tsx              # Porch slab & structural columns
│   │   ├── WallsMesh.tsx              # Exterior walls with window/door cutouts
│   │   ├── RoofMesh.tsx               # Parametric Gable, Single Slope, Hip, Flat roofs
│   │   ├── WindowsMesh.tsx            # Window frames & transparent glazing panes
│   │   ├── DoorMesh.tsx               # Entry door, frame & handle hardware
│   │   └── ShadingElements.tsx        # Louvers, overhangs & solar shading devices
│   ├── scene/
│   │   ├── EnvironmentScene.tsx       # Ground plane, terrain ring, ambient & hemisphere lights
│   │   ├── SolarSystem3D.tsx          # NOAA sun sphere, soft shadows & 24h spline arc
│   │   ├── Compass3D.tsx              # 3D cardinal orientation compass
│   │   └── HeatFlowParticles.tsx      # Conceptual ventilation & heat flux vectors
│   └── utils/
│       ├── cameraTransitions.ts       # Smooth camera position lerping
│       └── solarCalculations.ts       # Astronomical solar coordinates
│
├── components/
│   ├── digitalTwin/
│   │   ├── DigitalTwinWorkspace.tsx   # Master 5-zone workspace container
│   │   ├── TopControlBar.tsx          # Location, Date, Time Slider, Season, Sim Play/Pause/Screenshot
│   │   ├── LeftSidebar.tsx            # Design thumbnails, Building parameters & Material selects
│   │   ├── RightSidebar.tsx           # Climate conditions, Performance metrics & Thermal legend
│   │   ├── BottomControlBar.tsx       # View mode tabs, Time slider, Camera presets & Visibility toggles
│   │   ├── Viewport3D.tsx             # Canvas wrapper with ErrorBoundary, loaders & overlay HUD
│   │   ├── DesignSelection.tsx        # Design presets dropdown + thumbnail grid + New Design
│   │   ├── BuildingParameters.tsx     # Dimensions, roof slope, WWR, overhang with Edit modal
│   │   ├── MaterialSelection.tsx      # Wall, Roof, Floor, Glazing, Door dropdowns with previews
│   │   ├── MaterialPalette.tsx        # Modal palette drawer with categorized cards & checkmarks
│   │   ├── ClimateConditions.tsx      # Outdoor temp, GHI solar, wind speed/dir, humidity
│   │   ├── PerformancePanel.tsx       # PMV comfort, peak/avg indoor temp, HVAC kWh, CapEx, resilience
│   │   ├── ThermalLegend.tsx          # Modeled Sol-Air thermal load vertical gradient
│   │   ├── ViewModeControls.tsx       # Normal, Solar, Thermal, Ventilation, Heat Flow buttons
│   │   ├── TimeControls.tsx           # Play/pause animation & time slider
│   │   ├── CameraControls.tsx         # Camera preset buttons (Front, Side, Top, Iso, Reset)
│   │   └── ComponentVisibility.tsx    # Roof, Walls, Windows, Shading, Shadows checkboxes
│   │
│   ├── ui/
│   │   ├── Panel.tsx                  # Dark engineering panel container
│   │   ├── MetricRow.tsx              # Compact label-value metric row with status accent
│   │   ├── IconButton.tsx             # Tooltipped icon action button
│   │   ├── SectionTitle.tsx           # Clean header with badge/action slot
│   │   ├── MaterialCard.tsx           # Visual material card with thumbnail & PBR properties
│   │   ├── Tooltip.tsx                # Accessible hover tooltip
│   │   ├── Slider.tsx                 # High-density numerical range slider
│   │   └── Select.tsx                 # Styled select dropdown
│   │
│   └── layout/
│       ├── AppLayout.tsx              # Global navigation wrapper
│       ├── Sidebar.tsx                # Left collapsible main module navigation
│       └── Header.tsx                 # Global station badge & simulation trigger
│
└── pages/
    ├── DigitalTwinPage.tsx            # Digital Twin Workspace page route
    ├── HomePage.tsx                   # Platform Overview & Pipeline
    ├── LocationClimatePage.tsx        # Meteorological Station Catalog
    ├── ClimateIntelligencePage.tsx    # Diurnal Charts & Heatwave Diagnostics
    ├── ShelterDesignLabPage.tsx       # Parametric CAD & Sizing
    ├── OptimizationPage.tsx           # NSGA-II Pareto Trade-off
    ├── WhatIfLabPage.tsx              # Sensitivity & Retrofit Comparison
    └── ResultsPage.tsx                # Top 4 Alternatives & PDF Audit
```

---

## 4. Execution Plan (Step-by-Step)

1. **Phase 1 (Design System & UI Library)**: Create design tokens in CSS and build reusable UI primitives (`Panel`, `MetricRow`, `IconButton`, `SectionTitle`, `MaterialCard`, `Tooltip`, `Slider`, `Select`).
2. **Phase 2 (PBR Materials & Architecture Model Library)**: Build `materialLibrary.ts` and modular parametric architectural components: `FoundationMesh`, `PorchMesh`, `WallsMesh`, `RoofMesh`, `WindowsMesh`, `DoorMesh`, `ShadingElements`, and master `ShelterModel`.
3. **Phase 3 (3D Scene, Solar Tracking & Environment)**: Implement `EnvironmentScene`, `SolarSystem3D` with NOAA solar coordinates, `Compass3D`, and `HeatFlowParticles`.
4. **Phase 4 (Workspace Panels)**:
   - `TopControlBar.tsx` (Location, date, time of day slider, season, sim controls, screenshot capture)
   - `LeftSidebar.tsx` (Design selection thumbnail grid, building parameters with edit mode, material selection with preview triggers)
   - `MaterialPalette.tsx` (Category tabs: Wall, Roof, Floor, Window, Door with PBR material cards)
   - `RightSidebar.tsx` (Climate conditions, performance metrics with empty/loading state, modeled thermal load legend)
   - `BottomControlBar.tsx` (View modes: Normal, Solar, Thermal, Ventilation, Heat Flow; camera presets; component visibility toggles)
5. **Phase 5 (Viewport3D & State Integration)**: Assemble `Viewport3D.tsx` and `DigitalTwinWorkspace.tsx` with error boundaries, camera lerp transitions, and bidirectional state synchronization with Zustand and FastAPI.
6. **Phase 6 (Verification & Production Build)**: Verify build with TypeScript compiler, validate real simulation updates, test responsiveness, and ensure zero fake data.
