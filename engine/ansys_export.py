"""
ansys_export.py — Generates parameterized PyANSYS (PyFluent / MAPDL) scripts and input decks
for validating ShelterAI lumped-parameter transient thermal simulations against high-fidelity
ANSYS Conjugate Heat Transfer (CHT) and Discrete Ordinates (DO) Solar Ray Tracing CFD models.
"""

from typing import Dict, Any, List
import json
from engine.geometry import ShelterGeometry
from engine.materials import get_material_by_id


def generate_pyansys_fluent_script(
    geometry: ShelterGeometry,
    materials: Dict[str, Any],
    climate_data: Dict[str, Any],
    simulation_summary: Dict[str, Any]
) -> str:
    """
    Generate an executable Python script using the PyANSYS `ansys-fluent-core` (PyFluent) API.
    Configures a 3D conjugate heat transfer (CHT) domain with solar ray tracing,
    multi-layer envelope conduction, and buoyancy-driven natural convection.
    """
    length = geometry.length
    width = geometry.width
    height = geometry.height
    pitch = geometry.roof_pitch
    wwr = geometry.wwr
    azimuth = geometry.orientation

    wall_mat = get_material_by_id(materials.get("wall_mat_id", "trombe_wall_mass"))
    roof_mat = get_material_by_id(materials.get("roof_mat_id", "roof_insulated_timber_deck"))
    glaz_mat = get_material_by_id(materials.get("glazing_mat_id", "glazing_double"))

    script = f'''# ==============================================================================
# PyANSYS Fluent Benchmark Script for ShelterAI Passive Thermal Validation
# Model: High-Altitude Cold Region Shelter (Ladakh Showcase)
# Generated automatically by ShelterAI Engineering Engine
# ==============================================================================

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

# 1. Initialize Fluent Session in 3D Double-Precision
print("Initializing ANSYS Fluent 3D CHT Session...")
solver = pyfluent.launch_fluent(precision="double", processor_count=4, mode="solver")

# 2. Parametric Domain Dimensions (meters)
LENGTH = {length:.2f}
WIDTH = {width:.2f}
HEIGHT = {height:.2f}
ROOF_PITCH_DEG = {pitch:.1f}
ORIENTATION_AZIMUTH_DEG = {azimuth:.1f}
WWR_PCT = {wwr:.1f}

# 3. Enable Physics Models
# Energy Equation
solver.setup.models.energy.enabled = True

# Viscous Model (k-omega SST for buoyancy-induced thermal plumes)
solver.setup.models.viscous.model = "k-omega"
solver.setup.models.viscous.k_omega_model = "sst"

# Solar Ray Tracing / Discrete Ordinates (DO) Radiation Model
solver.setup.models.radiation.model = "discrete-ordinates"
solver.setup.models.radiation.solar_ray_tracing.enabled = True
solver.setup.models.radiation.solar_calculator.latitude = {climate_data.get("lat", 34.1526)}
solver.setup.models.radiation.solar_calculator.longitude = {climate_data.get("lon", 77.5771)}
solver.setup.models.radiation.solar_calculator.day = {climate_data.get("day", 15)}
solver.setup.models.radiation.solar_calculator.month = {climate_data.get("month", 1)}
solver.setup.models.radiation.solar_calculator.sunshine_fraction = 0.95

# 4. Define Material Thermophysical Properties
# Air Domain (Boussinesq approximation for indoor air density variations)
air = solver.setup.materials.fluid["air"]
air.density.option = "boussinesq"
air.density.boussinesq.operating_temperature = 293.15  # 20°C
air.density.boussinesq.thermal_expansion_coefficient = 0.00343

# Solid Material: Wall Envelope ({wall_mat["name"]})
wall_solid = solver.setup.materials.solid.create("{wall_mat["id"]}")
wall_solid.thermal_conductivity = {wall_mat["thermal_cond_w_mk"]}
wall_solid.density = {wall_mat["density_kg_m3"]}
wall_solid.specific_heat = {wall_mat["specific_heat_j_kgk"]}

# Solid Material: Roof Envelope ({roof_mat["name"]})
roof_solid = solver.setup.materials.solid.create("{roof_mat["id"]}")
roof_solid.thermal_conductivity = {roof_mat["thermal_cond_w_mk"]}
roof_solid.density = {roof_mat["density_kg_m3"]}
roof_solid.specific_heat = {roof_mat["specific_heat_j_kgk"]}

# Semi-Transparent Glazing ({glaz_mat["name"]})
glaz_solid = solver.setup.materials.solid.create("{glaz_mat["id"]}")
glaz_solid.thermal_conductivity = {glaz_mat["thermal_cond_w_mk"]}
glaz_solid.radiation.refractive_index = 1.52
glaz_solid.radiation.absorption_coefficient = 15.0

# 5. Boundary Conditions Setup
# Ambient Environment (-15°C to +2°C Diurnal Boundary)
T_EXT_AMB_K = {climate_data.get("t_min_c", -15.0) + 273.15:.2f}

# Exterior Wall Boundary
ext_wall = solver.setup.boundary_conditions.wall["wall_exterior"]
ext_wall.thermal.thermal_bc = "Convection"
ext_wall.thermal.heat_transfer_coefficient = 22.7  # External wind convection (W/m²K)
ext_wall.thermal.free_stream_temperature = T_EXT_AMB_K
ext_wall.thermal.internal_emissivity = 0.90
ext_wall.radiation.solar_transmissivity = 0.0

# South Glazing Window Aperture
win_bc = solver.setup.boundary_conditions.wall["window_south"]
win_bc.thermal.thermal_bc = "Convection"
win_bc.thermal.heat_transfer_coefficient = 15.0
win_bc.thermal.free_stream_temperature = T_EXT_AMB_K
win_bc.radiation.semi_transparent = True

# 6. Solution Monitors & Transient Solver Configuration
solver.solution.run_calculation.transient_time_step_size = 300.0  # 5-minute sub-steps
solver.solution.run_calculation.number_of_time_steps = 288       # 24-hour transient run

# Initialize and compute
solver.solution.initialization.hybrid_initialize()
print("Starting 24-Hour Transient Conjugate Heat Transfer (CHT) Solution...")
# solver.solution.run_calculation.calculate()

print("PyANSYS Benchmark Configuration generated successfully for ShelterAI.")
'''
    return script


def generate_ansys_apdl_deck(
    geometry: ShelterGeometry,
    materials: Dict[str, Any],
    climate_data: Dict[str, Any]
) -> str:
    """
    Generate an ANSYS Parametric Design Language (APDL) / MAPDL macro deck for thermal stress
    and transient RC finite-element thermal diffusion analysis.
    """
    wall_mat = get_material_by_id(materials.get("wall_mat_id", "trombe_wall_mass"))
    roof_mat = get_material_by_id(materials.get("roof_mat_id", "roof_insulated_timber_deck"))

    deck = f"""! ==============================================================================
! ANSYS APDL / MAPDL Thermal Simulation Macro Deck
! ShelterAI Validation Script: Ladakh Cold-Climate Diurnal Thermal Storage
! ==============================================================================
/BATCH
/PREP7
/TITLE, ShelterAI Transient Passive Thermal Model - Ladakh Case Study

! 1. PARAMETRIC GEOMETRY DEFINITION (MKS Units)
L_SHELTER = {geometry.length:.3f}
W_SHELTER = {geometry.width:.3f}
H_SHELTER = {geometry.height:.3f}
WALL_THICK = {geometry.wall_thickness_cm / 100.0:.3f}
AZIMUTH_DEG = {geometry.orientation:.1f}

! 2. ELEMENT TYPE (3D 8-Node Thermal Solid)
ET,1,SOLID70

! 3. MATERIAL PROPERTIES (SI Units: W/m-K, kg/m3, J/kg-K)
! Material 1: Wall Envelope ({wall_mat["name"]})
MP,KXX,1,{wall_mat["thermal_cond_w_mk"]}
MP,DENS,1,{wall_mat["density_kg_m3"]}
MP,C,1,{wall_mat["specific_heat_j_kgk"]}

! Material 2: Roof Assembly ({roof_mat["name"]})
MP,KXX,2,{roof_mat["thermal_cond_w_mk"]}
MP,DENS,2,{roof_mat["density_kg_m3"]}
MP,C,2,{roof_mat["specific_heat_j_kgk"]}

! 4. GEOMETRY GENERATION (Bounding Solid Shell)
BLOCK,0,L_SHELTER,0,W_SHELTER,0,H_SHELTER

! Mesh Volume
VMESH,ALL

! 5. BOUNDARY CONDITIONS & LOADS
! Sub-zero ambient night temperature (-15 C = 258.15 K)
T_EXT = {climate_data.get("t_min_c", -15.0) + 273.15:.2f}
H_CONV = 22.7

! Apply Convection on Exterior Surfaces
SFA,ALL,1,CONV,H_CONV,T_EXT

! Initial Temperature (Uniform 293.15 K = 20 C)
TUNIF,293.15

! 6. TRANSIENT SOLUTION SETUP (24 Hours in 288 Steps)
/SOLU
ANTYPE,TRANS
TIME,86400
DELTIM,300,60,600
AUTOTS,ON
OUTRES,ALL,ALL

! Solve Transient Diffusion
SOLVE
FINISH

/POST1
SET,LAST
PLNSOL,TEMP
"""
    return deck
