import React from 'react';
import { clsx } from 'clsx';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
}

export const Card: React.FC<CardProps> = ({ children, className, hoverable = false, ...props }) => {
  return (
    <div
      className={clsx(
        'glass-panel rounded-xl p-5 border border-surface-border text-slate-100 shadow-lg',
        hoverable && 'glass-panel-hover cursor-pointer',
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
