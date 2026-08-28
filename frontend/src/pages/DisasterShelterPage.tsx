import React, { useState } from 'react';
import { useShelterStore } from '../store/shelterStore';
import {
  Flame,
  Waves,
  Wind,
  Activity,
  CloudRain,
  SunMedium,
  Users,
  Box,
  Truck,
  ShieldAlert,
  ArrowRight,
  CheckCircle2,
  AlertTriangle,
  Info
} from 'lucide-react';
import { clsx } from 'clsx';
import { useNavigate } from 'react-router-dom';

export const DisasterShelterPage: React.FC = () => {
  const navigate = useNavigate();
  const {
    currentDesign,
    activeDesignMode,
    setActiveDesignMode,
    activeDisasterHazard,
    setActiveDisasterHazard,
    migrantModuleCount,
    setMigrantModuleCount,
    updateGeometry,
    updateMaterials,
    setOccupants
  } = useShelterStore();

  const [activeTab, setActiveTab] = useState<'disaster' | 'migrant'>(
    activeDesignMode === 'migrant' ? 'migrant' : 'disaster'
  );

  // Disaster Hazards catalog
  const disasterHazards = [
    {
      id: 'Heatwave',
      name: 'Heatwave & Extreme Solar',
      icon: <Flame className="w-5 h-5 text-rose-400" />,
      color: 'rose',
      priorities: [
        'High Solar Reflectance Index (SRI > 80) cool roof coating',
        'Continuous 50mm Rockwool thermal barrier',
        'Deep overhangs (>0.8m) on South/West facades',
        'Induced night-purge ventilation openings'
      ],
      autoConfig: {
        roof_mat_id: 'roof_cool_tile',
        wall_mat_id: 'aac_block',
        insulation_mat_id: 'insulation_rockwool',
        insulation_thickness_cm: 5.0,
        overhang_m: 0.85
      }
    },
    {
      id: 'Flood',
      name: 'Flood & Inundation Resilient',
      icon: <Waves className="w-5 h-5 text-cyan-400" />,
      color: 'cyan',
      priorities: [
        'Elevated stilt / plinth height (0.8 - 1.2m above high water mark)',
        'Moisture-resistant CSEB / treated bamboo framing',
        'Quick-drain impervious concrete subfloor',
        'Raised electrical conduit line'
      ],
      autoConfig: {
        roof_mat_id: 'roof_cgi_insulated',
        wall_mat_id: 'cseb_interlocking',
        floor_mat_id: 'floor_concrete_screed',
        plinth_height_m: 1.0,
        overhang_m: 0.7
      }
    },
    {
      id: 'Cyclone',
      name: 'Tropical Cyclone & High Wind',
      icon: <Wind className="w-5 h-5 text-amber-400" />,
      color: 'amber',
      priorities: [
        'Aerodynamic hipped / 25° pitched roof profile minimizing uplift suction',
        'J-bolt hurricane tie connections into RCC tie-beams',
        'High-impact storm shutter window protection',
        'Weatherstripped perimeter gaskets'
      ],
      autoConfig: {
        roof_type: 'hipped',
        roof_pitch_deg: 25.0,
        roof_mat_id: 'roof_concrete_slab',
        wall_mat_id: 'brick_standard',
        door_mat_id: 'door_insulated_metal',
        overhang_m: 0.45
      }
    },
    {
      id: 'Earthquake',
      name: 'Seismic Ductile Shelter',
      icon: <Activity className="w-5 h-5 text-purple-400" />,
      color: 'purple',
      priorities: [
        'Lightweight ductile envelope with low inertial mass',
        'Symmetrical rectangular floor plan (aspect ratio <= 1.5)',
        'Continuous reinforced lintel and plinth tie-bands',
        'Flexible joint connections'
      ],
      autoConfig: {
        roof_type: 'pitched',
        roof_mat_id: 'roof_cgi_insulated',
        wall_mat_id: 'eps_sandwich',
        overhang_m: 0.5
      }
    },
    {
      id: 'Extreme Rain',
      name: 'Extreme Monsoon Rainfall',
      icon: <CloudRain className="w-5 h-5 text-blue-400" />,
      color: 'blue',
      priorities: [
        'Steep roof pitch (>30°) for rapid stormwater evacuation',
        'Deep eave overhangs (>0.9m) preventing wall saturation',
        'Perimeter gutter catchments with rainwater harvesting',
        'Breathable lime plaster finishes'
      ],
      autoConfig: {
        roof_type: 'pitched',
        roof_pitch_deg: 30.0,
        roof_mat_id: 'roof_bamboo_thatch',
        wall_mat_id: 'cseb_interlocking',
        overhang_m: 1.0
      }
    }
  ];

  const handleSelectHazard = (hazard: typeof disasterHazards[0]) => {
    setActiveDesignMode('disaster');
    setActiveDisasterHazard(hazard.id);
    if (hazard.autoConfig) {
      const { roof_type, roof_pitch_deg, overhang_m, plinth_height_m, ...mats } = hazard.autoConfig as any;
      updateGeometry({
        ...(roof_type && { roof_type }),
        ...(roof_pitch_deg && { roof_pitch_deg }),
        ...(overhang_m && { overhang_m }),
        ...(plinth_height_m && { plinth_height_m })
      });
      updateMaterials(mats);
    }
  };

  const handleSelectMigrant = (modulesCount: number) => {
    setActiveDesignMode('migrant');
    setActiveDisasterHazard(null);
    setMigrantModuleCount(modulesCount);

    // Dynamic sizing based on modular units (6x4m per pod)
    const occupantsTotal = modulesCount * 6; // 6 people per 24m² module = 4m²/person (Sphere standard)
    setOccupants(occupantsTotal);
    updateGeometry({
      length_m: 6.0 * Math.min(2, modulesCount),
      width_m: 4.0 * Math.ceil(modulesCount / 2),
      height_m: 2.8,
      roof_type: 'pitched',
      roof_pitch_deg: 15.0,
      wwr_pct: 18.0,
      overhang_m: 0.75
    });
    updateMaterials({
      wall_mat_id: 'cseb_interlocking',
      roof_mat_id: 'roof_cgi_insulated',
      insulation_mat_id: 'insulation_rockwool',
      insulation_thickness_cm: 5.0,
      glazing_mat_id: 'glazing_louvers'
    });
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto pb-12">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-surface-border pb-6">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-1 rounded-md text-[10px] font-mono uppercase tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/20">
              Module 09 — Humanitarian & Disaster Modes
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-white mt-2 flex items-center gap-3">
            Disaster Relief & Migrant Temporary Housing Mode
          </h1>
          <p className="text-sm text-slate-400 mt-1 max-w-3xl">
            Dedicated design configurations tailored for rapid emergency deployment, extreme natural hazards (Heatwaves, Floods, Cyclones, Earthquakes), and high-density humanitarian worker housing.
          </p>
        </div>

        {/* Tab Switcher */}
        <div className="flex items-center gap-2 bg-surface p-1 rounded-xl border border-surface-border shrink-0">
          <button
            onClick={() => setActiveTab('disaster')}
            className={clsx(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition',
              activeTab === 'disaster'
                ? 'bg-amber-500 text-slate-950 shadow-md shadow-amber-950/40'
                : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <ShieldAlert className="w-4 h-4" />
            <span>Disaster Shelter Mode</span>
          </button>
          <button
            onClick={() => setActiveTab('migrant')}
            className={clsx(
              'flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-semibold transition',
              activeTab === 'migrant'
                ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-950/40'
                : 'text-slate-400 hover:text-slate-200'
            )}
          >
            <Users className="w-4 h-4" />
            <span>Migrant / Temporary Housing</span>
          </button>
        </div>
      </div>

      {/* Non-Structural Certification Disclaimer */}
      <div className="p-4 rounded-xl bg-surface/80 border border-amber-500/30 flex items-start gap-3.5 text-xs text-slate-300">
        <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="space-y-0.5">
          <p className="font-semibold text-amber-300">Preliminary Climate-Resilience Engineering Planning</p>
          <p className="text-slate-400">
            ShelterAI recommendations provide early-stage envelope, passive ventilation, and thermal protection strategies. <strong>Final structural framing and anchoring must be verified by a qualified structural engineer.</strong>
          </p>
        </div>
      </div>

      {/* DISASTER MODE CONTENT */}
      {activeTab === 'disaster' && (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-base font-bold text-white flex items-center gap-2">
              <ShieldAlert className="w-5 h-5 text-amber-400" />
              <span>Select Disaster Hazard Profile</span>
            </h2>
            <span className="text-xs font-mono text-slate-400">Auto-tunes Geometry & Materials</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {disasterHazards.map((haz) => {
              const isSelected = activeDesignMode === 'disaster' && activeDisasterHazard === haz.id;
              return (
                <div
                  key={haz.id}
                  onClick={() => handleSelectHazard(haz)}
                  className={clsx(
                    'p-5 rounded-2xl bg-surface border flex flex-col justify-between space-y-4 cursor-pointer transition-all hover:scale-[1.01]',
                    isSelected
                      ? 'border-amber-500 ring-2 ring-amber-500/20 bg-amber-950/15 shadow-xl shadow-amber-950/20'
                      : 'border-surface-border hover:border-surface-border/80'
                  )}
                >
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <div className="p-2.5 rounded-xl bg-surface-raised border border-surface-border">
                        {haz.icon}
                      </div>
                      {isSelected && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-amber-500 text-slate-950 font-bold">
                          Active Mode
                        </span>
                      )}
                    </div>

                    <h3 className="text-base font-bold text-white">{haz.name}</h3>

                    <div className="space-y-1.5 text-xs text-slate-300">
                      <div className="font-semibold text-slate-400 text-[11px] uppercase font-mono tracking-wider">
                        Design Priorities:
                      </div>
                      {haz.priorities.map((p, idx) => (
                        <div key={idx} className="flex items-start gap-1.5 text-[11px] text-slate-300">
                          <span className="text-amber-400 font-bold">✓</span>
                          <span>{p}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="pt-3 border-t border-surface-border flex justify-between items-center text-xs">
                    <span className="text-slate-400 text-[10px] font-mono">Rapid Deployment</span>
                    <button className="text-amber-400 font-bold text-xs flex items-center gap-1">
                      <span>Apply Preset</span>
                      <ArrowRight className="w-3.5 h-3.5" />
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* MIGRANT / TEMPORARY HOUSING MODE CONTENT */}
      {activeTab === 'migrant' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-surface border border-surface-border space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-border pb-4">
              <div>
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                  <Users className="w-5 h-5 text-emerald-400" />
                  <span>Modular High-Density Migrant Housing</span>
                </h2>
                <p className="text-xs text-slate-400 mt-1">
                  Configure repeatable modular pods meeting Sphere Humanitarian Standards for floor area, privacy, and cross ventilation.
                </p>
              </div>

              <div className="flex items-center gap-3">
                <span className="text-xs text-slate-400 font-mono">Cluster Layout:</span>
                {[1, 2, 4, 8].map((mods) => (
                  <button
                    key={mods}
                    onClick={() => handleSelectMigrant(mods)}
                    className={clsx(
                      'px-3.5 py-1.5 rounded-lg text-xs font-bold font-mono transition',
                      migrantModuleCount === mods && activeDesignMode === 'migrant'
                        ? 'bg-emerald-500 text-slate-950 shadow-md shadow-emerald-950/40'
                        : 'bg-surface-raised border border-surface-border text-slate-300 hover:text-white'
                    )}
                  >
                    {mods} {mods === 1 ? 'Pod' : 'Pods'}
                  </button>
                ))}
              </div>
            </div>

            {/* Modular Layout Visual representation */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {Array.from({ length: migrantModuleCount }).map((_, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-surface-raised border border-emerald-500/30 space-y-3">
                  <div className="flex items-center justify-between text-xs">
                    <span className="font-mono font-bold text-emerald-400">MODULE {String.fromCharCode(65 + idx)}</span>
                    <span className="text-[10px] font-mono text-slate-400">24.0 m²</span>
                  </div>
                  <div className="h-20 bg-background rounded-lg border border-dashed border-slate-700 flex items-center justify-center text-xs text-slate-400 font-mono">
                    6.0m × 4.0m Living Zone (6 Occupants)
                  </div>
                  <div className="flex justify-between text-[11px] text-slate-300">
                    <span>Capacity: 6 Persons</span>
                    <span className="font-mono text-emerald-400">4.0 m²/person</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Humanitarian Metrics Bar */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 pt-2">
              <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border">
                <div className="text-[10px] text-slate-400 font-mono uppercase">Total Capacity</div>
                <div className="text-xl font-mono font-bold text-emerald-400">{migrantModuleCount * 6} People</div>
              </div>
              <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border">
                <div className="text-[10px] text-slate-400 font-mono uppercase">Total Usable Area</div>
                <div className="text-xl font-mono font-bold text-white">{migrantModuleCount * 24} m²</div>
              </div>
              <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border">
                <div className="text-[10px] text-slate-400 font-mono uppercase">Sphere Allocation</div>
                <div className="text-xl font-mono font-bold text-cyan-400">4.0 m² / person</div>
              </div>
              <div className="p-3.5 rounded-xl bg-surface-raised border border-surface-border">
                <div className="text-[10px] text-slate-400 font-mono uppercase">Est. Assembly Time</div>
                <div className="text-xl font-mono font-bold text-amber-400">{migrantModuleCount * 2} Days</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Bottom Action */}
      <div className="flex justify-end">
        <button
          onClick={() => navigate('/design')}
          className="flex items-center gap-2 px-5 py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-bold text-xs shadow-xl shadow-emerald-950/40 transition"
        >
          <span>Open in Interactive Design Simulator</span>
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
