import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useShelterStore } from '../store/shelterStore';
import { fetchClimateAnalysis } from '../api/endpoints';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { SectionHeader } from '../components/ui/SectionHeader';
import { ClimateAnalysisResponse } from '../types';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import {
  CloudSun,
  Thermometer,
  Sun,
  Wind,
  AlertTriangle,
  Flame,
  Snowflake,
  Lightbulb,
  ArrowRight
} from 'lucide-react';

export const ClimateIntelligencePage: React.FC = () => {
  const navigate = useNavigate();
  const { selectedLocationId, selectedMonth } = useShelterStore();
  const [analysis, setAnalysis] = useState<ClimateAnalysisResponse | null>(null);

  useEffect(() => {
    fetchClimateAnalysis(selectedLocationId, selectedMonth)
      .then((data) => setAnalysis(data))
      .catch((err) => console.error('Error in climate intelligence:', err));
  }, [selectedLocationId, selectedMonth]);

  const chartData = (analysis?.hourly_records_24h || []).map((r) => ({
    hour: `${String(r.hour).padStart(2, '0')}:00`,
    temperature: r.dry_bulb_temp_c,
    solar: r.solar_ghi_w_m2,
    humidity: r.relative_humidity_pct,
    wind: r.wind_speed_m_s,
  }));

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300">
      <SectionHeader
        title="03. Climate Intelligence & Diagnostics"
        subtitle="Diurnal temperature trends, solar irradiation profiles, extreme heat stress risks, and actionable architectural rules"
        icon={<CloudSun className="w-5 h-5 text-sky-400" />}
        action={
          <Button
            variant="primary"
            icon={<ArrowRight className="w-4 h-4" />}
            onClick={() => navigate('/design')}
          >
            Open Parametric Design Lab
          </Button>
        }
      />

      {/* Metrics Row */}
      {analysis && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
          <MetricCard
            label="Annual Mean Temp"
            value={analysis.summary.annual_mean_temp}
            unit="°C"
            icon={<Thermometer className="w-4 h-4 text-emerald-400" />}
          />
          <MetricCard
            label="Peak Extreme Temp"
            value={analysis.summary.peak_summer_temp}
            unit="°C"
            icon={<Flame className="w-4 h-4 text-rose-400" />}
            trend="negative"
          />
          <MetricCard
            label="Min Winter Temp"
            value={analysis.summary.min_winter_temp}
            unit="°C"
            icon={<Snowflake className="w-4 h-4 text-sky-400" />}
            trend="positive"
          />
          <MetricCard
            label="Hot Hours (>35°C)"
            value={analysis.summary.hot_hours_count}
            unit="hrs/yr"
            icon={<AlertTriangle className="w-4 h-4 text-amber-400" />}
            trend="solar"
          />
          <MetricCard
            label="Peak Solar Hours"
            value={analysis.summary.high_solar_hours_count}
            unit="hrs/yr"
            icon={<Sun className="w-4 h-4 text-amber-400" />}
            trend="solar"
          />
        </div>
      )}

      {/* Interactive Trajectory Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Temperature Diurnal Trajectory */}
        <Card className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Thermometer className="w-4 h-4 text-rose-400" />
              24-Hour Diurnal Temperature Profile (°C)
            </h3>
            <Badge variant="rose" size="sm">
              Diurnal Swing: {analysis?.summary.diurnal_range_c}°C
            </Badge>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis dataKey="hour" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#161b22', borderColor: '#30363d', borderRadius: '8px' }}
                />
                <Line
                  type="monotone"
                  dataKey="temperature"
                  name="Ambient Temp (°C)"
                  stroke="#ef4444"
                  strokeWidth={2.5}
                  dot={{ r: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </Card>

        {/* Solar Radiation Profile */}
        <Card className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sun className="w-4 h-4 text-amber-400" />
              Hourly Solar Radiation GHI (W/m²)
            </h3>
            <Badge variant="amber" size="sm">
              Peak: {analysis?.summary.peak_solar_ghi} W/m²
            </Badge>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="solarGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8} />
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                <XAxis dataKey="hour" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#161b22', borderColor: '#30363d', borderRadius: '8px' }}
                />
                <Area
                  type="monotone"
                  dataKey="solar"
                  name="Solar GHI (W/m²)"
                  stroke="#f59e0b"
                  fillOpacity={1}
                  fill="url(#solarGrad)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </Card>
      </div>

      {/* Actionable Passive Architectural Heuristics */}
      <Card className="space-y-3">
        <h3 className="text-sm font-bold text-white flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-emerald-400" />
          Actionable Passive Design Heuristics for Active Climate Zone
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
          {analysis?.summary.actionable_insights.map((insight, idx) => (
            <div
              key={idx}
              className="p-4 rounded-xl bg-surface-raised border border-surface-border text-xs text-slate-300 leading-relaxed flex flex-col justify-between"
            >
              <p>{insight}</p>
              <div className="mt-3 text-[10px] font-semibold text-emerald-400 uppercase tracking-wider">
                Recommended Action
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};
