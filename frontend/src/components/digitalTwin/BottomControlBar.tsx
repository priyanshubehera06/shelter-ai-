import React from 'react';
import { ViewModeControls } from './ViewModeControls';
import { CameraControls } from './CameraControls';
import { ComponentVisibility } from './ComponentVisibility';

export const BottomControlBar: React.FC = () => {
  return (
    <footer className="h-12 bg-[#11161f] border-t border-[#232c3d] px-4 flex items-center justify-between gap-3 text-xs shrink-0 z-30 shadow-md">
      {/* 1. VIEW MODES */}
      <ViewModeControls />

      {/* 2. COMPONENT VISIBILITY */}
      <ComponentVisibility />

      {/* 3. CAMERA VIEW PRESETS */}
      <CameraControls />
    </footer>
  );
};
