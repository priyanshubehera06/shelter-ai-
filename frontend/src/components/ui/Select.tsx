import React from 'react';
import { clsx } from 'clsx';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: SelectOption[];
  className?: string;
}

export const Select: React.FC<SelectProps> = ({ label, options, className, ...props }) => {
  return (
    <div className="flex flex-col gap-1.5 w-full">
      {label && <label className="text-xs font-medium text-slate-300">{label}</label>}
      <select
        className={clsx(
          'w-full bg-surface-raised border border-surface-border rounded-lg px-3 py-2 text-sm text-slate-100 focus:outline-none focus:ring-2 focus:ring-emerald-500/50 focus:border-emerald-500 transition-all cursor-pointer',
          className
        )}
        {...props}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value} className="bg-surface text-slate-100">
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
};
