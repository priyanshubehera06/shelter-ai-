import React from 'react';
import { clsx } from 'clsx';

interface SectionTitleProps {
  title: string;
  subtitle?: string;
  badge?: React.ReactNode;
  action?: React.ReactNode;
  icon?: React.ReactNode;
  className?: string;
}

export const SectionTitle: React.FC<SectionTitleProps> = ({
  title,
  subtitle,
  badge,
  action,
  icon,
  className,
}) => {
  return (
    <div className={clsx('flex items-center justify-between gap-2 pb-2 mb-2.5 border-b border-[#232c3d]', className)}>
      <div className="flex items-center gap-1.5 truncate">
        {icon && <span className="text-emerald-400 shrink-0">{icon}</span>}
        <span className="text-[11px] font-bold tracking-wider text-slate-300 uppercase truncate">
          {title}
        </span>
        {subtitle && <span className="text-[10px] text-slate-500 font-normal truncate">({subtitle})</span>}
      </div>
      <div className="flex items-center gap-1.5 shrink-0">
        {badge}
        {action}
      </div>
    </div>
  );
};
