import React, { useEffect, useState } from 'react';
import { useShelterStore } from '../store/shelterStore';
import { runOptimization } from '../api/endpoints';
import { ParetoCandidate, RecommendedTop4 } from '../types';
import {
  TrendingUp,
  Coins,
  Smile,
  Zap,
  Target,
  Sparkles,
  Award,
  ArrowRight,
  Sliders,
  CheckCircle2,
  HelpCircle,
  RefreshCw,
  Eye
} from 'lucide-react';
import { clsx } from 'clsx';
import { useNavigate } from 'react-router-dom';

export const CostComfortDashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    selectedLocationId,
    optimizationResult,
    setOptimizationResult,
    isOptimizing,
    setIsOptimizing,
    costComfortPreference,
    setCostComfortPreference,
    loadDesign,
    currentDesign
  } = useShelterStore();

  const [selectedCandidate, setSelectedCandidate] = useState<ParetoCandidate | null>(null);

  const runParetoSearch = async () => {
    setIsOptimizing(true);
    try {
      // Preference slider: 0 = 100% Cost, 100 = 100% Comfort
      const wComfort = Math.max(0.1, costComfortPreference / 100);
      const wCost = Math.max(0.1, (100 - costComfortPreference) / 100);
      const wCarbon = 0.2;

      const data = await runOptimization({
        location_id: selectedLocationId,
        w_comfort: wComfort,
        w_cost: wCost,
        w_carbon: wCarbon,
        population_size: 40
      });

      setOptimizationResult(data);
      if (data.top_4_designs?.best_balanced) {
        setSelectedCandidate(data.top_4_designs.best_balanced);
      }
    } catch (err) {
      console.error('Failed to run Pareto optimization:', err);
    } finally {
      setIsOptimizing(false);
    }
  };

  useEffect(() => {
    if (!optimizationResult) {
      runParetoSearch();
    } else if (optimizationResult.top_4_designs?.best_balanced && !selectedCandidate) {
      setSelectedCandidate(optimizationResult.top_4_designs.best_balanced);
    }
  }, []);

  const handleApplyCandidate = (cand: ParetoCandidate) => {
    if (!cand.candidate) return;
    const c = cand.candidate;
    loadDesign({
      ...currentDesign,
      name: cand.recommendation_type || `Design Option (Score ${cand.comfort_score})`,
      geometry: {
        ...currentDesign.geometry,
        length_m: c.length_m || currentDesign.geometry.length_m,
        width_m: c.width_m || currentDesign.geometry.width_m,
        height_m: c.height_m || currentDesign.geometry.height_m,
        roof_type: c.roof_type || currentDesign.geometry.roof_type,
        roof_pitch_deg: c.roof_pitch_deg || currentDesign.geometry.roof_pitch_deg,
        wwr_pct: c.wwr_pct || currentDesign.geometry.wwr_pct,
        overhang_m: c.overhang_m || currentDesign.geometry.overhang_m,
        orientation_deg: c.orientation_deg || currentDesign.geometry.orientation_deg,
      },
      materials: {
        wall_mat_id: c.wall_mat_id || currentDesign.materials.wall_mat_id,
        wall_thickness_cm: c.wall_thickness_cm || currentDesign.materials.wall_thickness_cm,
        roof_mat_id: c.roof_mat_id || currentDesign.materials.roof_mat_id,
        insulation_mat_id: c.insulation_mat_id,
        insulation_thickness_cm: c.insulation_thickness_cm || 0,
        glazing_mat_id: c.glazing_mat_id || currentDesign.materials.glazing_mat_id,
      }
    });
    navigate('/digital-twin');
  };

  // Min and max bounds for scatter plot normalization
  const allPoints = optimizationResult?.all_candidates || [];
  const minCost = allPoints.length ? Math.min(...allPoints.map(p => p.cost_inr)) : 100000;
  const maxCost = allPoints.length ? Math.max(...allPoints.map(p => p.cost_inr)) : 400000;
  const minComfort = allPoints.length ? Math.min(...allPoints.map(p => p.comfort_score)) : 40;
  const maxComfort = allPoints.length ? Math.max(...allPoints.map(p => p.comfort_score)) : 100;

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-surface-border pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-md text-[10px] font-mono uppercase tracking-wider bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              Module 08 — Decision Trade-Offs
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mt-2 flex items-center gap-3">
            Cost vs Comfort Trade-Off Dashboard
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Explore the multi-objective Pareto Frontier of non-dominated design candidates. Analyze the exact cost-benefit delta before committing capital investments.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={runParetoSearch}
            disabled={isOptimizing}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold shadow-lg shadow-emerald-950/40 transition disabled:opacity-50"
          >
            <RefreshCw className={clsx('w-3.5 h-3.5', isOptimizing && 'animate-spin')} />
            <span>Run Pareto Optimization</span>
          </button>
        </div>
      </div>

      {/* "What Matters Most?" Preference Slider */}
      <div className="p-6 rounded-2xl bg-surface border border-surface-border space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-emerald-400" />
            <h2 className="text-sm font-semibold text-white">What Matters Most to Your Project?</h2>
          </div>
          <span className="text-xs font-mono text-slate-400">
            Current Focus: {costComfortPreference < 35 ? '💰 Lowest Construction Cost' : (costComfortPreference > 65 ? '🌡️ Maximum Thermal Comfort' : '⚖️ Balanced Optimization')}
          </span>
        </div>

        <div className="space-y-2 pt-2">
          <div className="flex justify-between text-xs font-semibold">
            <span className="text-amber-400 flex items-center gap-1.5"><Coins className="w-3.5 h-3.5" /> Strict Budget / Lowest CapEx (0%)</span>
            <span className="text-slate-400 font-mono">Balanced Compromise (50%)</span>
            <span className="text-emerald-400 flex items-center gap-1.5"><Smile className="w-3.5 h-3.5" /> Maximum Comfort / ASHRAE 55 (100%)</span>
          </div>
          <input
            type="range"
            min="0"
            max="100"
            value={costComfortPreference}
            onChange={(e) => setCostComfortPreference(Number(e.target.value))}
            className="w-full h-2.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
          />
        </div>
      </div>

      {/* Main Grid: Interactive Pareto Scatter Chart + Selected Candidate Details */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Interactive Scatter Plot */}
        <div className="lg:col-span-7 p-6 rounded-2xl bg-surface border border-surface-border space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Target className="w-4 h-4 text-cyan-400" />
              <span>Simulated Design Candidates (Pareto Frontier)</span>
            </h3>
            <span className="text-[11px] font-mono text-slate-400">
              {allPoints.length} Candidates Evaluated
            </span>
          </div>

          {/* Interactive Scatter Canvas */}
          <div className="relative w-full h-80 bg-background/80 rounded-xl border border-surface-border p-6 flex flex-col justify-between overflow-hidden">
            {/* Y Axis Label */}
            <div className="absolute top-3 left-3 text-[10px] font-mono uppercase text-slate-400 tracking-wider">
              ↑ Comfort Score (0 - 100)
            </div>
            {/* X Axis Label */}
            <div className="absolute bottom-2 right-3 text-[10px] font-mono uppercase text-slate-400 tracking-wider">
              Total Construction CapEx (₹ Lakh) →
            </div>

            {/* Scatter Points */}
            <div className="relative w-full h-full my-4">
              {allPoints.map((pt, idx) => {
                const normX = ((pt.cost_inr - minCost) / Math.max(1, maxCost - minCost)) * 90 + 5;
                const normY = 95 - (((pt.comfort_score - minComfort) / Math.max(1, maxComfort - minComfort)) * 90);
                const isSelected = selectedCandidate?.id === pt.id;

                return (
                  <button
                    key={idx}
                    onClick={() => setSelectedCandidate(pt)}
                    style={{ left: `${normX}%`, top: `${normY}%` }}
                    className={clsx(
                      'absolute -translate-x-1/2 -translate-y-1/2 rounded-full transition-all duration-200 focus:outline-none',
                      pt.is_pareto
                        ? (isSelected ? 'w-5 h-5 bg-cyan-400 ring-4 ring-cyan-400/40 z-20' : 'w-3.5 h-3.5 bg-cyan-500 hover:scale-125 z-10')
                        : (isSelected ? 'w-4 h-4 bg-slate-200 ring-2 ring-white z-20' : 'w-2 h-2 bg-slate-600 hover:bg-slate-400')
                    )}
                    title={`Cost: ₹${(pt.cost_inr / 100000).toFixed(2)}L | Comfort: ${pt.comfort_score}`}
                  />
                );
              })}
            </div>
          </div>

          <div className="flex items-center justify-between text-[11px] text-slate-400">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-cyan-400 inline-block" />
              <span>Pareto-Optimal Design (Non-Dominated)</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-slate-600 inline-block" />
              <span>Dominated Alternative</span>
            </div>
          </div>
        </div>

        {/* Right Column: Selected Design Deep-Dive Card */}
        <div className="lg:col-span-5 space-y-4">
          {selectedCandidate ? (
            <div className="p-6 rounded-2xl bg-surface border border-surface-border space-y-5">
              <div className="flex items-center justify-between border-b border-surface-border pb-4">
                <div>
                  <span className="px-2.5 py-0.5 rounded text-[10px] font-mono uppercase bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                    {selectedCandidate.recommendation_type || (selectedCandidate.is_pareto ? 'Pareto Optimal Design' : 'Exploratory Design')}
                  </span>
                  <h3 className="text-xl font-bold text-white mt-1">Design Performance Breakdown</h3>
                </div>

                <div className="text-right">
                  <div className="text-[10px] font-mono text-slate-400 uppercase">CapEx Cost</div>
                  <div className="text-lg font-mono font-bold text-emerald-400">
                    ₹{(selectedCandidate.cost_inr / 100000).toFixed(2)} Lakh
                  </div>
                </div>
              </div>

              {/* Explainable Engineering Reason */}
              <div className="p-4 rounded-xl bg-surface-raised border border-surface-border space-y-1.5 text-xs">
                <div className="font-semibold text-slate-300 flex items-center gap-1.5">
                  <HelpCircle className="w-4 h-4 text-emerald-400" />
                  <span>Why this design?</span>
                </div>
                <p className="text-slate-400 leading-relaxed">
                  {selectedCandidate.rationale || `Delivers a high Comfort Score of ${selectedCandidate.comfort_score}/100 while maintaining annual energy demand at ${selectedCandidate.annual_energy_kwh.toFixed(0)} kWh.`}
                </p>
              </div>

              {/* Key Metrics Grid */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-xl bg-surface-raised border border-surface-border space-y-0.5">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Comfort Score</div>
                  <div className="text-xl font-mono font-bold text-emerald-400">{selectedCandidate.comfort_score} / 100</div>
                </div>

                <div className="p-3 rounded-xl bg-surface-raised border border-surface-border space-y-0.5">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Annual Energy Demand</div>
                  <div className="text-xl font-mono font-bold text-cyan-400">{selectedCandidate.annual_energy_kwh.toFixed(0)} kWh</div>
                </div>

                <div className="p-3 rounded-xl bg-surface-raised border border-surface-border space-y-0.5">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Peak Indoor Temp</div>
                  <div className="text-xl font-mono font-bold text-amber-400">{selectedCandidate.peak_indoor_temp?.toFixed(1) || '31.2'} °C</div>
                </div>

                <div className="p-3 rounded-xl bg-surface-raised border border-surface-border space-y-0.5">
                  <div className="text-[10px] text-slate-400 uppercase font-mono">Embodied Carbon</div>
                  <div className="text-xl font-mono font-bold text-purple-400">{selectedCandidate.carbon_kg.toFixed(0)} kg CO₂</div>
                </div>
              </div>

              {/* Action: Apply to Digital Twin */}
              <button
                onClick={() => handleApplyCandidate(selectedCandidate)}
                className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-lg shadow-emerald-950/50 transition"
              >
                <Eye className="w-4 h-4" />
                <span>Load into 3D Digital Twin & Simulate</span>
              </button>
            </div>
          ) : (
            <div className="p-12 text-center text-slate-400">Click any scatter point to inspect design trade-offs.</div>
          )}
        </div>
      </div>

      {/* Top 4 Recommended Designs Highlights */}
      {optimizationResult?.top_4_designs && (
        <div className="space-y-4">
          <h2 className="text-base font-bold text-white flex items-center gap-2">
            <Award className="w-5 h-5 text-emerald-400" />
            <span>Top Recommended Engineering Designs</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {Object.entries(optimizationResult.top_4_designs).map(([key, design]) => (
              <div
                key={key}
                onClick={() => setSelectedCandidate(design)}
                className={clsx(
                  'p-5 rounded-2xl bg-surface border flex flex-col justify-between space-y-3 cursor-pointer transition-all hover:scale-[1.02]',
                  selectedCandidate?.id === design.id
                    ? 'border-emerald-500 ring-2 ring-emerald-500/20 bg-emerald-950/10'
                    : 'border-surface-border hover:border-surface-border/80'
                )}
              >
                <div className="space-y-2">
                  <span className="text-xs font-bold text-white">{design.recommendation_type}</span>
                  <div className="flex justify-between items-baseline pt-1">
                    <span className="text-lg font-mono font-bold text-emerald-400">₹{(design.cost_inr / 100000).toFixed(2)}L</span>
                    <span className="text-xs font-mono font-bold text-slate-300">Comfort: {design.comfort_score}/100</span>
                  </div>
                  <p className="text-[11px] text-slate-400 line-clamp-3 leading-relaxed">{design.rationale}</p>
                </div>

                <div className="pt-2 border-t border-surface-border flex justify-between items-center text-[10px] text-slate-400 font-mono">
                  <span>Energy: {design.annual_energy_kwh.toFixed(0)} kWh</span>
                  <span className="text-emerald-400 font-bold">Select →</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
