import React from 'react';
import { clsx } from 'clsx';

interface IconButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  icon: React.ReactNode;
  label?: string;
  isActive?: boolean;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'primary' | 'danger' | 'ghost';
}

export const IconButton: React.FC<IconButtonProps> = ({
  icon,
  label,
  isActive = false,
  size = 'md',
  variant = 'default',
  className,
  ...props
}) => {
  const sizeStyles = {
    sm: 'p-1.5 text-xs',
    md: 'p-2 text-sm',
    lg: 'p-2.5 text-base',
  };

  const variantStyles = {
    default: isActive
      ? 'bg-emerald-600 text-white border-emerald-500 shadow-sm'
      : 'bg-[#1c2433] text-slate-300 hover:text-white hover:bg-[#253043] border-[#232c3d]',
    primary: 'bg-emerald-600 hover:bg-emerald-500 text-white border-emerald-500',
    danger: 'bg-rose-600 hover:bg-rose-500 text-white border-rose-500',
    ghost: 'text-slate-400 hover:text-white hover:bg-[#1c2433] border-transparent',
  };

  return (
    <button
      title={label}
      aria-label={label}
      className={clsx(
        'inline-flex items-center justify-center rounded-lg border transition-all duration-150 focus:outline-none focus:ring-1 focus:ring-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed',
        sizeStyles[size],
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {icon}
    </button>
  );
};
