"""
simulation.py — Pydantic schemas for Physics-Based Transient Thermal & Energy Simulation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from backend.schemas.design import GeometryParams, MaterialSelection


class SimulationRequest(BaseModel):
    location_id: Optional[str] = "leh_ladakh"
    month: int = Field(1, ge=1, le=12)
    geometry: GeometryParams = Field(default_factory=GeometryParams)
    materials: MaterialSelection = Field(default_factory=MaterialSelection)
    occupants: int = Field(4, ge=1, le=50)
    thermal_mass_level: Optional[str] = "medium"
    custom_climate_records: Optional[List[Dict[str, Any]]] = None
    include_energy: bool = True
    include_cost: bool = True


class HourlySimulationRecord(BaseModel):
    hour: int
    t_outdoor: float
    t_indoor: float
    t_sol_air: float
    t_mass: Optional[float] = None
    q_roof_w: float
    q_wall_w: float
    q_floor_w: Optional[float] = 0.0
    q_window_w: Optional[float] = 0.0
    q_door_w: Optional[float] = 0.0
    q_solar_w: float
    q_vent_w: float
    q_mass_w: Optional[float] = 0.0
    q_internal_w: float
    net_heat_flow_w: Optional[float] = 0.0
    pmv: float
    ppd_pct: float
    is_comfortable: bool


class SimulationSummary(BaseModel):
    peak_indoor_temp_c: float
    avg_indoor_temp_c: float
    min_indoor_temp_c: float
    daytime_avg_indoor_temp_c: Optional[float] = None
    nighttime_avg_indoor_temp_c: Optional[float] = None
    nighttime_min_indoor_temp_c: Optional[float] = None
    sunset_temp_drop_c: Optional[float] = None
    indoor_temperature_swing_c: float
    peak_ambient_temp_c: float
    thermal_damping_pct: float
    thermal_lag_hours: float
    total_daily_solar_captured_kwh: Optional[float] = None
    total_daily_heat_loss_kwh: Optional[float] = None
    net_thermal_balance_kwh: Optional[float] = None
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
    u_floor: Optional[float] = None
    u_door: Optional[float] = None
    explanation_narrative: Optional[str] = None


class WhatIfCompareRequest(BaseModel):
    location_id: Optional[str] = "leh_ladakh"
    month: int = 1
    geometry: GeometryParams = Field(default_factory=GeometryParams)
    baseline_materials: MaterialSelection
    modified_materials: MaterialSelection
    occupants: int = 4
    custom_climate_records: Optional[List[Dict[str, Any]]] = None


class WhatIfCompareResponse(BaseModel):
    peak_temperature_drop_c: float
    avg_temperature_drop_c: float
    nighttime_temperature_gain_c: Optional[float] = 0.0
    solar_capture_delta_kwh: Optional[float] = 0.0
    heat_loss_reduction_kwh: Optional[float] = 0.0
    discomfort_hours_reduced: int
    summary_statement: str
    baseline_hourly: List[HourlySimulationRecord]
    modified_hourly: List[HourlySimulationRecord]
    baseline_summary: SimulationSummary
    modified_summary: SimulationSummary
