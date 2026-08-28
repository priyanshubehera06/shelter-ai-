import React, { useEffect, useState } from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { fetchDigitalTwinConfig } from '../../api/endpoints';
import { ClimateConditions } from './ClimateConditions';
import { PerformancePanel } from './PerformancePanel';
import { ThermalLegend } from './ThermalLegend';
import { DigitalTwinConfigResponse } from '../../types';

export const RightSidebar: React.FC = () => {
  const { currentDesign, selectedLocationId, selectedMonth, simHour, activeViewMode } = useShelterStore();
  const [telemetry, setTelemetry] = useState<DigitalTwinConfigResponse | null>(null);

  useEffect(() => {
    fetchDigitalTwinConfig({
      geometry: currentDesign.geometry,
      materials: currentDesign.materials,
      hour_of_day: simHour,
      location_id: selectedLocationId,
      month: selectedMonth,
      view_mode: activeViewMode,
    })
      .then((data) => setTelemetry(data))
      .catch((err) => console.error('Failed to fetch digital twin telemetry:', err));
  }, [currentDesign, simHour, selectedLocationId, selectedMonth, activeViewMode]);

  return (
    <aside className="w-[280px] bg-[#11161f] border-l border-[#232c3d] p-3 flex flex-col space-y-4 overflow-y-auto shrink-0 z-20 shadow-lg">
      {/* 1. CLIMATE CONDITIONS */}
      <ClimateConditions telemetry={telemetry} />

      {/* 2. PERFORMANCE METRICS */}
      <PerformancePanel />

      {/* 3. THERMAL LEGEND */}
      <ThermalLegend />
    </aside>
  );
};
