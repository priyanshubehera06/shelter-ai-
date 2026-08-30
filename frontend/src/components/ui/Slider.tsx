import React from 'react';
import { clsx } from 'clsx';
import { Minus, Plus } from 'lucide-react';

interface SliderProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  onChange: (val: number) => void;
  className?: string;
  displayFormat?: (val: number) => string;
  showSteppers?: boolean;
}

export const Slider: React.FC<SliderProps> = ({
  label,
  value,
  min,
  max,
  step = 1,
  unit = '',
  onChange,
  className,
  displayFormat,
  showSteppers = true,
}) => {
  const handleDecrement = () => {
    const next = Math.max(min, Number((value - step).toFixed(2)));
    onChange(next);
  };

  const handleIncrement = () => {
    const next = Math.min(max, Number((value + step).toFixed(2)));
    onChange(next);
  };

  return (
    <div className={clsx('flex flex-col gap-1.5', className)}>
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-slate-300 truncate">{label}</span>
        <span className="font-mono text-emerald-400 font-semibold shrink-0">
          {displayFormat ? displayFormat(value) : `${value} ${unit}`}
        </span>
      </div>

      <div className="flex items-center gap-2">
        {showSteppers && (
          <button
            type="button"
            onClick={handleDecrement}
            disabled={value <= min}
            aria-label={`Decrease ${label}`}
            className="w-7 h-7 rounded-lg bg-surface-raised border border-surface-border text-slate-300 hover:text-white hover:bg-slate-700 flex items-center justify-center shrink-0 disabled:opacity-30 disabled:pointer-events-none active:scale-95 transition"
          >
            <Minus className="w-3.5 h-3.5" />
          </button>
        )}

        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(parseFloat(e.target.value))}
          className="w-full h-2 bg-surface-raised rounded-lg appearance-none cursor-pointer accent-emerald-500 hover:accent-emerald-400 focus:outline-none touch-manipulation"
        />

        {showSteppers && (
          <button
            type="button"
            onClick={handleIncrement}
            disabled={value >= max}
            aria-label={`Increase ${label}`}
            className="w-7 h-7 rounded-lg bg-surface-raised border border-surface-border text-slate-300 hover:text-white hover:bg-slate-700 flex items-center justify-center shrink-0 disabled:opacity-30 disabled:pointer-events-none active:scale-95 transition"
          >
            <Plus className="w-3.5 h-3.5" />
          </button>
        )}
      </div>

      <div className="flex justify-between text-[10px] text-slate-400">
        <span>{displayFormat ? displayFormat(min) : `${min}${unit}`}</span>
        <span>{displayFormat ? displayFormat(max) : `${max}${unit}`}</span>
      </div>
    </div>
  );
};

