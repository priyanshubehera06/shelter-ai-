import React from 'react';
import { clsx } from 'clsx';

interface ShelterAILogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
}

export const ShelterAILogo: React.FC<ShelterAILogoProps> = ({
  size = 'md',
  showText = false,
  className,
}) => {
  const sizeMap = {
    sm: { icon: 28, text: 'text-sm', subtext: 'text-[9px]' },
    md: { icon: 36, text: 'text-base', subtext: 'text-[10px]' },
    lg: { icon: 48, text: 'text-xl', subtext: 'text-xs' },
    xl: { icon: 64, text: 'text-2xl', subtext: 'text-sm' },
  };

  const currentSize = sizeMap[size];

  return (
    <div className={clsx('flex items-center gap-3 select-none', className)}>
      {/* High-Tech Geometric Shelter + Neural AI Core SVG */}
      <div className="relative shrink-0 flex items-center justify-center">
        <svg
          width={currentSize.icon}
          height={currentSize.icon}
          viewBox="0 0 48 48"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="drop-shadow-[0_0_12px_rgba(16,185,129,0.35)] transition-transform hover:scale-105 duration-300"
        >
          {/* Subtle Outer Hex/Shield Circuit Boundary */}
          <path
            d="M24 3L42 12V32L24 43L6 32V12L24 3Z"
            fill="url(#shield_gradient)"
            stroke="url(#shield_stroke)"
            strokeWidth="1.2"
            strokeDasharray="2 2"
            className="opacity-40"
          />

          {/* Pitched Geometric Shelter Structure */}
          <path
            d="M24 8L39 18V38H9V18L24 8Z"
            fill="url(#shelter_roof_fill)"
            stroke="url(#shelter_outline)"
            strokeWidth="2"
            strokeLinejoin="round"
          />

          {/* Isometric Facet / Roof Ridge */}
          <path
            d="M24 8V38"
            stroke="url(#ridge_gradient)"
            strokeWidth="1.5"
            strokeDasharray="3 2"
          />

          {/* AI Neural Circuit Traces */}
          {/* Left Wing Traces */}
          <path
            d="M14 26H20M14 26L10 22M20 26L24 22"
            stroke="#10b981"
            strokeWidth="1.2"
            strokeLinecap="round"
          />
          {/* Right Wing Traces */}
          <path
            d="M34 26H28M34 26L38 22M28 26L24 22"
            stroke="#06b6d4"
            strokeWidth="1.2"
            strokeLinecap="round"
          />
          {/* Foundation Anchor Traces */}
          <path
            d="M17 38V33M31 38V33"
            stroke="#10b981"
            strokeWidth="1.5"
            strokeLinecap="round"
          />

          {/* AI Neural Interconnect Nodes (Micro Dots) */}
          <circle cx="10" cy="22" r="1.5" fill="#34d399" />
          <circle cx="14" cy="26" r="1.8" fill="#10b981" />
          <circle cx="20" cy="26" r="1.8" fill="#10b981" />
          <circle cx="28" cy="26" r="1.8" fill="#06b6d4" />
          <circle cx="34" cy="26" r="1.8" fill="#06b6d4" />
          <circle cx="38" cy="22" r="1.5" fill="#38bdf8" />
          <circle cx="24" cy="8" r="2.2" fill="#fbbf24" stroke="#78350f" strokeWidth="1" />

          {/* Radiant Central Thermal-Solar Energy Core */}
          <circle cx="24" cy="22" r="4.5" fill="url(#core_gradient)" />
          <circle cx="24" cy="22" r="2" fill="#ffffff" className="animate-pulse" />

          {/* Gradients */}
          <defs>
            <linearGradient id="shield_gradient" x1="24" y1="3" x2="24" y2="43" gradientUnits="userSpaceOnUse">
              <stop stopColor="#064e3b" stopOpacity="0.3" />
              <stop stopColor="#022c22" stopOpacity="0.05" />
            </linearGradient>

            <linearGradient id="shield_stroke" x1="6" y1="3" x2="42" y2="43" gradientUnits="userSpaceOnUse">
              <stop stopColor="#10b981" />
              <stop stopColor="#06b6d4" stopOpacity="0.3" />
            </linearGradient>

            <linearGradient id="shelter_roof_fill" x1="24" y1="8" x2="24" y2="38" gradientUnits="userSpaceOnUse">
              <stop stopColor="#062f28" />
              <stop stopColor="#0c1926" />
            </linearGradient>

            <linearGradient id="shelter_outline" x1="9" y1="8" x2="39" y2="38" gradientUnits="userSpaceOnUse">
              <stop stopColor="#34d399" />
              <stop stopColor="#06b6d4" />
            </linearGradient>

            <linearGradient id="ridge_gradient" x1="24" y1="8" x2="24" y2="38" gradientUnits="userSpaceOnUse">
              <stop stopColor="#fbbf24" />
              <stop stopColor="#10b981" />
            </linearGradient>

            <radialGradient id="core_gradient" cx="24" cy="22" r="4.5" gradientUnits="userSpaceOnUse">
              <stop stopColor="#f59e0b" />
              <stop offset="0.7" stopColor="#10b981" />
              <stop offset="1" stopColor="#047857" stopOpacity="0" />
            </radialGradient>
          </defs>
        </svg>
      </div>

      {/* Brand Title Text */}
      {showText && (
        <div className="flex flex-col">
          <div className="flex items-center gap-1.5 leading-none">
            <span className={clsx('font-black tracking-tight text-white uppercase', currentSize.text)}>
              SHELTER
            </span>
            <span className={clsx('font-mono font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400', currentSize.text)}>
              AI
            </span>
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping ml-0.5" />
          </div>
          <span className={clsx('text-slate-400 tracking-wider uppercase font-mono mt-1 font-medium', currentSize.subtext)}>
            Passive Thermal Platform
          </span>
        </div>
      )}
    </div>
  );
};
