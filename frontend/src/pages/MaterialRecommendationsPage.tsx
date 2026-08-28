import React, { useEffect, useState } from 'react';
import { useShelterStore } from '../store/shelterStore';
import { fetchEngineeringRecommendations, fetchMaterials } from '../api/endpoints';
import { MaterialItem } from '../types';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import {
  Layers,
  Sparkles,
  Sliders,
  ShieldAlert,
  Coins,
  CheckCircle2,
  HelpCircle,
  TrendingDown,
  Hammer,
  ArrowRight,
  RefreshCw,
  Cpu,
  Table,
  Box,
  Flame,
  Snowflake,
  Activity
} from 'lucide-react';
import { clsx } from 'clsx';
import { useNavigate } from 'react-router-dom';

export const MaterialRecommendationsPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentDesign,
    selectedLocationId,
    selectedState,
    updateMaterials,
    recommendationResult,
    setRecommendationResult,
    isLoadingRecommendations,
    setIsLoadingRecommendations
  } = useShelterStore();

  const [activeTab, setActiveTab] = useState<'recommendations' | 'catalog' | 'composite'>('recommendations');
  const [budgetLevel, setBudgetLevel] = useState<string>('medium');
  const [materialsCatalog, setMaterialsCatalog] = useState<MaterialItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [weights, setWeights] = useState({
    thermal: 35,
    cost: 25,
    resilience: 20,
    constructability: 10,
    availability: 10
  });

  useEffect(() => {
    fetchMaterials()
      .then((data) => setMaterialsCatalog(data))
      .catch((err) => console.error('Failed to load materials catalog:', err));
  }, []);

  const runRecommendationsFetch = async () => {
    setIsLoadingRecommendations(true);
    try {
      const normalizedWeights = {
        thermal: weights.thermal / 100,
        cost: weights.cost / 100,
        resilience: weights.resilience / 100,
        constructability: weights.constructability / 100,
        availability: weights.availability / 100
      };

      const data = await fetchEngineeringRecommendations({
        climate_zone: selectedLocationId.includes('ladakh') ? 'Cold' : 'Composite',
        state_code: selectedState,
        budget_level: budgetLevel,
        shelter_type: currentDesign.archetype || 'Standard Residential',
        disaster_mode: currentDesign.disaster_mode,
        weights: normalizedWeights
      });
      setRecommendationResult(data);
    } catch (err) {
      console.error('Failed to run recommendation engine:', err);
    } finally {
      setIsLoadingRecommendations(false);
    }
  };

  useEffect(() => {
    runRecommendationsFetch();
  }, [selectedState, budgetLevel, currentDesign.disaster_mode]);

  const handleApplyToShelter = (item: string, materialId?: string) => {
    if (!materialId) return;
    if (item === 'WALL SYSTEM' || item === 'Wall') {
      updateMaterials({ wall_mat_id: materialId });
    } else if (item === 'ROOF SYSTEM' || item === 'Roof') {
      updateMaterials({ roof_mat_id: materialId });
    } else if (item === 'INSULATION' || item === 'Insulation') {
      updateMaterials({ insulation_mat_id: materialId });
    } else if (item === 'WINDOW SYSTEM' || item === 'Glazing') {
      updateMaterials({ glazing_mat_id: materialId });
    } else if (item === 'FLOOR SYSTEM' || item === 'Flooring') {
      updateMaterials({ floor_mat_id: materialId });
    } else if (item === 'DOOR SYSTEM' || item === 'Door') {
      updateMaterials({ door_mat_id: materialId });
    }
  };

  const filteredCatalog = selectedCategory === 'All'
    ? materialsCatalog
    : materialsCatalog.filter((m) => m.category === selectedCategory);

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12 animate-in fade-in duration-300">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-surface-border pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-md text-[10px] font-mono uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              04. Materials & Construction
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mt-2 flex items-center gap-3">
            Material & Construction System Recommendations
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Multi-criteria physics evaluation across Wall, Roof, Floor, Windows, Doors, Insulation, and Assembly methods based on local climate exposure, thermo-physical properties, and budget constraints.
          </p>
        </div>

        <div className="flex items-center gap-3 shrink-0">
          <button
            onClick={runRecommendationsFetch}
            disabled={isLoadingRecommendations}
            className="flex items-center gap-2 px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-slate-950 text-xs font-bold shadow-lg shadow-emerald-950/40 transition disabled:opacity-50"
          >
            <RefreshCw className={clsx('w-3.5 h-3.5', isLoadingRecommendations && 'animate-spin')} />
            <span>Re-evaluate Recommendations</span>
          </button>
        </div>
      </div>

      {/* Tab Switcher */}
      <div className="flex items-center gap-2 bg-surface-raised p-1.5 rounded-xl border border-surface-border overflow-x-auto">
        <button
          onClick={() => setActiveTab('recommendations')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'recommendations'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          ✨ Climate-Optimized Recommendations
        </button>
        <button
          onClick={() => setActiveTab('catalog')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'catalog'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          📊 Thermo-Physical Material Database
        </button>
        <button
          onClick={() => setActiveTab('composite')}
          className={`px-4 py-2 rounded-lg text-xs font-semibold shrink-0 transition-all ${
            activeTab === 'composite'
              ? 'bg-emerald-600 text-white shadow-md'
              : 'text-slate-400 hover:text-slate-200'
          }`}
        >
          🧱 Composite Multi-Layer Envelope
        </button>
      </div>

      {/* TAB 1: Climate-Optimized Recommendations */}
      {activeTab === 'recommendations' && (
        <div className="space-y-6">
          {/* Constraints & Multi-Factor Weights Customizer */}
          <div className="p-5 rounded-2xl bg-surface border border-surface-border space-y-4">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div className="flex items-center gap-2">
                <Sliders className="w-4 h-4 text-emerald-400" />
                <span className="text-xs font-bold uppercase tracking-wider text-slate-200">
                  Target Priorities & Weight Allocation
                </span>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-400">Budget Constraint:</span>
                <select
                  value={budgetLevel}
                  onChange={(e) => setBudgetLevel(e.target.value)}
                  className="bg-surface-raised border border-surface-border rounded-lg px-2.5 py-1 text-xs text-white focus:outline-none focus:border-emerald-500"
                >
                  <option value="low">Low Budget (Affordable/Disaster)</option>
                  <option value="medium">Medium (Standard Resilient)</option>
                  <option value="high">High (High Performance/Low-E)</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-5 gap-4 pt-2">
              {Object.entries(weights).map(([key, val]) => (
                <div key={key} className="space-y-1">
                  <div className="flex justify-between text-[11px]">
                    <span className="capitalize text-slate-400 font-medium">{key}</span>
                    <span className="font-mono text-emerald-400 font-bold">{val}%</span>
                  </div>
                  <input
                    type="range"
                    min="5"
                    max="60"
                    value={val}
                    onChange={(e) => setWeights({ ...weights, [key]: Number(e.target.value) })}
                    className="w-full h-1 bg-surface-border rounded-lg appearance-none cursor-pointer accent-emerald-500"
                  />
                </div>
              ))}
            </div>
          </div>

          {/* Recommended System Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {recommendationResult?.material_recommendations?.map((rec, idx) => (
              <div
                key={idx}
                className="p-5 rounded-2xl bg-surface border border-surface-border hover:border-emerald-500/40 transition flex flex-col justify-between space-y-4 group"
              >
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-slate-400 bg-surface-raised px-2 py-0.5 rounded border border-surface-border">
                      {rec.item}
                    </span>
                    <div className="flex items-center gap-1.5">
                      <span className="text-xs font-mono font-bold text-emerald-400">{rec.score}/100</span>
                      <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                    </div>
                  </div>

                  <h3 className="text-base font-bold text-white group-hover:text-emerald-300 transition">
                    {rec.recommended_option}
                  </h3>

                  <div className="p-3 rounded-xl bg-surface-raised/70 border border-surface-border space-y-1 text-xs">
                    <div className="font-semibold text-slate-300 flex items-center gap-1.5">
                      <HelpCircle className="w-3.5 h-3.5 text-emerald-400" />
                      <span>Why this selection?</span>
                    </div>
                    <p className="text-slate-400 leading-relaxed">{rec.reason}</p>
                  </div>

                  <div className="space-y-1.5 text-xs">
                    <div className="flex items-start gap-2 text-slate-300">
                      <TrendingDown className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
                      <span><strong>Thermal Benefit:</strong> {rec.thermal_benefit}</span>
                    </div>
                    <div className="flex items-start gap-2 text-slate-300">
                      <Coins className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
                      <span><strong>Cost Impact:</strong> {rec.cost_impact}</span>
                    </div>
                  </div>
                </div>

                <div className="pt-2 border-t border-surface-border flex items-center justify-between">
                  <span className="text-[10px] text-slate-400 font-mono">Confidence: {rec.confidence}</span>
                  {rec.material_id && (
                    <button
                      onClick={() => handleApplyToShelter(rec.item, rec.material_id)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-600/20 hover:bg-emerald-600 text-emerald-300 hover:text-slate-950 text-xs font-semibold border border-emerald-500/30 transition"
                    >
                      <CheckCircle2 className="w-3.5 h-3.5" />
                      <span>Apply to 3D Model</span>
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* TAB 2: Thermo-Physical Material Database */}
      {activeTab === 'catalog' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 overflow-x-auto">
              {['All', 'Wall', 'Roof', 'Glazing', 'Insulation', 'Flooring', 'Door', 'Shading'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition ${
                    selectedCategory === cat
                      ? 'bg-emerald-600 text-white'
                      : 'bg-surface border border-surface-border text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
            <span className="text-xs font-mono text-slate-400">{filteredCatalog.length} Materials Sourced</span>
          </div>

          <Card className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-surface-border text-slate-400">
                  <th className="py-3 px-3">Material Name</th>
                  <th className="py-3 px-3">Category</th>
                  <th className="py-3 px-3">Thermal Cond (W/m·K)</th>
                  <th className="py-3 px-3">Density (kg/m³)</th>
                  <th className="py-3 px-3">Specific Heat (J/kg·K)</th>
                  <th className="py-3 px-3">Embodied Carbon</th>
                  <th className="py-3 px-3">Unit Cost (₹/m²)</th>
                  <th className="py-3 px-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-border">
                {filteredCatalog.map((mat) => (
                  <tr key={mat.id} className="hover:bg-surface-raised transition-colors">
                    <td className="py-3 px-3 font-semibold text-white">
                      {mat.name}
                      <span className="block text-[10px] text-slate-400 font-mono">{mat.description}</span>
                    </td>
                    <td className="py-3 px-3">
                      <Badge variant="slate" size="sm">{mat.category}</Badge>
                    </td>
                    <td className="py-3 px-3 font-mono text-emerald-400">{mat.thermal_cond_w_mk}</td>
                    <td className="py-3 px-3 font-mono">{mat.density_kg_m3}</td>
                    <td className="py-3 px-3 font-mono">{mat.specific_heat_j_kgk}</td>
                    <td className="py-3 px-3 font-mono">{mat.embodied_carbon_kgco2_kg} kgCO₂/kg</td>
                    <td className="py-3 px-3 font-mono font-semibold">₹{mat.unit_cost_inr_m2}</td>
                    <td className="py-3 px-3 text-right">
                      <button
                        onClick={() => handleApplyToShelter(mat.category, mat.id)}
                        className="px-2.5 py-1 rounded bg-emerald-600/20 hover:bg-emerald-600 text-emerald-300 hover:text-slate-950 text-[11px] font-semibold transition"
                      >
                        Apply
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </Card>
        </div>
      )}

      {/* TAB 3: Composite Multi-Layer Envelope */}
      {activeTab === 'composite' && (
        <Card className="space-y-6">
          <div className="border-b border-surface-border pb-4">
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <Layers className="w-5 h-5 text-emerald-400" />
              <span>Multi-Layer High-Altitude Wall Assembly (Trombe System)</span>
            </h3>
            <p className="text-xs text-slate-400 mt-1">
              Engineered 4-layer envelope configured for sub-zero Ladakh winter conditions: Exterior weather barrier + Continuous sheep wool insulation + High thermal mass Trombe core + Interior timber lining.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
            <div className="p-4 rounded-xl bg-amber-950/20 border border-amber-500/30 space-y-1.5">
              <span className="text-[10px] font-mono uppercase text-amber-400 font-bold">Layer 1 (Exterior)</span>
              <h4 className="font-bold text-white">Mud Plaster / Lime Render</h4>
              <p className="text-slate-400 text-[11px]">Thickness: 2.0 cm | k = 0.40 W/m·K</p>
            </div>

            <div className="p-4 rounded-xl bg-sky-950/20 border border-sky-500/30 space-y-1.5">
              <span className="text-[10px] font-mono uppercase text-sky-400 font-bold">Layer 2 (Insulation)</span>
              <h4 className="font-bold text-white">Indigenous Sheep Wool Batt</h4>
              <p className="text-slate-400 text-[11px]">Thickness: 7.5 cm | k = 0.039 W/m·K</p>
            </div>

            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30 space-y-1.5">
              <span className="text-[10px] font-mono uppercase text-emerald-400 font-bold">Layer 3 (Thermal Mass)</span>
              <h4 className="font-bold text-white">Trombe Earth Storage Masonry</h4>
              <p className="text-slate-400 text-[11px]">Thickness: 30.0 cm | k = 0.85 W/m·K</p>
            </div>

            <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30 space-y-1.5">
              <span className="text-[10px] font-mono uppercase text-purple-400 font-bold">Layer 4 (Interior)</span>
              <h4 className="font-bold text-white">Poplar / Bamboo Board</h4>
              <p className="text-slate-400 text-[11px]">Thickness: 2.0 cm | k = 0.15 W/m·K</p>
            </div>
          </div>

          <div className="p-4 rounded-xl bg-surface-raised border border-surface-border flex flex-wrap items-center justify-between gap-4 text-xs">
            <div>
              <span className="text-slate-400">Composite Wall U-Value:</span>
              <span className="ml-2 font-mono font-bold text-emerald-400 text-sm">0.428 W/m²K</span>
            </div>
            <div>
              <span className="text-slate-400">Total Thermal Mass:</span>
              <span className="ml-2 font-mono font-bold text-sky-400 text-sm">730.0 kJ/m²K</span>
            </div>
            <div>
              <span className="text-slate-400">Total Assembly Thickness:</span>
              <span className="ml-2 font-mono font-bold text-amber-400 text-sm">41.5 cm</span>
            </div>
            <Button
              size="sm"
              variant="primary"
              icon={<Box className="w-3.5 h-3.5" />}
              onClick={() => navigate('/design')}
            >
              Simulate in Design Lab
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};
