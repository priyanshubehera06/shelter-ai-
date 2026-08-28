import React, { useEffect, useState } from 'react';
import { useShelterStore } from '../store/shelterStore';
import { fetchMaterials, runWhatIfComparison } from '../api/endpoints';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { Select } from '../components/ui/Select';
import { Slider } from '../components/ui/Slider';
import { SectionHeader } from '../components/ui/SectionHeader';
import { MaterialItem, MaterialSelection, WhatIfCompareResponse } from '../types';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import {
  GitCompare,
  ArrowDownRight,
  Clock,
  Sparkles,
  Layers,
  Thermometer
} from 'lucide-react';

export const WhatIfLabPage: React.FC = () => {
  const { currentDesign, selectedLocationId, selectedMonth } = useShelterStore();
  const [materials, setMaterials] = useState<MaterialItem[]>([]);
  const [comparison, setComparison] = useState<WhatIfCompareResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Baseline Scenario State
  const [baselineMat, setBaselineMat] = useState<MaterialSelection>({
    wall_mat_id: 'brick_standard',
    wall_thickness_cm: 20.0,
    roof_mat_id: 'roof_cgi_sheet',
    insulation_mat_id: null,
    insulation_thickness_cm: 0.0,
    glazing_mat_id: 'glazing_single',
  });

  // Modified Scenario State
  const [modifiedMat, setModifiedMat] = useState<MaterialSelection>({
    wall_mat_id: 'cseb_interlocking',
    wall_thickness_cm: 20.0,
    roof_mat_id: 'roof_cgi_insulated',
    insulation_mat_id: 'insulation_rockwool',
    insulation_thickness_cm: 5.0,
    glazing_mat_id: 'glazing_single',
  });

  useEffect(() => {
    fetchMaterials().then((data) => setMaterials(data));
  }, []);

  const handleCompare = async () => {
    setIsLoading(true);
    try {
      const res = await runWhatIfComparison({
        location_id: selectedLocationId,
        month: selectedMonth,
        geometry: currentDesign.geometry,
        baseline_materials: baselineMat,
        modified_materials: modifiedMat,
        occupants: currentDesign.occupants,
      });
      setComparison(res);
    } catch (e) {
      console.error('What-If error:', e);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    handleCompare();
  }, [baselineMat, modifiedMat, selectedLocationId, selectedMonth]);

  const wallMaterials = materials.filter((m) => m.category === 'Wall');
  const roofMaterials = materials.filter((m) => m.category === 'Roof');
  const insMaterials = materials.filter((m) => m.category === 'Insulation');

  const chartData = (comparison?.baseline_hourly || []).map((b, idx) => ({
    hour: `${String(b.hour).padStart(2, '0')}:00`,
    baseline: b.t_indoor,
    modified: comparison?.modified_hourly[idx]?.t_indoor || b.t_indoor,
    ambient: b.t_outdoor,
  }));

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300">
      <SectionHeader
        badge="06. COMPARATIVE THERMAL DESIGN"
        title="Comparative Thermal Design Studio"
        subtitle="Compare baseline shelter assemblies against retrofitted or optimized passive configurations in real-time"
        icon={<GitCompare className="w-5 h-5 text-amber-400" />}
      />

      {/* Side-by-Side Scenario Configuration */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Baseline Scenario */}
        <Card className="space-y-4 border-rose-500/30">
          <div className="flex items-center justify-between border-b border-surface-border pb-2">
            <h3 className="text-sm font-bold text-rose-400 flex items-center gap-2">
              <Layers className="w-4 h-4" />
              🔴 Baseline Design Assembly
            </h3>
          </div>

          <Select
            label="Baseline Wall Material"
            options={wallMaterials.map((m) => ({ value: m.id, label: m.name }))}
            value={baselineMat.wall_mat_id}
            onChange={(e) => setBaselineMat({ ...baselineMat, wall_mat_id: e.target.value })}
          />

          <Select
            label="Baseline Roofing System"
            options={roofMaterials.map((m) => ({ value: m.id, label: m.name }))}
            value={baselineMat.roof_mat_id}
            onChange={(e) => setBaselineMat({ ...baselineMat, roof_mat_id: e.target.value })}
          />

          <Select
            label="Baseline Insulation"
            options={[
              { value: '', label: 'None (Uninsulated)' },
              ...insMaterials.map((m) => ({ value: m.id, label: m.name })),
            ]}
            value={baselineMat.insulation_mat_id || ''}
            onChange={(e) =>
              setBaselineMat({
                ...baselineMat,
                insulation_mat_id: e.target.value || null,
                insulation_thickness_cm: e.target.value ? 5.0 : 0.0,
              })
            }
          />
        </Card>

        {/* Modified Scenario */}
        <Card className="space-y-4 border-emerald-500/30">
          <div className="flex items-center justify-between border-b border-surface-border pb-2">
            <h3 className="text-sm font-bold text-emerald-400 flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              🟢 Modified / Retrofit Scenario
            </h3>
          </div>

          <Select
            label="Modified Wall Material"
            options={wallMaterials.map((m) => ({ value: m.id, label: m.name }))}
            value={modifiedMat.wall_mat_id}
            onChange={(e) => setModifiedMat({ ...modifiedMat, wall_mat_id: e.target.value })}
          />

          <Select
            label="Modified Roofing System"
            options={roofMaterials.map((m) => ({ value: m.id, label: m.name }))}
            value={modifiedMat.roof_mat_id}
            onChange={(e) => setModifiedMat({ ...modifiedMat, roof_mat_id: e.target.value })}
          />

          <div className="grid grid-cols-2 gap-3">
            <Select
              label="Modified Insulation"
              options={[
                { value: '', label: 'None' },
                ...insMaterials.map((m) => ({ value: m.id, label: m.name })),
              ]}
              value={modifiedMat.insulation_mat_id || ''}
              onChange={(e) =>
                setModifiedMat({
                  ...modifiedMat,
                  insulation_mat_id: e.target.value || null,
                  insulation_thickness_cm: e.target.value ? 5.0 : 0.0,
                })
              }
            />
            {modifiedMat.insulation_mat_id && (
              <Slider
                label="Insulation (cm)"
                value={modifiedMat.insulation_thickness_cm}
                min={1.0}
                max={12.0}
                step={0.5}
                onChange={(val) => setModifiedMat({ ...modifiedMat, insulation_thickness_cm: val })}
              />
            )}
          </div>
        </Card>
      </div>

      {/* Comparison Metrics HUD */}
      {comparison && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <MetricCard
              label="Peak Temp Reduction"
              value={`${comparison.peak_temperature_drop_c > 0 ? '-' : '+'}${Math.abs(comparison.peak_temperature_drop_c)}`}
              unit="°C"
              icon={<ArrowDownRight className="w-4 h-4 text-emerald-400" />}
              trend="positive"
            />
            <MetricCard
              label="Average Temp Reduction"
              value={`${comparison.avg_temperature_drop_c > 0 ? '-' : '+'}${Math.abs(comparison.avg_temperature_drop_c)}`}
              unit="°C"
              icon={<Thermometer className="w-4 h-4 text-emerald-400" />}
              trend="positive"
            />
            <MetricCard
              label="Avoided Discomfort Hours"
              value={Math.max(0, comparison.discomfort_hours_reduced)}
              unit="hrs/day"
              icon={<Clock className="w-4 h-4 text-emerald-400" />}
              trend="positive"
            />
          </div>

          <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 text-xs text-emerald-300">
            💡 <b>Sensitivity Summary:</b> {comparison.summary_statement}
          </div>

          {/* Side-by-Side Indoor Trajectory Line Chart */}
          <Card className="space-y-3">
            <h3 className="text-sm font-bold text-white">
              Diurnal Indoor Temperature Trajectory (Baseline vs Modified vs Ambient)
            </h3>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                  <XAxis dataKey="hour" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" tick={{ fontSize: 11 }} domain={['auto', 'auto']} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#161b22', borderColor: '#30363d', borderRadius: '8px' }}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="baseline"
                    name="Baseline Indoor (°C)"
                    stroke="#ef4444"
                    strokeWidth={2.5}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="modified"
                    name="Modified Indoor (°C)"
                    stroke="#10b981"
                    strokeWidth={2.5}
                    dot={false}
                  />
                  <Line
                    type="monotone"
                    dataKey="ambient"
                    name="Outdoor Ambient (°C)"
                    stroke="#64748b"
                    strokeDasharray="4 4"
                    strokeWidth={1.5}
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
