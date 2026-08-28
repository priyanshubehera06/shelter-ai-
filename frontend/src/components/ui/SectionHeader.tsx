import React from 'react';

interface SectionHeaderProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({ title, subtitle, icon, action }) => {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6 pb-4 border-b border-surface-border">
      <div className="flex items-center gap-3">
        {icon && (
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
            {icon}
          </div>
        )}
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">{title}</h1>
          {subtitle && <p className="text-xs sm:text-sm text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
      </div>
      {action && <div className="flex items-center gap-2">{action}</div>}
    </div>
  );
};
