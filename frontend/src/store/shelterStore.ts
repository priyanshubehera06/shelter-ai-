import { create } from 'zustand';
import {
  ShelterDesign,
  GeometryParams,
  MaterialSelection,
  SimulationResponse,
  OptimizationResponse,
  LocationInfo
} from '../types';

interface ShelterState {
  // Location & Climate State
  selectedLocationId: string;
  selectedMonth: number;
  locationsList: LocationInfo[];
  setLocationId: (id: string) => void;
  setMonth: (month: number) => void;
  setLocationsList: (list: LocationInfo[]) => void;

  // Active Parametric Design
  currentDesign: ShelterDesign;
  savedDesigns: ShelterDesign[];
  updateGeometry: (geometry: Partial<GeometryParams>) => void;
  updateMaterials: (materials: Partial<MaterialSelection>) => void;
  setOccupants: (occupants: number) => void;
  loadDesign: (design: ShelterDesign) => void;
  setSavedDesigns: (designs: ShelterDesign[]) => void;

  // Simulation & Optimization State
  simulationResult: SimulationResponse | null;
  optimizationResult: OptimizationResponse | null;
  isSimulating: boolean;
  isOptimizing: boolean;
  setSimulationResult: (res: SimulationResponse | null) => void;
  setOptimizationResult: (res: OptimizationResponse | null) => void;
  setIsSimulating: (loading: boolean) => void;
  setIsOptimizing: (loading: boolean) => void;

  // 3D Digital Twin UI State
  simHour: number;
  activeViewMode: 'architectural' | 'solar_shading' | 'thermal_heatmap' | 'ventilation' | 'exploded';
  cameraPreset: 'isometric' | 'front' | 'side' | 'top' | 'north';
  componentVisibility: {
    roof: boolean;
    walls: boolean;
    windows: boolean;
    door: boolean;
    shading: boolean;
    ground: boolean;
    compass: boolean;
    sun_path: boolean;
  };
  setSimHour: (hour: number) => void;
  setActiveViewMode: (mode: 'architectural' | 'solar_shading' | 'thermal_heatmap' | 'ventilation' | 'exploded') => void;
  setCameraPreset: (preset: 'isometric' | 'front' | 'side' | 'top' | 'north') => void;
  toggleComponentVisibility: (key: keyof ShelterState['componentVisibility']) => void;
}

export const useShelterStore = create<ShelterState>((set) => ({
  selectedLocationId: 'sambalpur',
  selectedMonth: 5,
  locationsList: [],
  setLocationId: (id) => set({ selectedLocationId: id }),
  setMonth: (month) => set({ selectedMonth: month }),
  setLocationsList: (list) => set({ locationsList: list }),

  currentDesign: {
    id: 'design_current',
    name: 'Custom Parametric Shelter',
    archetype: 'Transitional Resilient',
    geometry: {
      length_m: 6.0,
      width_m: 4.0,
      height_m: 2.8,
      roof_type: 'pitched',
      roof_pitch_deg: 15.0,
      wall_thickness_cm: 20.0,
      wwr_pct: 15.0,
      overhang_m: 0.6,
      orientation_deg: 0.0,
      door_width_m: 0.9,
      door_height_m: 2.1,
      door_count: 1,
    },
    materials: {
      wall_mat_id: 'cseb_interlocking',
      wall_thickness_cm: 20.0,
      roof_mat_id: 'roof_cgi_insulated',
      insulation_mat_id: 'insulation_rockwool',
      insulation_thickness_cm: 5.0,
      glazing_mat_id: 'glazing_single',
    },
    occupants: 4,
    location_id: 'sambalpur',
  },
  savedDesigns: [],

  updateGeometry: (geom) =>
    set((state) => ({
      currentDesign: {
        ...state.currentDesign,
        geometry: { ...state.currentDesign.geometry, ...geom },
      },
    })),

  updateMaterials: (mats) =>
    set((state) => ({
      currentDesign: {
        ...state.currentDesign,
        materials: { ...state.currentDesign.materials, ...mats },
      },
    })),

  setOccupants: (occupants) =>
    set((state) => ({
      currentDesign: { ...state.currentDesign, occupants },
    })),

  loadDesign: (design) =>
    set({
      currentDesign: { ...design },
    }),

  setSavedDesigns: (designs) => set({ savedDesigns: designs }),

  simulationResult: null,
  optimizationResult: null,
  isSimulating: false,
  isOptimizing: false,
  setSimulationResult: (res) => set({ simulationResult: res }),
  setOptimizationResult: (res) => set({ optimizationResult: res }),
  setIsSimulating: (loading) => set({ isSimulating: loading }),
  setIsOptimizing: (loading) => set({ isOptimizing: loading }),

  simHour: 12,
  activeViewMode: 'architectural',
  cameraPreset: 'isometric',
  componentVisibility: {
    roof: true,
    walls: true,
    windows: true,
    door: true,
    shading: true,
    ground: true,
    compass: true,
    sun_path: true,
  },
  setSimHour: (hour) => set({ simHour: hour }),
  setActiveViewMode: (mode) => set({ activeViewMode: mode }),
  setCameraPreset: (preset) => set({ cameraPreset: preset }),
  toggleComponentVisibility: (key) =>
    set((state) => ({
      componentVisibility: {
        ...state.componentVisibility,
        [key]: !state.componentVisibility[key],
      },
    })),
}));
