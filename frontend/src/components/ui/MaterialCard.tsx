import React from 'react';
import { clsx } from 'clsx';
import { Check } from 'lucide-react';
import { MaterialItem } from '../../types';

interface MaterialCardProps {
  material: MaterialItem;
  isSelected?: boolean;
  onSelect?: () => void;
  className?: string;
}

export const MaterialCard: React.FC<MaterialCardProps> = ({
  material,
  isSelected = false,
  onSelect,
  className,
}) => {
  return (
    <div
      onClick={onSelect}
      className={clsx(
        'group relative rounded-lg border p-2.5 transition-all duration-150 cursor-pointer flex flex-col justify-between overflow-hidden',
        isSelected
          ? 'bg-emerald-950/30 border-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.25)]'
          : 'bg-[#161d28] border-[#232c3d] hover:border-slate-500 hover:bg-[#1d2634]',
        className
      )}
    >
      {/* Visual Texture Swatch */}
      <div className="relative w-full h-14 rounded-md overflow-hidden mb-2 border border-black/20 flex items-center justify-center">
        <div
          className="absolute inset-0 transition-transform group-hover:scale-105"
          style={{
            backgroundColor: material.color_hex || '#7f8c8d',
            backgroundImage: `radial-gradient(circle at 30% 30%, rgba(255,255,255,0.15), transparent)`,
          }}
        />
        {isSelected && (
          <div className="absolute top-1.5 right-1.5 w-4 h-4 rounded-full bg-emerald-500 text-slate-950 flex items-center justify-center shadow-md">
            <Check className="w-3 h-3 stroke-[3]" />
          </div>
        )}
      </div>

      {/* Info */}
      <div className="space-y-1">
        <div className="font-semibold text-xs text-white truncate group-hover:text-emerald-400 transition-colors">
          {material.name}
        </div>
        <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono">
          <span>U: {material.thermal_cond_w_mk} W/mK</span>
          <span className="text-slate-500">₹{material.unit_cost_inr_m2}/m²</span>
        </div>
      </div>
    </div>
  );
};
