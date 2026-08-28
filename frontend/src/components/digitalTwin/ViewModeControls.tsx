import React from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { Layers, Sun, Flame, Wind, ArrowDownUp } from 'lucide-react';

export const ViewModeControls: React.FC = () => {
  const { activeViewMode, setActiveViewMode } = useShelterStore();

  const modes: Array<{ id: 'architectural' | 'solar_shading' | 'thermal_heatmap' | 'ventilation' | 'heat_flow'; label: string; icon: any }> = [
    { id: 'architectural', label: 'Normal', icon: Layers },
    { id: 'solar_shading', label: 'Solar', icon: Sun },
    { id: 'thermal_heatmap', label: 'Thermal', icon: Flame },
    { id: 'ventilation', label: 'Ventilation', icon: Wind },
    { id: 'heat_flow', label: 'Heat Flow', icon: ArrowDownUp },
  ];

  return (
    <div className="flex items-center gap-1 bg-[#1c2433] p-1 rounded-lg border border-[#232c3d]">
      <span className="text-[9px] font-bold text-slate-400 uppercase tracking-wider px-1.5 hidden sm:inline">
        View:
      </span>
      {modes.map((m) => {
        const Icon = m.icon;
        const isActive = activeViewMode === m.id;
        return (
          <button
            key={m.id}
            onClick={() => setActiveViewMode(m.id as any)}
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-medium transition-all ${
              isActive
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-[#253043]'
            }`}
          >
            <Icon className="w-3.5 h-3.5" />
            <span>{m.label}</span>
          </button>
        );
      })}
    </div>
  );
};
