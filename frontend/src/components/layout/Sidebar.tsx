import React from 'react';
import { NavLink } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  Home,
  CloudSun,
  Hammer,
  Layers,
  Activity,
  GitCompare,
  Target,
  Award,
  ShieldCheck,
  Zap,
  Box
} from 'lucide-react';

interface SidebarProps {
  mobileOpen?: boolean;
  onCloseMobile?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ mobileOpen, onCloseMobile }) => {
  const navItems = [
    { path: '/', label: '01. Home', icon: <Home className="w-4 h-4" /> },
    { path: '/climate', label: '02. Climate & Solar', icon: <CloudSun className="w-4 h-4 text-sky-400" /> },
    { path: '/design', label: '03. Shelter Design', icon: <Hammer className="w-4 h-4 text-amber-400" /> },
    { path: '/materials', label: '04. Materials & Layers', icon: <Layers className="w-4 h-4 text-purple-400" /> },
    { path: '/simulate', label: '05. 3D Simulation & Twin', icon: <Box className="w-4 h-4 text-emerald-400" /> },
    { path: '/compare', label: '06. Compare Designs', icon: <GitCompare className="w-4 h-4 text-indigo-400" /> },
    { path: '/optimization', label: '07. Pareto Optimization', icon: <Target className="w-4 h-4 text-rose-400" /> },
    { path: '/results', label: '08. Results & Report', icon: <Award className="w-4 h-4 text-teal-400" /> },
  ];

  const sidebarContent = (
    <aside className={clsx(
      "w-64 border-r border-surface-border bg-surface flex flex-col justify-between shrink-0 h-screen",
      mobileOpen ? "flex" : "hidden md:flex sticky top-0"
    )}>
      <div className="overflow-y-auto">
        {/* Brand Header */}
        <div className="h-16 border-b border-surface-border px-5 flex items-center justify-between sticky top-0 bg-surface z-10">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center text-slate-950 font-bold shadow-lg shadow-emerald-950/50 shrink-0">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <span className="font-bold text-base tracking-tight text-white flex items-center gap-1.5">
                SHELTER<span className="text-emerald-400 font-mono">AI</span>
              </span>
              <p className="text-[10px] text-slate-400 tracking-wider uppercase font-mono">
                Passive Thermal Design
              </p>
            </div>
          </div>
          {onCloseMobile && (
            <button
              onClick={onCloseMobile}
              className="md:hidden p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-surface-raised"
            >
              ✕
            </button>
          )}
        </div>

        {/* Navigation Links */}
        <nav className="p-3 space-y-1">
          <div className="px-3 py-1.5 text-[10px] font-semibold tracking-wider text-slate-400 uppercase font-mono">
            Engineering Workflow
          </div>
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onCloseMobile}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-200 min-h-[44px]',
                  isActive
                    ? 'bg-emerald-600/15 text-emerald-400 border border-emerald-500/30 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-surface-raised'
                )
              }
            >
              {item.icon}
              <span className="truncate">{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </div>

      {/* Footer Meta */}
      <div className="p-4 border-t border-surface-border bg-background/50 text-[11px] text-slate-400 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-2">
          <Activity className="w-3.5 h-3.5 text-emerald-400 animate-pulse" />
          <span>Physics Engine: <b className="text-slate-300">Active</b></span>
        </div>
        <span className="font-mono text-[10px] text-slate-400">Ladakh Focus</span>
      </div>
    </aside>
  );

  if (mobileOpen) {
    return (
      <div className="fixed inset-0 z-50 md:hidden flex">
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={onCloseMobile} />
        <div className="relative z-10">
          {sidebarContent}
        </div>
      </div>
    );
  }

  return sidebarContent;
};

