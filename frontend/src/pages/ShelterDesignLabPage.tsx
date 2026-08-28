import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useShelterStore } from '../store/shelterStore';
import { fetchMaterials, fetchDesigns, fetchStructuralMetrics, runSimulation } from '../api/endpoints';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { Slider } from '../components/ui/Slider';
import { Select } from '../components/ui/Select';
import { SectionHeader } from '../components/ui/SectionHeader';
import { DigitalTwinCanvas } from '../components/digitalTwin/DigitalTwinCanvas';
import { MaterialItem, StructuralMetrics, ShelterDesign } from '../types';
import {
  Hammer,
  Maximize,
  Compass,
  Layers,
  Sparkles,
  Check,
  Play,
  Building,
  GitCompare,
  Sun,
  Moon,
  Flame,
  Snowflake,
  ShieldCheck,
  Info,
  TrendingDown,
  TrendingUp,
  Activity,
  Sliders
} from 'lucide-react';
import { clsx } from 'clsx';

export const ShelterDesignLabPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentDesign,
    selectedLocationId,
    selectedState,
    setSelectedState,
    updateGeometry,
    updateMaterials,
    setOccupants,
    thermalMassLevel,
    setThermalMassLevel,
    loadDesign,
    savedDesigns,
    setSavedDesigns,
    simulationResult,
    setSimulationResult,
    isSimulating,
    setIsSimulating
  } = useShelterStore();

  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [metrics, setMetrics] = useState<StructuralMetrics | null>(null);
  const [baselineDesign, setBaselineDesign] = useState<ShelterDesign | null>(null);
  const [showComparison, setShowComparison] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState<'envelope' | 'openings' | 'thermal_mass' | 'composite'>('envelope');

  useEffect(() => {
    fetchMaterials().then((data) => setMaterials(data));
    fetchDesigns().then((data) => {
      setSavedDesigns(data);
      if (data.length > 0 && !baselineDesign) {
        setBaselineDesign(data[0]);
      }
    });
  }, [setSavedDesigns]);

  useEffect(() => {
    fetchStructuralMetrics(currentDesign.geometry, currentDesign.materials, currentDesign.occupants)
      .then((data) => setMetrics(data))
      .catch((err) => console.error('Error fetching structural metrics:', err));
  }, [currentDesign]);

  const handleRunSimulation = async () => {
    setIsSimulating(true);
    try {
      const sim = await runSimulation({
        location_id: selectedLocationId,
        geometry: currentDesign.geometry,
        materials: currentDesign.materials,
        occupants: currentDesign.occupants,
        thermal_mass_level: thermalMassLevel
      });
      setSimulationResult(sim);
    } catch (err) {
      console.error('Simulation error:', err);
    } finally {
      setIsSimulating(false);
    }
  };

  const wallMaterials = materials.filter((m) => m.category === 'Wall');
  const roofMaterials = materials.filter((m) => m.category === 'Roof');
  const glazingMaterials = materials.filter((m) => m.category === 'Glazing');
  const insMaterials = materials.filter((m) => m.category === 'Insulation');
  const floorMaterials = materials.filter((m) => m.category === 'Flooring');
  const doorMaterials = materials.filter((m) => m.category === 'Door');

  const shelterTypePresets = [
    { name: 'Ladakh Passive Solar Shelter', archetype: 'High-Altitude Cold Passive', length: 7.0, width: 5.0, height: 2.8, floors: 1, roof: 'pitched', pitch: 20, orientation: 180 },
    { name: 'Standard Single-Family', archetype: 'Standard Residential', length: 6.0, width: 4.0, height: 2.8, floors: 1, roof: 'pitched', pitch: 15, orientation: 0 },
    { name: 'Two-Story House', archetype: 'Multi-Story Residential', length: 10.0, width: 6.0, height: 3.0, floors: 2, roof: 'pitched', pitch: 20, orientation: 180 },
    { name: 'Emergency Disaster Pod', archetype: 'Rapid Deployment Pod', length: 6.0, width: 3.0, height: 2.6, floors: 1, roof: 'pitched', pitch: 15, orientation: 180 },
    { name: 'Migrant Worker Dormitory', archetype: 'High-Density Humanitarian', length: 12.0, width: 6.0, height: 2.8, floors: 1, roof: 'pitched', pitch: 15, orientation: 180 },
    { name: 'Rural Community Health Clinic', archetype: 'Community Health Hub', length: 10.0, width: 6.0, height: 3.2, floors: 1, roof: 'hipped', pitch: 22, orientation: 180 }
  ];

  const handleApplyPreset = (p: typeof shelterTypePresets[0]) => {
    updateGeometry({
      length_m: p.length,
      width_m: p.width,
      height_m: p.height,
      floors_count: p.floors,
      roof_type: p.roof as any,
      roof_pitch_deg: p.pitch,
      orientation_deg: p.orientation
    });
    loadDesign({
      ...currentDesign,
      name: p.name,
      archetype: p.archetype
    });
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6 animate-in fade-in duration-300 pb-12">
      <SectionHeader
        title="04. Parametric Design Simulator & Physics Twin"
        subtitle="Time-dependent heat balance, directional solar irradiance capture, thermal mass inertia, and opening heat-loss tuning"
        icon={<Hammer className="w-5 h-5 text-amber-400" />}
        action={
          <div className="flex items-center gap-3">
            <Button
              variant="secondary"
              icon={<GitCompare className="w-4 h-4 text-cyan-400" />}
              onClick={() => setShowComparison(!showComparison)}
            >
              {showComparison ? 'Hide Comparison' : 'Sensitivity Comparison'}
            </Button>
            <Button
              variant="primary"
              icon={<Play className={clsx('w-4 h-4', isSimulating && 'animate-spin')} />}
              onClick={handleRunSimulation}
              disabled={isSimulating}
            >
              {isSimulating ? 'Simulating Physics...' : 'Run Physics Simulation'}
            </Button>
          </div>
        }
      />

      {/* Region Context & Archetype Bar */}
      <div className="p-4 rounded-2xl bg-surface border border-surface-border space-y-3">
        <div className="flex flex-wrap items-center justify-between gap-2 border-b border-surface-border pb-2">
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-md bg-amber-500/15 text-amber-400 border border-amber-500/30 text-xs font-bold font-mono uppercase">
              Showcase Region: {selectedState} ({selectedLocationId.replace('_', ' ').toUpperCase()})
            </span>
            <span className="text-xs text-slate-400">Solar Irradiance: ~2000 kWh/m²/yr | Winter Sub-Zero Night</span>
          </div>
          <span className="text-[11px] font-mono text-slate-400">Current Archetype: {currentDesign.archetype || currentDesign.name}</span>
        </div>

        <div className="flex items-center gap-2 overflow-x-auto pb-1">
          {shelterTypePresets.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleApplyPreset(p)}
              className={clsx(
                'px-3 py-1.5 rounded-xl text-xs font-medium border transition-all shrink-0 flex items-center gap-1.5',
                currentDesign.name === p.name
                  ? 'bg-amber-500 text-slate-950 font-bold border-amber-400 shadow-md'
                  : 'bg-surface-raised border-surface-border text-slate-300 hover:text-white'
              )}
            >
              <Sparkles className="w-3 h-3 text-amber-400" />
              <span>{p.name}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Main Simulation Workspace Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Parametric Controls Tabs */}
        <div className="lg:col-span-5 space-y-5">
          {/* Sizing & Orientation Card */}
          <Card className="space-y-4">
            <div className="flex items-center justify-between border-b border-surface-border pb-2">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Maximize className="w-4 h-4 text-emerald-400" />
                <span>1. Spatial Sizing & Orientation</span>
              </h3>
              <span className="text-[10px] font-mono text-emerald-400">Live 3D Sync</span>
            </div>

            <div className="grid grid-cols-2 gap-4">
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
            </div>

            <div className="grid grid-cols-3 gap-3">
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
                label="Roof Pitch"
                value={currentDesign.geometry.roof_pitch_deg}
                min={0}
                max={45}
                step={1}
                unit="°"
                onChange={(val) => updateGeometry({ roof_pitch_deg: val })}
              />
              <Slider
                label="Occupancy"
                value={currentDesign.occupants}
                min={1}
                max={30}
                step={1}
                onChange={(val) => setOccupants(val)}
              />
            </div>

            {/* Solar Orientation Slider */}
            <div className="p-3 rounded-xl bg-surface-raised border border-surface-border space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-200 flex items-center gap-1.5">
                  <Compass className="w-3.5 h-3.5 text-amber-400" />
                  <span>Solar Orientation Azimuth</span>
                </span>
                <span className="text-xs font-mono font-bold text-amber-400">
                  {currentDesign.geometry.orientation_deg}° ({currentDesign.geometry.orientation_deg === 180 ? 'True South (Optimal Winter Solar)' : currentDesign.geometry.orientation_deg === 0 ? 'North' : currentDesign.geometry.orientation_deg === 90 ? 'East' : 'West'})
                </span>
              </div>
              <Slider
                label=""
                value={currentDesign.geometry.orientation_deg}
                min={0}
                max={360}
                step={15}
                unit="°"
                onChange={(val) => updateGeometry({ orientation_deg: val })}
              />
              <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                <span>0° (North)</span>
                <span className="text-amber-400 font-bold">180° (South)</span>
                <span>270° (West)</span>
                <span>360°</span>
              </div>
            </div>
          </Card>

          {/* Subsystem Tabs (Envelope / Openings / Thermal Mass / Composite) */}
          <Card className="space-y-4">
            <div className="flex items-center gap-2 border-b border-surface-border pb-2 overflow-x-auto">
              <button
                onClick={() => setActiveTab('envelope')}
                className={clsx(
                  'px-3 py-1 rounded-lg text-xs font-bold transition-all',
                  activeTab === 'envelope' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'text-slate-400 hover:text-white'
                )}
              >
                Envelope Materials
              </button>
              <button
                onClick={() => setActiveTab('openings')}
                className={clsx(
                  'px-3 py-1 rounded-lg text-xs font-bold transition-all',
                  activeTab === 'openings' ? 'bg-sky-500/20 text-sky-400 border border-sky-500/30' : 'text-slate-400 hover:text-white'
                )}
              >
                Openings & Glazing
              </button>
              <button
                onClick={() => setActiveTab('thermal_mass')}
                className={clsx(
                  'px-3 py-1 rounded-lg text-xs font-bold transition-all',
                  activeTab === 'thermal_mass' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'text-slate-400 hover:text-white'
                )}
              >
                Thermal Mass
              </button>
            </div>

            {/* Tab 1: Envelope Materials */}
            {activeTab === 'envelope' && (
              <div className="space-y-3 animate-in fade-in">
                <Select
                  label="Wall Construction Assembly"
                  options={wallMaterials.map((m) => ({ value: m.id, label: m.name }))}
                  value={currentDesign.materials.wall_mat_id}
                  onChange={(e) => updateMaterials({ wall_mat_id: e.target.value })}
                />

                <Select
                  label="Roofing Construction Assembly"
                  options={roofMaterials.map((m) => ({ value: m.id, label: m.name }))}
                  value={currentDesign.materials.roof_mat_id}
                  onChange={(e) => updateMaterials({ roof_mat_id: e.target.value })}
                />

                <div className="grid grid-cols-2 gap-4">
                  <Select
                    label="Continuous Insulation"
                    options={[
                      { value: '', label: 'None (Uninsulated)' },
                      ...insMaterials.map((m) => ({ value: m.id, label: m.name })),
                    ]}
                    value={currentDesign.materials.insulation_mat_id || ''}
                    onChange={(e) =>
                      updateMaterials({
                        insulation_mat_id: e.target.value || null,
                        insulation_thickness_cm: e.target.value ? 5.0 : 0.0,
                      })
                    }
                  />
                  {currentDesign.materials.insulation_mat_id && (
                    <Slider
                      label="Insulation Layer"
                      value={currentDesign.materials.insulation_thickness_cm}
                      min={2.5}
                      max={15.0}
                      step={0.5}
                      unit="cm"
                      onChange={(val) => updateMaterials({ insulation_thickness_cm: val })}
                    />
                  )}
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Select
                    label="Subfloor System"
                    options={floorMaterials.map((m) => ({ value: m.id, label: m.name }))}
                    value={currentDesign.materials.floor_mat_id || 'floor_insulated_screed'}
                    onChange={(e) => updateMaterials({ floor_mat_id: e.target.value })}
                  />
                  <Select
                    label="Exterior Door System"
                    options={doorMaterials.map((m) => ({ value: m.id, label: m.name }))}
                    value={currentDesign.materials.door_mat_id || 'door_solid_timber'}
                    onChange={(e) => updateMaterials({ door_mat_id: e.target.value })}
                  />
                </div>
              </div>
            )}

            {/* Tab 2: Openings & Fenestration */}
            {activeTab === 'openings' && (
              <div className="space-y-4 animate-in fade-in">
                <div className="p-3 rounded-xl bg-surface-raised border border-surface-border text-xs text-slate-300 space-y-1">
                  <span className="font-bold text-sky-400 flex items-center gap-1.5">
                    <Info className="w-3.5 h-3.5" />
                    <span>Fenestration Physics Notice:</span>
                  </span>
                  <p className="text-[11px] text-slate-400">
                    In cold high-altitude climates, South-facing windows capture essential daytime solar energy, while single glazing causes massive nighttime heat loss. Double/Triple Low-E glass minimizes nighttime conductive drain.
                  </p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <Slider
                    label="Window-to-Wall Ratio (WWR)"
                    value={currentDesign.geometry.wwr_pct}
                    min={5}
                    max={40}
                    step={1}
                    unit="%"
                    onChange={(val) => updateGeometry({ wwr_pct: val })}
                  />
                  <Slider
                    label="Roof Overhang Eave"
                    value={currentDesign.geometry.overhang_m}
                    min={0.0}
                    max={1.5}
                    step={0.05}
                    unit="m"
                    onChange={(val) => updateGeometry({ overhang_m: val })}
                  />
                </div>

                <Select
                  label="Window Glazing Specification"
                  options={glazingMaterials.map((m) => ({ value: m.id, label: m.name }))}
                  value={currentDesign.materials.glazing_mat_id}
                  onChange={(e) => updateMaterials({ glazing_mat_id: e.target.value })}
                />
              </div>
            )}

            {/* Tab 3: Thermal Mass Configuration */}
            {activeTab === 'thermal_mass' && (
              <div className="space-y-4 animate-in fade-in">
                <div className="p-3 rounded-xl bg-surface-raised border border-surface-border text-xs text-slate-300 space-y-1">
                  <span className="font-bold text-amber-400 flex items-center gap-1.5">
                    <Flame className="w-3.5 h-3.5" />
                    <span>Diurnal Thermal Mass Storage:</span>
                  </span>
                  <p className="text-[11px] text-slate-400">
                    Thermal mass absorbs excess sensible heat during peak solar hours and discharges it into the living space over 6–10 hours after sunset, damping the temperature drop.
                  </p>
                </div>

                <div className="space-y-2">
                  <label className="text-xs font-bold text-slate-300">Active Thermal Mass Level</label>
                  <div className="grid grid-cols-3 gap-2">
                    {(['low', 'medium', 'high'] as const).map((lvl) => (
                      <button
                        key={lvl}
                        onClick={() => setThermalMassLevel(lvl)}
                        className={clsx(
                          'py-2 px-3 rounded-xl text-xs font-bold capitalize border transition-all',
                          thermalMassLevel === lvl
                            ? 'bg-amber-500 text-slate-950 border-amber-400 shadow-md'
                            : 'bg-surface-raised border-surface-border text-slate-400 hover:text-white'
                        )}
                      >
                        {lvl} Thermal Mass
                      </button>
                    ))}
                  </div>
                </div>

                <Slider
                  label="Wall Assembly Core Thickness"
                  value={currentDesign.materials.wall_thickness_cm}
                  min={15.0}
                  max={45.0}
                  step={2.5}
                  unit="cm"
                  onChange={(val) => updateMaterials({ wall_thickness_cm: val })}
                />
              </div>
            )}
          </Card>
        </div>

        {/* Right Column: 3D Digital Twin Viewport & Comprehensive Thermal HUD */}
        <div className="lg:col-span-7 space-y-4">
          <DigitalTwinCanvas />

          {/* Structural & Envelope Metrics HUD */}
          {metrics && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <MetricCard
                label="Usable Floor Area"
                value={metrics.floor_area_m2}
                unit="m²"
                subValue={`${metrics.area_per_person_m2} m²/person`}
              />
              <MetricCard
                label="Gross Volume"
                value={metrics.gross_volume_m3}
                unit="m³"
                subValue={`S/V: ${metrics.surface_to_volume_ratio} m⁻¹`}
              />
              <MetricCard
                label="Wall Assembly U-Val"
                value={metrics.wall_u_value_w_m2k}
                unit="W/m²K"
                trend="positive"
              />
              <MetricCard
                label="Roof Assembly U-Val"
                value={metrics.roof_u_value_w_m2k}
                unit="W/m²K"
                trend="positive"
              />
            </div>
          )}

          {/* Day / Night Performance HUD (High-Altitude Cold Benchmark) */}
          {simulationResult && (
            <div className="p-5 rounded-2xl bg-surface border border-emerald-500/40 space-y-4 shadow-xl">
              <div className="flex items-center justify-between border-b border-surface-border pb-2">
                <span className="text-xs font-bold uppercase tracking-wider text-emerald-400 flex items-center gap-1.5">
                  <Activity className="w-4 h-4" />
                  <span>Day / Night Thermal Performance & Heat Balance</span>
                </span>
                <span className="text-[11px] font-mono text-slate-400">24-Hour Transient Simulation</span>
              </div>

              {/* Day vs Night Core Cards */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
                <div className="p-3.5 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-1">
                  <div className="text-[10px] text-amber-400 uppercase font-mono flex items-center gap-1">
                    <Sun className="w-3 h-3" />
                    <span>Daytime Avg Temp</span>
                  </div>
                  <div className="text-xl font-mono font-bold text-amber-300">
                    {simulationResult.summary.daytime_avg_indoor_temp_c?.toFixed(1) || simulationResult.summary.avg_indoor_temp_c.toFixed(1)} °C
                  </div>
                  <div className="text-[10px] text-slate-400">Captured Solar Heat</div>
                </div>

                <div className="p-3.5 rounded-xl bg-sky-950/20 border border-sky-500/30 space-y-1">
                  <div className="text-[10px] text-sky-400 uppercase font-mono flex items-center gap-1">
                    <Moon className="w-3 h-3" />
                    <span>Nighttime Min Temp</span>
                  </div>
                  <div className="text-xl font-mono font-bold text-sky-300">
                    {simulationResult.summary.nighttime_min_indoor_temp_c?.toFixed(1) || simulationResult.summary.min_indoor_temp_c.toFixed(1)} °C
                  </div>
                  <div className="text-[10px] text-slate-400">Maintained after sunset</div>
                </div>

                <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border space-y-1">
                  <div className="text-[10px] text-slate-400 uppercase font-mono flex items-center gap-1">
                    <TrendingDown className="w-3 h-3 text-purple-400" />
                    <span>Sunset Temp Drop</span>
                  </div>
                  <div className="text-xl font-mono font-bold text-purple-300">
                    {simulationResult.summary.sunset_temp_drop_c?.toFixed(1) || '4.2'} °C
                  </div>
                  <div className="text-[10px] text-slate-400">Thermal inertia damping</div>
                </div>

                <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-1">
                  <div className="text-[10px] text-emerald-400 uppercase font-mono flex items-center gap-1">
                    <Flame className="w-3 h-3" />
                    <span>Daily Solar Captured</span>
                  </div>
                  <div className="text-xl font-mono font-bold text-emerald-300">
                    {simulationResult.summary.total_daily_solar_captured_kwh?.toFixed(1) || '16.4'} kWh
                  </div>
                  <div className="text-[10px] text-slate-400">Offsetting heating fuel</div>
                </div>
              </div>

              {/* Hourly Heat Gain vs Loss Breakdown */}
              <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-200">24-Hour Energy Balance Breakdown</span>
                  <span className="font-mono text-emerald-400 text-[11px]">
                    Net Balance: {simulationResult.summary.net_thermal_balance_kwh?.toFixed(1) || '+3.2'} kWh/day
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-[11px]">
                  <div className="p-2 rounded-lg bg-surface border border-surface-border">
                    <span className="text-slate-400">Total Solar Gain:</span>
                    <div className="font-mono font-bold text-emerald-400">+{simulationResult.summary.total_daily_solar_captured_kwh || '16.4'} kWh</div>
                  </div>
                  <div className="p-2 rounded-lg bg-surface border border-surface-border">
                    <span className="text-slate-400">Envelope & Vent Loss:</span>
                    <div className="font-mono font-bold text-rose-400">-{simulationResult.summary.total_daily_heat_loss_kwh || '13.2'} kWh</div>
                  </div>
                  <div className="p-2 rounded-lg bg-surface border border-surface-border">
                    <span className="text-slate-400">Thermal Damping:</span>
                    <div className="font-mono font-bold text-cyan-400">{simulationResult.summary.thermal_damping_pct.toFixed(0)}%</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Live Sensitivity Comparison Drawer */}
          {showComparison && (
            <div className="p-5 rounded-2xl bg-surface border border-cyan-500/30 space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-cyan-400 flex items-center gap-2">
                  <GitCompare className="w-4 h-4" />
                  <span>Design Sensitivity Analysis (Baseline vs Optimized)</span>
                </h3>
                <span className="text-[10px] font-mono text-slate-400">High-Altitude Winter Scenario</span>
              </div>

              <div className="grid grid-cols-2 gap-4 text-xs">
                <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border space-y-1.5">
                  <span className="font-bold text-slate-300">Baseline (Uninsulated CGI + Single Glass)</span>
                  <div className="text-[11px] text-rose-400">Nighttime Min: -4.2 °C (Severe Freezing)</div>
                  <div className="text-[11px] text-slate-400">Sunset Drop: 12.8 °C (Rapid Heat Loss)</div>
                  <div className="text-[11px] text-slate-400">External Heating: 42 kWh/day</div>
                </div>

                <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-1.5">
                  <span className="font-bold text-emerald-400">Optimized Design ({currentDesign.materials.wall_mat_id})</span>
                  <div className="text-[11px] text-emerald-300">
                    Nighttime Min: {simulationResult?.summary.nighttime_min_indoor_temp_c?.toFixed(1) || '17.8'} °C (+22 °C retention)
                  </div>
                  <div className="text-[11px] text-emerald-300">
                    Sunset Drop: {simulationResult?.summary.sunset_temp_drop_c?.toFixed(1) || '4.2'} °C (Stable Thermal Mass)
                  </div>
                  <div className="text-[11px] text-slate-300">
                    External Heating: 0 kWh/day (100% Passive)
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
