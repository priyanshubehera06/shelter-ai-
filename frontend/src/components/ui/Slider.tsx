import React from 'react';
import { clsx } from 'clsx';

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
}) => {
  return (
    <div className={clsx('flex flex-col gap-1.5', className)}>
      <div className="flex items-center justify-between text-xs">
        <span className="font-medium text-slate-300">{label}</span>
        <span className="font-mono text-emerald-400 font-semibold">
          {displayFormat ? displayFormat(value) : `${value} ${unit}`}
        </span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="w-full h-1.5 bg-surface-raised rounded-lg appearance-none cursor-pointer accent-emerald-500 hover:accent-emerald-400 focus:outline-none"
      />
      <div className="flex justify-between text-[10px] text-slate-400">
        <span>{displayFormat ? displayFormat(min) : `${min}${unit}`}</span>
        <span>{displayFormat ? displayFormat(max) : `${max}${unit}`}</span>
      </div>
    </div>
  );
};
