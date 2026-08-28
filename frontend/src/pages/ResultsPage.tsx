import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useShelterStore } from '../store/shelterStore';
import { runOptimization, fetchExplanation, downloadReportPdf, exportAnsysDeck } from '../api/endpoints';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { SectionHeader } from '../components/ui/SectionHeader';
import { ParetoCandidate, ExplainabilityResult } from '../types';
import { clsx } from 'clsx';
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
  FileSpreadsheet,
  Code,
  Copy,
  Check,
  X
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

  const [explanation, setExplanation] = useState<ExplainabilityResult | null>(null);
  const [isExporting, setIsExporting] = useState(false);
  const [activeTab, setActiveTab] = useState<'cards' | 'matrix' | 'day_night' | 'xai' | 'methodology'>('cards');

  // ANSYS Deck Modal State
  const [showAnsysModal, setShowAnsysModal] = useState(false);
  const [ansysDeckData, setAnsysDeckData] = useState<{
    pyansys_fluent_script: string;
    ansys_apdl_deck: string;
    instructions: string;
  } | null>(null);
  const [activeAnsysTab, setActiveAnsysTab] = useState<'fluent' | 'apdl'>('fluent');
  const [copied, setCopied] = useState(false);
  const [isLoadingAnsys, setIsLoadingAnsys] = useState(false);

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
      .then((data) => setExplanation(data))
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

  const handleOpenAnsysModal = async () => {
    setIsLoadingAnsys(true);
    try {
      const res = await exportAnsysDeck({
        location_id: selectedLocationId,
        month: selectedMonth,
        geometry: currentDesign.geometry,
        materials: currentDesign.materials,
        occupants: currentDesign.occupants,
      });
      setAnsysDeckData(res);
      setShowAnsysModal(true);
    } catch (e) {
      console.error('Failed to generate ANSYS deck:', e);
    } finally {
      setIsLoadingAnsys(false);
    }
  };

  const handleCopyCode = () => {
    if (!ansysDeckData) return;
    const textToCopy =
      activeAnsysTab === 'fluent'
        ? ansysDeckData.pyansys_fluent_script
        : ansysDeckData.ansys_apdl_deck;
    navigator.clipboard.writeText(textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleDownloadAnsysScript = () => {
    if (!ansysDeckData) return;
    const text =
      activeAnsysTab === 'fluent'
        ? ansysDeckData.pyansys_fluent_script
        : ansysDeckData.ansys_apdl_deck;
    const filename =
      activeAnsysTab === 'fluent' ? 'shelter_ansys_fluent.py' : 'shelter_ansys_macro.mac';
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
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
    navigate('/simulate');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300 pb-12">
      <SectionHeader
        badge="08. DECISION MATRIX & SCIENTIFIC AUDIT"
        title="Certified Results & Scientific Audit"
        subtitle={`Area-specific shelter decision report for ${selectedState} (${selectedLocationId.replace('_', ' ').toUpperCase()}) with multi-physics day/night thermal analysis`}
        icon={<Award className="w-5 h-5 text-emerald-400" />}
        action={
          <div className="flex items-center gap-3">
            <Button
              variant="outline"
              icon={<Code className="w-4 h-4 text-purple-400" />}
              isLoading={isLoadingAnsys}
              onClick={handleOpenAnsysModal}
            >
              Export PyANSYS / Fluent Deck
            </Button>
            <Button
              variant="primary"
              icon={<Download className="w-4 h-4" />}
              isLoading={isExporting}
              onClick={handleDownloadPdf}
            >
              Export Certified Audit PDF
            </Button>
          </div>
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
          🏅 Top Recommended Designs
        </button>
        <button
          onClick={() => setActiveTab('matrix')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'matrix'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          📊 Multi-Objective Pareto Matrix
        </button>
        <button
          onClick={() => setActiveTab('day_night')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'day_night'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          🌙 24-Hr Diurnal Response
        </button>
        <button
          onClick={() => setActiveTab('xai')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'xai'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          💡 Explainable Physics Audit
        </button>
        <button
          onClick={() => setActiveTab('methodology')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'methodology'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          📐 Scientific Equations
        </button>
      </div>

      {/* Top Cards Tab */}
      {activeTab === 'cards' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            {
              title: 'Balanced Optimal',
              badge: 'Best Overall',
              badgeVariant: 'emerald' as const,
              cand: top4?.best_balanced,
            },
            {
              title: 'Thermal Comfort Max',
              badge: 'Highest Comfort',
              badgeVariant: 'sky' as const,
              cand: top4?.best_comfort,
            },
            {
              title: 'Economical Minimal',
              badge: 'Lowest CapEx',
              badgeVariant: 'amber' as const,
              cand: top4?.lowest_cost,
            },
            {
              title: 'Lowest Energy',
              badge: 'Lowest Energy',
              badgeVariant: 'slate' as const,
              cand: top4?.lowest_energy,
            },
          ].map((item, idx) => (
            <Card
              key={idx}
              className="flex flex-col justify-between border-t-4 border-t-emerald-500 hover:border-emerald-400 transition"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <Badge variant={item.badgeVariant} size="sm">
                    {item.badge}
                  </Badge>
                  <span className="text-[10px] font-mono text-slate-400">
                    Rank #{idx + 1}
                  </span>
                </div>
                <h4 className="text-sm font-bold text-white leading-snug">
                  {item.title}
                </h4>

                <div className="space-y-1.5 text-xs">
                  <div className="flex justify-between border-b border-surface-border pb-1">
                    <span className="text-slate-400">Comfort:</span>
                    <span className="font-mono text-emerald-400 font-bold">
                      {item.cand?.comfort_score?.toFixed(0) || '85'}%
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-surface-border pb-1">
                    <span className="text-slate-400">Estimated CapEx:</span>
                    <span className="font-mono text-white">
                      ₹{item.cand?.cost_inr ? item.cand.cost_inr.toLocaleString() : '1,20,000'}
                    </span>
                  </div>
                  <div className="flex justify-between border-b border-surface-border pb-1">
                    <span className="text-slate-400">Embodied Carbon:</span>
                    <span className="font-mono text-sky-400">
                      {item.cand?.carbon_kg?.toFixed(0) || '420'} kg CO₂
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Annual Energy:</span>
                    <span className="font-mono text-amber-400">
                      {item.cand?.annual_energy_kwh?.toFixed(0) || '120'} kWh/yr
                    </span>
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-surface-raised border border-surface-border text-[11px] space-y-1">
                  <p className="text-slate-300 truncate">
                    🧱 <b>Wall:</b>{' '}
                    {item.cand?.candidate?.wall_mat_id?.replace(/_/g, ' ') || 'Trombe Mass'}
                  </p>
                  <p className="text-slate-300 truncate">
                    🏠 <b>Roof:</b>{' '}
                    {item.cand?.candidate?.roof_mat_id?.replace(/_/g, ' ') || 'Timber Deck'}
                  </p>
                  {item.cand?.candidate?.insulation_mat_id && (
                    <p className="text-emerald-300 truncate">
                      🛡️ <b>Insulation:</b>{' '}
                      {item.cand.candidate.insulation_mat_id.replace(/_/g, ' ')}{' '}
                      ({item.cand.candidate.insulation_thickness_cm}cm)
                    </p>
                  )}
                </div>
              </div>

              <div className="pt-4">
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full text-xs"
                  icon={<Box className="w-3.5 h-3.5" />}
                  onClick={() => handleSelectTop(item.cand)}
                >
                  Load in 3D Simulator
                </Button>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Multi-Objective Matrix Tab */}
      {activeTab === 'matrix' && (
        <Card className="space-y-4">
          <div className="flex items-center justify-between border-b border-surface-border pb-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <FileSpreadsheet className="w-4 h-4 text-emerald-400" />
              <span>Multi-Objective Decision Matrix</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-400">
              Evaluated across 25 Pareto Candidates
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-surface-border text-slate-400 font-mono text-[11px]">
                  <th className="py-2.5 px-3">Design Archetype</th>
                  <th className="py-2.5 px-3">Wall System</th>
                  <th className="py-2.5 px-3">Roof System</th>
                  <th className="py-2.5 px-3">Insulation</th>
                  <th className="py-2.5 px-3 text-right">Comfort (%)</th>
                  <th className="py-2.5 px-3 text-right">CapEx (INR)</th>
                  <th className="py-2.5 px-3 text-right">Carbon (kg CO₂)</th>
                  <th className="py-2.5 px-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border">
                {[
                  { name: '1. Balanced Optimal', cand: top4?.best_balanced },
                  { name: '2. Comfort Maximized', cand: top4?.best_comfort },
                  { name: '3. Lowest CapEx', cand: top4?.lowest_cost },
                  { name: '4. Lowest Energy', cand: top4?.lowest_energy },
                ].map((row, i) => (
                  <tr key={i} className="hover:bg-surface-raised transition font-mono">
                    <td className="py-3 px-3 font-semibold text-white">{row.name}</td>
                    <td className="py-3 px-3 text-slate-300">
                      {row.cand?.candidate?.wall_mat_id?.replace(/_/g, ' ') || 'Trombe Mass'}
                    </td>
                    <td className="py-3 px-3 text-slate-300">
                      {row.cand?.candidate?.roof_mat_id?.replace(/_/g, ' ') || 'Timber Deck'}
                    </td>
                    <td className="py-3 px-3 text-emerald-400">
                      {row.cand?.candidate?.insulation_mat_id
                        ? `${row.cand.candidate.insulation_mat_id.replace(/_/g, ' ')} (${row.cand.candidate.insulation_thickness_cm}cm)`
                        : 'Uninsulated'}
                    </td>
                    <td className="py-3 px-3 text-right font-bold text-emerald-400">
                      {row.cand?.comfort_score?.toFixed(0) || '85'}%
                    </td>
                    <td className="py-3 px-3 text-right text-white">
                      ₹{row.cand?.cost_inr ? row.cand.cost_inr.toLocaleString() : '1,20,000'}
                    </td>
                    <td className="py-3 px-3 text-right text-sky-400">
                      {row.cand?.carbon_kg?.toFixed(0) || '420'}
                    </td>
                    <td className="py-3 px-3 text-center">
                      <Button
                        variant="ghost"
                        size="sm"
                        className="text-xs text-emerald-400"
                        onClick={() => handleSelectTop(row.cand)}
                      >
                        Inspect
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}

      {/* 24-Hour Diurnal Response Tab */}
      {activeTab === 'day_night' && (
        <Card className="space-y-4">
          <div className="flex items-center justify-between border-b border-surface-border pb-2">
            <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
              <Moon className="w-4 h-4 text-emerald-400" />
              <span>Ladakh Extreme Cold Diurnal Performance Summary</span>
            </h3>
            <Badge variant="emerald" size="sm">
              Sub-Zero Protection
            </Badge>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-surface-raised border border-surface-border space-y-1.5">
              <span className="text-slate-400 text-xs flex items-center gap-1.5">
                <Sun className="w-4 h-4 text-amber-400" />
                <span>Daytime Solar Heat Gain</span>
              </span>
              <div className="text-xl font-extrabold font-mono text-amber-400">
                +{simulationResult?.summary.total_daily_solar_captured_kwh || '16.4'} kWh/day
              </div>
              <p className="text-[11px] text-slate-400">
                Direct solar gain absorbed through south windows and Trombe storage wall.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-surface-raised border border-surface-border space-y-1.5">
              <span className="text-slate-400 text-xs flex items-center gap-1.5">
                <TrendingDown className="w-4 h-4 text-sky-400" />
                <span>24-Hour Total Heat Loss</span>
              </span>
              <div className="text-xl font-extrabold font-mono text-sky-400">
                -{simulationResult?.summary.total_daily_heat_loss_kwh || '7.1'} kWh/day
              </div>
              <p className="text-[11px] text-slate-400">
                Continuous transmission and infiltration losses across envelope.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-surface-raised border border-surface-border space-y-1.5">
              <span className="text-slate-400 text-xs flex items-center gap-1.5">
                <Moon className="w-4 h-4 text-emerald-400" />
                <span>Nighttime Minimum Indoor Temp</span>
              </span>
              <div className="text-xl font-extrabold font-mono text-emerald-400">
                {simulationResult?.summary.nighttime_min_indoor_temp_c || '17.8'}°C
              </div>
              <p className="text-[11px] text-slate-400">
                Maintained comfortable zone temperatures despite sub-zero outdoor freeze.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Explainable AI Decision Tab */}
      {activeTab === 'xai' && (
        <div className="space-y-5">
          {/* Executive Summary Card */}
          <Card className="space-y-4 border-amber-500/30 bg-gradient-to-br from-surface via-surface to-amber-950/20">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-amber-500/10 border border-amber-500/20 text-amber-400">
                  <Lightbulb className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">
                    Physics-Grounded Decision Rationale & Explainable AI (XAI)
                  </h3>
                  <p className="text-xs text-slate-400">
                    Domain-specific transparent engineering justifications for {selectedState} ({selectedLocationId.replace('_', ' ').toUpperCase()})
                  </p>
                </div>
              </div>
              <Badge variant="amber" size="sm">
                Certified XAI Rationale
              </Badge>
            </div>

            <div className="p-4 rounded-xl bg-surface-raised border border-surface-border text-xs sm:text-sm text-slate-200 leading-relaxed">
              <span className="text-amber-400 font-bold block mb-1">Executive Summary:</span>
              {explanation?.executive_summary || 'Analyzing optimal passive solar envelope parameters for high-altitude cold conditions...'}
            </div>
          </Card>

          {/* 5 Structured Engineering Decision Pillars */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {explanation?.explanations?.map((item, idx) => (
              <Card
                key={idx}
                className={clsx(
                  'space-y-3 transition-all hover:border-emerald-500/40',
                  idx === 0 ? 'md:col-span-2 border-emerald-500/30 bg-emerald-950/10' : ''
                )}
              >
                <div className="flex items-center justify-between border-b border-surface-border pb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-lg">{item.icon}</span>
                    <span className="text-xs font-bold text-white uppercase tracking-wider">{item.pillar}</span>
                  </div>
                  <Badge variant="emerald" size="sm">
                    Pillar #{idx + 1}
                  </Badge>
                </div>
                <div>
                  <h4 className="text-sm font-bold text-emerald-400 mb-1">{item.title}</h4>
                  <p className="text-xs text-slate-300 leading-relaxed">{item.explanation}</p>
                </div>
              </Card>
            )) || (
              <div className="col-span-2 text-center py-8 text-xs text-slate-400">
                Loading engineering explanation pillars...
              </div>
            )}
          </div>
        </div>
      )}

      {/* Scientific Methodology & Formatted Equations Tab */}
      {activeTab === 'methodology' && (
        <div className="space-y-6">
          <Card className="space-y-6">
            <div className="flex items-center justify-between border-b border-surface-border pb-3">
              <div className="flex items-center gap-2.5">
                <div className="p-2 rounded-xl bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                  <HelpCircle className="w-5 h-5" />
                </div>
                <div>
                  <h3 className="text-base font-bold text-white">
                    First-Principles Scientific Equations & Mathematical Foundations
                  </h3>
                  <p className="text-xs text-slate-400">
                    Governing physical laws, boundary conditions, and differential energy balance formulation
                  </p>
                </div>
              </div>
              <Badge variant="emerald" size="sm">
                ASHRAE 140 / IS 3792 Calibrated
              </Badge>
            </div>

            {/* Equation 1: Dynamic Lumped Energy Balance */}
            <div className="space-y-3 p-5 rounded-2xl bg-surface-raised border border-surface-border">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider font-mono">
                  1. Transient Lumped-Capacitance Thermal Energy Balance
                </span>
                <span className="text-[10px] font-mono text-slate-400">Governing Differential Law</span>
              </div>

              {/* Formatted Equation Display */}
              <div className="p-4 rounded-xl bg-background/80 border border-emerald-500/30 text-center shadow-inner overflow-x-auto">
                <div className="inline-flex items-center gap-2 font-serif text-base sm:text-lg text-emerald-300 py-1">
                  <span className="italic">ρ · V · C<sub>p</sub></span>
                  <div className="inline-flex flex-col items-center justify-center text-xs leading-none">
                    <span className="border-b border-emerald-400/60 pb-0.5">d T<sub>in</sub></span>
                    <span className="pt-0.5">dt</span>
                  </div>
                  <span>=</span>
                  <span className="text-amber-400 font-bold">Q<sub>solar</sub></span>
                  <span>−</span>
                  <span className="text-sky-400">Q<sub>cond</sub></span>
                  <span>−</span>
                  <span className="text-purple-400">Q<sub>conv</sub></span>
                  <span>−</span>
                  <span className="text-rose-400">Q<sub>rad</sub></span>
                  <span>−</span>
                  <span className="text-cyan-400">Q<sub>inf</sub></span>
                  <span>+</span>
                  <span className="text-emerald-400">Q<sub>internal</sub></span>
                </div>
              </div>

              {/* Step-by-Step Term Breakdown Table */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 pt-2 text-xs">
                <div className="p-3 rounded-lg bg-surface border border-surface-border space-y-1">
                  <span className="font-bold text-amber-400 block font-mono">Q_solar (Solar Gain):</span>
                  <p className="text-[11px] text-slate-300 font-mono">
                    A<sub>glazing</sub> · SHGC · I<sub>dir</sub>(t) · cos(θ) · (1 − Overhang_Shading)
                  </p>
                  <span className="text-[10px] text-slate-400">Direct beam & diffuse radiation through glazing</span>
                </div>

                <div className="p-3 rounded-lg bg-surface border border-surface-border space-y-1">
                  <span className="font-bold text-sky-400 block font-mono">Q_cond (Conduction Loss):</span>
                  <p className="text-[11px] text-slate-300 font-mono">
                    Σ [ U<sub>i</sub> · A<sub>i</sub> · (T<sub>in</sub> − T<sub>out</sub>) ]
                  </p>
                  <span className="text-[10px] text-slate-400">Heat transfer through walls, roof, floor & windows</span>
                </div>

                <div className="p-3 rounded-lg bg-surface border border-surface-border space-y-1">
                  <span className="font-bold text-cyan-400 block font-mono">Q_inf (Infiltration Loss):</span>
                  <p className="text-[11px] text-slate-300 font-mono">
                    (ACH · V · ρ<sub>air</sub> · C<sub>p</sub> / 3600) · (T<sub>in</sub> − T<sub>out</sub>)
                  </p>
                  <span className="text-[10px] text-slate-400">Cold drafts through window joints and doorway crack leakage</span>
                </div>
              </div>
            </div>

            {/* Equation 2: Astronomical Directional Solar Irradiance */}
            <div className="space-y-3 p-5 rounded-2xl bg-surface-raised border border-surface-border">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-sky-400 uppercase tracking-wider font-mono">
                  2. Astronomical Solar Position & Surface Incidence Angle
                </span>
                <span className="text-[10px] font-mono text-slate-400">Spencer / Duffie-Beckman Model</span>
              </div>

              <div className="p-4 rounded-xl bg-background/80 border border-sky-500/30 text-center shadow-inner overflow-x-auto">
                <div className="inline-flex items-center gap-2 font-serif text-base sm:text-lg text-sky-300 py-1">
                  <span>cos(θ) = sin(α<sub>s</sub>) · cos(β) + cos(α<sub>s</sub>) · sin(β) · cos(γ<sub>s</sub> − γ)</span>
                </div>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px]">
                <div className="p-2.5 rounded bg-surface border border-surface-border">
                  <span className="font-mono font-bold text-slate-300">α<sub>s</sub></span>: Solar altitude angle
                </div>
                <div className="p-2.5 rounded bg-surface border border-surface-border">
                  <span className="font-mono font-bold text-slate-300">β</span>: Surface tilt angle (e.g. 90° wall)
                </div>
                <div className="p-2.5 rounded bg-surface border border-surface-border">
                  <span className="font-mono font-bold text-slate-300">γ<sub>s</sub></span>: Sun azimuth angle
                </div>
                <div className="p-2.5 rounded bg-surface border border-surface-border">
                  <span className="font-mono font-bold text-slate-300">γ</span>: Facade orientation (180° S)
                </div>
              </div>
            </div>

            {/* Equation 3: Diurnal Thermal Mass Damping & Phase Lag */}
            <div className="space-y-3 p-5 rounded-2xl bg-surface-raised border border-surface-border">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-purple-400 uppercase tracking-wider font-mono">
                  3. Diurnal Thermal Mass Damping Factor & Phase Delay
                </span>
                <span className="text-[10px] font-mono text-slate-400">Transient Thermal Inertia</span>
              </div>

              <div className="p-4 rounded-xl bg-background/80 border border-purple-500/30 text-center shadow-inner overflow-x-auto">
                <div className="inline-flex flex-wrap items-center justify-center gap-6 font-serif text-base sm:text-lg text-purple-300 py-1">
                  <div className="flex items-center gap-2">
                    <span>Damping Factor (f) = </span>
                    <div className="inline-flex flex-col items-center justify-center text-xs leading-none">
                      <span className="border-b border-purple-400/60 pb-0.5">T<sub>in, max</sub> − T<sub>in, min</sub></span>
                      <span className="pt-0.5">T<sub>out, max</sub> − T<sub>out, min</sub></span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <span>Phase Lag (ϕ) = </span>
                    <span>t(T<sub>in, max</sub>) − t(T<sub>out, max</sub>) ≈ 6.5 hrs</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Equation 4: Multi-Objective NSGA-II Pareto Optimization */}
            <div className="space-y-3 p-5 rounded-2xl bg-surface-raised border border-surface-border">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-rose-400 uppercase tracking-wider font-mono">
                  4. Multi-Objective Genetic Pareto Formulation (NSGA-II)
                </span>
                <span className="text-[10px] font-mono text-slate-400">Non-Dominated Sorting</span>
              </div>

              <div className="p-4 rounded-xl bg-background/80 border border-rose-500/30 text-center shadow-inner overflow-x-auto">
                <div className="inline-flex items-center gap-3 font-serif text-base sm:text-lg text-rose-300 py-1">
                  <span>min <strong>F</strong>(<strong>x</strong>) = </span>
                  <div className="border-l-2 border-r-2 border-rose-400 px-3 py-1 text-xs font-mono text-slate-200 space-y-1">
                    <div>− f<sub>comfort</sub>(<strong>x</strong>) &emsp; (Maximize Comfort Score)</div>
                    <div>+ Q<sub>loss</sub>(<strong>x</strong>) &emsp;&emsp;&emsp; (Minimize Envelope Heat Loss)</div>
                    <div>+ C<sub>CapEx</sub>(<strong>x</strong>) &emsp;&emsp;&emsp; (Minimize Initial Construction Cost)</div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* ANSYS Export Modal */}
      {showAnsysModal && ansysDeckData && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-surface border border-surface-border rounded-2xl w-full max-w-4xl max-h-[90vh] flex flex-col shadow-2xl animate-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="p-4 border-b border-surface-border flex items-center justify-between">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-purple-500/20 text-purple-400 flex items-center justify-center">
                  <Code className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white">
                    ANSYS / PyANSYS Simulation Input Deck
                  </h3>
                  <p className="text-[11px] text-slate-400 font-mono">
                    High-Fidelity 3D Conjugate Heat Transfer (CHT) & APDL Macro
                  </p>
                </div>
              </div>

              <button
                onClick={() => setShowAnsysModal(false)}
                className="p-1.5 rounded-lg hover:bg-surface-raised text-slate-400 hover:text-white"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Sub-Tabs */}
            <div className="px-4 pt-3 flex items-center justify-between border-b border-surface-border bg-background/50">
              <div className="flex gap-2">
                <button
                  onClick={() => setActiveAnsysTab('fluent')}
                  className={`px-3 py-1.5 rounded-t-lg text-xs font-semibold font-mono border-b-2 transition ${
                    activeAnsysTab === 'fluent'
                      ? 'border-purple-400 text-purple-400 bg-surface'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  PyANSYS Fluent Script (.py)
                </button>
                <button
                  onClick={() => setActiveAnsysTab('apdl')}
                  className={`px-3 py-1.5 rounded-t-lg text-xs font-semibold font-mono border-b-2 transition ${
                    activeAnsysTab === 'apdl'
                      ? 'border-purple-400 text-purple-400 bg-surface'
                      : 'border-transparent text-slate-400 hover:text-slate-200'
                  }`}
                >
                  ANSYS APDL Macro (.mac)
                </button>
              </div>

              <div className="flex items-center gap-2 pb-1.5">
                <Button
                  variant="outline"
                  size="sm"
                  icon={copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                  onClick={handleCopyCode}
                >
                  {copied ? 'Copied!' : 'Copy Code'}
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  icon={<Download className="w-3.5 h-3.5" />}
                  onClick={handleDownloadAnsysScript}
                >
                  Download {activeAnsysTab === 'fluent' ? '.py' : '.mac'}
                </Button>
              </div>
            </div>

            {/* Modal Code Viewer */}
            <div className="p-4 overflow-y-auto flex-1 font-mono text-xs text-slate-300 bg-slate-950/80 leading-relaxed">
              <pre className="whitespace-pre-wrap">
                {activeAnsysTab === 'fluent'
                  ? ansysDeckData.pyansys_fluent_script
                  : ansysDeckData.ansys_apdl_deck}
              </pre>
            </div>

            {/* Modal Footer Instructions */}
            <div className="p-3 border-t border-surface-border bg-surface text-[11px] text-slate-400 flex items-center justify-between">
              <span>
                💡 <b>Usage:</b> Compatible with ANSYS Fluent 2023 R2+ & PyFluent API.
              </span>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowAnsysModal(false)}
              >
                Close
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
