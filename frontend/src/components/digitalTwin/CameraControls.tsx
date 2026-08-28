import React from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { Camera, RotateCcw } from 'lucide-react';

export const CameraControls: React.FC = () => {
  const { cameraPreset, setCameraPreset } = useShelterStore();

  const presets: Array<{ id: 'isometric' | 'front' | 'side' | 'top' | 'north'; label: string }> = [
    { id: 'isometric', label: 'Isometric' },
    { id: 'front', label: 'Front' },
    { id: 'side', label: 'Side' },
    { id: 'top', label: 'Top' },
  ];

  return (
    <div className="flex items-center gap-1 bg-[#1c2433] p-1 rounded-lg border border-[#232c3d]">
      <Camera className="w-3.5 h-3.5 text-slate-400 ml-1 mr-0.5" />
      {presets.map((p) => {
        const isActive = cameraPreset === p.id;
        return (
          <button
            key={p.id}
            onClick={() => setCameraPreset(p.id)}
            className={`px-2 py-1 rounded text-xs font-medium transition-all ${
              isActive
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            {p.label}
          </button>
        );
      })}
      <button
        onClick={() => setCameraPreset('isometric')}
        title="Reset Camera Angle"
        className="px-1.5 py-1 text-slate-400 hover:text-white rounded hover:bg-[#253043]"
      >
        <RotateCcw className="w-3 h-3" />
      </button>
    </div>
  );
};
