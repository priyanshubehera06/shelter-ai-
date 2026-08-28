import React from 'react';
import { clsx } from 'clsx';

interface MetricCardProps {
  label: string;
  value: string | number;
  subValue?: string;
  unit?: string;
  icon?: React.ReactNode;
  trend?: 'positive' | 'negative' | 'neutral' | 'solar' | 'thermal';
  className?: string;
}

export const MetricCard: React.FC<MetricCardProps> = ({
  label,
  value,
  subValue,
  unit,
  icon,
  trend = 'neutral',
  className,
}) => {
  const trendColors = {
    positive: 'border-emerald-500/30 text-emerald-400 bg-emerald-950/20',
    negative: 'border-rose-500/30 text-rose-400 bg-rose-950/20',
    neutral: 'border-surface-border text-slate-100 bg-surface/80',
    solar: 'border-amber-500/30 text-amber-400 bg-amber-950/20',
    thermal: 'border-orange-500/30 text-orange-400 bg-orange-950/20',
  };

  return (
    <div
      className={clsx(
        'rounded-xl p-4 border backdrop-blur-md transition-all duration-200 hover:border-slate-500/50 flex flex-col justify-between',
        trendColors[trend],
        className
      )}
    >
      <div className="flex items-center justify-between gap-2 mb-2">
        <span className="text-xs font-medium text-slate-400 tracking-wider uppercase">{label}</span>
        {icon && <div className="text-slate-400">{icon}</div>}
      </div>

      <div className="flex items-baseline gap-1.5">
        <span className="text-2xl font-bold font-mono tracking-tight text-white">{value}</span>
        {unit && <span className="text-xs text-slate-400 font-normal">{unit}</span>}
      </div>

      {subValue && (
        <div className="mt-2 pt-2 border-t border-white/5 text-[11px] text-slate-400 truncate">
          {subValue}
        </div>
      )}
    </div>
  );
};
