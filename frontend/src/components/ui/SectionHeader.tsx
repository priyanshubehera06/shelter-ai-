import React from 'react';

interface SectionHeaderProps {
  badge?: string;
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
}

export const SectionHeader: React.FC<SectionHeaderProps> = ({ badge, title, subtitle, icon, action }) => {
  return (
    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6 pb-4 border-b border-surface-border">
      <div className="flex items-start sm:items-center gap-3">
        {icon && (
          <div className="p-2.5 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 shrink-0 mt-0.5 sm:mt-0">
            {icon}
          </div>
        )}
        <div className="space-y-1">
          {badge && (
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded-md text-[10px] font-mono uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-bold inline-block">
                {badge}
              </span>
            </div>
          )}
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-white">{title}</h1>
          {subtitle && <p className="text-xs sm:text-sm text-slate-400 mt-0.5">{subtitle}</p>}
        </div>
      </div>
      {action && <div className="flex flex-wrap items-center gap-2 shrink-0 w-full sm:w-auto">{action}</div>}
    </div>
  );
};
