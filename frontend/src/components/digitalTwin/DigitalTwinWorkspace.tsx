import React from 'react';
import { TopControlBar } from './TopControlBar';
import { LeftSidebar } from './LeftSidebar';
import { RightSidebar } from './RightSidebar';
import { BottomControlBar } from './BottomControlBar';
import { Viewport3D } from './Viewport3D';

export const DigitalTwinWorkspace: React.FC = () => {
  return (
    <div className="flex flex-col h-full w-full bg-[#0a0d12] text-slate-100 overflow-hidden select-none">
      {/* 1. TOP HORIZONTAL ENVIRONMENTAL & SIMULATION BAR */}
      <TopControlBar />

      {/* 2. THREE-PANE MAIN WORKSPACE (LEFT - 3D VIEWPORT - RIGHT) */}
      <div className="flex flex-1 min-h-0 w-full overflow-hidden">
        {/* Left Control Sidebar */}
        <LeftSidebar />

        {/* Central Immersive 3D Digital Twin Viewport */}
        <main className="flex-1 flex flex-col min-w-0 h-full relative overflow-hidden">
          <Viewport3D />
          {/* Bottom Dock Controls */}
          <BottomControlBar />
        </main>

        {/* Right Analytics Sidebar */}
        <RightSidebar />
      </div>
    </div>
  );
};
