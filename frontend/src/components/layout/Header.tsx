import React, { useEffect, useState } from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { fetchLocations, fetchIPLocation } from '../../api/endpoints';
import { Badge } from '../ui/Badge';
import { MapPin, Crosshair, Menu, ShieldCheck } from 'lucide-react';

interface HeaderProps {
  onOpenMobileMenu?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onOpenMobileMenu }) => {
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
    <header className="h-16 border-b border-surface-border bg-surface/90 backdrop-blur-md px-3 sm:px-6 flex items-center justify-between sticky top-0 z-30 shrink-0">
      {/* Mobile Drawer Trigger & Logo */}
      <div className="flex items-center gap-2 md:hidden">
        {onOpenMobileMenu && (
          <button
            onClick={onOpenMobileMenu}
            aria-label="Open navigation menu"
            className="p-2 rounded-xl text-slate-300 hover:text-white hover:bg-surface-raised border border-surface-border min-h-[44px] min-w-[44px] flex items-center justify-center active:scale-95 transition-transform"
          >
            <Menu className="w-5 h-5 text-emerald-400" />
          </button>
        )}
        <div className="flex items-center gap-1.5 font-bold text-sm text-white">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span>SHELTER<span className="text-emerald-400 font-mono">AI</span></span>
        </div>
      </div>

      {/* Location Selector */}
      <div className="flex items-center gap-2 sm:gap-3">
        <div className="flex items-center gap-1.5 sm:gap-2 bg-surface-raised px-2.5 sm:px-3 py-1.5 rounded-xl border border-surface-border text-sm min-h-[44px]">
          <MapPin className="w-4 h-4 text-emerald-400 shrink-0" />
          <select
            value={selectedLocationId}
            onChange={(e) => setLocationId(e.target.value)}
            className="bg-transparent text-slate-100 text-xs font-medium focus:outline-none cursor-pointer max-w-[130px] sm:max-w-[220px] truncate"
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
          className="flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 bg-surface-raised hover:bg-slate-700 border border-surface-border hover:border-emerald-500/40 rounded-xl text-xs text-slate-300 hover:text-emerald-400 transition-all font-medium disabled:opacity-50 min-h-[44px] min-w-[44px] justify-center active:scale-95"
        >
          <Crosshair className={`w-4 h-4 text-emerald-400 ${isDetectingIp ? 'animate-spin' : ''}`} />
          <span className="hidden sm:inline">Auto IP</span>
        </button>
      </div>
    </header>
  );
};


