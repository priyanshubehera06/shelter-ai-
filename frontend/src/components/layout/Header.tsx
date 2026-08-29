import React, { useEffect, useState } from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { fetchLocations, fetchIPLocation } from '../../api/endpoints';
import { Badge } from '../ui/Badge';
import { MapPin, Crosshair } from 'lucide-react';

export const Header: React.FC = () => {
  const {
    selectedLocationId,
    locationsList,
    setLocationsList,
    setLocationId,
  } = useShelterStore();

  const [isDetectingIp, setIsDetectingIp] = useState(false);

  useEffect(() => {
    fetchLocations()
      .then((data) => setLocationsList(data))
      .catch((err) => console.error('Failed to fetch locations:', err));
  }, [setLocationsList]);

  const activeLoc =
    locationsList.find(
      (l) =>
        l.id === selectedLocationId ||
        (selectedLocationId.includes('leh') && (l.id.includes('leh') || l.city?.toLowerCase() === 'leh'))
    ) ||
    locationsList.find((l) => l.city?.toLowerCase() === 'leh' || l.id.includes('leh')) ||
    locationsList[0];

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

  return (
    <header className="h-16 border-b border-surface-border bg-surface/90 backdrop-blur-md px-6 flex items-center justify-between sticky top-0 z-30">
      {/* Location Selector */}
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
      </div>
    </header>
  );
};

