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
  Sparkles
} from 'lucide-react';

export const LocationClimatePage: React.FC = () => {
  const navigate = useNavigate();
  const {
    selectedLocationId,
    setLocationId,
    selectedMonth,
    locationsList,
    setLocationsList,
  } = useShelterStore();

  const [analysis, setAnalysis] = useState<ClimateAnalysisResponse | null>(null);
  const [ipData, setIpData] = useState<IPLocationResponse | null>(null);
  const [isDetectingIp, setIsDetectingIp] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedZoneFilter, setSelectedZoneFilter] = useState('All');

  useEffect(() => {
    fetchLocations().then((data) => setLocationsList(data));
  }, [setLocationsList]);

  useEffect(() => {
    fetchClimateAnalysis(selectedLocationId, selectedMonth)
      .then((data) => setAnalysis(data))
      .catch((err) => console.error('Error fetching climate analysis:', err));
  }, [selectedLocationId, selectedMonth]);

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

  const activeLoc = locationsList.find((l) => l.id === selectedLocationId) || locationsList[0];

  // Filtering Indian Cities
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
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-300">
      <SectionHeader
        title="02. Target Location & Climate Setup"
        subtitle="Auto-detect current IP coordinates, browse 50+ major Indian meteorological stations across all states & Union Territories"
        icon={<MapPin className="w-5 h-5 text-emerald-400" />}
        action={
          <Button
            variant="primary"
            icon={<ArrowRight className="w-4 h-4" />}
            onClick={() => navigate('/climate')}
          >
            Proceed to Climate Intelligence
          </Button>
        }
      />

      {/* 1. IP GEOLOCATION AUTO-DETECTION HERO BANNER */}
      <div className="bg-gradient-to-r from-[#11161f] via-[#161d28] to-emerald-950/20 border border-[#232c3d] rounded-xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-lg">
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
            onClick={() => setLocationId('leh_ladakh')}
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

      {/* 2. MAJOR INDIAN CITIES CATALOG WITH SEARCH & ZONE FILTERS */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <Card className="lg:col-span-8 space-y-4">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-[#232c3d] pb-3">
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
                className="w-full bg-[#1c2433] border border-[#232c3d] rounded-lg pl-8 pr-3 py-1.5 text-xs text-slate-100 placeholder:text-slate-500 focus:outline-none focus:border-emerald-500"
              />
            </div>
          </div>

          {/* Climate Zone Filter Tabs */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1">
            <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider shrink-0 mr-1">
              Zone:
            </span>
            {zoneFilters.map((z) => (
              <button
                key={z}
                onClick={() => setSelectedZoneFilter(z)}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-all shrink-0 ${
                  selectedZoneFilter === z
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'bg-[#1c2433] text-slate-400 hover:text-slate-200'
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
                      : 'bg-[#161d28] border-[#232c3d] hover:border-slate-500 hover:bg-[#1d2634]'
                  }`}
                >
                  <div className="flex items-start justify-between gap-1.5">
                    <span className="font-semibold text-xs text-white truncate">{loc.name}</span>
                    {isSelected && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />}
                  </div>
                  <div className="mt-2 text-[10px] text-slate-400 flex items-center justify-between">
                    <span className="truncate">{loc.region_type}</span>
                    <span className="font-mono text-[9px] text-slate-500 shrink-0">
                      {loc.lat.toFixed(1)}°N, {loc.lon.toFixed(1)}°E
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        </Card>

        {/* Selected City Details Card & CSV Uploader */}
        <div className="lg:col-span-4 space-y-4">
          <Card className="space-y-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider border-b border-[#232c3d] pb-2 flex items-center justify-between">
              <span>Active Target Station</span>
              <Badge variant="emerald" size="sm">{activeLoc?.region_type}</Badge>
            </h4>

            <div className="space-y-2 text-xs text-slate-300">
              <div className="font-bold text-base text-white">{activeLoc?.name}</div>
              <p className="text-[11px] text-slate-400 leading-relaxed">
                {activeLoc?.description}
              </p>
              <div className="p-2 bg-[#1c2433] rounded border border-[#232c3d] space-y-1 font-mono text-[10px]">
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
              </div>
            </div>
          </Card>

          {/* Custom CSV Upload */}
          <Card className="space-y-3">
            <h4 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
              <Upload className="w-3.5 h-3.5 text-sky-400" />
              Upload Custom Weather CSV
            </h4>
            <div className="border border-dashed border-[#232c3d] hover:border-emerald-500/50 rounded-lg p-4 text-center cursor-pointer bg-[#0d1117] transition-colors">
              <Upload className="w-5 h-5 text-slate-500 mx-auto mb-1" />
              <span className="text-xs text-slate-300 block">Drag & drop EPW/IMD CSV</span>
              <span className="text-[9px] text-slate-500 mt-0.5 block">Hourly dry-bulb, RH, GHI</span>
            </div>
          </Card>
        </div>
      </div>

      {/* Climate Summary Telemetry */}
      {analysis && (
        <div className="space-y-2.5">
          <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">
            Live Station Meteorological Telemetry ({analysis.summary.location_name})
          </h3>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            <MetricCard
              label="Peak Summer Temp"
              value={analysis.summary.peak_summer_temp}
              unit="°C"
              icon={<Thermometer className="w-4 h-4 text-rose-400" />}
              trend="negative"
            />
            <MetricCard
              label="Min Winter Temp"
              value={analysis.summary.min_winter_temp}
              unit="°C"
              icon={<Thermometer className="w-4 h-4 text-sky-400" />}
              trend="positive"
            />
            <MetricCard
              label="Average Relative Humidity"
              value={analysis.summary.avg_relative_humidity}
              unit="%"
              icon={<Droplets className="w-4 h-4 text-sky-400" />}
              trend="neutral"
            />
            <MetricCard
              label="Peak Solar GHI"
              value={analysis.summary.peak_solar_ghi}
              unit="W/m²"
              icon={<Sun className="w-4 h-4 text-amber-400" />}
              trend="solar"
            />
          </div>
        </div>
      )}
    </div>
  );
};
