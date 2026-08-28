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
  Minimize2,
  Settings,
  Sliders,
  Compass,
  X,
  Maximize,
  TrendingDown
} from 'lucide-react';
import { clsx } from 'clsx';

export const DigitalTwinCanvas: React.FC = () => {
  const {
    currentDesign,
    updateGeometry,
    selectedLocationId,
    selectedState,
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
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [showCadDrawer, setShowCadDrawer] = useState(true);

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

  // Handle ESC key to exit fullscreen
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isFullscreen) {
        setIsFullscreen(false);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isFullscreen]);

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
    { id: 'north', label: '🧭 North' },
  ];

  const viewModesList: Array<{ id: 'architectural' | 'solar_shading' | 'thermal_heatmap' | 'ventilation' | 'exploded'; label: string; icon: any }> = [
    { id: 'architectural', label: 'Architectural', icon: Layers },
    { id: 'solar_shading', label: 'Solar & Shading', icon: Sun },
    { id: 'thermal_heatmap', label: 'Thermal Heatmap', icon: Flame },
    { id: 'ventilation', label: 'Passive Ventilation', icon: Wind },
    { id: 'exploded', label: 'Exploded Assembly', icon: Maximize2 },
  ];

  const usableArea = (currentDesign.geometry.length_m * currentDesign.geometry.width_m).toFixed(1);
  const grossVolume = (currentDesign.geometry.length_m * currentDesign.geometry.width_m * currentDesign.geometry.height_m).toFixed(1);

  return (
    <div
      className={clsx(
        'overflow-hidden bg-slate-950 shadow-2xl flex flex-col transition-all duration-300',
        isFullscreen
          ? 'fixed inset-0 z-50 w-screen h-screen rounded-none border-none p-4'
          : 'relative w-full h-[620px] rounded-2xl border border-surface-border'
      )}
    >
      {/* Top Floating Header & CAD Toolbar */}
      <div className="absolute top-3.5 left-3.5 right-3.5 z-20 flex flex-col lg:flex-row items-start lg:items-center justify-between gap-2.5 pointer-events-none">
        {/* Left: View Mode Tabs */}
        <div className="flex items-center gap-1 bg-surface/90 backdrop-blur-md p-1.5 rounded-xl border border-surface-border pointer-events-auto shadow-xl overflow-x-auto max-w-full">
          {viewModesList.map((mode) => {
            const Icon = mode.icon;
            const isActive = activeViewMode === mode.id;
            return (
              <button
                key={mode.id}
                onClick={() => setActiveViewMode(mode.id)}
                className={`flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all shrink-0 ${
                  isActive
                    ? 'bg-emerald-600 text-white shadow-md font-semibold'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-raised'
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{mode.label}</span>
              </button>
            );
          })}
        </div>

        {/* Right: Camera Presets CAD Toolbar + Fullscreen Toggle + Filters */}
        <div className="flex items-center gap-2 pointer-events-auto max-w-full overflow-x-auto">
          {/* Camera View Presets Toolbar */}
          <div className="flex items-center gap-1 bg-surface/90 backdrop-blur-md p-1.5 rounded-xl border border-surface-border shadow-xl">
            <div className="flex items-center gap-1 pl-1 pr-1.5 text-[11px] font-mono text-slate-400 border-r border-surface-border shrink-0">
              <Camera className="w-3.5 h-3.5 text-emerald-400" />
              <span className="hidden xl:inline text-[10px] uppercase font-bold text-slate-400">View:</span>
            </div>
            {cameraPresetsList.map((cam) => (
              <button
                key={cam.id}
                onClick={() => setCameraPreset(cam.id)}
                className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-all shrink-0 ${
                  cameraPreset === cam.id
                    ? 'bg-emerald-500 text-slate-950 font-bold border border-emerald-400 shadow-md'
                    : 'text-slate-300 hover:text-white hover:bg-surface-raised'
                }`}
              >
                {cam.label}
              </button>
            ))}
          </div>

          {/* Fullscreen Mode Specific Controls */}
          {isFullscreen && (
            <button
              onClick={() => setShowCadDrawer(!showCadDrawer)}
              className={clsx(
                'flex items-center gap-1.5 bg-surface/90 backdrop-blur-md px-3 py-1.5 rounded-xl border text-xs font-medium shadow-xl transition shrink-0',
                showCadDrawer
                  ? 'border-emerald-500/50 bg-emerald-950/40 text-emerald-400'
                  : 'border-surface-border text-slate-300 hover:text-white hover:bg-surface-raised'
              )}
            >
              <Sliders className="w-3.5 h-3.5" />
              <span>CAD Controls</span>
            </button>
          )}

          {/* Visibility Filter Toggle */}
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-1.5 bg-surface/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-surface-border text-xs font-medium text-slate-300 hover:text-white shadow-xl hover:bg-surface-raised transition shrink-0"
          >
            <Settings className="w-3.5 h-3.5 text-emerald-400" />
            <span className="hidden sm:inline">Filters</span>
          </button>

          {/* Fullscreen Expand / Minimize Toggle */}
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className={clsx(
              'flex items-center gap-1.5 px-3 py-1.5 rounded-xl border text-xs font-bold shadow-xl transition shrink-0',
              isFullscreen
                ? 'bg-rose-500/20 border-rose-500/40 text-rose-300 hover:bg-rose-500/30'
                : 'bg-emerald-500/20 border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/30'
            )}
            title={isFullscreen ? 'Exit Fullscreen (Esc)' : 'Expand to Fullscreen View'}
          >
            {isFullscreen ? (
              <>
                <Minimize2 className="w-3.5 h-3.5" />
                <span>Exit Fullscreen</span>
                <span className="text-[10px] font-mono px-1 py-0.2 rounded bg-surface border border-surface-border text-slate-400">
                  ESC
                </span>
              </>
            ) : (
              <>
                <Maximize2 className="w-3.5 h-3.5" />
                <span>Fullscreen</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Fullscreen Floating Live CAD Sizing Drawer (Left) */}
      {isFullscreen && showCadDrawer && (
        <div className="absolute top-18 left-3.5 z-20 bg-surface/95 backdrop-blur-md p-4 rounded-2xl border border-surface-border shadow-2xl w-72 space-y-3.5 text-xs animate-in fade-in slide-in-from-left-4 max-h-[82vh] overflow-y-auto">
          <div className="flex items-center justify-between border-b border-surface-border pb-2">
            <span className="font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Sliders className="w-3.5 h-3.5 text-emerald-400" />
              <span>Live Parametric CAD</span>
            </span>
            <button
              onClick={() => setShowCadDrawer(false)}
              className="text-slate-400 hover:text-white"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="space-y-3">
            <Slider
              label="Length (East-West)"
              value={currentDesign.geometry.length_m}
              min={3.0}
              max={24.0}
              step={0.5}
              unit="m"
              onChange={(val) => updateGeometry({ length_m: val })}
            />
            <Slider
              label="Width (North-South)"
              value={currentDesign.geometry.width_m}
              min={2.5}
              max={16.0}
              step={0.5}
              unit="m"
              onChange={(val) => updateGeometry({ width_m: val })}
            />
            <Slider
              label="Floor Height"
              value={currentDesign.geometry.height_m}
              min={2.2}
              max={5.0}
              step={0.1}
              unit="m"
              onChange={(val) => updateGeometry({ height_m: val })}
            />
            <Slider
              label="Window-to-Wall Ratio"
              value={currentDesign.geometry.wwr_pct}
              min={5}
              max={50}
              step={1}
              unit="%"
              onChange={(val) => updateGeometry({ wwr_pct: val })}
            />
            <Slider
              label="Roof Pitch"
              value={currentDesign.geometry.roof_pitch_deg}
              min={0}
              max={45}
              step={5}
              unit="°"
              onChange={(val) => updateGeometry({ roof_pitch_deg: val })}
            />
            <Slider
              label="Solar Orientation"
              value={currentDesign.geometry.orientation_deg}
              min={0}
              max={360}
              step={5}
              unit="°"
              onChange={(val) => updateGeometry({ orientation_deg: val })}
            />
          </div>
        </div>
      )}

      {/* Fullscreen Floating Live Telemetry HUD (Right) */}
      {isFullscreen && (
        <div className="absolute top-18 right-3.5 z-20 bg-surface/95 backdrop-blur-md p-4 rounded-2xl border border-surface-border shadow-2xl w-64 space-y-2.5 text-xs animate-in fade-in slide-in-from-right-4">
          <div className="font-bold text-white uppercase tracking-wider border-b border-surface-border pb-1.5 flex items-center justify-between">
            <span>Shelter Geometry HUD</span>
            <span className="text-[10px] font-mono text-emerald-400">Live Sync</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-[11px]">
            <div className="p-2 rounded-lg bg-surface-raised border border-surface-border">
              <span className="text-slate-400 block">Usable Area:</span>
              <span className="font-mono font-bold text-white text-sm">{usableArea} m²</span>
            </div>
            <div className="p-2 rounded-lg bg-surface-raised border border-surface-border">
              <span className="text-slate-400 block">Gross Volume:</span>
              <span className="font-mono font-bold text-white text-sm">{grossVolume} m³</span>
            </div>
            <div className="p-2 rounded-lg bg-surface-raised border border-surface-border">
              <span className="text-slate-400 block">Orientation:</span>
              <span className="font-mono font-bold text-amber-400 text-xs">{currentDesign.geometry.orientation_deg}° {currentDesign.geometry.orientation_deg === 180 ? '(True South)' : ''}</span>
            </div>
            <div className="p-2 rounded-lg bg-surface-raised border border-surface-border">
              <span className="text-slate-400 block">South WWR:</span>
              <span className="font-mono font-bold text-sky-400 text-xs">{currentDesign.geometry.wwr_pct}% Aperture</span>
            </div>
          </div>
        </div>
      )}

      {/* Component Visibility Drawer */}
      {showFilters && (
        <div className="absolute top-16 right-3.5 z-30 bg-surface/95 backdrop-blur-md p-4 rounded-xl border border-surface-border shadow-2xl text-xs space-y-2.5 w-60 animate-in fade-in slide-in-from-top-2">
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
      <div className="absolute bottom-3.5 left-3.5 right-3.5 z-20 flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-3 pointer-events-none">
        {/* Left: View & Orbit Helper Badge */}
        <div className="bg-surface/90 backdrop-blur-md px-3 py-1.5 rounded-xl border border-surface-border pointer-events-auto shadow-lg inline-flex items-center gap-2 text-xs font-mono text-slate-300 self-start">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="capitalize font-semibold text-white">{cameraPreset} View</span>
          <span className="text-slate-600">|</span>
          <span className="text-slate-400 text-[11px]">Left Click + Drag: Orbit • Scroll: Zoom</span>
        </div>

        {/* Right: Simulation Time Slider & Solar HUD */}
        <div className="bg-surface/90 backdrop-blur-md px-4 py-2 rounded-xl border border-surface-border pointer-events-auto shadow-xl flex items-center gap-4 self-end sm:self-auto">
          <div className="w-40 sm:w-48">
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
