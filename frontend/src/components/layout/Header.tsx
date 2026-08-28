import React, { useEffect, useState } from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { fetchLocations, fetchIPLocation, runSimulation } from '../../api/endpoints';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';
import { MapPin, Sun, Zap, Crosshair } from 'lucide-react';

export const Header: React.FC = () => {
  const {
    selectedLocationId,
    selectedMonth,
    locationsList,
    setLocationsList,
    setLocationId,
    setMonth,
    currentDesign,
    isSimulating,
    setIsSimulating,
    setSimulationResult,
    simulationResult
  } = useShelterStore();

  const [isDetectingIp, setIsDetectingIp] = useState(false);

  useEffect(() => {
    fetchLocations()
      .then((data) => setLocationsList(data))
      .catch((err) => console.error('Failed to fetch locations:', err));
  }, [setLocationsList]);

  const activeLoc = locationsList.find((l) => l.id === selectedLocationId) || locationsList[0];

  const handleDetectIP = async () => {
    setIsDetectingIp(true);
    try {
      const res = await fetchIPLocation();
      if (res.nearest_station_id) {
        setLocationId(res.nearest_station_id);
      }
    } catch (e) {
      console.error('IP detection error:', e);
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
      console.error('Simulation error:', e);
    } finally {
      setIsSimulating(false);
    }
  };

  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  return (
    <header className="h-16 border-b border-surface-border bg-surface/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Location & Month Selector */}
      <div className="flex items-center gap-3">
        <div className="flex items-center gap-2 bg-surface-raised px-3 py-1.5 rounded-lg border border-surface-border text-sm">
          <MapPin className="w-4 h-4 text-emerald-400 shrink-0" />
          <select
            value={selectedLocationId}
            onChange={(e) => setLocationId(e.target.value)}
            className="bg-transparent text-slate-100 text-xs font-medium focus:outline-none cursor-pointer max-w-[180px] sm:max-w-[240px] truncate"
          >
            {locationsList.map((loc) => (
              <option key={loc.id} value={loc.id} className="bg-surface text-slate-100">
                {loc.name}
              </option>
            ))}
          </select>
          {activeLoc && (
            <Badge variant="emerald" size="sm" className="hidden lg:inline-flex">
              {activeLoc.region_type}
            </Badge>
          )}
        </div>

        {/* IP Auto-detect Button */}
        <button
          onClick={handleDetectIP}
          disabled={isDetectingIp}
          title="Auto-detect location from IP"
          className="flex items-center gap-1.5 px-2.5 py-1.5 bg-surface-raised hover:bg-slate-700 border border-surface-border hover:border-emerald-500/40 rounded-lg text-xs text-slate-300 hover:text-emerald-400 transition-all font-medium disabled:opacity-50"
        >
          <Crosshair className={`w-3.5 h-3.5 text-emerald-400 ${isDetectingIp ? 'animate-spin' : ''}`} />
          <span className="hidden md:inline">Auto-Detect IP</span>
        </button>

        <div className="flex items-center gap-2 bg-surface-raised px-3 py-1.5 rounded-lg border border-surface-border text-sm">
          <Sun className="w-4 h-4 text-amber-400 shrink-0" />
          <select
            value={selectedMonth}
            onChange={(e) => setMonth(parseInt(e.target.value))}
            className="bg-transparent text-slate-100 text-xs font-medium focus:outline-none cursor-pointer"
          >
            {months.map((m, idx) => (
              <option key={idx + 1} value={idx + 1} className="bg-surface text-slate-100">
                {m}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Quick Telemetry & Simulation Trigger */}
      <div className="flex items-center gap-4">
        {simulationResult && (
          <div className="hidden md:flex items-center gap-3 text-xs bg-emerald-950/30 border border-emerald-500/20 px-3 py-1.5 rounded-lg">
            <span className="text-slate-400">Comfort:</span>
            <span className="font-mono font-bold text-emerald-400">
              {simulationResult.summary.comfort_score}%
            </span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">CapEx:</span>
            <span className="font-mono font-bold text-slate-200">
              ₹{simulationResult.summary.total_capex_cost_inr.toLocaleString()}
            </span>
          </div>
        )}

        <Button
          size="sm"
          variant="primary"
          icon={<Zap className="w-3.5 h-3.5" />}
          isLoading={isSimulating}
          onClick={handleQuickSimulate}
        >
          Run Physics Sim
        </Button>
      </div>
    </header>
  );
};
