"""
simulation.py — Pydantic schemas for Physics-Based Transient Thermal & Energy Simulation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.schemas.design import GeometryParams, MaterialSelection


class SimulationRequest(BaseModel):
    location_id: Optional[str] = "sambalpur"
    month: int = Field(5, ge=1, le=12)
    geometry: GeometryParams = Field(default_factory=GeometryParams)
    materials: MaterialSelection = Field(default_factory=MaterialSelection)
    occupants: int = Field(4, ge=1, le=50)
    include_energy: bool = True
    include_cost: bool = True


class HourlySimulationRecord(BaseModel):
    hour: int
    t_outdoor: float
    t_indoor: float
    t_sol_air: float
    q_roof_w: float
    q_wall_w: float
    q_solar_w: float
    q_vent_w: float
    q_internal_w: float
    pmv: float
    ppd_pct: float
    is_comfortable: bool


class SimulationSummary(BaseModel):
    peak_indoor_temp_c: float
    avg_indoor_temp_c: float
    min_indoor_temp_c: float
    indoor_temperature_swing_c: float
    peak_ambient_temp_c: float
    thermal_damping_pct: float
    thermal_lag_hours: float
    comfort_score: float = Field(..., description="Overall comfort compliance percentage 0-100")
    avg_pmv: float
    discomfort_hours: int
    annual_cooling_kwh: float
    annual_heating_kwh: float
    total_annual_energy_kwh: float
    total_capex_cost_inr: float
    embodied_carbon_kgco2e: float
    resilience_score: float
    holistic_score: float


class SimulationResponse(BaseModel):
    summary: SimulationSummary
    hourly_results: List[HourlySimulationRecord]
    u_wall: float
    u_roof: float
    u_glazing: float
    explanation_narrative: Optional[str] = None


class WhatIfCompareRequest(BaseModel):
    location_id: Optional[str] = "sambalpur"
    month: int = 5
    geometry: GeometryParams = Field(default_factory=GeometryParams)
    baseline_materials: MaterialSelection
    modified_materials: MaterialSelection
    occupants: int = 4


class WhatIfCompareResponse(BaseModel):
    peak_temperature_drop_c: float
    avg_temperature_drop_c: float
    discomfort_hours_reduced: int
    summary_statement: str
    baseline_hourly: List[HourlySimulationRecord]
    modified_hourly: List[HourlySimulationRecord]
    baseline_summary: SimulationSummary
    modified_summary: SimulationSummary
