import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useShelterStore } from '../store/shelterStore';
import { fetchMaterials, fetchDesigns, fetchStructuralMetrics } from '../api/endpoints';
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
  ArrowRight,
  Sparkles,
  Users,
  Check
} from 'lucide-react';

export const ShelterDesignLabPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentDesign,
    updateGeometry,
    updateMaterials,
    setOccupants,
    loadDesign,
    savedDesigns,
    setSavedDesigns,
  } = useShelterStore();

  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [metrics, setMetrics] = useState<StructuralMetrics | null>(null);

  useEffect(() => {
    fetchMaterials().then((data) => setMaterials(data));
    fetchDesigns().then((data) => setSavedDesigns(data));
  }, [setSavedDesigns]);

  useEffect(() => {
    fetchStructuralMetrics(currentDesign.geometry, currentDesign.materials, currentDesign.occupants)
      .then((data) => setMetrics(data))
      .catch((err) => console.error('Error fetching structural metrics:', err));
  }, [currentDesign]);

  const wallMaterials = materials.filter((m) => m.category === 'Wall');
  const roofMaterials = materials.filter((m) => m.category === 'Roof');
  const glazingMaterials = materials.filter((m) => m.category === 'Glazing');
  const insMaterials = materials.filter((m) => m.category === 'Insulation');

  const roofTypeOptions = [
    { value: 'pitched', label: 'Pitched (Dual Gable)' },
    { value: 'monoslope', label: 'Monoslope (Single Shed)' },
    { value: 'hipped', label: 'Hipped (4-Slope)' },
    { value: 'flat', label: 'Flat (Terrace Slab)' },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300">
      <SectionHeader
        title="04. Parametric Shelter Design Lab"
        subtitle="Configure physical geometry, roof slope, fenestration ratios, and layered construction materials with real-time 3D blueprint response"
        icon={<Hammer className="w-5 h-5 text-amber-400" />}
        action={
          <Button
            variant="primary"
            icon={<ArrowRight className="w-4 h-4" />}
            onClick={() => navigate('/digital-twin')}
          >
            Launch Full 3D Digital Twin
          </Button>
        }
      />

      {/* Preset Archetypes Selector */}
      {savedDesigns.length > 0 && (
        <div className="flex items-center gap-3 overflow-x-auto pb-2">
          <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider shrink-0">
            Design Presets:
          </span>
          {savedDesigns.map((d, idx) => (
            <button
              key={idx}
              onClick={() => loadDesign(d)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all shrink-0 flex items-center gap-1.5 ${
                currentDesign.name === d.name
                  ? 'bg-emerald-600 text-white border-emerald-500 shadow-md'
                  : 'bg-surface-raised border-surface-border text-slate-300 hover:text-white'
              }`}
            >
              <Sparkles className="w-3 h-3 text-amber-400" />
              <span>{d.name}</span>
            </button>
          ))}
        </div>
      )}

      {/* Main Grid: Parametric Controls + Real-Time 3D Viewport */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Column: Parametric Sliders & Material Selectors */}
        <div className="lg:col-span-5 space-y-5">
          {/* Dimensions Card */}
          <Card className="space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-surface-border pb-2">
              <Maximize className="w-4 h-4 text-emerald-400" />
              1. Spatial Dimensions & Sizing
            </h3>

            <div className="grid grid-cols-2 gap-4">
              <Slider
                label="Length"
                value={currentDesign.geometry.length_m}
                min={3.0}
                max={14.0}
                step={0.5}
                unit="m"
                onChange={(val) => updateGeometry({ length_m: val })}
              />
              <Slider
                label="Width"
                value={currentDesign.geometry.width_m}
                min={2.5}
                max={8.0}
                step={0.5}
                unit="m"
                onChange={(val) => updateGeometry({ width_m: val })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Slider
                label="Wall Height"
                value={currentDesign.geometry.height_m}
                min={2.2}
                max={4.0}
                step={0.1}
                unit="m"
                onChange={(val) => updateGeometry({ height_m: val })}
              />
              <Slider
                label="Occupancy (Persons)"
                value={currentDesign.occupants}
                min={1}
                max={12}
                step={1}
                onChange={(val) => setOccupants(val)}
              />
            </div>
          </Card>

          {/* Roof & Fenestration Card */}
          <Card className="space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-surface-border pb-2">
              <Compass className="w-4 h-4 text-sky-400" />
              2. Roof Assembly & Shading
            </h3>

            <Select
              label="Roof Form / Type"
              options={roofTypeOptions}
              value={currentDesign.geometry.roof_type}
              onChange={(e) => updateGeometry({ roof_type: e.target.value as any })}
            />

            <div className="grid grid-cols-2 gap-4">
              <Slider
                label="Roof Pitch Slope"
                value={currentDesign.geometry.roof_pitch_deg}
                min={0}
                max={45}
                step={1}
                unit="°"
                onChange={(val) => updateGeometry({ roof_pitch_deg: val })}
              />
              <Slider
                label="Overhang Shading"
                value={currentDesign.geometry.overhang_m}
                min={0.0}
                max={1.5}
                step={0.1}
                unit="m"
                onChange={(val) => updateGeometry({ overhang_m: val })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <Slider
                label="Window Ratio (WWR)"
                value={currentDesign.geometry.wwr_pct}
                min={5}
                max={40}
                step={1}
                unit="%"
                onChange={(val) => updateGeometry({ wwr_pct: val })}
              />
              <Slider
                label="Orientation (Azimuth)"
                value={currentDesign.geometry.orientation_deg}
                min={0}
                max={360}
                step={15}
                unit="°"
                onChange={(val) => updateGeometry({ orientation_deg: val })}
              />
            </div>
          </Card>

          {/* Materials Envelope Card */}
          <Card className="space-y-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-surface-border pb-2">
              <Layers className="w-4 h-4 text-amber-400" />
              3. Envelope Materials Catalog
            </h3>

            <Select
              label="Wall Assembly Material"
              options={wallMaterials.map((m) => ({ value: m.id, label: m.name }))}
              value={currentDesign.materials.wall_mat_id}
              onChange={(e) => updateMaterials({ wall_mat_id: e.target.value })}
            />

            <Select
              label="Roofing System Material"
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
                  min={1.0}
                  max={12.0}
                  step={0.5}
                  unit="cm"
                  onChange={(val) => updateMaterials({ insulation_thickness_cm: val })}
                />
              )}
            </div>
          </Card>
        </div>

        {/* Right Column: Real-Time 3D Digital Twin Viewport & Metrics */}
        <div className="lg:col-span-7 space-y-4">
          <DigitalTwinCanvas />

          {/* Structural Metrics HUD */}
          {metrics && (
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <MetricCard
                label="Usable Floor Area"
                value={metrics.floor_area_m2}
                unit="m²"
                subValue={`${metrics.area_per_person_m2} m²/person`}
              />
              <MetricCard
                label="Internal Air Volume"
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
        </div>
      </div>
    </div>
  );
};
