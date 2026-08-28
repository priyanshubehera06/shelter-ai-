import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SectionHeader } from '../components/ui/SectionHeader';
import { Badge } from '../components/ui/Badge';
import {
  ShieldCheck,
  MapPin,
  CloudSun,
  Hammer,
  Box,
  Target,
  GitCompare,
  Award,
  ArrowRight,
  Sparkles,
  Zap,
  Activity
} from 'lucide-react';

export const HomePage: React.FC = () => {
  const navigate = useNavigate();

  const pipelineStages = [
    {
      step: '01',
      title: 'Location & Climate Setup',
      desc: 'Select from major meteorological stations or upload custom weather CSVs with automatic solar and psychrometric validation.',
      path: '/location',
      icon: <MapPin className="w-5 h-5 text-emerald-400" />,
      tag: 'Data Ingestion',
      tagVariant: 'emerald' as const,
    },
    {
      step: '02',
      title: 'Climate Intelligence',
      desc: 'Deep micro-climate diagnostics, extreme heatwave stress analysis, diurnal temperature swings, and passive architectural heuristics.',
      path: '/climate',
      icon: <CloudSun className="w-5 h-5 text-sky-400" />,
      tag: 'Physics Analytics',
      tagVariant: 'sky' as const,
    },
    {
      step: '03',
      title: 'Parametric Design Lab',
      desc: 'Dynamic 3D geometric sizing, occupancy standards (Sphere humanitarian standard), and layered envelope U-value calculation.',
      path: '/design',
      icon: <Hammer className="w-5 h-5 text-amber-400" />,
      tag: 'Generative CAD',
      tagVariant: 'amber' as const,
    },
    {
      step: '04',
      title: '3D Digital Twin',
      desc: 'Interactive hardware-accelerated WebGL digital twin with real-time astronomical solar tracking, Sol-Air heatmaps, and camera presets.',
      path: '/digital-twin',
      icon: <Box className="w-5 h-5 text-emerald-400" />,
      tag: 'R3F WebGL',
      tagVariant: 'emerald' as const,
    },
    {
      step: '05',
      title: 'Pareto Optimization (NSGA-II)',
      desc: 'Evolutionary multi-objective search simultaneously optimizing Thermal Comfort (PMV), Operational Energy, and CapEx Construction Cost.',
      path: '/optimization',
      icon: <Target className="w-5 h-5 text-rose-400" />,
      tag: 'Genetic Algorithm',
      tagVariant: 'rose' as const,
    },
    {
      step: '06',
      title: 'What-If Sensitivity Lab',
      desc: 'Side-by-side scenario comparator evaluating retrofit options, insulation thicknesses, and avoided discomfort hours.',
      path: '/what-if',
      icon: <GitCompare className="w-5 h-5 text-amber-400" />,
      tag: 'Sensitivity Matrix',
      tagVariant: 'amber' as const,
    },
    {
      step: '07',
      title: 'Certified Results & XAI',
      desc: 'Top 4 recommended climate-adaptive alternatives, transparent Explainable AI decision narratives, and certified PDF audit generation.',
      path: '/results',
      icon: <Award className="w-5 h-5 text-emerald-400" />,
      tag: 'Decision Support',
      tagVariant: 'emerald' as const,
    },
  ];

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Hero Banner */}
      <div className="relative rounded-3xl p-8 md:p-10 border border-surface-border bg-gradient-to-br from-surface via-surface to-emerald-950/20 shadow-2xl overflow-hidden">
        <div className="absolute top-0 right-0 -mt-8 -mr-8 w-72 h-72 bg-emerald-500/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-3xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI-Driven Climate-Adaptive Shelter Engineering Platform</span>
          </div>

          <h1 className="text-3xl sm:text-4xl md:text-5xl font-extrabold text-white tracking-tight leading-tight">
            Design Thermal Comfort & Resilient Shelters with <span className="text-emerald-400">Physics AI</span>
          </h1>

          <p className="text-slate-300 text-sm sm:text-base leading-relaxed">
            Software-based model development for design of area-specific shelters. Seamlessly bridges
            empirical meteorological data, lumped RC transient thermodynamic models, NSGA-II genetic optimization,
            and an interactive 3D WebGL Digital Twin.
          </p>

          <div className="pt-2 flex flex-wrap items-center gap-3">
            <Button
              size="lg"
              variant="primary"
              icon={<ArrowRight className="w-4 h-4" />}
              onClick={() => navigate('/location')}
            >
              Start Engineering Workflow
            </Button>
            <Button
              size="lg"
              variant="secondary"
              icon={<Box className="w-4 h-4" />}
              onClick={() => navigate('/digital-twin')}
            >
              Launch 3D Digital Twin
            </Button>
          </div>
        </div>
      </div>

      {/* Engineering Workflow Architecture Cards */}
      <div>
        <SectionHeader
          title="Modular Platform Pipeline"
          subtitle="Explore the 7 core computational modules of the ShelterAI platform"
          icon={<ShieldCheck className="w-5 h-5 text-emerald-400" />}
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {pipelineStages.map((stage) => (
            <Card
              key={stage.path}
              hoverable
              onClick={() => navigate(stage.path)}
              className="flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-xs font-bold text-slate-500">{stage.step}</span>
                    <div className="p-2 rounded-lg bg-surface-raised border border-surface-border">
                      {stage.icon}
                    </div>
                  </div>
                  <Badge variant={stage.tagVariant} size="sm">
                    {stage.tag}
                  </Badge>
                </div>

                <h3 className="text-base font-bold text-white group-hover:text-emerald-400 transition-colors">
                  {stage.title}
                </h3>
                <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                  {stage.desc}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-surface-border flex items-center justify-between text-xs text-emerald-400 font-medium">
                <span>Launch Module</span>
                <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-1 transition-transform" />
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
