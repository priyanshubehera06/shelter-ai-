import React from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { SectionTitle } from '../ui/SectionTitle';
import { ShelterDesign } from '../../types';
import { Sparkles, Plus, Check } from 'lucide-react';

export const DesignSelection: React.FC = () => {
  const { currentDesign, savedDesigns, loadDesign } = useShelterStore();

  const handleSelectDesign = (design: ShelterDesign) => {
    loadDesign(design);
  };

  const handleNewDesign = () => {
    loadDesign({
      name: `Custom Design ${savedDesigns.length + 1}`,
      archetype: 'Custom Sized',
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
    });
  };

  return (
    <div className="space-y-2.5">
      <SectionTitle
        title="Design Selection"
        icon={<Sparkles className="w-3.5 h-3.5" />}
        action={
          <button
            onClick={handleNewDesign}
            className="flex items-center gap-1 text-[10px] text-emerald-400 hover:text-emerald-300 font-semibold uppercase tracking-wider"
          >
            <Plus className="w-3 h-3" />
            New
          </button>
        }
      />

      {/* Choose Design Dropdown */}
      <select
        value={currentDesign.name}
        onChange={(e) => {
          const d = savedDesigns.find((des) => des.name === e.target.value);
          if (d) handleSelectDesign(d);
        }}
        className="w-full bg-[#1c2433] border border-[#232c3d] rounded px-2.5 py-1.5 text-xs text-slate-200 font-medium focus:outline-none focus:border-emerald-500 cursor-pointer"
      >
        {savedDesigns.map((d, idx) => (
          <option key={idx} value={d.name} className="bg-[#11161f]">
            {d.name}
          </option>
        ))}
      </select>

      {/* Design Thumbnails Grid */}
      <div className="grid grid-cols-2 gap-2 pt-1">
        {savedDesigns.map((design, idx) => {
          const isSelected = currentDesign.name === design.name;
          return (
            <div
              key={idx}
              onClick={() => handleSelectDesign(design)}
              className={`relative rounded-md border p-2 text-left transition-all cursor-pointer flex flex-col justify-between ${
                isSelected
                  ? 'bg-emerald-950/25 border-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.2)]'
                  : 'bg-[#161d28] border-[#232c3d] hover:border-slate-500'
              }`}
            >
              {/* Mini Isometric 3D Preview Box */}
              <div className="h-10 rounded bg-[#0d1117] border border-[#232c3d] flex items-center justify-center text-slate-500 font-mono text-[10px] mb-1.5">
                <span>{design.geometry.roof_type.toUpperCase()}</span>
                {isSelected && (
                  <div className="absolute top-1.5 right-1.5 w-3.5 h-3.5 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center">
                    <Check className="w-2.5 h-2.5 stroke-[3]" />
                  </div>
                )}
              </div>
              <span className="text-[11px] font-semibold text-slate-200 truncate block">
                {design.name}
              </span>
              <span className="text-[9px] text-slate-400 truncate block font-mono">
                {design.geometry.length_m}m × {design.geometry.width_m}m • {design.geometry.roof_type}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
