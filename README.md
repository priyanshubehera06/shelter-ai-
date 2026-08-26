# Shelter-AI: Area-Specific Passive Shelter Optimization & Thermal Performance Engine

**Shelter-AI** is an advanced physics-driven application designed for area-specific passive thermal shelter engineering, climate dynamic analysis, embodied carbon accounting, multi-objective Pareto optimization, and automated PDF BOQ audit reports.

---

## 📁 Directory Architecture

```
shelter-ai/
│
├── app.py                      # Streamlit multi-page portal entry point & state setup
│
├── pages/                      # Multi-page Streamlit views
│   ├── 01_Home.py              # Landing page, quick start presets & feature roadmaps
│   ├── 02_Climate_Analysis.py  # Diurnal weather dynamics, psychrometrics & solar GHI
│   ├── 03_Shelter_Design.py    # 3D parametric blueprint builder & 24h thermal simulator
│   ├── 04_Optimization.py      # Multi-Objective Pareto trade-off solver
│   └── 05_Results.py           # 5-Pillar MCDA sustainability score & PDF report exporter
│
├── engine/                     # Core computational & physics modules
│   ├── climate.py              # Climate data processing & psychrometric calculations
│   ├── materials.py            # Material database, U-value & thermal mass math
│   ├── geometry.py             # Building envelope surface area & shading geometry
│   ├── thermal.py              # 2-Node dynamic RC thermal dynamic differential solver
│   ├── comfort.py              # Fanger PMV/PPD (ISO 7730) & ASHRAE 55 Adaptive Comfort
│   ├── energy.py              # Thermal energy demand (kWh/m²/yr) & load savings
│   ├── cost.py                 # Bill of Quantities (BOQ), CapEx, OpEx & Life-Cycle Cost
│   ├── optimizer.py            # Multi-objective Pareto optimization engine
│   └── scoring.py              # 5-Pillar MCDA sustainability rating system
│
├── database/                   # Relational data layer
│   ├── schema.sql              # SQLite database schema
│   ├── seed.py                 # Database initialization & seeding script
│   └── shelter.db              # SQLite persistent store
│
├── data/                       # Datasets
│   ├── climate/                # Micro-climate records
│   │   └── sambalpur.csv       # Sambalpur, Odisha composite weather dataset
│   └── materials.csv           # Thermo-physical properties catalog of local materials
│
├── visualization/              # Graphics & rendering
│   ├── charts.py               # Interactive Plotly charts (diurnal, Pareto, radar)
│   └── shelter_3d.py           # 3D parametric shelter mesh renderer (PyDeck & Plotly 3D)
│
├── reports/                    # Document generation
│   └── report_generator.py     # Executive PDF engineering report builder (FPDF2)
│
├── tests/                      # Automated test suite
│   └── test_thermal.py         # Pytest verification for thermal physics & optimizer
│
├── requirements.txt            # Python dependencies
└── README.md                   # System documentation
```

---

## ⚡ Quick Start

### 1. Installation
Install required dependencies:
```bash
pip install -r requirements.txt
```

### 2. Database Initialization
Seed the SQLite database with material thermo-physical properties and baseline shelter presets:
```bash
python database/seed.py
```

### 3. Run Unit Tests
Verify physics equations and optimization solvers:
```bash
python tests/test_thermal.py
```

### 4. Launch Web Application
Run the multi-page Streamlit portal:
```bash
streamlit run app.py
```

---

## 🔬 Mathematical Physics & Formulas

1. **Overall Heat Transfer Coefficient (U-Value)**:
   $$R_{\text{total}} = R_{si} + \sum \frac{d_i}{k_i} + R_{se}, \quad U = \frac{1}{R_{\text{total}}}$$

2. **Sol-Air Temperature ($T_{\text{sol-air}}$)**:
   $$T_{\text{sol-air}} = T_{\text{outdoor}} + \frac{\alpha \cdot GHI}{h_o}$$

3. **Fanger PMV Thermal Comfort Index**:
   $$PMV = [0.303 \cdot e^{-0.036 \cdot M} + 0.028] \cdot (M - W - H_{\text{loss}})$$

4. **ASHRAE 55 Adaptive Comfort Temperature**:
   $$T_{\text{comfort}} = 17.8 + 0.31 \cdot T_{\text{outdoor, mean}}$$

5. **20-Year Life Cycle Cost (LCC)**:
   $$\text{LCC} = \text{CapEx} + \sum_{t=1}^{20} \frac{\text{OpEx}_t}{(1 + r)^t}$$
