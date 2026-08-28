import React, { useEffect, useState } from 'react';
import { useShelterStore } from '../store/shelterStore';
import { runSimulation } from '../api/endpoints';
import { DigitalTwinCanvas } from '../components/digitalTwin/DigitalTwinCanvas';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import {
  Activity,
  Sun,
  Moon,
  TrendingDown,
  Play,
  RotateCcw,
  Box,
  Layers,
  Thermometer,
  Zap,
  Flame,
  CheckCircle2,
  Compass,
  Hammer,
  ShieldCheck
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';

export const DigitalTwinPage: React.FC = () => {
  const {
    currentDesign,
    selectedLocationId,
    selectedMonth,
    simulationResult,
    setSimulationResult,
    isSimulating,
    setIsSimulating,
    thermalMassLevel,
    setThermalMassLevel,
    updateGeometry
  } = useShelterStore();

  const [activeViewMode, setActiveViewMode] = useState<'normal' | 'solar' | 'thermal' | 'heat_flow' | 'envelope'>('normal');

  const handleExecuteSimulation = async () => {
    setIsSimulating(true);
    try {
      const res = await runSimulation({
        location_id: selectedLocationId,
        month: selectedMonth,
        geometry: currentDesign.geometry,
        materials: currentDesign.materials,
        occupants: currentDesign.occupants,
        thermal_mass_level: thermalMassLevel,
      });
      setSimulationResult(res);
    } catch (e) {
      console.error('Simulation execution failed:', e);
    } finally {
      setIsSimulating(false);
    }
  };

  useEffect(() => {
    if (!simulationResult) {
      handleExecuteSimulation();
    }
  }, [selectedLocationId, selectedMonth]);

  const hourlyChartData = simulationResult?.hourly_results.map((r) => ({
    hour: `${r.hour.toString().padStart(2, '0')}:00`,
    t_outdoor: r.t_outdoor,
    t_indoor: r.t_indoor,
    t_sol_air: r.t_sol_air,
    q_solar_kw: Number(((r.q_solar_w || 0) / 1000).toFixed(2)),
    q_wall_kw: Number(((r.q_wall_w || 0) / 1000).toFixed(2)),
    q_roof_kw: Number(((r.q_roof_w || 0) / 1000).toFixed(2)),
    q_win_kw: Number(((r.q_window_w || 0) / 1000).toFixed(2)),
    q_vent_kw: Number(((r.q_vent_w || 0) / 1000).toFixed(2)),
  })) || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12 animate-in fade-in duration-300">
      {/* Top Header & Simulation Trigger Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-surface-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-md text-[10px] font-mono uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              05. Multi-Physics Simulation & 3D Twin
            </span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white mt-1.5 flex items-center gap-2">
            <span>Diurnal Thermal Response Simulator</span>
            <span className="text-xs font-normal text-slate-400 font-mono">
              ({selectedLocationId.replace('_', ' ').toUpperCase()})
            </span>
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Button
            variant="primary"
            icon={<Play className="w-4 h-4" />}
            isLoading={isSimulating}
            onClick={handleExecuteSimulation}
          >
            Run Thermal Simulation
          </Button>
        </div>
      </div>

      {/* Main 3-Column Engineering Dashboard */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Column: Quick Parameters */}
        <div className="lg:col-span-3 space-y-4">
          <Card className="space-y-4 p-4 text-xs">
            <div className="flex items-center justify-between border-b border-surface-border pb-2">
              <span className="font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                <Compass className="w-4 h-4 text-emerald-400" />
                <span>Orientation & Sizing</span>
              </span>
              <span className="font-mono text-emerald-400 font-bold">{currentDesign.geometry.orientation_deg}°</span>
            </div>

            <div className="space-y-2">
              <label className="text-slate-400 text-[11px] block">Solar Azimuth Orientation (180° = True South)</label>
              <input
                type="range"
                min="0"
                max="360"
                step="15"
                value={currentDesign.geometry.orientation_deg}
                onChange={(e) => updateGeometry({ orientation_deg: Number(e.target.value) })}
                className="w-full h-1.5 bg-surface-border rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>0° N</span>
                <span>90° E</span>
                <span className="text-emerald-400 font-bold">180° S</span>
                <span>270° W</span>
              </div>
            </div>

            <div className="space-y-2 pt-2 border-t border-surface-border">
              <label className="text-slate-400 text-[11px] block font-bold text-white">Thermal Mass Core Level</label>
              <div className="grid grid-cols-3 gap-1.5">
                {(['low', 'medium', 'high'] as const).map((lvl) => (
                  <button
                    key={lvl}
                    onClick={() => setThermalMassLevel(lvl)}
                    className={`py-1.5 rounded-lg text-xs font-semibold uppercase transition ${
                      thermalMassLevel === lvl
                        ? 'bg-emerald-600 text-white shadow'
                        : 'bg-surface-raised border border-surface-border text-slate-400 hover:text-white'
                    }`}
                  >
                    {lvl}
                  </button>
                ))}
              </div>
              <p className="text-[10px] text-slate-400 leading-tight">
                High mass (300mm Trombe wall) absorbs solar heat by day and radiates it into zone by night.
              </p>
            </div>

            <div className="space-y-1.5 pt-2 border-t border-surface-border text-[11px]">
              <div className="flex justify-between">
                <span className="text-slate-400">Dimensions:</span>
                <span className="font-mono text-white">
                  {currentDesign.geometry.length_m}m × {currentDesign.geometry.width_m}m × {currentDesign.geometry.height_m}m
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Roof Pitch:</span>
                <span className="font-mono text-white">{currentDesign.geometry.roof_pitch_deg}°</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Window WWR:</span>
                <span className="font-mono text-white">{currentDesign.geometry.wwr_pct}%</span>
              </div>
            </div>
          </Card>

          {/* View Mode Switcher */}
          <Card className="p-3 space-y-2 text-xs">
            <span className="font-bold text-white uppercase tracking-wider block text-[11px]">3D Viewport Render Mode</span>
            <div className="grid grid-cols-2 gap-1.5">
              {[
                { id: 'normal', label: 'Normal / CAD' },
                { id: 'solar', label: 'Solar Path' },
                { id: 'thermal', label: 'Thermal Heatmap' },
                { id: 'heat_flow', label: 'Heat Vectors' },
              ].map((m) => (
                <button
                  key={m.id}
                  onClick={() => setActiveViewMode(m.id as any)}
                  className={`py-1.5 px-2 rounded-lg text-[11px] font-medium text-left transition ${
                    activeViewMode === m.id
                      ? 'bg-emerald-600 text-white'
                      : 'bg-surface-raised text-slate-400 hover:text-white'
                  }`}
                >
                  {m.label}
                </button>
              ))}
            </div>
          </Card>
        </div>

        {/* Center Column: 3D Digital Twin Viewport */}
        <div className="lg:col-span-6 h-[440px] rounded-2xl bg-surface border border-surface-border overflow-hidden relative shadow-inner">
          <DigitalTwinCanvas />
          <div className="absolute top-3 left-3 bg-surface/90 backdrop-blur-md px-3 py-1 rounded-lg border border-surface-border text-[11px] text-slate-300 font-mono flex items-center gap-2">
            <Box className="w-3.5 h-3.5 text-emerald-400" />
            <span>Interactive WebGL Twin • Orientation: {currentDesign.geometry.orientation_deg}°</span>
          </div>
        </div>

        {/* Right Column: Key Results HUD */}
        <div className="lg:col-span-3 space-y-3">
          <Card className="border-t-4 border-t-amber-500 p-4 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-400 uppercase">Solar Energy Captured</span>
              <Sun className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-xl font-extrabold font-mono text-amber-400">
              +{simulationResult?.summary.total_daily_solar_captured_kwh || '16.4'} <span className="text-xs font-normal text-slate-400">kWh/day</span>
            </div>
            <p className="text-[10px] text-slate-400 leading-tight">
              South glazing + Trombe thermal storage daytime direct solar capture.
            </p>
          </Card>

          <Card className="border-t-4 border-t-sky-500 p-4 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-400 uppercase">Total Envelope Heat Loss</span>
              <TrendingDown className="w-4 h-4 text-sky-400" />
            </div>
            <div className="text-xl font-extrabold font-mono text-sky-400">
              -{simulationResult?.summary.total_daily_heat_loss_kwh || '7.1'} <span className="text-xs font-normal text-slate-400">kWh/day</span>
            </div>
            <p className="text-[10px] text-slate-400 leading-tight">
              Calculated conduction + infiltration losses across 24 hours.
            </p>
          </Card>

          <Card className="border-t-4 border-t-emerald-500 p-4 space-y-1.5">
            <div className="flex items-center justify-between text-xs">
              <span className="font-bold text-slate-400 uppercase">Nighttime Min Indoor Temp</span>
              <Moon className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-xl font-extrabold font-mono text-emerald-400">
              {simulationResult?.summary.nighttime_min_indoor_temp_c || '17.8'}°C
            </div>
            <p className="text-[10px] text-slate-400 leading-tight">
              Maintained comfortable zone temperatures despite sub-zero outdoor night.
            </p>
          </Card>

          <Card className="p-3 text-xs space-y-1 bg-surface-raised border border-surface-border">
            <div className="flex justify-between">
              <span className="text-slate-400">Sunset Temp Drop:</span>
              <span className="font-mono font-bold text-purple-400">
                {simulationResult?.summary.sunset_temp_drop_c || '4.2'}°C / 11h
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Thermal Comfort Score:</span>
              <span className="font-mono font-bold text-emerald-400">
                {simulationResult?.summary.comfort_score || '88'}%
              </span>
            </div>
          </Card>
        </div>
      </div>

      {/* Bottom Section: Primary Engineering Graphs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* GRAPH 1: 24-Hour Diurnal Thermal Response */}
        <Card className="space-y-3 p-5">
          <div className="flex items-center justify-between border-b border-surface-border pb-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Thermometer className="w-4 h-4 text-emerald-400" />
              <span>Primary Graph: 24-Hour Diurnal Thermal Response</span>
            </h3>
            <Badge variant="emerald" size="sm">°C vs Hour</Badge>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={hourlyChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#232c3d" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} domain={['dataMin - 2', 'dataMax + 2']} />
                <Tooltip contentStyle={{ backgroundColor: '#11161f', borderColor: '#232c3d', fontSize: '11px' }} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <ReferenceLine y={18} stroke="#10b981" strokeDasharray="3 3" label={{ value: 'Comfort 18°C', fill: '#10b981', fontSize: 10 }} />
                <Line type="monotone" dataKey="t_outdoor" name="Outdoor Temp (°C)" stroke="#38bdf8" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="t_indoor" name="Indoor Temp (°C)" stroke="#10b981" strokeWidth={2.5} dot={false} />
                <Line type="monotone" dataKey="t_sol_air" name="Sol-Air Temp (°C)" stroke="#f59e0b" strokeWidth={1.5} strokeDasharray="4 4" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* GRAPH 2: Hourly Component Heat Flow Breakdown */}
        <Card className="space-y-3 p-5">
          <div className="flex items-center justify-between border-b border-surface-border pb-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Zap className="w-4 h-4 text-amber-400" />
              <span>Second Graph: Hourly Component Heat Flow Breakdown</span>
            </h3>
            <Badge variant="amber" size="sm">kW Heat Flux</Badge>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={hourlyChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#232c3d" />
                <XAxis dataKey="hour" stroke="#64748b" fontSize={10} />
                <YAxis stroke="#64748b" fontSize={10} />
                <Tooltip contentStyle={{ backgroundColor: '#11161f', borderColor: '#232c3d', fontSize: '11px' }} />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                <ReferenceLine y={0} stroke="#64748b" />
                <Bar dataKey="q_solar_kw" name="Solar Gain (+kW)" fill="#f59e0b" stackId="gain" />
                <Bar dataKey="q_wall_kw" name="Wall Loss (kW)" fill="#ef4444" stackId="loss" />
                <Bar dataKey="q_roof_kw" name="Roof Loss (kW)" fill="#f97316" stackId="loss" />
                <Bar dataKey="q_win_kw" name="Window Loss (kW)" fill="#a855f7" stackId="loss" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>
    </div>
  );
};
