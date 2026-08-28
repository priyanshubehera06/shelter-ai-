import React, { useState } from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { SectionTitle } from '../ui/SectionTitle';
import { MetricRow } from '../ui/MetricRow';
import { Slider } from '../ui/Slider';
import { Select } from '../ui/Select';
import { Edit3, Check, Sliders } from 'lucide-react';

export const BuildingParameters: React.FC = () => {
  const { currentDesign, updateGeometry } = useShelterStore();
  const [isEditing, setIsEditing] = useState(false);

  const {
    length_m: L,
    width_m: W,
    height_m: H,
    roof_type,
    roof_pitch_deg,
    wwr_pct,
    overhang_m,
    orientation_deg,
  } = currentDesign.geometry;

  const floorArea = (L * W).toFixed(2);

  const getOrientationLabel = (deg: number) => {
    if (deg >= 337.5 || deg < 22.5) return `${deg}° (N)`;
    if (deg >= 22.5 && deg < 67.5) return `${deg}° (NE)`;
    if (deg >= 67.5 && deg < 112.5) return `${deg}° (E)`;
    if (deg >= 112.5 && deg < 157.5) return `${deg}° (SE)`;
    if (deg >= 157.5 && deg < 202.5) return `${deg}° (S)`;
    if (deg >= 202.5 && deg < 247.5) return `${deg}° (SW)`;
    if (deg >= 247.5 && deg < 292.5) return `${deg}° (W)`;
    return `${deg}° (NW)`;
  };

  const roofTypeLabels: Record<string, string> = {
    pitched: 'Dual Gable',
    monoslope: 'Single Slope',
    hipped: 'Hipped (4-Slope)',
    flat: 'Flat Slab',
  };

  return (
    <div className="space-y-2.5">
      <SectionTitle
        title="Building Parameters"
        icon={<Sliders className="w-3.5 h-3.5" />}
        action={
          <button
            onClick={() => setIsEditing(!isEditing)}
            className="flex items-center gap-1 text-[10px] text-emerald-400 hover:text-emerald-300 font-semibold uppercase tracking-wider"
          >
            {isEditing ? <Check className="w-3 h-3" /> : <Edit3 className="w-3 h-3" />}
            {isEditing ? 'Done' : 'Edit'}
          </button>
        }
      />

      {!isEditing ? (
        <div className="bg-[#161d28] border border-[#232c3d] rounded p-2.5 space-y-0.5">
          <MetricRow label="Length" value={L.toFixed(2)} unit="m" />
          <MetricRow label="Width" value={W.toFixed(2)} unit="m" />
          <MetricRow label="Height" value={H.toFixed(2)} unit="m" />
          <MetricRow label="Floor Area" value={floorArea} unit="m²" accent="green" />
          <MetricRow label="Orientation" value={getOrientationLabel(orientation_deg)} />
          <MetricRow label="Roof Type" value={roofTypeLabels[roof_type] || roof_type} />
          <MetricRow label="Roof Slope" value={roof_pitch_deg.toFixed(1)} unit="°" />
          <MetricRow label="Window Ratio" value={wwr_pct.toFixed(0)} unit="%" />
          <MetricRow label="Shading Depth" value={overhang_m.toFixed(2)} unit="m" />
        </div>
      ) : (
        <div className="bg-[#161d28] border border-emerald-500/50 rounded p-2.5 space-y-3 animate-in fade-in duration-150">
          <div className="grid grid-cols-2 gap-2">
            <Slider
              label="Length"
              value={L}
              min={3.5}
              max={12.0}
              step={0.5}
              unit="m"
              onChange={(val) => updateGeometry({ length_m: val })}
            />
            <Slider
              label="Width"
              value={W}
              min={2.5}
              max={8.0}
              step={0.5}
              unit="m"
              onChange={(val) => updateGeometry({ width_m: val })}
            />
          </div>

          <div className="grid grid-cols-2 gap-2">
            <Slider
              label="Height"
              value={H}
              min={2.2}
              max={3.8}
              step={0.1}
              unit="m"
              onChange={(val) => updateGeometry({ height_m: val })}
            />
            <Slider
              label="Orientation"
              value={orientation_deg}
              min={0}
              max={360}
              step={15}
              unit="°"
              onChange={(val) => updateGeometry({ orientation_deg: val })}
            />
          </div>

          <Select
            label="Roof Type"
            options={[
              { value: 'pitched', label: 'Dual Gable (Pitched)' },
              { value: 'monoslope', label: 'Single Slope (Monoslope)' },
              { value: 'hipped', label: 'Hipped (4-Slope)' },
              { value: 'flat', label: 'Flat Slab' },
            ]}
            value={roof_type}
            onChange={(e) => updateGeometry({ roof_type: e.target.value as any })}
          />

          <div className="grid grid-cols-2 gap-2">
            <Slider
              label="Roof Slope"
              value={roof_pitch_deg}
              min={0}
              max={40}
              step={1}
              unit="°"
              onChange={(val) => updateGeometry({ roof_pitch_deg: val })}
            />
            <Slider
              label="Shading Depth"
              value={overhang_m}
              min={0.2}
              max={1.5}
              step={0.1}
              unit="m"
              onChange={(val) => updateGeometry({ overhang_m: val })}
            />
          </div>
        </div>
      )}
    </div>
  );
};
