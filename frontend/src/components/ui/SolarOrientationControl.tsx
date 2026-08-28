import React from 'react';
import { Compass, Sun } from 'lucide-react';
import { clsx } from 'clsx';

interface SolarOrientationControlProps {
  value: number;
  onChange: (value: number) => void;
  className?: string;
}

export function getAzimuthCardinal(deg: number): { name: string; fullLabel: string; isOptimal: boolean } {
  const norm = ((deg % 360) + 360) % 360;
  if (norm >= 337.5 || norm < 22.5) return { name: 'North (N)', fullLabel: 'North', isOptimal: false };
  if (norm >= 22.5 && norm < 67.5) return { name: 'North-East (NE)', fullLabel: 'North-East', isOptimal: false };
  if (norm >= 67.5 && norm < 112.5) return { name: 'East (E)', fullLabel: 'East', isOptimal: false };
  if (norm >= 112.5 && norm < 157.5) return { name: 'South-East (SE)', fullLabel: 'South-East (High Morning Solar)', isOptimal: false };
  if (norm >= 157.5 && norm < 202.5) return { name: 'True South (S)', fullLabel: 'True South (Optimal Winter Solar Capture)', isOptimal: true };
  if (norm >= 202.5 && norm < 247.5) return { name: 'South-West (SW)', fullLabel: 'South-West (High Afternoon Solar)', isOptimal: false };
  if (norm >= 247.5 && norm < 292.5) return { name: 'West (W)', fullLabel: 'West', isOptimal: false };
  return { name: 'North-West (NW)', fullLabel: 'North-West', isOptimal: false };
}

export const SolarOrientationControl: React.FC<SolarOrientationControlProps> = ({
  value,
  onChange,
  className,
}) => {
  const cardinal = getAzimuthCardinal(value);

  const presets = [
    { label: '0° N', deg: 0 },
    { label: '90° E', deg: 90 },
    { label: '180° S (Optimal)', deg: 180, isOptimal: true },
    { label: '270° W', deg: 270 },
  ];

  return (
    <div className={clsx('p-3.5 rounded-xl bg-surface-raised border border-surface-border space-y-3', className)}>
      {/* Header Info */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-xs font-bold text-white flex items-center gap-1.5">
          <Compass className="w-4 h-4 text-amber-400" />
          <span>Solar Orientation Azimuth</span>
        </span>

        <div className="flex items-center gap-2">
          {cardinal.isOptimal && (
            <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
              <Sun className="w-3 h-3 text-amber-400 animate-pulse" />
              Optimal Solar
            </span>
          )}
          <span className="px-2.5 py-0.5 rounded-md font-mono text-xs font-bold bg-background text-amber-400 border border-surface-border">
            {value}° • {cardinal.name}
          </span>
        </div>
      </div>

      {/* Main Slider Track */}
      <div className="space-y-1.5">
        <input
          type="range"
          min={0}
          max={360}
          step={5}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400 hover:accent-amber-300 focus:outline-none"
        />

        {/* Cardinal Ticks */}
        <div className="flex justify-between text-[10px] font-mono text-slate-400 px-0.5">
          <span className={value === 0 || value === 360 ? 'text-white font-bold' : ''}>0° N</span>
          <span className={value === 90 ? 'text-white font-bold' : ''}>90° E</span>
          <span className={value === 180 ? 'text-emerald-400 font-bold' : 'text-amber-400 font-semibold'}>180° S (Optimal)</span>
          <span className={value === 270 ? 'text-white font-bold' : ''}>270° W</span>
          <span className={value === 360 ? 'text-white font-bold' : ''}>360°</span>
        </div>
      </div>

      {/* Quick Snap Preset Buttons */}
      <div className="grid grid-cols-4 gap-1.5 pt-1">
        {presets.map((p) => {
          const isSelected = Math.abs(value - p.deg) < 2.5 || (p.deg === 0 && Math.abs(value - 360) < 2.5);
          return (
            <button
              key={p.deg}
              type="button"
              onClick={() => onChange(p.deg)}
              className={clsx(
                'py-1 px-1.5 rounded-lg text-[11px] font-medium font-mono text-center transition-all truncate',
                isSelected
                  ? p.isOptimal
                    ? 'bg-emerald-600 text-white font-bold shadow-sm shadow-emerald-900/50'
                    : 'bg-amber-500 text-slate-950 font-bold'
                  : p.isOptimal
                  ? 'bg-surface border border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10'
                  : 'bg-surface border border-surface-border text-slate-400 hover:text-slate-200 hover:bg-surface-raised'
              )}
            >
              {p.label}
            </button>
          );
        })}
      </div>

      {/* Subtext description */}
      <p className="text-[10px] text-slate-400 leading-tight">
        {cardinal.fullLabel}. In Ladakh (34°N), south-facing fenestrations (180°) maximize direct winter solar heat capture into the thermal mass.
      </p>
    </div>
  );
};
