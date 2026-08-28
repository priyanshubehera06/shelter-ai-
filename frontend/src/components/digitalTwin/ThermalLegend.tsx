import React from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { SectionTitle } from '../ui/SectionTitle';
import { Flame } from 'lucide-react';

export const ThermalLegend: React.FC = () => {
  const { activeViewMode } = useShelterStore();

  if (activeViewMode !== 'thermal_heatmap' && activeViewMode !== 'solar_shading') {
    return null;
  }

  return (
    <div className="space-y-2 pt-1 animate-in fade-in duration-200">
      <SectionTitle
        title="Thermal & Sol-Air Legend"
        icon={<Flame className="w-3.5 h-3.5 text-rose-400" />}
      />

      <div className="bg-[#161d28] border border-[#232c3d] rounded p-2.5 space-y-2">
        <div className="flex items-center justify-between text-[10px] font-mono text-slate-300">
          <span>High Thermal Load (Sol-Air)</span>
          <span className="text-rose-400 font-bold">&gt; 42°C</span>
        </div>

        {/* Continuous Gradient Bar */}
        <div className="h-3 w-full rounded bg-gradient-to-r from-sky-500 via-amber-400 to-rose-600 border border-black/30" />

        <div className="flex items-center justify-between text-[9px] font-mono text-slate-400">
          <span>&lt; 28°C (Shaded / Cool)</span>
          <span>35°C (Ambient)</span>
          <span>45°C (Peak Beam)</span>
        </div>

        <div className="pt-1 text-[9px] text-slate-400 italic">
          * Modeled Thermal Load calculated from Sol-Air temperature flux ($T_o + \alpha \cdot GHI / h_o$).
        </div>
      </div>
    </div>
  );
};
