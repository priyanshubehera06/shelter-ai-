import React from 'react';
import { clsx } from 'clsx';

interface PanelProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  highlighted?: boolean;
}

export const Panel: React.FC<PanelProps> = ({
  children,
  className,
  hoverable = false,
  highlighted = false,
  ...props
}) => {
  return (
    <div
      className={clsx(
        'bg-[#11161f] border border-[#232c3d] rounded-lg p-3.5 text-slate-100 shadow-md',
        hoverable && 'hover:bg-[#171e2a] hover:border-[#334155] transition-all cursor-pointer',
        highlighted && 'border-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.2)]',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
