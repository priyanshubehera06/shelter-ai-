import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useShelterStore } from '../store/shelterStore';
import { runOptimization } from '../api/endpoints';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { Slider } from '../components/ui/Slider';
import { Badge } from '../components/ui/Badge';
import { SectionHeader } from '../components/ui/SectionHeader';
import { ParetoCandidate } from '../types';
import {
  ResponsiveContainer,
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import {
  Target,
  Zap,
  Box,
  Trophy,
  Flame,
  Award,
  Sparkles,
  ArrowRight
} from 'lucide-react';

export const OptimizationPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    selectedLocationId,
    selectedMonth,
    optimizationResult,
    setOptimizationResult,
    isOptimizing,
    setIsOptimizing,
    loadDesign,
  } = useShelterStore();

  const [wComfort, setWComfort] = useState(0.4);
  const [wCost, setWCost] = useState(0.3);
  const [wCarbon, setWCarbon] = useState(0.3);
  const [popSize, setPopSize] = useState(25);

  const handleRunOptimization = async () => {
    setIsOptimizing(true);
    try {
      const res = await runOptimization({
        location_id: selectedLocationId,
        month: selectedMonth,
        w_comfort: wComfort,
        w_cost: wCost,
        w_carbon: wCarbon,
        population_size: popSize,
      });
      setOptimizationResult(res);
    } catch (e) {
      console.error('Optimization error:', e);
    } finally {
      setIsOptimizing(false);
    }
  };

  const handleSelectCandidate = (cand: ParetoCandidate) => {
    const c = cand.candidate;
    loadDesign({
      name: `Optimized Design (${c.wall_mat_id} + ${c.roof_mat_id})`,
      archetype: 'Pareto Optimal',
      geometry: {
        length_m: c.length_m || 6.0,
        width_m: c.width_m || 4.0,
        height_m: c.height_m || 2.8,
        roof_type: c.roof_type || 'pitched',
        roof_pitch_deg: c.roof_pitch_deg || 15.0,
        wall_thickness_cm: c.wall_thickness_cm || 20.0,
        wwr_pct: c.wwr_pct || 15.0,
        overhang_m: c.overhang_m || 0.6,
        orientation_deg: c.orientation_deg || 0.0,
        door_width_m: 0.9,
        door_height_m: 2.1,
        door_count: 1,
      },
      materials: {
        wall_mat_id: c.wall_mat_id,
        wall_thickness_cm: c.wall_thickness_cm || 20.0,
        roof_mat_id: c.roof_mat_id,
        insulation_mat_id: c.insulation_mat_id,
        insulation_thickness_cm: c.insulation_thickness_cm || 0.0,
        glazing_mat_id: c.glazing_mat_id || 'glazing_single',
      },
      occupants: 4,
      location_id: selectedLocationId,
    });
    navigate('/digital-twin');
  };

  const paretoData = (optimizationResult?.pareto_front || []).map((p) => ({
    x: p.cost_inr,
    y: p.annual_energy_kwh,
    z: p.comfort_score,
    name: `${p.candidate.wall_mat_id} + ${p.candidate.roof_mat_id}`,
    candidate: p,
  }));

  const allCandidatesData = (optimizationResult?.all_candidates || [])
    .filter((c) => !c.is_pareto)
    .map((p) => ({
      x: p.cost_inr,
      y: p.annual_energy_kwh,
      z: p.comfort_score,
      name: `${p.candidate.wall_mat_id} + ${p.candidate.roof_mat_id}`,
      candidate: p,
    }));

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300">
      <SectionHeader
        title="06. Multi-Objective Pareto Optimization (NSGA-II)"
        subtitle="Simultaneously optimizes Thermal Comfort (Maximize), Operational Energy Demand (Minimize), and CapEx Construction Cost (Minimize)"
        icon={<Target className="w-5 h-5 text-rose-400" />}
      />

      {/* Controls & Objectives Card */}
      <Card className="space-y-4">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-surface-border pb-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-400" />
            Genetic Algorithm Objective Weights & Population
          </h3>
          <Button
            variant="primary"
            icon={<Zap className="w-4 h-4" />}
            isLoading={isOptimizing}
            onClick={handleRunOptimization}
          >
            Run Multi-Objective Pareto Search
          </Button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-4 gap-4 pt-1">
          <Slider
            label="Weight: Thermal Comfort"
            value={wComfort}
            min={0.1}
            max={0.8}
            step={0.05}
            onChange={(val) => setWComfort(val)}
          />
          <Slider
            label="Weight: CapEx Construction Cost"
            value={wCost}
            min={0.1}
            max={0.8}
            step={0.05}
            onChange={(val) => setWCost(val)}
          />
          <Slider
            label="Weight: Embodied Carbon"
            value={wCarbon}
            min={0.1}
            max={0.8}
            step={0.05}
            onChange={(val) => setWCarbon(val)}
          />
          <Slider
            label="Population Size"
            value={popSize}
            min={10}
            max={50}
            step={5}
            onChange={(val) => setPopSize(val)}
          />
        </div>
      </Card>

      {/* Optimization Results */}
      {optimizationResult && (
        <div className="space-y-6">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
            <MetricCard
              label="Total Evaluated"
              value={optimizationResult.total_evaluated}
              unit="designs"
            />
            <MetricCard
              label="Pareto Optimal Solutions"
              value={optimizationResult.pareto_front_count}
              unit="solutions"
              trend="positive"
            />
            <MetricCard
              label="Highest Comfort Score"
              value={optimizationResult.top_4_designs.best_comfort.comfort_score}
              unit="%"
              trend="positive"
            />
            <MetricCard
              label="Lowest CapEx Outlay"
              value={`₹${optimizationResult.top_4_designs.lowest_cost.cost_inr.toLocaleString()}`}
              trend="solar"
            />
          </div>

          {/* Pareto Trade-Off Scatter Chart */}
          <Card className="space-y-3">
            <h3 className="text-sm font-bold text-white flex items-center justify-between">
              <span>Pareto Trade-Off Space (Construction CapEx vs Annual HVAC Energy)</span>
              <Badge variant="emerald" size="sm">Non-Dominated Front</Badge>
            </h3>

            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#21262d" />
                  <XAxis
                    type="number"
                    dataKey="x"
                    name="CapEx (₹)"
                    unit=" ₹"
                    stroke="#64748b"
                    tick={{ fontSize: 11 }}
                  />
                  <YAxis
                    type="number"
                    dataKey="y"
                    name="Annual Energy"
                    unit=" kWh"
                    stroke="#64748b"
                    tick={{ fontSize: 11 }}
                  />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    contentStyle={{ backgroundColor: '#161b22', borderColor: '#30363d', borderRadius: '8px' }}
                  />
                  <Legend />
                  <Scatter
                    name="Candidate Designs"
                    data={allCandidatesData}
                    fill="#64748b"
                    opacity={0.4}
                  />
                  <Scatter
                    name="🏆 Pareto Optimal Front"
                    data={paretoData}
                    fill="#10b981"
                  />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Pareto Candidates Table */}
          <Card className="space-y-4">
            <h3 className="text-sm font-bold text-white border-b border-surface-border pb-2">
              🏆 Non-Dominated Pareto-Optimal Shelter Configurations
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-surface-border text-slate-400">
                    <th className="py-2.5 px-3">Rank</th>
                    <th className="py-2.5 px-3">Wall Assembly</th>
                    <th className="py-2.5 px-3">Roof Assembly</th>
                    <th className="py-2.5 px-3">Comfort Score</th>
                    <th className="py-2.5 px-3">Annual Energy</th>
                    <th className="py-2.5 px-3">Estimated CapEx</th>
                    <th className="py-2.5 px-3 text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-border">
                  {optimizationResult.pareto_front.map((cand, idx) => (
                    <tr key={cand.id} className="hover:bg-surface-raised transition-colors">
                      <td className="py-3 px-3 font-mono font-bold text-emerald-400">#{idx + 1}</td>
                      <td className="py-3 px-3 capitalize">{cand.candidate.wall_mat_id.replace('_', ' ')}</td>
                      <td className="py-3 px-3 capitalize">{cand.candidate.roof_mat_id.replace('_', ' ')}</td>
                      <td className="py-3 px-3 font-mono font-semibold">{cand.comfort_score}%</td>
                      <td className="py-3 px-3 font-mono">{cand.annual_energy_kwh.toLocaleString()} kWh</td>
                      <td className="py-3 px-3 font-mono">₹{cand.cost_inr.toLocaleString()}</td>
                      <td className="py-3 px-3 text-right">
                        <Button
                          size="sm"
                          variant="secondary"
                          icon={<Box className="w-3 h-3 text-emerald-400" />}
                          onClick={() => handleSelectCandidate(cand)}
                        >
                          View in 3D
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
};
