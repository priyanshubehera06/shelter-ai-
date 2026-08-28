import React from 'react';
import { clsx } from 'clsx';

interface MetricRowProps {
  label: string;
  value: string | number;
  unit?: string;
  icon?: React.ReactNode;
  accent?: 'green' | 'yellow' | 'orange' | 'red' | 'blue' | 'muted' | 'default';
  className?: string;
}

export const MetricRow: React.FC<MetricRowProps> = ({
  label,
  value,
  unit,
  icon,
  accent = 'default',
  className,
}) => {
  const accentColors = {
    green: 'text-emerald-400',
    yellow: 'text-amber-400',
    orange: 'text-orange-400',
    red: 'text-rose-400',
    blue: 'text-sky-400',
    muted: 'text-slate-400',
    default: 'text-slate-200',
  };

  return (
    <div
      className={clsx(
        'flex items-center justify-between py-1.5 border-b border-[#232c3d]/60 last:border-0 text-xs font-mono',
        className
      )}
    >
      <div className="flex items-center gap-2 text-slate-400 font-sans text-[11px] truncate">
        {icon && <span className="text-slate-400 shrink-0">{icon}</span>}
        <span className="truncate">{label}</span>
      </div>
      <div className="flex items-baseline gap-1 shrink-0 ml-2 font-semibold">
        <span className={clsx('tracking-tight', accentColors[accent])}>{value}</span>
        {unit && <span className="text-[10px] text-slate-500 font-normal">{unit}</span>}
      </div>
    </div>
  );
};
