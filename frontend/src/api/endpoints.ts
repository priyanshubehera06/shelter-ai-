import { apiClient } from './client';
import {
  LocationInfo,
  IPLocationResponse,
  ClimateAnalysisResponse,
  MaterialItem,
  ShelterDesign,
  GeometryParams,
  MaterialSelection,
  StructuralMetrics,
  SimulationResponse,
  WhatIfCompareResponse,
  OptimizationResponse,
  DigitalTwinConfigResponse,
  AllStatesTVIResponse,
  StateTVI,
  RecommendationResponse,
  ComplianceCheckResponse
} from '../types';

// -------------------------------------------------------------
// Climate APIs
// -------------------------------------------------------------
export const fetchLocations = async (): Promise<LocationInfo[]> => {
  const { data } = await apiClient.get<LocationInfo[]>('/climate/locations');
  return data;
};

export const fetchIPLocation = async (): Promise<IPLocationResponse> => {
  const { data } = await apiClient.get<IPLocationResponse>('/climate/ip-location');
  return data;
};

export const fetchClimateAnalysis = async (locationId: string, month: number = 5): Promise<ClimateAnalysisResponse> => {
  const { data } = await apiClient.get<ClimateAnalysisResponse>(`/climate/analyze/${locationId}?month=${month}`);
  return data;
};

// -------------------------------------------------------------
// Thermal Vulnerability Index (TVI) APIs
// -------------------------------------------------------------
export const fetchAllThermalVulnerability = async (weights?: Record<string, number>): Promise<AllStatesTVIResponse> => {
  const params = weights ? {
    w_heat_exposure: weights.heat_exposure,
    w_extreme_heat: weights.extreme_heat,
    w_thermal_stress: weights.thermal_stress,
    w_cooling_burden: weights.cooling_burden,
    w_pop_vuln: weights.population_vulnerability,
    w_bldg_vuln: weights.building_vulnerability,
    w_adaptive_cap: weights.adaptive_capacity,
  } : {};
  const { data } = await apiClient.get<AllStatesTVIResponse>('/thermal-vulnerability', { params });
  return data;
};

export const fetchStateThermalVulnerability = async (stateName: string, weights?: Record<string, number>): Promise<StateTVI> => {
  const params = weights ? {
    w_heat_exposure: weights.heat_exposure,
    w_extreme_heat: weights.extreme_heat,
    w_thermal_stress: weights.thermal_stress,
    w_cooling_burden: weights.cooling_burden,
    w_pop_vuln: weights.population_vulnerability,
    w_bldg_vuln: weights.building_vulnerability,
    w_adaptive_cap: weights.adaptive_capacity,
  } : {};
  const { data } = await apiClient.get<StateTVI>(`/thermal-vulnerability/${encodeURIComponent(stateName)}`, { params });
  return data;
};

// -------------------------------------------------------------
// Materials & Recommendation APIs
// -------------------------------------------------------------
export const fetchMaterials = async (category?: string): Promise<MaterialItem[]> => {
  const url = category ? `/materials?category=${category}` : '/materials';
  const { data } = await apiClient.get<MaterialItem[]>(url);
  return data;
};

export const fetchEngineeringRecommendations = async (payload: {
  climate_zone?: string;
  state_code?: string;
  budget_level?: string;
  shelter_type?: string;
  disaster_mode?: string | null;
  rapid_deployment_needed?: boolean;
  weights?: Record<string, number>;
}): Promise<RecommendationResponse> => {
  const { data } = await apiClient.post<RecommendationResponse>('/recommendations/run', payload);
  return data;
};

// -------------------------------------------------------------
// Policy & Compliance APIs
// -------------------------------------------------------------
export const checkPolicyCompliance = async (payload: {
  state_name: string;
  building_type?: string;
  geometry: GeometryParams;
  materials: MaterialSelection;
  simulation_metrics?: Record<string, any>;
}): Promise<ComplianceCheckResponse> => {
  const { data } = await apiClient.post<ComplianceCheckResponse>('/compliance/check', payload);
  return data;
};

export const fetchStateRegulations = async (stateName: string): Promise<any> => {
  const { data } = await apiClient.get(`/compliance/regulations/${encodeURIComponent(stateName)}`);
  return data;
};

// -------------------------------------------------------------
// Designs & Geometry APIs
// -------------------------------------------------------------
export const fetchDesigns = async (): Promise<ShelterDesign[]> => {
  const { data } = await apiClient.get<ShelterDesign[]>('/designs');
  return data;
};

export const fetchStructuralMetrics = async (
  geometry: GeometryParams,
  materials: MaterialSelection,
  occupants: number = 4
): Promise<StructuralMetrics> => {
  const { data } = await apiClient.post<StructuralMetrics>('/designs/metrics', null, {
    params: { occupants },
    data: { geometry, materials }
  });
  return data;
};

// -------------------------------------------------------------
// Simulation APIs
// -------------------------------------------------------------
export const runSimulation = async (payload: {
  location_id?: string;
  month?: number;
  geometry: GeometryParams;
  materials: MaterialSelection;
  occupants?: number;
  thermal_mass_level?: string;
}): Promise<SimulationResponse> => {
  const { data } = await apiClient.post<SimulationResponse>('/simulation/run', payload);
  return data;
};

export const runWhatIfComparison = async (payload: {
  location_id?: string;
  month?: number;
  geometry: GeometryParams;
  baseline_materials: MaterialSelection;
  modified_materials: MaterialSelection;
  occupants?: number;
}): Promise<WhatIfCompareResponse> => {
  const { data } = await apiClient.post<WhatIfCompareResponse>('/simulation/what-if', payload);
  return data;
};

// -------------------------------------------------------------
// Optimization APIs
// -------------------------------------------------------------
export const runOptimization = async (payload: {
  location_id?: string;
  month?: number;
  w_comfort?: number;
  w_cost?: number;
  w_carbon?: number;
  population_size?: number;
}): Promise<OptimizationResponse> => {
  const { data } = await apiClient.post<OptimizationResponse>('/optimization/run', payload);
  return data;
};

// -------------------------------------------------------------
// Digital Twin APIs
// -------------------------------------------------------------
export const fetchDigitalTwinConfig = async (payload: {
  geometry: GeometryParams;
  materials: MaterialSelection;
  hour_of_day: number;
  location_id?: string;
  month?: number;
  view_mode?: string;
}): Promise<DigitalTwinConfigResponse> => {
  const { data } = await apiClient.post<DigitalTwinConfigResponse>('/digital-twin/config', payload);
  return data;
};

// -------------------------------------------------------------
// Explainability & PDF
// -------------------------------------------------------------
export const fetchExplanation = async (design: ShelterDesign): Promise<{ explanation: string }> => {
  const { data } = await apiClient.post<{ explanation: string }>('/results/explain', design);
  return data;
};

export const downloadReportPdf = async (design: ShelterDesign): Promise<Blob> => {
  const { data } = await apiClient.post('/results/pdf', design, {
    responseType: 'blob'
  });
  return data;
};
