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
  DigitalTwinConfigResponse
} from '../types';

// Climate APIs
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

// Materials APIs
export const fetchMaterials = async (category?: string): Promise<MaterialItem[]> => {
  const url = category ? `/materials?category=${category}` : '/materials';
  const { data } = await apiClient.get<MaterialItem[]>(url);
  return data;
};

// Designs & Geometry APIs
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

// Simulation APIs
export const runSimulation = async (payload: {
  location_id?: string;
  month?: number;
  geometry: GeometryParams;
  materials: MaterialSelection;
  occupants?: number;
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

// Optimization APIs
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

// Digital Twin APIs
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

// Explainability & PDF
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
