import React from 'react';
import { SectionTitle } from '../ui/SectionTitle';
import { MetricRow } from '../ui/MetricRow';
import { DigitalTwinConfigResponse } from '../../types';
import { CloudSun, Thermometer, Sun, Wind, Compass, Droplets } from 'lucide-react';

interface ClimateConditionsProps {
  telemetry?: DigitalTwinConfigResponse | null;
}

export const ClimateConditions: React.FC<ClimateConditionsProps> = ({ telemetry }) => {
  const amb = telemetry?.ambient || {
    temperature_c: 36.4,
    humidity_pct: 58,
    wind_speed_m_s: 2.8,
    wind_dir_deg: 220,
  };

  const solarGhi = telemetry?.solar?.solar_ghi_w_m2 || 820;

  const getWindDirectionLabel = (deg: number) => {
    if (deg >= 337.5 || deg < 22.5) return `${deg}° (N)`;
    if (deg >= 22.5 && deg < 67.5) return `${deg}° (NE)`;
    if (deg >= 67.5 && deg < 112.5) return `${deg}° (E)`;
    if (deg >= 112.5 && deg < 157.5) return `${deg}° (SE)`;
    if (deg >= 157.5 && deg < 202.5) return `${deg}° (S)`;
    if (deg >= 202.5 && deg < 247.5) return `${deg}° (SW)`;
    if (deg >= 247.5 && deg < 292.5) return `${deg}° (W)`;
    return `${deg}° (NW)`;
  };

  return (
    <div className="space-y-2.5">
      <SectionTitle
        title="Climate Conditions"
        subtitle="Local Station Telemetry"
        icon={<CloudSun className="w-3.5 h-3.5 text-sky-400" />}
      />

      <div className="bg-[#161d28] border border-[#232c3d] rounded p-2.5 space-y-0.5">
        <MetricRow
          label="Outdoor Temperature"
          value={amb.temperature_c.toFixed(1)}
          unit="°C"
          icon={<Thermometer className="w-3 h-3 text-rose-400" />}
          accent="red"
        />
        <MetricRow
          label="Solar Radiation (GHI)"
          value={solarGhi.toFixed(0)}
          unit="W/m²"
          icon={<Sun className="w-3 h-3 text-amber-400" />}
          accent="yellow"
        />
        <MetricRow
          label="Wind Velocity"
          value={amb.wind_speed_m_s.toFixed(1)}
          unit="m/s"
          icon={<Wind className="w-3 h-3 text-sky-400" />}
          accent="blue"
        />
        <MetricRow
          label="Wind Direction"
          value={getWindDirectionLabel(amb.wind_dir_deg)}
          icon={<Compass className="w-3 h-3 text-slate-400" />}
        />
        <MetricRow
          label="Relative Humidity"
          value={amb.humidity_pct.toFixed(0)}
          unit="%"
          icon={<Droplets className="w-3 h-3 text-sky-400" />}
          accent="blue"
        />
      </div>
    </div>
  );
};
