import React, { useEffect, useState } from 'react';
import { fetchMaterials, fetchDesigns } from '../../api/endpoints';
import { useShelterStore } from '../../store/shelterStore';
import { DesignSelection } from './DesignSelection';
import { BuildingParameters } from './BuildingParameters';
import { MaterialSelection } from './MaterialSelection';
import { MaterialItem } from '../../types';

export const LeftSidebar: React.FC = () => {
  const { setSavedDesigns } = useShelterStore();
  const [materials, setMaterials] = useState<MaterialItem[]>([]);

  useEffect(() => {
    fetchMaterials().then((data) => setMaterials(data));
    fetchDesigns().then((designs) => setSavedDesigns(designs));
  }, [setSavedDesigns]);

  return (
    <aside className="w-[270px] bg-[#11161f] border-r border-[#232c3d] p-3 flex flex-col space-y-4 overflow-y-auto shrink-0 z-20 shadow-lg">
      {/* 1. DESIGN SELECTION */}
      <DesignSelection />

      {/* 2. BUILDING PARAMETERS */}
      <BuildingParameters />

      {/* 3. MATERIAL SELECTION */}
      <MaterialSelection materials={materials} />
    </aside>
  );
};
