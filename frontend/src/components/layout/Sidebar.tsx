import React from 'react';
import { NavLink } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  Home,
  MapPin,
  CloudSun,
  Hammer,
  Box,
  Target,
  GitCompare,
  Award,
  ShieldCheck,
  Activity
} from 'lucide-react';

export const Sidebar: React.FC = () => {
  const navItems = [
    { path: '/', label: '01. Platform Overview', icon: <Home className="w-4 h-4" /> },
    { path: '/location', label: '02. Location Setup', icon: <MapPin className="w-4 h-4" /> },
    { path: '/climate', label: '03. Climate Intelligence', icon: <CloudSun className="w-4 h-4" /> },
    { path: '/design', label: '04. Parametric Design Lab', icon: <Hammer className="w-4 h-4" /> },
    { path: '/digital-twin', label: '05. 3D Digital Twin', icon: <Box className="w-4 h-4" /> },
    { path: '/optimization', label: '06. Pareto Optimization', icon: <Target className="w-4 h-4" /> },
    { path: '/what-if', label: '07. What-If Scenario Lab', icon: <GitCompare className="w-4 h-4" /> },
    { path: '/results', label: '08. Certified Results & XAI', icon: <Award className="w-4 h-4" /> },
  ];

  return (
    <aside className="w-64 border-r border-surface-border bg-surface flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="h-16 border-b border-surface-border px-6 flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-slate-950 font-bold shadow-lg shadow-emerald-950/50">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <span className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
              SHELTER<span className="text-emerald-400 font-mono">AI</span>
            </span>
            <p className="text-[10px] text-slate-400 tracking-wider uppercase font-mono">
              Thermal Digital Twin
            </p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          <div className="px-3 py-2 text-[10px] font-semibold tracking-wider text-slate-400 uppercase">
            Engineering Modules
          </div>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2 rounded-lg text-xs font-medium transition-all duration-200',
                  isActive
                    ? 'bg-emerald-600/15 text-emerald-400 border border-emerald-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-raised'
                )
              }
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer Meta */}
      <div className="p-4 border-t border-surface-border bg-background/50 text-[11px] text-slate-400 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span>Physics Engine: <b className="text-slate-300">Active</b></span>
        </div>
        <span className="font-mono text-[10px] text-slate-400">v1.0.0</span>
      </div>
    </aside>
  );
};
