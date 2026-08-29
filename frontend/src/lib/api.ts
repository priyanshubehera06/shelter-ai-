/**
 * api.ts — Centralized ShelterAI API Client
 * Interfaces with FastAPI backend deployed on Render or local dev server.
 */

import { apiClient, API_BASE_URL } from '../api/client';
import * as endpoints from '../api/endpoints';
import {
  LocationInfo,
  IPLocationResponse,
  ClimateAnalysisResponse,
  MaterialItem,
  ShelterDesign,
  GeometryParams,
  MaterialSelection,
  SimulationResponse,
  WhatIfCompareResponse,
  OptimizationResponse,
  DigitalTwinConfigResponse
} from '../types';

export { API_BASE_URL, apiClient };
export * from '../api/endpoints';

/**
 * Health check endpoint to verify backend connectivity.
 */
export const checkHealth = async (): Promise<{ status: string }> => {
  const { data } = await apiClient.get<{ status: string }>('/health');
  return data;
};

/**
 * Fetch climate analysis and 24-hr diurnal cycle for a location and month.
 */
export const getClimate = async (
  locationId: string = 'leh_ladakh',
  month: number = 1
): Promise<ClimateAnalysisResponse> => {
  return endpoints.fetchClimateAnalysis(locationId, month);
};

/**
 * Detect user IP/GPS and retrieve current live climate telemetry.
 */
export const getCurrentClimate = async (
  lat?: number,
  lon?: number
): Promise<IPLocationResponse> => {
  const params = lat !== undefined && lon !== undefined ? { lat, lon } : {};
  const { data } = await apiClient.get<IPLocationResponse>('/climate/ip-location', { params });
  return data;
};

/**
 * Fetch historical or standard EPW meteorological profile for a location.
 */
export const getHistoricalClimate = async (
  locationId: string = 'leh_ladakh'
): Promise<ClimateAnalysisResponse> => {
  return endpoints.fetchClimateAnalysis(locationId, 1);
};

/**
 * Fetch catalog of certified construction and passive insulation materials.
 */
export const getMaterials = async (category?: string): Promise<MaterialItem[]> => {
  return endpoints.fetchMaterials(category);
};

/**
 * Execute 24-hour transient physics-based thermal simulation.
 */
export const runSimulation = async (payload: {
  location_id?: string;
  month?: number;
  geometry: GeometryParams;
  materials: MaterialSelection;
  occupants?: number;
  thermal_mass_level?: string;
  custom_climate_records?: any[];
}): Promise<SimulationResponse> => {
  return endpoints.runSimulation(payload);
};

/**
 * Compare baseline and modified shelter designs side-by-side.
 */
export const compareDesigns = async (payload: {
  location_id?: string;
  month?: number;
  geometry: GeometryParams;
  baseline_materials: MaterialSelection;
  modified_materials: MaterialSelection;
  occupants?: number;
  custom_climate_records?: any[];
}): Promise<WhatIfCompareResponse> => {
  return endpoints.runWhatIfComparison(payload);
};

/**
 * Run NSGA-II Multi-Objective Evolutionary Optimization.
 */
export const optimizeDesign = async (payload: {
  location_id?: string;
  month?: number;
  w_comfort?: number;
  w_cost?: number;
  w_carbon?: number;
  population_size?: number;
}): Promise<OptimizationResponse> => {
  return endpoints.runOptimization(payload);
};

/**
 * Fetch 3D Digital Twin configuration and solar vector angles.
 */
export const getDigitalTwinConfig = async (payload: {
  geometry: GeometryParams;
  materials: MaterialSelection;
  hour_of_day: number;
  location_id?: string;
  month?: number;
  view_mode?: string;
}): Promise<DigitalTwinConfigResponse> => {
  return endpoints.fetchDigitalTwinConfig(payload);
};

const api = {
  checkHealth,
  getClimate,
  getCurrentClimate,
  getHistoricalClimate,
  getMaterials,
  runSimulation,
  compareDesigns,
  optimizeDesign,
  getDigitalTwinConfig,
  fetchLocations: endpoints.fetchLocations,
  fetchIPLocation: endpoints.fetchIPLocation,
  fetchClimateAnalysis: endpoints.fetchClimateAnalysis,
  fetchMaterials: endpoints.fetchMaterials,
  fetchEngineeringRecommendations: endpoints.fetchEngineeringRecommendations,
  checkPolicyCompliance: endpoints.checkPolicyCompliance,
  fetchStateRegulations: endpoints.fetchStateRegulations,
  fetchDesigns: endpoints.fetchDesigns,
  fetchStructuralMetrics: endpoints.fetchStructuralMetrics,
  runWhatIfComparison: endpoints.runWhatIfComparison,
  exportAnsysDeck: endpoints.exportAnsysDeck,
  runOptimization: endpoints.runOptimization,
  fetchDigitalTwinConfig: endpoints.fetchDigitalTwinConfig,
  fetchExplanation: endpoints.fetchExplanation,
  downloadReportPdf: endpoints.downloadReportPdf,
};

export default api;
