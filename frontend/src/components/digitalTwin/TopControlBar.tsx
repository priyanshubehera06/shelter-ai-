import React, { useState, useEffect } from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { runSimulation, fetchIPLocation } from '../../api/endpoints';
import { IconButton } from '../ui/IconButton';
import { Tooltip } from '../ui/Tooltip';
import {
  MapPin,
  Clock,
  Sun,
  Play,
  Pause,
  RotateCcw,
  Camera,
  Zap,
  Crosshair,
  Globe
} from 'lucide-react';

export const TopControlBar: React.FC = () => {
  const {
    selectedLocationId,
    setLocationId,
    selectedMonth,
    setMonth,
    locationsList,
    simHour,
    setSimHour,
    currentDesign,
    isSimulating,
    setIsSimulating,
    setSimulationResult,
    simulationResult,
  } = useShelterStore();

  const [isPlaying, setIsPlaying] = useState(false);
  const [isDetectingIp, setIsDetectingIp] = useState(false);
  const [selectedSeason, setSelectedSeason] = useState('summer');

  // Animation Loop for Diurnal Sun Tracking
  useEffect(() => {
    let interval: any = null;
    if (isPlaying) {
      interval = setInterval(() => {
        setSimHour((simHour + 0.5) % 24);
      }, 300);
    }
    return () => clearInterval(interval);
  }, [isPlaying, simHour, setSimHour]);

  const activeLoc = locationsList.find((l) => l.id === selectedLocationId) || locationsList[0];

  const handleDetectIP = async () => {
    setIsDetectingIp(true);
    try {
      const res = await fetchIPLocation();
      if (res.nearest_station_id) {
        setLocationId(res.nearest_station_id);
      }
    } catch (e) {
      console.error('IP Detection failed:', e);
    } finally {
      setIsDetectingIp(false);
    }
  };

  const handleQuickSimulate = async () => {
    setIsSimulating(true);
    try {
      const res = await runSimulation({
        location_id: selectedLocationId,
        month: selectedMonth,
        geometry: currentDesign.geometry,
        materials: currentDesign.materials,
        occupants: currentDesign.occupants,
      });
      setSimulationResult(res);
    } catch (e) {
      console.error('Simulation execution error:', e);
    } finally {
      setIsSimulating(false);
    }
  };

  const handleScreenshot = () => {
    const canvas = document.querySelector('canvas');
    if (canvas) {
      const image = canvas.toDataURL('image/png');
      const link = document.createElement('a');
      link.download = `ShelterAI_3D_DigitalTwin_${Date.now()}.png`;
      link.href = image;
      link.click();
    }
  };

  const handleReset = () => {
    setIsPlaying(false);
    setSimHour(12);
  };

  const handleSeasonChange = (season: string) => {
    setSelectedSeason(season);
    if (season === 'summer') setMonth(5); // May
    else if (season === 'monsoon') setMonth(7); // July
    else if (season === 'winter') setMonth(1); // January
    else setMonth(4);
  };

  return (
    <header className="h-14 bg-[#11161f] border-b border-[#232c3d] px-4 flex items-center justify-between text-xs shrink-0 z-30 shadow-md">
      {/* 1. LOCATION SELECTOR & IP AUTO-DETECT */}
      <div className="flex items-center gap-2">
        <div className="flex items-center gap-2 bg-[#1c2433] px-2.5 py-1.5 rounded border border-[#232c3d]">
          <MapPin className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <div className="flex flex-col">
            <select
              value={selectedLocationId}
              onChange={(e) => setLocationId(e.target.value)}
              className="bg-transparent text-slate-100 font-semibold focus:outline-none cursor-pointer text-xs pr-2 max-w-[200px] truncate"
            >
              {locationsList.map((loc) => (
                <option key={loc.id} value={loc.id} className="bg-[#11161f] text-slate-100">
                  {loc.name}
                </option>
              ))}
            </select>
            {activeLoc && (
              <span className="text-[9px] text-slate-400 font-mono">
                {activeLoc.lat.toFixed(2)}°N, {activeLoc.lon.toFixed(2)}°E • {activeLoc.region_type}
              </span>
            )}
          </div>
        </div>

        {/* 1-Click IP Geolocation Auto-Detect Button */}
        <Tooltip content="Auto-detect current IP location & nearest Indian meteorological station">
          <button
            onClick={handleDetectIP}
            disabled={isDetectingIp}
            className="flex items-center gap-1.5 px-2.5 py-1.5 bg-[#1c2433] hover:bg-[#253043] border border-[#232c3d] hover:border-emerald-500/40 rounded text-xs text-slate-300 hover:text-emerald-400 transition-all font-medium disabled:opacity-50"
          >
            <Crosshair className={`w-3.5 h-3.5 text-emerald-400 ${isDetectingIp ? 'animate-spin' : ''}`} />
            <span className="hidden sm:inline">Detect IP</span>
          </button>
        </Tooltip>

        {/* 2. SEASON SELECTOR */}
        <div className="hidden xl:flex items-center gap-1.5 bg-[#1c2433] px-2.5 py-1.5 rounded border border-[#232c3d]">
          <Sun className="w-3.5 h-3.5 text-amber-400" />
          <select
            value={selectedSeason}
            onChange={(e) => handleSeasonChange(e.target.value)}
            className="bg-transparent text-slate-200 font-medium focus:outline-none cursor-pointer text-xs"
          >
            <option value="summer" className="bg-[#11161f]">☀️ Summer (May Peak)</option>
            <option value="monsoon" className="bg-[#11161f]">🌧️ Monsoon (July)</option>
            <option value="winter" className="bg-[#11161f]">❄️ Winter (January)</option>
            <option value="annual" className="bg-[#11161f]">🌐 Annual Average</option>
          </select>
        </div>
      </div>

      {/* 3. TIME OF DAY SLIDER */}
      <div className="flex items-center gap-3 bg-[#1c2433] px-3 py-1.5 rounded border border-[#232c3d]">
        <Clock className="w-3.5 h-3.5 text-slate-400" />
        <span className="font-mono font-bold text-emerald-400 w-12 text-center text-xs">
          {String(Math.floor(simHour)).padStart(2, '0')}:{String(Math.floor((simHour % 1) * 60)).padStart(2, '0')}
        </span>
        <div className="flex flex-col w-28 sm:w-44">
          <input
            type="range"
            min={0}
            max={23.5}
            step={0.5}
            value={simHour}
            onChange={(e) => setSimHour(parseFloat(e.target.value))}
            className="w-full h-1 bg-[#232c3d] rounded appearance-none cursor-pointer accent-emerald-500"
          />
          <div className="flex justify-between text-[9px] text-slate-400 font-mono mt-0.5">
            <span>06:00</span>
            <span>12:00</span>
            <span>18:00</span>
          </div>
        </div>
      </div>

      {/* 4. SIMULATION & INTERACTION CONTROLS */}
      <div className="flex items-center gap-2">
        <Tooltip content={isPlaying ? 'Pause Animation' : 'Play Diurnal Solar Animation'}>
          <IconButton
            icon={isPlaying ? <Pause className="w-3.5 h-3.5" /> : <Play className="w-3.5 h-3.5" />}
            size="sm"
            onClick={() => setIsPlaying(!isPlaying)}
            isActive={isPlaying}
          />
        </Tooltip>

        <Tooltip content="Reset Sun to Noon (12:00)">
          <IconButton
            icon={<RotateCcw className="w-3.5 h-3.5" />}
            size="sm"
            onClick={handleReset}
          />
        </Tooltip>

        <Tooltip content="Capture Viewport Screenshot">
          <IconButton
            icon={<Camera className="w-3.5 h-3.5" />}
            size="sm"
            onClick={handleScreenshot}
          />
        </Tooltip>

        {/* Physics Simulation Trigger */}
        <button
          onClick={handleQuickSimulate}
          disabled={isSimulating}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded bg-emerald-600 hover:bg-emerald-500 text-white font-medium text-xs shadow-sm transition-all active:scale-[0.98] disabled:opacity-50"
        >
          {isSimulating ? (
            <span className="inline-block animate-spin h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full" />
          ) : (
            <Zap className="w-3.5 h-3.5" />
          )}
          <span className="hidden sm:inline">Calculate Physics</span>
        </button>
      </div>
    </header>
  );
};
