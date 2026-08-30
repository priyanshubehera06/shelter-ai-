import React from 'react';
import { NavLink } from 'react-router-dom';
import { clsx } from 'clsx';
import {
  Home,
  CloudSun,
  Hammer,
  Box,
  Target,
  Award
} from 'lucide-react';

export const MobileBottomNav: React.FC = () => {
  const navItems = [
    { path: '/', label: 'Home', icon: <Home className="w-5 h-5" /> },
    { path: '/climate', label: 'Climate', icon: <CloudSun className="w-5 h-5" /> },
    { path: '/design', label: 'Design', icon: <Hammer className="w-5 h-5" /> },
    { path: '/simulate', label: '3D Twin', icon: <Box className="w-5 h-5" /> },
    { path: '/optimization', label: 'Optimize', icon: <Target className="w-5 h-5" /> },
    { path: '/results', label: 'Results', icon: <Award className="w-5 h-5" /> },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-surface/95 backdrop-blur-lg border-t border-surface-border bottom-nav-safe">
      <div className="flex items-center justify-around h-16 px-1">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              clsx(
                'flex flex-col items-center justify-center flex-1 min-w-0 py-1.5 px-0.5 rounded-xl transition-all duration-150',
                isActive
                  ? 'text-emerald-400 font-semibold'
                  : 'text-slate-400 hover:text-slate-200'
              )
            }
          >
            {({ isActive }) => (
              <>
                <div
                  className={clsx(
                    'p-1 rounded-lg transition-transform duration-150',
                    isActive ? 'scale-110 bg-emerald-500/15' : ''
                  )}
                >
                  {item.icon}
                </div>
                <span className="text-[10px] tracking-tight truncate mt-0.5">
                  {item.label}
                </span>
              </>
            )}
          </NavLink>
        ))}
      </div>
    </nav>
  );
};
