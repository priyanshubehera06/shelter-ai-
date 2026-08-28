import React, { useEffect, useState } from 'react';
import { Canvas } from '@react-three/fiber';
import { useShelterStore } from '../../store/shelterStore';
import { fetchDigitalTwinConfig } from '../../api/endpoints';
import { ShelterScene } from './ShelterScene';
import { Button } from '../ui/Button';
import { Slider } from '../ui/Slider';
import { Badge } from '../ui/Badge';
import { DigitalTwinConfigResponse } from '../../types';
import {
  Sun,
  Eye,
  Camera,
  Layers,
  Flame,
  Wind,
  Maximize2,
  Settings
} from 'lucide-react';

export const DigitalTwinCanvas: React.FC = () => {
  const {
    currentDesign,
    selectedLocationId,
    selectedMonth,
    simHour,
    setSimHour,
    activeViewMode,
    setActiveViewMode,
    cameraPreset,
    setCameraPreset,
    componentVisibility,
    toggleComponentVisibility,
  } = useShelterStore();

  const [twinConfig, setTwinConfig] = useState<DigitalTwinConfigResponse | null>(null);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchDigitalTwinConfig({
      geometry: currentDesign.geometry,
      materials: currentDesign.materials,
      hour_of_day: simHour,
      location_id: selectedLocationId,
      month: selectedMonth,
      view_mode: activeViewMode,
    })
      .then((data) => setTwinConfig(data))
      .catch((err) => console.error('Failed to fetch digital twin telemetry:', err));
  }, [currentDesign, simHour, selectedLocationId, selectedMonth, activeViewMode]);

  // Extract surface thermal colors for thermal heatmap mode
  const thermalColors: Record<string, string> = {};
  if (twinConfig) {
    twinConfig.components.forEach((c) => {
      if (c.name.includes('South')) thermalColors['south'] = c.thermal_color_hex || '#b58d6b';
      if (c.name.includes('North')) thermalColors['north'] = c.thermal_color_hex || '#b58d6b';
      if (c.name.includes('East')) thermalColors['east'] = c.thermal_color_hex || '#b58d6b';
      if (c.name.includes('West')) thermalColors['west'] = c.thermal_color_hex || '#b58d6b';
      if (c.name.includes('Roof')) thermalColors['roof'] = c.thermal_color_hex || '#34495e';
    });
  }

  const cameraPresetsList: Array<{ id: 'isometric' | 'front' | 'side' | 'top' | 'north'; label: string }> = [
    { id: 'isometric', label: '📐 Isometric' },
    { id: 'front', label: '🏠 Front (South)' },
    { id: 'side', label: '↔️ Side (East)' },
    { id: 'top', label: '🔝 Top (Plan)' },
    { id: 'north', label: '🧭 North Elevation' },
  ];

  const viewModesList: Array<{ id: 'architectural' | 'solar_shading' | 'thermal_heatmap' | 'ventilation' | 'exploded'; label: string; icon: any }> = [
    { id: 'architectural', label: 'Architectural', icon: Layers },
    { id: 'solar_shading', label: 'Solar & Shading', icon: Sun },
    { id: 'thermal_heatmap', label: 'Thermal Heatmap', icon: Flame },
    { id: 'ventilation', label: 'Passive Ventilation', icon: Wind },
    { id: 'exploded', label: 'Exploded Assembly', icon: Maximize2 },
  ];

  return (
    <div className="relative w-full h-[620px] rounded-2xl overflow-hidden border border-surface-border bg-slate-950 shadow-2xl flex flex-col">
      {/* Top Floating Control Bar */}
      <div className="absolute top-4 left-4 right-4 z-10 flex flex-wrap items-center justify-between gap-3 pointer-events-none">
        {/* View Mode Switcher */}
        <div className="flex items-center gap-1 bg-surface/90 backdrop-blur-md p-1.5 rounded-xl border border-surface-border pointer-events-auto shadow-lg">
          {viewModesList.map((mode) => {
            const Icon = mode.icon;
            const isActive = activeViewMode === mode.id;
            return (
              <button
                key={mode.id}
                onClick={() => setActiveViewMode(mode.id)}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-md'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-raised'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{mode.label}</span>
              </button>
            );
          })}
        </div>

        {/* Visibility Filter Toggle */}
        <button
          onClick={() => setShowFilters(!showFilters)}
          className="flex items-center gap-1.5 bg-surface/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-surface-border text-xs font-medium text-slate-300 hover:text-white pointer-events-auto shadow-lg"
        >
          <Settings className="w-3.5 h-3.5 text-emerald-400" />
          <span>Filters</span>
        </button>
      </div>

      {/* Component Visibility Drawer */}
      {showFilters && (
        <div className="absolute top-16 right-4 z-20 bg-surface/95 backdrop-blur-md p-4 rounded-xl border border-surface-border shadow-2xl text-xs space-y-2.5 w-60 animate-in fade-in slide-in-from-top-2">
          <div className="font-semibold text-slate-300 border-b border-surface-border pb-1.5 flex items-center justify-between">
            <span>Component Visibility</span>
            <span className="text-[10px] text-emerald-400">PBR / R3F</span>
          </div>
          {Object.entries(componentVisibility).map(([key, val]) => (
            <label key={key} className="flex items-center justify-between cursor-pointer text-slate-300 hover:text-white">
              <span className="capitalize">{key.replace('_', ' ')}</span>
              <input
                type="checkbox"
                checked={val}
                onChange={() => toggleComponentVisibility(key as any)}
                className="rounded bg-surface-raised border-surface-border text-emerald-500 focus:ring-emerald-500"
              />
            </label>
          ))}
        </div>
      )}

      {/* R3F 3D Canvas */}
      <div className="flex-1 w-full h-full cursor-grab active:cursor-grabbing">
        <Canvas
          shadows
          camera={{ position: [8, 6, 9], fov: 45 }}
          className="w-full h-full"
        >
          <ShelterScene
            solarData={twinConfig?.solar}
            thermalColors={thermalColors}
          />
        </Canvas>
      </div>

      {/* Bottom Floating Telemetry & Time Controls */}
      <div className="absolute bottom-4 left-4 right-4 z-10 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pointer-events-none">
        {/* Camera View Presets */}
        <div className="flex items-center gap-1 bg-surface/90 backdrop-blur-md p-1.5 rounded-xl border border-surface-border pointer-events-auto shadow-lg overflow-x-auto">
          <Camera className="w-3.5 h-3.5 text-slate-400 ml-1.5 mr-1 shrink-0" />
          {cameraPresetsList.map((cam) => (
            <button
              key={cam.id}
              onClick={() => setCameraPreset(cam.id)}
              className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all shrink-0 ${
                cameraPreset === cam.id
                  ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {cam.label}
            </button>
          ))}
        </div>

        {/* Simulation Time Slider & Solar HUD */}
        <div className="bg-surface/90 backdrop-blur-md px-4 py-2 rounded-xl border border-surface-border pointer-events-auto shadow-lg flex items-center gap-4">
          <div className="w-44">
            <Slider
              label="Simulation Time"
              value={simHour}
              min={0}
              max={23}
              step={1}
              displayFormat={(v) => `${String(Math.floor(v)).padStart(2, '0')}:00`}
              onChange={(val) => setSimHour(val)}
            />
          </div>

          {twinConfig?.solar && (
            <div className="hidden md:flex items-center gap-3 pl-3 border-l border-surface-border text-[11px] font-mono">
              <span className="text-amber-400">
                Alt: <b>{twinConfig.solar.altitude_deg}°</b>
              </span>
              <span className="text-slate-400">
                Az: <b>{twinConfig.solar.azimuth_deg}°</b>
              </span>
              <Badge variant={twinConfig.solar.is_daylight ? 'amber' : 'slate'} size="sm">
                {twinConfig.solar.is_daylight ? '☀️ Daylight' : '🌙 Night'}
              </Badge>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
