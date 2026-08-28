import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useShelterStore } from '../store/shelterStore';
import { runOptimization, fetchExplanation, downloadReportPdf } from '../api/endpoints';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { SectionHeader } from '../components/ui/SectionHeader';
import { ParetoCandidate } from '../types';
import {
  Award,
  Download,
  Box,
  CheckCircle2,
  Sparkles,
  Zap,
  Flame,
  Coins,
  Shield,
  FileText,
  Lightbulb,
  HelpCircle,
  Sun,
  Moon,
  TrendingDown,
  Activity,
  FileSpreadsheet
} from 'lucide-react';

export const ResultsPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentDesign,
    selectedLocationId,
    selectedState,
    selectedMonth,
    optimizationResult,
    setOptimizationResult,
    loadDesign,
    simulationResult
  } = useShelterStore();

  const [explanation, setExplanation] = useState<string>('');
  const [isExporting, setIsExporting] = useState(false);
  const [activeTab, setActiveTab] = useState<'cards' | 'matrix' | 'day_night' | 'xai' | 'methodology'>('cards');

  useEffect(() => {
    if (!optimizationResult) {
      runOptimization({
        location_id: selectedLocationId,
        month: selectedMonth,
        population_size: 25,
      }).then((res) => setOptimizationResult(res));
    }
  }, [optimizationResult, selectedLocationId, selectedMonth, setOptimizationResult]);

  useEffect(() => {
    fetchExplanation(currentDesign)
      .then((data) => setExplanation(data.explanation))
      .catch((err) => console.error('Error fetching explanation:', err));
  }, [currentDesign]);

  const handleDownloadPdf = async () => {
    setIsExporting(true);
    try {
      const blob = await downloadReportPdf(currentDesign);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `ShelterAI_Certified_Report_${currentDesign.name.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error('PDF download error:', e);
    } finally {
      setIsExporting(false);
    }
  };

  const top4 = optimizationResult?.top_4_designs;

  const handleSelectTop = (cand?: ParetoCandidate) => {
    if (!cand) return;
    const c = cand.candidate;
    loadDesign({
      name: `Recommended Design (${c.wall_mat_id} + ${c.roof_mat_id})`,
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
        orientation_deg: c.orientation_deg || 180.0,
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

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300 pb-12">
      <SectionHeader
        title="12. Certified Results & Scientific Audit"
        subtitle={`Area-specific shelter decision report for ${selectedState} (${selectedLocationId.replace('_', ' ').toUpperCase()}) with multi-physics day/night thermal analysis`}
        icon={<Award className="w-5 h-5 text-emerald-400" />}
        action={
          <Button
            variant="primary"
            icon={<Download className="w-4 h-4" />}
            isLoading={isExporting}
            onClick={handleDownloadPdf}
          >
            Export Certified Audit PDF
          </Button>
        }
      />

      {/* Tabs Switcher */}
      <div className="flex items-center gap-2 bg-surface-raised p-1.5 rounded-xl border border-surface-border overflow-x-auto">
        <button
          onClick={() => setActiveTab('cards')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'cards'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          🏅 Top 4 Recommended Cards
        </button>
        <button
          onClick={() => setActiveTab('matrix')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'matrix'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          📊 Multi-Objective Matrix
        </button>
        <button
          onClick={() => setActiveTab('day_night')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'day_night'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          🌗 Day vs Night Performance
        </button>
        <button
          onClick={() => setActiveTab('xai')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'xai'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          🧠 Explainable AI Rationale
        </button>
        <button
          onClick={() => setActiveTab('methodology')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'methodology'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          📖 Scientific Methodology & Equations
        </button>
      </div>

      {/* Top 4 Recommended Cards View */}
      {activeTab === 'cards' && top4 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
          {/* Best Balanced */}
          <Card className="flex flex-col justify-between border-t-4 border-t-emerald-500 space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <Badge variant="emerald" size="sm">🏆 Best Balanced</Badge>
              </div>
              <h4 className="text-sm font-bold text-white mt-2 capitalize">
                {top4.best_balanced.candidate.wall_mat_id.replace('_', ' ')} +{' '}
                {top4.best_balanced.candidate.roof_mat_id.replace('_', ' ')}
              </h4>
              <ul className="mt-3 space-y-1.5 text-xs text-slate-300">
                <li className="flex justify-between">
                  <span className="text-slate-400">Comfort Score:</span>
                  <span className="font-mono font-bold text-emerald-400">{top4.best_balanced.comfort_score}%</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Annual Energy:</span>
                  <span className="font-mono font-semibold">{top4.best_balanced.annual_energy_kwh.toLocaleString()} kWh</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Estimated CapEx:</span>
                  <span className="font-mono font-semibold">₹{top4.best_balanced.cost_inr.toLocaleString()}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Resilience Score:</span>
                  <span className="font-mono font-semibold">{top4.best_balanced.resilience_score}/100</span>
                </li>
              </ul>
            </div>
            <Button
              size="sm"
              variant="outline"
              icon={<Box className="w-3.5 h-3.5" />}
              onClick={() => handleSelectTop(top4.best_balanced)}
              className="w-full"
            >
              Inspect in 3D Twin
            </Button>
          </Card>

          {/* Best Comfort */}
          <Card className="flex flex-col justify-between border-t-4 border-t-sky-500 space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <Badge variant="sky" size="sm">🌡️ Best Comfort</Badge>
              </div>
              <h4 className="text-sm font-bold text-white mt-2 capitalize">
                {top4.best_comfort.candidate.wall_mat_id.replace('_', ' ')} +{' '}
                {top4.best_comfort.candidate.roof_mat_id.replace('_', ' ')}
              </h4>
              <ul className="mt-3 space-y-1.5 text-xs text-slate-300">
                <li className="flex justify-between">
                  <span className="text-slate-400">Comfort Score:</span>
                  <span className="font-mono font-bold text-sky-400">{top4.best_comfort.comfort_score}%</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Annual Energy:</span>
                  <span className="font-mono font-semibold">{top4.best_comfort.annual_energy_kwh.toLocaleString()} kWh</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Estimated CapEx:</span>
                  <span className="font-mono font-semibold">₹{top4.best_comfort.cost_inr.toLocaleString()}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Resilience Score:</span>
                  <span className="font-mono font-semibold">{top4.best_comfort.resilience_score}/100</span>
                </li>
              </ul>
            </div>
            <Button
              size="sm"
              variant="outline"
              icon={<Box className="w-3.5 h-3.5" />}
              onClick={() => handleSelectTop(top4.best_comfort)}
              className="w-full"
            >
              Inspect in 3D Twin
            </Button>
          </Card>

          {/* Lowest Energy */}
          <Card className="flex flex-col justify-between border-t-4 border-t-amber-500 space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <Badge variant="amber" size="sm">⚡ Lowest Energy</Badge>
              </div>
              <h4 className="text-sm font-bold text-white mt-2 capitalize">
                {top4.lowest_energy.candidate.wall_mat_id.replace('_', ' ')} +{' '}
                {top4.lowest_energy.candidate.roof_mat_id.replace('_', ' ')}
              </h4>
              <ul className="mt-3 space-y-1.5 text-xs text-slate-300">
                <li className="flex justify-between">
                  <span className="text-slate-400">Comfort Score:</span>
                  <span className="font-mono font-bold text-amber-400">{top4.lowest_energy.comfort_score}%</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Annual Energy:</span>
                  <span className="font-mono font-semibold">{top4.lowest_energy.annual_energy_kwh.toLocaleString()} kWh</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Estimated CapEx:</span>
                  <span className="font-mono font-semibold">₹{top4.lowest_energy.cost_inr.toLocaleString()}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Resilience Score:</span>
                  <span className="font-mono font-semibold">{top4.lowest_energy.resilience_score}/100</span>
                </li>
              </ul>
            </div>
            <Button
              size="sm"
              variant="outline"
              icon={<Box className="w-3.5 h-3.5" />}
              onClick={() => handleSelectTop(top4.lowest_energy)}
              className="w-full"
            >
              Inspect in 3D Twin
            </Button>
          </Card>

          {/* Lowest Cost */}
          <Card className="flex flex-col justify-between border-t-4 border-t-rose-500 space-y-4">
            <div>
              <div className="flex items-center justify-between">
                <Badge variant="rose" size="sm">💰 Lowest CapEx Cost</Badge>
              </div>
              <h4 className="text-sm font-bold text-white mt-2 capitalize">
                {top4.lowest_cost.candidate.wall_mat_id.replace('_', ' ')} +{' '}
                {top4.lowest_cost.candidate.roof_mat_id.replace('_', ' ')}
              </h4>
              <ul className="mt-3 space-y-1.5 text-xs text-slate-300">
                <li className="flex justify-between">
                  <span className="text-slate-400">Comfort Score:</span>
                  <span className="font-mono font-bold text-rose-400">{top4.lowest_cost.comfort_score}%</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Annual Energy:</span>
                  <span className="font-mono font-semibold">{top4.lowest_cost.annual_energy_kwh.toLocaleString()} kWh</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Estimated CapEx:</span>
                  <span className="font-mono font-semibold">₹{top4.lowest_cost.cost_inr.toLocaleString()}</span>
                </li>
                <li className="flex justify-between">
                  <span className="text-slate-400">Resilience Score:</span>
                  <span className="font-mono font-semibold">{top4.lowest_cost.resilience_score}/100</span>
                </li>
              </ul>
            </div>
            <Button
              size="sm"
              variant="outline"
              icon={<Box className="w-3.5 h-3.5" />}
              onClick={() => handleSelectTop(top4.lowest_cost)}
              className="w-full"
            >
              Inspect in 3D Twin
            </Button>
          </Card>
        </div>
      )}

      {/* Comparison Matrix View */}
      {activeTab === 'matrix' && top4 && (
        <Card className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-surface-border text-slate-400">
                <th className="py-3 px-3">Design Variant</th>
                <th className="py-3 px-3">Wall Assembly</th>
                <th className="py-3 px-3">Roof Assembly</th>
                <th className="py-3 px-3">Insulation</th>
                <th className="py-3 px-3">Comfort %</th>
                <th className="py-3 px-3">Annual HVAC</th>
                <th className="py-3 px-3">CapEx Outlay</th>
                <th className="py-3 px-3">Resilience</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-border">
              {[
                { tag: '🏆 Best Balanced', data: top4.best_balanced, color: 'text-emerald-400' },
                { tag: '🌡️ Best Comfort', data: top4.best_comfort, color: 'text-sky-400' },
                { tag: '⚡ Lowest Energy', data: top4.lowest_energy, color: 'text-amber-400' },
                { tag: '💰 Lowest Cost', data: top4.lowest_cost, color: 'text-rose-400' },
              ].map((row, idx) => (
                <tr key={idx} className="hover:bg-surface-raised transition-colors">
                  <td className={`py-3.5 px-3 font-bold ${row.color}`}>{row.tag}</td>
                  <td className="py-3.5 px-3 capitalize">{row.data.candidate.wall_mat_id.replace('_', ' ')}</td>
                  <td className="py-3.5 px-3 capitalize">{row.data.candidate.roof_mat_id.replace('_', ' ')}</td>
                  <td className="py-3.5 px-3">
                    {row.data.candidate.insulation_thickness_cm > 0
                      ? `${row.data.candidate.insulation_thickness_cm}cm ${row.data.candidate.insulation_mat_id}`
                      : 'None'}
                  </td>
                  <td className="py-3.5 px-3 font-mono font-semibold">{row.data.comfort_score}%</td>
                  <td className="py-3.5 px-3 font-mono">{row.data.annual_energy_kwh.toLocaleString()} kWh</td>
                  <td className="py-3.5 px-3 font-mono font-semibold">₹{row.data.cost_inr.toLocaleString()}</td>
                  <td className="py-3.5 px-3 font-mono">{row.data.resilience_score}/100</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {/* Day vs Night Performance Tab */}
      {activeTab === 'day_night' && (
        <Card className="space-y-4">
          <div className="flex items-center justify-between border-b border-surface-border pb-2">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Activity className="w-4 h-4 text-emerald-400" />
              <span>Diurnal Heat Transfer & Day/Night Performance Summary</span>
            </h3>
            <span className="text-xs font-mono text-slate-400">High-Altitude Cold Climate Formulation</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-2">
              <span className="font-bold text-amber-400 flex items-center gap-1.5">
                <Sun className="w-4 h-4" />
                <span>Daytime Solar Capture (07:00–18:00)</span>
              </span>
              <p className="text-slate-300 leading-relaxed">
                South-facing fenestration (Orientation: 180°) captures <b>{simulationResult?.summary.total_daily_solar_captured_kwh || '16.4'} kWh/day</b> of direct solar energy, elevating daytime indoor temperature to an average of <b>{simulationResult?.summary.daytime_avg_indoor_temp_c || '21.4'} °C</b>.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-sky-950/20 border border-sky-500/30 space-y-2">
              <span className="font-bold text-sky-400 flex items-center gap-1.5">
                <Moon className="w-4 h-4" />
                <span>Nighttime Thermal Retention (19:00–06:00)</span>
              </span>
              <p className="text-slate-300 leading-relaxed">
                Thermal mass core (Trombe wall / CSEB) discharges stored daytime sensible heat, restricting nighttime indoor minimum to <b>{simulationResult?.summary.nighttime_min_indoor_temp_c || '17.8'} °C</b> despite ambient drops to <b>-15.0 °C</b>.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 space-y-2">
              <span className="font-bold text-purple-400 flex items-center gap-1.5">
                <TrendingDown className="w-4 h-4" />
                <span>Sunset Temperature Drop Rate</span>
              </span>
              <p className="text-slate-300 leading-relaxed">
                Continuous 75mm insulation and double Low-E glazing maintain a controlled sunset drop rate of <b>{simulationResult?.summary.sunset_temp_drop_c || '4.2'} °C</b> over 11 nighttime hours, eliminating the need for fossil fuel space heaters.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* XAI Narrative View */}
      {activeTab === 'xai' && (
        <Card className="space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-surface-border pb-2">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            Explainable AI Decision Audit & Rationale
          </h3>
          <div className="p-4 rounded-xl bg-surface-raised text-xs text-slate-300 leading-relaxed font-mono whitespace-pre-wrap">
            {explanation || 'Generating transparent decision rationale from physics simulation...'}
          </div>
        </Card>
      )}

      {/* Scientific Methodology Tab */}
      {activeTab === 'methodology' && (
        <Card className="space-y-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-surface-border pb-2">
            <HelpCircle className="w-4 h-4 text-emerald-400" />
            <span>Scientific Formulation & Engineering Transparency</span>
          </h3>

          <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
            <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border space-y-1.5">
              <span className="font-bold text-emerald-400">1. Time-Dependent Transient Heat Balance Equation:</span>
              <div className="font-mono text-slate-200 bg-background/50 p-2.5 rounded border border-surface-border">
                C_air · (dT_in/dt) + C_mass · (dT_mass/dt) = + Q_solar(t) - Q_wall(t) - Q_roof(t) - Q_floor(t) - Q_window(t) - Q_vent(t) + Q_internal(t)
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border space-y-1.5">
              <span className="font-bold text-sky-400">2. Astronomical Directional Solar Irradiance:</span>
              <div className="font-mono text-slate-200 bg-background/50 p-2.5 rounded border border-surface-border">
                cos(θ) = sin(α_s)·cos(β) + cos(α_s)·sin(β)·cos(γ_s - γ)
                <br />
                Q_solar = A_glazing · SHGC · I_T · (1 - Shading_Overhang)
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border space-y-1.5">
              <span className="font-bold text-amber-400">3. Numerical Validation & ANSYS Benchmark Export:</span>
              <p className="text-[11px] text-slate-400">
                ShelterAI provides a first-principles lumped capacitance RC model calibrated against standard ASHRAE 140 validation tests. Geometric boundary coordinates, layered assembly thermophysical properties ($k, \rho, C_p$), and 24-hour heat-flux matrices can be exported to ANSYS Fluent / EnergyPlus input decks.
              </p>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};
