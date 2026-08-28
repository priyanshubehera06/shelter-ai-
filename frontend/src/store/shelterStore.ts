import { create } from 'zustand';
import {
  ShelterDesign,
  GeometryParams,
  MaterialSelection,
  SimulationResponse,
  OptimizationResponse,
  LocationInfo,
  StateTVI,
  RecommendationResponse,
  ComplianceCheckResponse
} from '../types';

interface ShelterState {
  // Location & Climate State
  selectedLocationId: string;
  selectedState: string;
  selectedMonth: number;
  locationsList: LocationInfo[];
  activeStateTVI: StateTVI | null;
  allStatesTVI: StateTVI[];
  customClimateInputs: {
    t_min: number;
    t_max: number;
    solar_peak_ghi: number;
    wind_speed: number;
    relative_humidity: number;
  } | null;
  setLocationId: (id: string) => void;
  setSelectedState: (state: string) => void;
  setMonth: (month: number) => void;
  setLocationsList: (list: LocationInfo[]) => void;
  setActiveStateTVI: (tvi: StateTVI | null) => void;
  setAllStatesTVI: (list: StateTVI[]) => void;
  setCustomClimateInputs: (inputs: ShelterState['customClimateInputs']) => void;

  // Active Parametric Design
  currentDesign: ShelterDesign;
  savedDesigns: ShelterDesign[];
  activeDesignMode: 'normal' | 'disaster' | 'migrant';
  activeDisasterHazard: string | null;
  migrantModuleCount: number;
  thermalMassLevel: 'low' | 'medium' | 'high';
  updateGeometry: (geometry: Partial<GeometryParams>) => void;
  updateMaterials: (materials: Partial<MaterialSelection>) => void;
  setOccupants: (occupants: number) => void;
  setThermalMassLevel: (level: 'low' | 'medium' | 'high') => void;
  setActiveDesignMode: (mode: 'normal' | 'disaster' | 'migrant') => void;
  setActiveDisasterHazard: (hazard: string | null) => void;
  setMigrantModuleCount: (count: number) => void;
  loadDesign: (design: ShelterDesign) => void;
  setSavedDesigns: (designs: ShelterDesign[]) => void;

  // Recommendations & Compliance State
  recommendationResult: RecommendationResponse | null;
  complianceResult: ComplianceCheckResponse | null;
  isLoadingRecommendations: boolean;
  isLoadingCompliance: boolean;
  setRecommendationResult: (res: RecommendationResponse | null) => void;
  setComplianceResult: (res: ComplianceCheckResponse | null) => void;
  setIsLoadingRecommendations: (loading: boolean) => void;
  setIsLoadingCompliance: (loading: boolean) => void;

  // Simulation & Optimization State
  simulationResult: SimulationResponse | null;
  optimizationResult: OptimizationResponse | null;
  isSimulating: boolean;
  isOptimizing: boolean;
  costComfortPreference: number; // 0 (Max Cost Priority) to 100 (Max Comfort Priority)
  setSimulationResult: (res: SimulationResponse | null) => void;
  setOptimizationResult: (res: OptimizationResponse | null) => void;
  setIsSimulating: (loading: boolean) => void;
  setIsOptimizing: (loading: boolean) => void;
  setCostComfortPreference: (val: number) => void;

  // 3D Digital Twin UI State
  simHour: number;
  activeViewMode: 'architectural' | 'solar_shading' | 'thermal_heatmap' | 'ventilation' | 'exploded' | 'heat_flow';
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
  setActiveViewMode: (mode: 'architectural' | 'solar_shading' | 'thermal_heatmap' | 'ventilation' | 'exploded' | 'heat_flow') => void;
  setCameraPreset: (preset: 'isometric' | 'front' | 'side' | 'top' | 'north') => void;
  toggleComponentVisibility: (key: keyof ShelterState['componentVisibility']) => void;
}

export const useShelterStore = create<ShelterState>((set) => ({
  selectedLocationId: 'leh_ladakh',
  selectedState: 'Ladakh',
  selectedMonth: 1, // January cold winter baseline
  locationsList: [],
  activeStateTVI: null,
  allStatesTVI: [],
  customClimateInputs: null,

  setLocationId: (id) => {
    let state = 'Ladakh';
    if (id.includes('leh') || id.includes('kargil') || id.includes('ladakh')) state = 'Ladakh';
    else if (id.includes('jodhpur') || id.includes('jaipur')) state = 'Rajasthan';
    else if (id.includes('mumbai') || id.includes('nagpur') || id.includes('pune')) state = 'Maharashtra';
    else if (id.includes('bengaluru') || id.includes('bangalore')) state = 'Karnataka';
    else if (id.includes('chennai')) state = 'Tamil Nadu';
    else if (id.includes('ahmedabad') || id.includes('bhuj')) state = 'Gujarat';
    else if (id.includes('kolkata')) state = 'West Bengal';
    else if (id.includes('guwahati') || id.includes('silchar')) state = 'Assam';
    else if (id.includes('delhi')) state = 'Delhi';
    else if (id.includes('lucknow')) state = 'Uttar Pradesh';
    else if (id.includes('patna')) state = 'Bihar';
    else if (id.includes('kochi') || id.includes('trivandrum')) state = 'Kerala';
    else if (id.includes('sambalpur') || id.includes('bhubaneswar')) state = 'Odisha';
    
    set({ selectedLocationId: id, selectedState: state });
  },
  setSelectedState: (state) => set({ selectedState: state }),
  setMonth: (month) => set({ selectedMonth: month }),
  setLocationsList: (list) => set({ locationsList: list }),
  setActiveStateTVI: (tvi) => set({ activeStateTVI: tvi }),
  setAllStatesTVI: (list) => set({ allStatesTVI: list }),
  setCustomClimateInputs: (inputs) => set({ customClimateInputs: inputs }),

  currentDesign: {
    id: 'design_ladakh_passive_solar',
    name: 'Ladakh Passive Solar Heated Shelter',
    archetype: 'High-Altitude Cold Passive',
    mode: 'normal',
    disaster_mode: null,
    migrant_modules: 1,
    geometry: {
      length_m: 7.0,
      width_m: 5.0,
      height_m: 2.8,
      floors_count: 1,
      roof_type: 'pitched',
      roof_pitch_deg: 20.0,
      wall_thickness_cm: 30.0,
      wwr_pct: 20.0,
      overhang_m: 0.5,
      orientation_deg: 180.0, // South-facing for maximum winter solar radiation capture
      door_width_m: 0.9,
      door_height_m: 2.1,
      door_count: 1,
      plinth_height_m: 0.45,
    },
    materials: {
      wall_mat_id: 'trombe_wall_mass',
      wall_thickness_cm: 30.0,
      roof_mat_id: 'roof_insulated_timber_deck',
      insulation_mat_id: 'insulation_sheep_wool',
      insulation_thickness_cm: 7.5,
      glazing_mat_id: 'glazing_double',
      floor_mat_id: 'floor_insulated_screed',
      door_mat_id: 'door_solid_timber',
    },
    occupants: 4,
    location_id: 'leh_ladakh',
  },
  savedDesigns: [],
  activeDesignMode: 'normal',
  activeDisasterHazard: null,
  migrantModuleCount: 1,
  thermalMassLevel: 'high',

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

  setThermalMassLevel: (level) => set({ thermalMassLevel: level }),

  setActiveDesignMode: (mode) =>
    set((state) => ({
      activeDesignMode: mode,
      currentDesign: { ...state.currentDesign, mode },
    })),

  setActiveDisasterHazard: (hazard) =>
    set((state) => ({
      activeDisasterHazard: hazard,
      currentDesign: { ...state.currentDesign, disaster_mode: hazard },
    })),

  setMigrantModuleCount: (count) =>
    set((state) => ({
      migrantModuleCount: count,
      currentDesign: { ...state.currentDesign, migrant_modules: count },
    })),

  loadDesign: (design) =>
    set({
      currentDesign: { ...design },
      activeDesignMode: design.mode || 'normal',
      activeDisasterHazard: design.disaster_mode || null,
      migrantModuleCount: design.migrant_modules || 1,
    }),

  setSavedDesigns: (designs) => set({ savedDesigns: designs }),

  recommendationResult: null,
  complianceResult: null,
  isLoadingRecommendations: false,
  isLoadingCompliance: false,
  setRecommendationResult: (res) => set({ recommendationResult: res }),
  setComplianceResult: (res) => set({ complianceResult: res }),
  setIsLoadingRecommendations: (loading) => set({ isLoadingRecommendations: loading }),
  setIsLoadingCompliance: (loading) => set({ isLoadingCompliance: loading }),

  simulationResult: null,
  optimizationResult: null,
  isSimulating: false,
  isOptimizing: false,
  costComfortPreference: 50,
  setSimulationResult: (res) => set({ simulationResult: res }),
  setOptimizationResult: (res) => set({ optimizationResult: res }),
  setIsSimulating: (loading) => set({ isSimulating: loading }),
  setIsOptimizing: (loading) => set({ isOptimizing: loading }),
  setCostComfortPreference: (val) => set({ costComfortPreference: val }),

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
