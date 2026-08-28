import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useShelterStore } from '../store/shelterStore';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SectionHeader } from '../components/ui/SectionHeader';
import { Badge } from '../components/ui/Badge';
import {
  ShieldCheck,
  MapPin,
  Sun,
  Flame,
  Activity,
  Hammer,
  Box,
  Target,
  GitCompare,
  Award,
  ArrowRight,
  TrendingDown,
  Layers,
  Thermometer,
  Zap,
  CheckCircle2,
  Compass
} from 'lucide-react';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();
  const { setLocationId, setMonth, loadDesign } = useShelterStore();

  const handleExploreLadakh = () => {
    setLocationId('leh_ladakh');
    setMonth(1); // Winter January
    loadDesign({
      name: 'Ladakh Passive Solar Heated Residential Shelter',
      archetype: 'Passive Solar Residential',
      geometry: {
        length_m: 7.0,
        width_m: 5.0,
        height_m: 2.8,
        roof_type: 'pitched',
        roof_pitch_deg: 20.0,
        wall_thickness_cm: 30.0,
        wwr_pct: 20.0,
        overhang_m: 0.5,
        orientation_deg: 180.0, // True South
        door_width_m: 0.9,
        door_height_m: 2.1,
        door_count: 1,
      },
      materials: {
        wall_mat_id: 'trombe_wall_mass',
        wall_thickness_cm: 30.0,
        roof_mat_id: 'roof_insulated_timber_deck',
        insulation_mat_id: 'insulation_sheep_wool',
        insulation_thickness_cm: 7.5,
        glazing_mat_id: 'glazing_double',
        floor_mat_id: 'floor_insulated_screed',
        door_mat_id: 'door_solid_timber',
      },
      occupants: 4,
      location_id: 'leh_ladakh',
    });
    navigate('/design');
  };

  const workflowStages = [
    {
      step: '01',
      title: 'Climate & Atmospheric Profile',
      desc: 'Ambient temperature, solar irradiance (GHI), wind speed, and diurnal temperature swing analysis with Ladakh case study presets.',
      path: '/location',
      icon: <MapPin className="w-5 h-5 text-emerald-400" />,
      tag: 'Meteorology',
      tagVariant: 'emerald' as const,
    },
    {
      step: '02',
      title: 'Parametric Design Lab',
      desc: 'Geometric sizing, True-South solar orientation compass (0°–360°), openings ratio, and thermal mass storage configuration.',
      path: '/design',
      icon: <Hammer className="w-5 h-5 text-amber-400" />,
      tag: 'CAD & Sizing',
      tagVariant: 'amber' as const,
    },
    {
      step: '03',
      title: 'Materials & Multi-Layer Construction',
      desc: 'Composite envelope builder (Trombe wall + sheep wool insulation) and side-by-side material thermal inertia comparison.',
      path: '/recommendations',
      icon: <Layers className="w-5 h-5 text-sky-400" />,
      tag: 'Thermo-physics',
      tagVariant: 'sky' as const,
    },
    {
      step: '04',
      title: '3D Digital Twin Simulation',
      desc: 'Interactive hardware-accelerated WebGL twin with real-time astronomical solar tracking, thermal heatmap, and heat-flow vectors.',
      path: '/digital-twin',
      icon: <Box className="w-5 h-5 text-emerald-400" />,
      tag: 'R3F WebGL',
      tagVariant: 'emerald' as const,
    },
    {
      step: '05',
      title: 'Design A vs B Comparison',
      desc: 'Side-by-side scenario comparator evaluating retrofit options, insulation thicknesses, and avoided discomfort hours.',
      path: '/what-if',
      icon: <GitCompare className="w-5 h-5 text-sky-400" />,
      tag: 'Sensitivity Matrix',
      tagVariant: 'sky' as const,
    },
    {
      step: '06',
      title: 'Pareto Optimization (NSGA-II)',
      desc: 'Multi-objective genetic algorithm minimizing heat loss and CapEx cost while maximizing passive indoor thermal comfort.',
      path: '/optimization',
      icon: <Target className="w-5 h-5 text-rose-400" />,
      tag: 'Genetic Algorithm',
      tagVariant: 'rose' as const,
    },
    {
      step: '07',
      title: 'Certified Results & Scientific Audit',
      desc: '24-hour diurnal thermal response curves, hourly component heat-flow breakdown, and downloadable certified PDF audit.',
      path: '/results',
      icon: <Award className="w-5 h-5 text-emerald-400" />,
      tag: 'Decision Support',
      tagVariant: 'emerald' as const,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-300 pb-12">
      {/* Hero Banner */}
      <div className="relative rounded-3xl p-8 md:p-10 border border-surface-border bg-gradient-to-br from-surface via-surface to-emerald-950/20 shadow-2xl overflow-hidden">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <Compass className="w-3.5 h-3.5" />
            <span>High-Altitude Cold Climate & Multi-Physics Thermal Platform</span>
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white tracking-tight leading-tight uppercase">
            Area-Specific <span className="text-emerald-400">Passive Shelter Design</span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Design and evaluate climate-responsive shelters for improved thermal comfort with reduced external energy requirements.
            Investigate how solar radiation, geometry, orientation, thermal mass, and composite materials eliminate nighttime temperature drops in high-altitude cold regions.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <Button
              size="lg"
              variant="primary"
              icon={<ArrowRight className="w-4 h-4" />}
              onClick={() => navigate('/design')}
            >
              Start Design
            </Button>
            <Button
              size="lg"
              variant="secondary"
              icon={<Sun className="w-4 h-4 text-amber-400" />}
              onClick={handleExploreLadakh}
            >
              Explore Ladakh Case Study
            </Button>
          </div>
        </div>
      </div>

      {/* 3 Core Live Engineering Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <Card className="border-t-4 border-t-amber-500 p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">01. Solar Heat Gain</span>
            <Sun className="w-5 h-5 text-amber-400" />
          </div>
          <div className="text-2xl font-extrabold font-mono text-amber-400">
            +16.4 <span className="text-sm font-normal text-slate-400">kWh/day</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Direct daytime solar capture via South-oriented fenestration (180° azimuth) and Trombe mass absorption.
          </p>
        </Card>

        <Card className="border-t-4 border-t-sky-500 p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">02. Thermal Heat Loss</span>
            <TrendingDown className="w-5 h-5 text-sky-400" />
          </div>
          <div className="text-2xl font-extrabold font-mono text-sky-400">
            -7.1 <span className="text-sm font-normal text-slate-400">kWh/day</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Minimized envelope conductive loss via continuous 75mm sheep wool insulation and double Low-E glazing.
          </p>
        </Card>

        <Card className="border-t-4 border-t-emerald-500 p-5 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">03. Indoor Temperature Lift</span>
            <Thermometer className="w-5 h-5 text-emerald-400" />
          </div>
          <div className="text-2xl font-extrabold font-mono text-emerald-400">
            +18.5 <span className="text-sm font-normal text-slate-400">°C vs Ambient</span>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            Maintains comfortable indoor temperatures (17°C–22°C) without active heating during -15°C sub-zero winter nights.
          </p>
        </Card>
      </div>

      {/* Simplified Engineering Visual Flow */}
      <Card className="p-6 space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
          <Activity className="w-4 h-4 text-emerald-400" />
          <span>Passive Thermal Engineering Workflow</span>
        </h3>

        <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-5 gap-3 text-center text-xs">
          <div className="p-3 rounded-xl bg-surface-raised border border-surface-border">
            <span className="font-bold text-slate-200">1. Climate & Solar</span>
            <p className="text-[11px] text-slate-400 mt-1">NOAA solar radiation & sub-zero ambient</p>
          </div>
          <div className="p-3 rounded-xl bg-surface-raised border border-surface-border">
            <span className="font-bold text-slate-200">2. Sizing & Orientation</span>
            <p className="text-[11px] text-slate-400 mt-1">Parametric 3D CAD & True-South azimuth</p>
          </div>
          <div className="p-3 rounded-xl bg-surface-raised border border-surface-border">
            <span className="font-bold text-slate-200">3. Multi-Layer Materials</span>
            <p className="text-[11px] text-slate-400 mt-1">Trombe mass & high R-value insulation</p>
          </div>
          <div className="p-3 rounded-xl bg-surface-raised border border-surface-border">
            <span className="font-bold text-slate-200">4. Transient RC Balance</span>
            <p className="text-[11px] text-slate-400 mt-1">24-hour heat flow & Day/Night curves</p>
          </div>
          <div className="p-3 rounded-xl bg-surface-raised border border-surface-border col-span-2 sm:col-span-1">
            <span className="font-bold text-emerald-400">5. Pareto Optimization</span>
            <p className="text-[11px] text-slate-400 mt-1">Cost vs Comfort multi-objective search</p>
          </div>
        </div>
      </Card>

      {/* Computational Pipeline Modules */}
      <div>
        <SectionHeader
          title="Modular Platform Pipeline"
          subtitle="Explore the 7 core computational modules of the ShelterAI platform"
          icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mt-4">
          {workflowStages.map((stage) => (
            <Card
              key={stage.step}
              className="flex flex-col justify-between hover:border-emerald-500/40 transition-all cursor-pointer group"
              onClick={() => navigate(stage.path)}
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="p-2 rounded-xl bg-surface-raised border border-surface-border group-hover:border-emerald-500/30 transition-all">
                    {stage.icon}
                  </div>
                  <Badge variant={stage.tagVariant} size="sm">
                    {stage.tag}
                  </Badge>
                </div>
                <h3 className="font-bold text-slate-100 text-sm group-hover:text-emerald-400 transition-colors">
                  {stage.step}. {stage.title}
                </h3>
                <p className="text-xs text-slate-400 leading-relaxed">
                  {stage.desc}
                </p>
              </div>
              <div className="pt-4 flex items-center justify-between text-xs font-semibold text-emerald-400 border-t border-surface-border mt-4">
                <span>Launch Module</span>
                <ArrowRight className="w-3.5 h-3.5 transform group-hover:translate-x-1 transition-transform" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
