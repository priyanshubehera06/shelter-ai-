import React from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { Eye } from 'lucide-react';

export const ComponentVisibility: React.FC = () => {
  const { componentVisibility, toggleComponentVisibility } = useShelterStore();

  const toggles = [
    { key: 'roof', label: 'Roof' },
    { key: 'walls', label: 'Walls' },
    { key: 'windows', label: 'Windows' },
    { key: 'shading', label: 'Shading' },
  ];

  return (
    <div className="hidden xl:flex items-center gap-2 bg-[#1c2433] px-2.5 py-1 rounded-lg border border-[#232c3d] text-xs">
      <Eye className="w-3.5 h-3.5 text-slate-400" />
      {toggles.map((item) => (
        <label
          key={item.key}
          className="flex items-center gap-1 text-[11px] text-slate-300 hover:text-white cursor-pointer select-none"
        >
          <input
            type="checkbox"
            checked={(componentVisibility as any)[item.key]}
            onChange={() => toggleComponentVisibility(item.key as any)}
            className="w-3 h-3 rounded bg-[#11161f] border-[#232c3d] text-emerald-500 focus:ring-0"
          />
          <span>{item.label}</span>
        </label>
      ))}
    </div>
  );
};
