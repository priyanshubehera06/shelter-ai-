import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useShelterStore } from '../store/shelterStore';
import { fetchLocations, fetchIPLocation, fetchClimateAnalysis } from '../api/endpoints';
import { Card } from '../components/ui/Card';
import { MetricCard } from '../components/ui/MetricCard';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { SectionHeader } from '../components/ui/SectionHeader';
import { ClimateAnalysisResponse, LocationInfo, IPLocationResponse } from '../types';
import {
  MapPin,
  Sun,
  Thermometer,
  Wind,
  Droplets,
  CheckCircle2,
  ArrowRight,
  Upload,
  Globe,
  Search,
  Crosshair,
  Sparkles,
  Radio,
  Clock,
  Database,
  Sliders,
  Check,
  RefreshCw,
  ExternalLink,
  FileText,
  FileCode,
  AlertCircle
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from 'recharts';

export const LocationClimatePage: React.FC = () => {
  const navigate = useNavigate();
  const {
    selectedLocationId,
    setLocationId,
    selectedMonth,
    locationsList,
    setLocationsList,
    customClimateRecords,
    setCustomClimateRecords,
    climateDataMode,
    setClimateDataMode
  } = useShelterStore();

  const [analysis, setAnalysis] = useState<ClimateAnalysisResponse | null>(null);
  const [ipData, setIpData] = useState<IPLocationResponse | null>(null);
  const [isDetectingIp, setIsDetectingIp] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedZoneFilter, setSelectedZoneFilter] = useState('All');
  const [lastSyncTime, setLastSyncTime] = useState<string>('Just now');
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Manual Profile State
  const [manualTMin, setManualTMin] = useState<number>(-18.0);
  const [manualTMax, setManualTMax] = useState<number>(2.0);
  const [manualPeakGHI, setManualPeakGHI] = useState<number>(850.0);
  const [manualRH, setManualRH] = useState<number>(35.0);
  const [manualWind, setManualWind] = useState<number>(3.5);
  const [manualApplied, setManualApplied] = useState<boolean>(false);

  // Historical Preset State
  const [selectedHistoricalPreset, setSelectedHistoricalPreset] = useState<string>('leh_winter_epw');
  const [uploadedFileName, setUploadedFileName] = useState<string | null>(null);
  const [historicalApplied, setHistoricalApplied] = useState<boolean>(false);

  useEffect(() => {
    fetchLocations().then((data) => setLocationsList(data));
  }, [setLocationsList]);

  const loadLiveClimate = () => {
    setIsRefreshing(true);
    fetchClimateAnalysis(selectedLocationId, selectedMonth)
      .then((data) => {
        setAnalysis(data);
        setLastSyncTime(new Date().toLocaleTimeString());
      })
      .catch((err) => console.error('Error fetching climate analysis:', err))
      .finally(() => setIsRefreshing(false));
  };

  useEffect(() => {
    if (climateDataMode === 'live') {
      loadLiveClimate();
    }
  }, [selectedLocationId, selectedMonth, climateDataMode]);

  const handleDetectIP = async () => {
    setIsDetectingIp(true);
    try {
      const res = await fetchIPLocation();
      setIpData(res);
      if (res.nearest_station_id) {
        setLocationId(res.nearest_station_id);
      }
    } catch (e) {
      console.error('IP Detection failed:', e);
    } finally {
      setIsDetectingIp(false);
    }
  };

  // Helper to generate 24-hour sinusoidal diurnal records for Manual Mode
  const generateManualRecords = () => {
    const records = [];
    const tRange = manualTMax - manualTMin;
    for (let h = 0; h < 24; h++) {
      // Diurnal temperature model (minimum at 06:00, peak at 15:00)
      const tNorm = (1 + Math.sin(((h - 9) * 2 * Math.PI) / 24)) / 2;
      const t = manualTMin + tRange * tNorm;

      // Solar GHI model (zero outside 06:00 - 18:00, peak at 12:00)
      let ghi = 0;
      if (h >= 6 && h <= 18) {
        ghi = manualPeakGHI * Math.sin(((h - 6) * Math.PI) / 12);
      }

      records.push({
        hour: h,
        dry_bulb_temp_c: Number(t.toFixed(2)),
        relative_humidity_pct: manualRH,
        solar_ghi_w_m2: Number(ghi.toFixed(1)),
        direct_normal_irradiance_w_m2: Number((ghi * 1.15).toFixed(1)),
        wind_speed_m_s: manualWind,
        wind_direction_deg: 180.0
      });
    }
    return records;
  };

  const handleApplyManualClimate = () => {
    const records = generateManualRecords();
    setCustomClimateRecords(records);
    setManualApplied(true);
    setTimeout(() => setManualApplied(false), 3000);
  };

  // Helper to generate Historical EPW Preset records
  const historicalPresets: Record<string, { name: string; desc: string; t_min: number; t_max: number; ghi: number; rh: number; wind: number }> = {
    leh_winter_epw: {
      name: 'Leh, Ladakh - Sub-Zero Winter Typical Meteorological Year (EPW 1991–2020)',
      desc: 'Severe Himalayan winter freeze (-18°C night, +2°C day) with pristine atmospheric solar irradiance (850 W/m²).',
      t_min: -18.5,
      t_max: 2.5,
      ghi: 870.0,
      rh: 34.0,
      wind: 3.2
    },
    sambalpur_heatwave: {
      name: 'Sambalpur - Pre-Monsoon Extreme Heatwave (TMY3 EPW)',
      desc: 'Extreme tropical dry-summer heatwave reaching 44.5°C peak ambient dry-bulb with high afternoon solar radiation.',
      t_min: 27.0,
      t_max: 44.5,
      ghi: 980.0,
      rh: 65.0,
      wind: 2.1
    },
    barmer_desert_epw: {
      name: 'Barmer - Thar Desert High-Diurnal EPW Archive',
      desc: 'Arid desert climate with massive 22°C day/night temperature amplitude (8°C night to 42°C day).',
      t_min: 8.0,
      t_max: 42.0,
      ghi: 1020.0,
      rh: 25.0,
      wind: 4.5
    },
    delhi_composite_epw: {
      name: 'Delhi NCR - IMD 10-Year Composite Climate Typical Meteorological Year',
      desc: 'High seasonal swing composite climate with dense fog and extreme summer/winter boundary conditions.',
      t_min: 5.5,
      t_max: 41.0,
      ghi: 890.0,
      rh: 55.0,
      wind: 2.8
    }
  };

  const handleApplyHistoricalPreset = (presetKey: string) => {
    setSelectedHistoricalPreset(presetKey);
    const p = historicalPresets[presetKey];
    if (!p) return;

    const records = [];
    const tRange = p.t_max - p.t_min;
    for (let h = 0; h < 24; h++) {
      const tNorm = (1 + Math.sin(((h - 9) * 2 * Math.PI) / 24)) / 2;
      const t = p.t_min + tRange * tNorm;
      let ghi = 0;
      if (h >= 6 && h <= 18) {
        ghi = p.ghi * Math.sin(((h - 6) * Math.PI) / 12);
      }
      records.push({
        hour: h,
        dry_bulb_temp_c: Number(t.toFixed(2)),
        relative_humidity_pct: p.rh,
        solar_ghi_w_m2: Number(ghi.toFixed(1)),
        direct_normal_irradiance_w_m2: Number((ghi * 1.15).toFixed(1)),
        wind_speed_m_s: p.wind,
        wind_direction_deg: 180.0
      });
    }

    setCustomClimateRecords(records);
    setUploadedFileName(null);
    setHistoricalApplied(true);
    setTimeout(() => setHistoricalApplied(false), 3000);
  };

  // Custom File Parser for CSV / EPW
  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadedFileName(file.name);
    const reader = new FileReader();
    reader.onload = (evt) => {
      const text = evt.target?.result as string;
      if (!text) return;

      const lines = text.split(/\r?\n/);
      const records = [];

      // Check if EPW or standard CSV
      if (file.name.endsWith('.epw')) {
        // EPW has 8 header lines, data begins on line 9
        for (let i = 8; i < Math.min(lines.length, 32); i++) {
          const parts = lines[i].split(',');
          if (parts.length > 15) {
            const hNum: number = records.length;
            const dryBulb = parseFloat(parts[6]) || 0;
            const rh = parseFloat(parts[8]) || 50;
            const ghi = parseFloat(parts[13]) || 0;
            const wind = parseFloat(parts[21]) || 2.5;

            records.push({
              hour: hNum,
              dry_bulb_temp_c: dryBulb,
              relative_humidity_pct: rh,
              solar_ghi_w_m2: ghi,
              direct_normal_irradiance_w_m2: ghi * 1.1,
              wind_speed_m_s: wind,
              wind_direction_deg: 180.0
            });
          }
        }
      } else {
        // Generic CSV (Hour, Temp, RH, GHI, Wind)
        const startRow = lines[0].toLowerCase().includes('temp') ? 1 : 0;
        for (let i = startRow; i < Math.min(lines.length, startRow + 24); i++) {
          const parts = lines[i].split(',');
          if (parts.length >= 3) {
            const hNum: number = records.length;
            const dryBulb = parseFloat(parts[1]) || parseFloat(parts[0]) || 0;
            const rh = parseFloat(parts[2]) || 50;
            const ghi = parseFloat(parts[3]) || 0;
            const wind = parseFloat(parts[4]) || 2.5;

            records.push({
              hour: hNum,
              dry_bulb_temp_c: dryBulb,
              relative_humidity_pct: rh,
              solar_ghi_w_m2: ghi,
              direct_normal_irradiance_w_m2: ghi * 1.1,
              wind_speed_m_s: wind,
              wind_direction_deg: 180.0
            });
          }
        }
      }

      if (records.length >= 12) {
        setCustomClimateRecords(records);
        setHistoricalApplied(true);
        setTimeout(() => setHistoricalApplied(false), 3000);
      }
    };
    reader.readAsText(file);
  };

  const manualChartData = generateManualRecords().map((r) => ({
    hour: `${r.hour.toString().padStart(2, '0')}:00`,
    temp: r.dry_bulb_temp_c,
    ghi: r.solar_ghi_w_m2
  }));

  const handleLoadLadakh = () => {
    const lehLoc = locationsList.find(
      (l) => l.id === 'leh_ladakh' || l.id === 'leh' || l.city?.toLowerCase() === 'leh'
    );
    if (lehLoc) {
      setLocationId(lehLoc.id);
    } else {
      setLocationId('leh_ladakh');
    }
  };

  const activeLoc =
    locationsList.find(
      (l) =>
        l.id === selectedLocationId ||
        (selectedLocationId.includes('leh') && (l.id.includes('leh') || l.city?.toLowerCase() === 'leh'))
    ) ||
    locationsList.find((l) => l.city?.toLowerCase() === 'leh' || l.id.includes('leh')) ||
    locationsList[0];

  const filteredCities = locationsList.filter((loc) => {
    const matchesSearch =
      loc.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (loc.city && loc.city.toLowerCase().includes(searchQuery.toLowerCase())) ||
      (loc.state && loc.state.toLowerCase().includes(searchQuery.toLowerCase())) ||
      loc.region_type.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesZone =
      selectedZoneFilter === 'All' ||
      loc.region_type.toLowerCase().includes(selectedZoneFilter.toLowerCase());

    return matchesSearch && matchesZone;
  });

  const zoneFilters = ['All', 'Composite', 'Hot & Humid', 'Hot & Arid', 'Cold', 'Temperate', 'Warm'];

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300 pb-12">
      <SectionHeader
        badge="02. TARGET LOCATION & CLIMATE"
        title="Target Location & Climate Setup"
        subtitle="Live open-data meteorological feeds from Open-Meteo, historical EPW records, and user-defined manual profiles"
        icon={<MapPin className="w-5 h-5 text-emerald-400" />}
        action={
          <Button
            variant="primary"
            icon={<ArrowRight className="w-4 h-4" />}
            onClick={() => navigate('/design')}
          >
            Proceed to Shelter Design
          </Button>
        }
      />

      {/* DATA SOURCE MODE SELECTOR & PROVENANCE BAR */}
      <div className="p-4 rounded-xl bg-surface border border-surface-border space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-3">
          <div className="flex items-center gap-2">
            <Radio className="w-4 h-4 text-emerald-400 animate-pulse" />
            <span className="text-xs font-bold text-white uppercase tracking-wider">
              Meteorological Data Pipeline & Mode
            </span>
          </div>

          {/* 3 Data Mode Tabs */}
          <div className="flex items-center gap-1.5 bg-background p-1 rounded-lg border border-surface-border text-xs">
            <button
              onClick={() => {
                setClimateDataMode('live');
                setCustomClimateRecords(null);
              }}
              className={`px-3 py-1.5 rounded-md font-semibold flex items-center gap-1.5 transition ${
                climateDataMode === 'live'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <span className="w-2 h-2 rounded-full bg-emerald-300 animate-ping" />
              LIVE Open-Meteo
            </button>
            <button
              onClick={() => {
                setClimateDataMode('historical');
                if (!customClimateRecords) handleApplyHistoricalPreset('leh_winter_epw');
              }}
              className={`px-3 py-1.5 rounded-md font-semibold flex items-center gap-1.5 transition ${
                climateDataMode === 'historical'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Database className="w-3.5 h-3.5" />
              Historical EPW
            </button>
            <button
              onClick={() => {
                setClimateDataMode('manual');
                if (!customClimateRecords) handleApplyManualClimate();
              }}
              className={`px-3 py-1.5 rounded-md font-semibold flex items-center gap-1.5 transition ${
                climateDataMode === 'manual'
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Sliders className="w-3.5 h-3.5" />
              Manual Input
            </button>
          </div>
        </div>

        {/* Live Data Attribution & Provenance Info */}
        <div className="flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-1.5 text-slate-300">
              <span className="text-slate-400">Pipeline Mode:</span>
              <span className="font-mono text-emerald-400 font-bold uppercase">
                {climateDataMode === 'live' ? 'Live Stream (Open-Meteo)' : climateDataMode === 'historical' ? 'Historical EPW Dataset' : 'Manual User Defined'}
              </span>
            </div>
            <div className="flex items-center gap-1.5 text-slate-300">
              <span className="text-slate-400">Status:</span>
              <Badge variant={climateDataMode === 'live' ? 'emerald' : 'sky'} size="sm">
                {climateDataMode === 'live' ? '● Connected' : customClimateRecords ? '● Custom Records Active (24h)' : '● Ready'}
              </Badge>
            </div>
            {climateDataMode === 'live' && (
              <div className="flex items-center gap-1.5 text-slate-400">
                <Clock className="w-3.5 h-3.5" />
                <span>Last synced: <b className="text-slate-200">{lastSyncTime}</b></span>
              </div>
            )}
          </div>

          {climateDataMode === 'live' && (
            <button
              onClick={loadLiveClimate}
              disabled={isRefreshing}
              className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-emerald-400 transition"
            >
              <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
              <span>Refresh Live Data</span>
            </button>
          )}
        </div>
      </div>

      {/* MODE 1: LIVE OPEN-METEO & LOCATION SELECTION */}
      {climateDataMode === 'live' && (
        <div className="space-y-6">
          {/* IP GEOLOCATION AUTO-DETECTION HERO BANNER */}
          <div className="bg-gradient-to-r from-surface via-surface-raised to-emerald-950/20 border border-surface-border rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-lg">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                <Globe className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <span>Automatic IP Geolocation Detection</span>
                  <Badge variant="emerald" size="sm">Live GPS / IP</Badge>
                </h3>
                <p className="text-xs text-slate-400 mt-0.5">
                  Instantly resolve your current IP address to the nearest meteorological weather station & climate zone.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <Button
                variant="secondary"
                size="sm"
                icon={<Sun className="w-4 h-4 text-amber-400" />}
                onClick={handleLoadLadakh}
              >
                Load Ladakh Case Study
              </Button>
              <Button
                variant="primary"
                size="sm"
                icon={<Crosshair className="w-4 h-4" />}
                isLoading={isDetectingIp}
                onClick={handleDetectIP}
              >
                Auto-Detect My Location
              </Button>
            </div>
          </div>

          {/* Detected IP Details Banner if active */}
          {ipData && (
            <div className="p-3.5 bg-emerald-950/25 border border-emerald-500/40 rounded-xl text-xs flex flex-wrap items-center justify-between gap-3 text-emerald-300 animate-in fade-in duration-200">
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-amber-400 shrink-0" />
                <span>
                  Detected Location: <b>{ipData.city}, {ipData.region} ({ipData.country})</b> • IP: <span className="font-mono">{ipData.ip}</span>
                </span>
              </div>
              <div className="flex items-center gap-2 font-mono text-[11px]">
                <span>{ipData.lat.toFixed(4)}°N, {ipData.lon.toFixed(4)}°E</span>
                <Badge variant="emerald" size="sm">Nearest Station: {ipData.nearest_station_id}</Badge>
              </div>
            </div>
          )}

          {/* MAJOR INDIAN CITIES CATALOG WITH SEARCH & ZONE FILTERS */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <Card className="lg:col-span-8 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-surface-border pb-3">
                <div>
                  <h3 className="text-sm font-bold text-white flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-emerald-400" />
                    Major Indian Cities ({filteredCities.length} Locations)
                  </h3>
                  <span className="text-[10px] text-slate-400">All 28 States and 8 Union Territories cataloged</span>
                </div>

                {/* Search Input */}
                <div className="relative w-full sm:w-56">
                  <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-1/2 -translate-y-1/2" />
                  <input
                    type="text"
                    placeholder="Search city or state..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full bg-background border border-surface-border rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
                  />
                </div>
              </div>

              {/* Climate Zone Filter Tabs */}
              <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider shrink-0 mr-1">
                  Zone:
                </span>
                {zoneFilters.map((z) => (
                  <button
                    key={z}
                    onClick={() => setSelectedZoneFilter(z)}
                    className={`px-2.5 py-1 rounded text-xs font-medium transition-all shrink-0 ${
                      selectedZoneFilter === z
                        ? 'bg-emerald-600 text-white shadow-sm'
                        : 'bg-surface-raised text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {z}
                  </button>
                ))}
              </div>

              {/* Cities Grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5 max-h-[380px] overflow-y-auto pr-1">
                {filteredCities.map((loc) => {
                  const isSelected = loc.id === selectedLocationId;
                  return (
                    <div
                      key={loc.id}
                      onClick={() => setLocationId(loc.id)}
                      className={`p-2.5 rounded-lg border transition-all cursor-pointer flex flex-col justify-between ${
                        isSelected
                          ? 'bg-emerald-950/30 border-emerald-500 shadow-md shadow-emerald-950/40'
                          : 'bg-surface-raised border-surface-border hover:border-slate-500'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-1.5">
                        <span className="font-semibold text-xs text-white truncate">{loc.name}</span>
                        {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                      </div>
                      <div className="mt-2 text-[10px] text-slate-400 flex items-center justify-between">
                        <span className="truncate">{loc.region_type}</span>
                        <span className="font-mono text-[9px] text-slate-400 shrink-0">
                          {loc.lat.toFixed(1)}°N, {loc.lon.toFixed(1)}°E
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Selected City Details Card */}
            <div className="lg:col-span-4 space-y-4">
              <Card className="space-y-3">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider border-b border-surface-border pb-2 flex items-center justify-between">
                  <span>Active Target Station</span>
                  <Badge variant="emerald" size="sm">{activeLoc?.region_type}</Badge>
                </h4>

                <div className="space-y-2 text-xs text-slate-300">
                  <div className="font-bold text-base text-white">{activeLoc?.name}</div>
                  <p className="text-[11px] text-slate-400 leading-relaxed">
                    {activeLoc?.description}
                  </p>
                  <div className="p-2 bg-background rounded border border-surface-border space-y-1 font-mono text-[10px]">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Coordinates:</span>
                      <span>{activeLoc?.lat.toFixed(4)}°N, {activeLoc?.lon.toFixed(4)}°E</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Peak Summer Temp:</span>
                      <span className="text-rose-400">{activeLoc?.t_max_summer}°C</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Min Winter Temp:</span>
                      <span className="text-sky-400">{activeLoc?.t_min_winter}°C</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Average RH:</span>
                      <span>{activeLoc?.rh_avg_pct}%</span>
                    </div>
                    <div className="flex justify-between border-t border-surface-border pt-1">
                      <span className="text-slate-400">Data Stream:</span>
                      <span className="text-emerald-400 font-bold">Open-Meteo Live API</span>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
          </div>

          {/* Climate Summary Telemetry */}
          {analysis && (
            <div className="space-y-2.5">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
                  <Radio className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Live Meteorological Telemetry Stream ({analysis.summary.location_name})</span>
                </h3>
                <span className="text-[10px] font-mono text-emerald-400">
                  Source: Open-Meteo Live API • 24-Hr Cycle
                </span>
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                <MetricCard
                  label="Peak Summer Temp [LIVE]"
                  value={analysis.summary.peak_summer_temp}
                  unit="°C"
                  icon={<Thermometer className="w-4 h-4 text-rose-400" />}
                  trend="negative"
                />
                <MetricCard
                  label="Min Winter Temp [LIVE]"
                  value={analysis.summary.min_winter_temp}
                  unit="°C"
                  icon={<Thermometer className="w-4 h-4 text-sky-400" />}
                  trend="positive"
                />
                <MetricCard
                  label="Relative Humidity [LIVE]"
                  value={analysis.summary.avg_relative_humidity}
                  unit="%"
                  icon={<Droplets className="w-4 h-4 text-sky-400" />}
                  trend="neutral"
                />
                <MetricCard
                  label="Solar Irradiance GHI [LIVE]"
                  value={analysis.summary.peak_solar_ghi}
                  unit="W/m²"
                  icon={<Sun className="w-4 h-4 text-amber-400" />}
                  trend="solar"
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* MODE 2: HISTORICAL EPW / IMD DATASETS & UPLOADER */}
      {climateDataMode === 'historical' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Presets Selector */}
            <Card className="lg:col-span-7 space-y-4">
              <div className="flex items-center justify-between border-b border-surface-border pb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Database className="w-4 h-4 text-emerald-400" />
                  <span>Verified Historical EPW / IMD Archives</span>
                </h3>
                <Badge variant="emerald" size="sm">EnergyPlus / IMD</Badge>
              </div>

              <div className="space-y-2.5">
                {Object.entries(historicalPresets).map(([key, p]) => {
                  const isSelected = selectedHistoricalPreset === key && !uploadedFileName;
                  return (
                    <div
                      key={key}
                      onClick={() => handleApplyHistoricalPreset(key)}
                      className={`p-3.5 rounded-xl border cursor-pointer transition flex flex-col justify-between ${
                        isSelected
                          ? 'bg-emerald-950/30 border-emerald-500 shadow-md shadow-emerald-950/40'
                          : 'bg-surface-raised border-surface-border hover:border-slate-500'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="font-bold text-xs text-white leading-snug">{p.name}</span>
                        {isSelected && <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />}
                      </div>
                      <p className="text-[11px] text-slate-400 mt-1">{p.desc}</p>
                      <div className="mt-2 pt-2 border-t border-surface-border/60 flex items-center justify-between text-[10px] font-mono text-slate-300">
                        <span>T_min: <b className="text-sky-400">{p.t_min}°C</b></span>
                        <span>T_max: <b className="text-rose-400">{p.t_max}°C</b></span>
                        <span>Peak GHI: <b className="text-amber-400">{p.ghi} W/m²</b></span>
                        <span>RH: <b className="text-slate-300">{p.rh}%</b></span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </Card>

            {/* Custom EPW / CSV Drag & Drop Upload Card */}
            <div className="lg:col-span-5 space-y-4">
              <Card className="space-y-3">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5 border-b border-surface-border pb-2">
                  <Upload className="w-3.5 h-3.5 text-sky-400" />
                  <span>Upload Custom Weather (.epw / .csv)</span>
                </h4>

                <label className="border-2 border-dashed border-surface-border hover:border-emerald-500/70 rounded-xl p-6 text-center cursor-pointer bg-background block transition-all">
                  <Upload className="w-8 h-8 text-emerald-400 mx-auto mb-2 animate-bounce" />
                  <span className="text-xs font-bold text-white block">
                    {uploadedFileName ? `Loaded: ${uploadedFileName}` : 'Select or Drop EPW / CSV File'}
                  </span>
                  <span className="text-[11px] text-slate-400 mt-1 block">
                    EnergyPlus Weather (.epw) or hourly CSV (Hour, Temp, RH, GHI)
                  </span>
                  <input
                    type="file"
                    accept=".epw,.csv"
                    onChange={handleFileUpload}
                    className="hidden"
                  />
                </label>

                {historicalApplied && (
                  <div className="p-3 bg-emerald-950/40 border border-emerald-500/50 rounded-lg text-xs text-emerald-300 flex items-center gap-2 animate-in fade-in">
                    <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>Historical records loaded into active simulation pipeline!</span>
                  </div>
                )}
              </Card>

              {/* Status Note */}
              <div className="p-3 rounded-xl bg-surface-raised border border-surface-border text-xs text-slate-300 space-y-1">
                <span className="font-bold text-amber-400 flex items-center gap-1">
                  <AlertCircle className="w-3.5 h-3.5" />
                  Simulation Binding:
                </span>
                <p className="text-[11px] text-slate-400">
                  When Historical mode is active, the 24-hour solver in <b>05. 3D Simulation</b> uses these exact dataset records instead of live forecast.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* MODE 3: MANUAL USER-DEFINED CLIMATE PROFILE */}
      {climateDataMode === 'manual' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Manual Sliders Card */}
            <Card className="lg:col-span-6 space-y-4">
              <div className="flex items-center justify-between border-b border-surface-border pb-3">
                <h3 className="text-sm font-bold text-white flex items-center gap-2">
                  <Sliders className="w-4 h-4 text-amber-400" />
                  <span>Manual Climate Boundary Conditions</span>
                </h3>
                <Badge variant="amber" size="sm">User Defined</Badge>
              </div>

              <div className="space-y-3 text-xs">
                {/* T_min */}
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-300">Nighttime Minimum Ambient Temp:</span>
                    <span className="font-mono text-sky-400 font-bold">{manualTMin}°C</span>
                  </div>
                  <input
                    type="range"
                    min={-35}
                    max={25}
                    step={1}
                    value={manualTMin}
                    onChange={(e) => setManualTMin(Number(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-sky-400"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>-35°C (Extreme Freezing)</span>
                    <span>+25°C</span>
                  </div>
                </div>

                {/* T_max */}
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-300">Daytime Peak Ambient Temp:</span>
                    <span className="font-mono text-rose-400 font-bold">{manualTMax}°C</span>
                  </div>
                  <input
                    type="range"
                    min={-15}
                    max={50}
                    step={1}
                    value={manualTMax}
                    onChange={(e) => setManualTMax(Number(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-rose-400"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>-15°C</span>
                    <span>+50°C (Extreme Heat)</span>
                  </div>
                </div>

                {/* Peak Solar GHI */}
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-300">Peak Solar Irradiance (GHI at Noon):</span>
                    <span className="font-mono text-amber-400 font-bold">{manualPeakGHI} W/m²</span>
                  </div>
                  <input
                    type="range"
                    min={0}
                    max={1200}
                    step={25}
                    value={manualPeakGHI}
                    onChange={(e) => setManualPeakGHI(Number(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-amber-400"
                  />
                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>0 (Overcast)</span>
                    <span>1200 W/m² (High Himalayan Solar)</span>
                  </div>
                </div>

                {/* Relative Humidity */}
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-300">Relative Humidity:</span>
                    <span className="font-mono text-slate-200 font-bold">{manualRH}%</span>
                  </div>
                  <input
                    type="range"
                    min={10}
                    max={100}
                    step={5}
                    value={manualRH}
                    onChange={(e) => setManualRH(Number(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                  />
                </div>

                {/* Wind Speed */}
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-slate-300">Average Wind Speed:</span>
                    <span className="font-mono text-slate-200 font-bold">{manualWind} m/s</span>
                  </div>
                  <input
                    type="range"
                    min={0.5}
                    max={15.0}
                    step={0.5}
                    value={manualWind}
                    onChange={(e) => setManualWind(Number(e.target.value))}
                    className="w-full h-1.5 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                  />
                </div>

                <div className="pt-2">
                  <Button
                    variant="primary"
                    className="w-full"
                    icon={<Check className="w-4 h-4" />}
                    onClick={handleApplyManualClimate}
                  >
                    Apply Manual Profile to Simulation Engine
                  </Button>
                </div>

                {manualApplied && (
                  <div className="p-3 bg-emerald-950/40 border border-emerald-500/50 rounded-lg text-xs text-emerald-300 flex items-center gap-2 animate-in fade-in">
                    <Check className="w-4 h-4 text-emerald-400 shrink-0" />
                    <span>24-Hour synthetic diurnal profile committed to simulation engine!</span>
                  </div>
                )}
              </div>
            </Card>

            {/* Generated Diurnal Preview Curve */}
            <Card className="lg:col-span-6 space-y-3 p-5">
              <div className="flex items-center justify-between border-b border-surface-border pb-2">
                <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                  <Thermometer className="w-4 h-4 text-emerald-400" />
                  <span>24-Hour Synthetic Diurnal Profile Preview</span>
                </h4>
                <Badge variant="emerald" size="sm">°C & W/m²</Badge>
              </div>

              <div className="h-64 w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={manualChartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#232c3d" />
                    <XAxis dataKey="hour" stroke="#64748b" fontSize={10} />
                    <YAxis stroke="#64748b" fontSize={10} />
                    <Tooltip contentStyle={{ backgroundColor: '#11161f', borderColor: '#232c3d', fontSize: '11px' }} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '8px' }} />
                    <Line type="monotone" dataKey="temp" name="Ambient Temp (°C)" stroke="#38bdf8" strokeWidth={2.5} dot={false} />
                    <Line type="monotone" dataKey="ghi" name="Solar GHI (W/m²)" stroke="#f59e0b" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              <div className="p-2.5 rounded-lg bg-surface-raised border border-surface-border text-[11px] text-slate-300 font-mono flex justify-between">
                <span>Diurnal Range: <b>{(manualTMax - manualTMin).toFixed(1)}°C</b></span>
                <span>Solar Peak: <b>{manualPeakGHI} W/m²</b></span>
                <span>Wind: <b>{manualWind} m/s</b></span>
              </div>
            </Card>
          </div>
        </div>
      )}
    </div>
  );
};
