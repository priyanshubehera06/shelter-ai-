import React from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { SectionTitle } from '../ui/SectionTitle';
import { MetricRow } from '../ui/MetricRow';
import { Activity, Zap, ShieldCheck } from 'lucide-react';

export const PerformancePanel: React.FC = () => {
  const { simulationResult, isSimulating } = useShelterStore();

  return (
    <div className="space-y-2.5">
      <SectionTitle
        title="Performance Metrics"
        subtitle="Physics RC Model"
        icon={<Activity className="w-3.5 h-3.5 text-emerald-400" />}
      />

      {isSimulating ? (
        <div className="bg-[#161d28] border border-[#232c3d] rounded p-6 text-center space-y-2">
          <div className="animate-spin w-5 h-5 border-2 border-emerald-500 border-t-transparent rounded-full mx-auto" />
          <span className="text-xs text-slate-400 block">Simulating transient heat transfer...</span>
        </div>
      ) : simulationResult ? (
        <div className="bg-[#161d28] border border-[#232c3d] rounded p-2.5 space-y-0.5 animate-in fade-in duration-200">
          <MetricRow
            label="Comfort Compliance (PMV)"
            value={simulationResult.summary.comfort_score}
            unit="%"
            accent={simulationResult.summary.comfort_score >= 75 ? 'green' : 'yellow'}
          />
          <MetricRow
            label="Peak Indoor Temperature"
            value={simulationResult.summary.peak_indoor_temp_c.toFixed(1)}
            unit="°C"
            accent="red"
          />
          <MetricRow
            label="Average Indoor Temp"
            value={simulationResult.summary.avg_indoor_temp_c.toFixed(1)}
            unit="°C"
          />
          <MetricRow
            label="Annual Operational HVAC"
            value={simulationResult.summary.total_annual_energy_kwh.toLocaleString()}
            unit="kWh/yr"
            accent="orange"
          />
          <MetricRow
            label="Estimated CapEx Outlay"
            value={`₹${(simulationResult.summary.total_capex_cost_inr / 100000).toFixed(2)} Lakh`}
            accent="default"
          />
          <MetricRow
            label="Resilience Factor Score"
            value={`${simulationResult.summary.resilience_score} / 100`}
            accent="green"
          />
        </div>
      ) : (
        <div className="bg-[#161d28] border border-[#232c3d] rounded p-4 text-center space-y-2">
          <Zap className="w-6 h-6 text-slate-500 mx-auto" />
          <p className="text-xs text-slate-400 leading-relaxed">
            Click <b>"Calculate Physics"</b> in top bar to compute transient thermal performance.
          </p>
        </div>
      )}
    </div>
  );
};
