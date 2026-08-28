import React, { useState } from 'react';
import { MaterialItem } from '../../types';
import { MaterialCard } from '../ui/MaterialCard';
import { SectionTitle } from '../ui/SectionTitle';
import { X, Layers } from 'lucide-react';

interface MaterialPaletteProps {
  materials: MaterialItem[];
  isOpen: boolean;
  onClose: () => void;
  activeCategory?: string;
  selectedMaterialId: string;
  onSelectMaterial: (materialId: string, category: string) => void;
}

export const MaterialPalette: React.FC<MaterialPaletteProps> = ({
  materials,
  isOpen,
  onClose,
  activeCategory = 'Wall',
  selectedMaterialId,
  onSelectMaterial,
}) => {
  const [currentTab, setCurrentTab] = useState<string>(activeCategory);

  if (!isOpen) return null;

  const categories = ['Wall', 'Roof', 'Floor', 'Glazing'];
  const filteredMaterials = materials.filter((m) => m.category === currentTab);

  return (
    <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 animate-in fade-in duration-200">
      <div className="bg-[#11161f] border border-[#232c3d] rounded-xl max-w-2xl w-full p-5 shadow-2xl space-y-4 max-h-[85vh] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-[#232c3d] pb-3">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-emerald-400" />
            <div>
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Engineering Materials Palette
              </h3>
              <p className="text-[11px] text-slate-400">
                PBR Surface Rendering & Certified Physical Thermodynamic Properties
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-[#1c2433]"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Category Tabs */}
        <div className="flex items-center gap-1.5 bg-[#1c2433] p-1 rounded-lg border border-[#232c3d] shrink-0">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setCurrentTab(cat)}
              className={`flex-1 py-1.5 text-xs font-semibold rounded transition-all ${
                currentTab === cat
                  ? 'bg-emerald-600 text-white shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {cat} Materials
            </button>
          ))}
        </div>

        {/* Materials Card Grid */}
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 overflow-y-auto pr-1 py-1">
          {filteredMaterials.map((mat) => (
            <MaterialCard
              key={mat.id}
              material={mat}
              isSelected={selectedMaterialId === mat.id}
              onSelect={() => {
                onSelectMaterial(mat.id, currentTab);
                onClose();
              }}
            />
          ))}
        </div>

        {/* Footer info */}
        <div className="pt-3 border-t border-[#232c3d] flex items-center justify-between text-[11px] text-slate-400 shrink-0">
          <span>* Selected material updates 3D PBR appearance and thermal simulation</span>
          <button
            onClick={onClose}
            className="px-3 py-1 bg-[#1c2433] hover:bg-[#253043] rounded text-slate-200 font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
