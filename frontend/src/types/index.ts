/**
 * types/index.ts — Strongly typed TypeScript interfaces mirroring backend Pydantic models.
 */

export interface LocationInfo {
  id: string;
  name: string;
  city?: string;
  state?: string;
  region_type: string;
  lat: number;
  lon: number;
  source: string;
  t_max_summer: number;
  t_min_winter: number;
  rh_avg_pct: number;
  solar_irradiance_peak: number;
  description?: string;
}

export interface IPLocationResponse {
  ip?: string;
  city: string;
  region: string;
  country: string;
  lat: number;
  lon: number;
  climate_zone: string;
  nearest_station_id: string;
  source: string;
}

export interface HourlyClimateRecord {
  hour: number;
  dry_bulb_temp_c: number;
  relative_humidity_pct: number;
  solar_ghi_w_m2: number;
  wind_speed_m_s: number;
  wind_direction_deg: number;
  dew_point_c?: number;
}

export interface ClimateSummary {
  location_id: string;
  location_name: string;
  climate_zone: string;
  lat: number;
  lon: number;
  annual_mean_temp: number;
  peak_summer_temp: number;
  min_winter_temp: number;
  diurnal_range_c: number;
  avg_relative_humidity: number;
  peak_solar_ghi: number;
  hot_hours_count: number;
  cold_hours_count: number;
  high_solar_hours_count: number;
  actionable_insights: string[];
}

export interface ClimateAnalysisResponse {
  summary: ClimateSummary;
  hourly_records_24h: HourlyClimateRecord[];
  extreme_scenarios?: Record<string, any>;
}

export interface MaterialItem {
  id: string;
  name: string;
  category: 'Wall' | 'Roof' | 'Floor' | 'Glazing' | 'Insulation' | string;
  thermal_cond_w_mk: number;
  density_kg_m3: number;
  specific_heat_j_kgk: number;
  embodied_carbon_kgco2_kg: number;
  unit_cost_inr_m2: number;
  thickness_options?: string;
  availability_score: number;
  description?: string;
  color_hex?: string;
  roughness?: number;
  metalness?: number;
}

export interface GeometryParams {
  length_m: number;
  width_m: number;
  height_m: number;
  roof_type: 'pitched' | 'monoslope' | 'hipped' | 'flat';
  roof_pitch_deg: number;
  wall_thickness_cm: number;
  wwr_pct: number;
  overhang_m: number;
  orientation_deg: number;
  door_width_m: number;
  door_height_m: number;
  door_count: number;
}

export interface MaterialSelection {
  wall_mat_id: string;
  wall_thickness_cm: number;
  roof_mat_id: string;
  insulation_mat_id?: string | null;
  insulation_thickness_cm: number;
  glazing_mat_id: string;
}

export interface ShelterDesign {
  id?: string;
  name: string;
  archetype?: string;
  geometry: GeometryParams;
  materials: MaterialSelection;
  occupants: number;
  location_id?: string;
  created_at?: string;
}

export interface StructuralMetrics {
  floor_area_m2: number;
  gross_volume_m3: number;
  gross_wall_area_m2: number;
  net_wall_area_m2: number;
  window_area_m2: number;
  door_area_m2: number;
  roof_area_m2: number;
  surface_to_volume_ratio: number;
  roof_peak_height_m: number;
  area_per_person_m2: number;
  wall_u_value_w_m2k: number;
  roof_u_value_w_m2k: number;
}

export interface HourlySimulationRecord {
  hour: number;
  t_outdoor: number;
  t_indoor: number;
  t_sol_air: number;
  q_roof_w: number;
  q_wall_w: number;
  q_solar_w: number;
  q_vent_w: number;
  q_internal_w: number;
  pmv: number;
  ppd_pct: number;
  is_comfortable: boolean;
}

export interface SimulationSummary {
  peak_indoor_temp_c: number;
  avg_indoor_temp_c: number;
  min_indoor_temp_c: number;
  indoor_temperature_swing_c: number;
  peak_ambient_temp_c: number;
  thermal_damping_pct: number;
  thermal_lag_hours: number;
  comfort_score: number;
  avg_pmv: number;
  discomfort_hours: number;
  annual_cooling_kwh: number;
  annual_heating_kwh: number;
  total_annual_energy_kwh: number;
  total_capex_cost_inr: number;
  embodied_carbon_kgco2e: number;
  resilience_score: number;
  holistic_score: number;
}

export interface SimulationResponse {
  summary: SimulationSummary;
  hourly_results: HourlySimulationRecord[];
  u_wall: number;
  u_roof: number;
  u_glazing: number;
  explanation_narrative?: string;
}

export interface WhatIfCompareResponse {
  peak_temperature_drop_c: number;
  avg_temperature_drop_c: number;
  discomfort_hours_reduced: number;
  summary_statement: string;
  baseline_hourly: HourlySimulationRecord[];
  modified_hourly: HourlySimulationRecord[];
  baseline_summary: SimulationSummary;
  modified_summary: SimulationSummary;
}

export interface ParetoCandidate {
  id: string;
  rank: number;
  is_pareto: boolean;
  candidate: Record<string, any>;
  comfort_score: number;
  annual_energy_kwh: number;
  cost_inr: number;
  carbon_kg: number;
  resilience_score: number;
  discomfort_pmv: number;
  avg_indoor_temp: number;
  peak_indoor_temp: number;
  fitness_score: number;
  rationale?: string;
}

export interface RecommendedTop4 {
  best_balanced: ParetoCandidate;
  best_comfort: ParetoCandidate;
  lowest_energy: ParetoCandidate;
  lowest_cost: ParetoCandidate;
}

export interface OptimizationResponse {
  location_id: string;
  population_size: number;
  weights: Record<string, number>;
  total_evaluated: number;
  pareto_front_count: number;
  pareto_front: ParetoCandidate[];
  all_candidates: ParetoCandidate[];
  top_4_designs: RecommendedTop4;
}

export interface SolarPositionData {
  hour: number;
  altitude_deg: number;
  azimuth_deg: number;
  is_daylight: boolean;
  solar_vector: [number, number, number];
  sun_position_3d: [number, number, number];
  solar_path_spline: number[][];
  solar_ghi_w_m2: number;
}

export interface ComponentGeometryData {
  name: string;
  component_type: string;
  dimensions: Record<string, number>;
  position: [number, number, number];
  rotation: [number, number, number];
  material_id: string;
  material_name: string;
  u_value: number;
  sol_air_temp_c?: number;
  thermal_color_hex?: string;
  heat_flux_w?: number;
}

export interface DigitalTwinConfigResponse {
  geometry: GeometryParams;
  materials: MaterialSelection;
  components: ComponentGeometryData[];
  solar: SolarPositionData;
  ambient: {
    temperature_c: number;
    humidity_pct: number;
    wind_speed_m_s: number;
    wind_dir_deg: number;
  };
  camera_presets: Record<string, { position: [number, number, number]; target: [number, number, number] }>;
  airflow_vectors?: Array<{ start: number[]; end: number[]; speed: number; direction_deg: number }>;
}
