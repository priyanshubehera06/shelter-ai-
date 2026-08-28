import React, { useState } from 'react';
import { useShelterStore } from '../../store/shelterStore';
import { MaterialItem } from '../../types';
import { SectionTitle } from '../ui/SectionTitle';
import { MaterialPalette } from './MaterialPalette';
import { Layers, Palette, Check } from 'lucide-react';

interface MaterialSelectionProps {
  materials: MaterialItem[];
}

export const MaterialSelection: React.FC<MaterialSelectionProps> = ({ materials }) => {
  const { currentDesign, updateMaterials } = useShelterStore();
  const [paletteOpen, setPaletteOpen] = useState(false);
  const [activeCategory, setActiveCategory] = useState('Wall');

  const wallMaterials = materials.filter((m) => m.category === 'Wall');
  const roofMaterials = materials.filter((m) => m.category === 'Roof');
  const glazingMaterials = materials.filter((m) => m.category === 'Glazing');

  const activeWall = wallMaterials.find((m) => m.id === currentDesign.materials.wall_mat_id) || wallMaterials[0];
  const activeRoof = roofMaterials.find((m) => m.id === currentDesign.materials.roof_mat_id) || roofMaterials[0];
  const activeGlazing = glazingMaterials.find((m) => m.id === currentDesign.materials.glazing_mat_id) || glazingMaterials[0];

  const handleOpenPalette = (category: string) => {
    setActiveCategory(category);
    setPaletteOpen(true);
  };

  const handleSelectFromPalette = (matId: string, category: string) => {
    if (category === 'Wall') updateMaterials({ wall_mat_id: matId });
    else if (category === 'Roof') updateMaterials({ roof_mat_id: matId });
    else if (category === 'Glazing') updateMaterials({ glazing_mat_id: matId });
  };

  return (
    <div className="space-y-2.5">
      <SectionTitle
        title="Material Selection"
        icon={<Layers className="w-3.5 h-3.5" />}
        action={
          <button
            onClick={() => handleOpenPalette('Wall')}
            className="flex items-center gap-1 text-[10px] text-emerald-400 hover:text-emerald-300 font-semibold uppercase tracking-wider"
          >
            <Palette className="w-3 h-3" />
            Palette
          </button>
        }
      />

      <div className="space-y-2">
        {/* Wall Material Picker */}
        <div className="bg-[#161d28] border border-[#232c3d] rounded p-2 flex items-center justify-between">
          <div className="flex items-center gap-2 truncate">
            <div
              className="w-5 h-5 rounded border border-black/30 shrink-0"
              style={{ backgroundColor: activeWall?.color_hex || '#b58d6b' }}
            />
            <div className="truncate">
              <span className="text-[10px] text-slate-400 block">Wall Assembly</span>
              <span className="text-xs font-semibold text-white truncate block">
                {activeWall?.name || 'CSEB Interlocking'}
              </span>
            </div>
          </div>
          <button
            onClick={() => handleOpenPalette('Wall')}
            className="px-2 py-1 text-[10px] font-medium bg-[#1c2433] hover:bg-[#253043] rounded text-slate-300 shrink-0"
          >
            Change
          </button>
        </div>

        {/* Roof Material Picker */}
        <div className="bg-[#161d28] border border-[#232c3d] rounded p-2 flex items-center justify-between">
          <div className="flex items-center gap-2 truncate">
            <div
              className="w-5 h-5 rounded border border-black/30 shrink-0"
              style={{ backgroundColor: activeRoof?.color_hex || '#34495e' }}
            />
            <div className="truncate">
              <span className="text-[10px] text-slate-400 block">Roof Assembly</span>
              <span className="text-xs font-semibold text-white truncate block">
                {activeRoof?.name || 'Insulated CGI'}
              </span>
            </div>
          </div>
          <button
            onClick={() => handleOpenPalette('Roof')}
            className="px-2 py-1 text-[10px] font-medium bg-[#1c2433] hover:bg-[#253043] rounded text-slate-300 shrink-0"
          >
            Change
          </button>
        </div>

        {/* Glazing Window Material Picker */}
        <div className="bg-[#161d28] border border-[#232c3d] rounded p-2 flex items-center justify-between">
          <div className="flex items-center gap-2 truncate">
            <div
              className="w-5 h-5 rounded border border-black/30 shrink-0"
              style={{ backgroundColor: activeGlazing?.color_hex || '#81ecec' }}
            />
            <div className="truncate">
              <span className="text-[10px] text-slate-400 block">Window Glazing</span>
              <span className="text-xs font-semibold text-white truncate block">
                {activeGlazing?.name || 'Single Clear Glass'}
              </span>
            </div>
          </div>
          <button
            onClick={() => handleOpenPalette('Glazing')}
            className="px-2 py-1 text-[10px] font-medium bg-[#1c2433] hover:bg-[#253043] rounded text-slate-300 shrink-0"
          >
            Change
          </button>
        </div>
      </div>

      {/* Material Palette Modal */}
      <MaterialPalette
        materials={materials}
        isOpen={paletteOpen}
        onClose={() => setPaletteOpen(false)}
        activeCategory={activeCategory}
        selectedMaterialId={
          activeCategory === 'Wall'
            ? currentDesign.materials.wall_mat_id
            : activeCategory === 'Roof'
            ? currentDesign.materials.roof_mat_id
            : currentDesign.materials.glazing_mat_id
        }
        onSelectMaterial={handleSelectFromPalette}
      />
    </div>
  );
};
