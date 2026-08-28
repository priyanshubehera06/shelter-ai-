import React from 'react';
import { GeometryParams } from '../../types';

interface FoundationMeshProps {
  geometry: GeometryParams;
  explodedOffset?: number;
}

export const FoundationMesh: React.FC<FoundationMeshProps> = ({
  geometry,
  explodedOffset = 0,
}) => {
  const { length_m: L, width_m: W } = geometry;
  const plinthHeight = 0.35;
  const plinthExt = 0.20;

  const yOffset = -explodedOffset * 0.4;

  return (
    <group position={[0, yOffset, 0]}>
      {/* 1. Main Reinforced Concrete Foundation Plinth */}
      <mesh position={[0, plinthHeight / 2, 0]} receiveShadow castShadow>
        <boxGeometry args={[L + plinthExt * 2, plinthHeight, W + plinthExt * 2]} />
        <meshStandardMaterial color="#3b4252" roughness={0.90} metalness={0.05} />
      </mesh>

      {/* 2. Top Floor Screed Surface Layer */}
      <mesh position={[0, plinthHeight + 0.01, 0]} receiveShadow>
        <boxGeometry args={[L + 0.05, 0.02, W + 0.05]} />
        <meshStandardMaterial color="#4c566a" roughness={0.80} metalness={0.08} />
      </mesh>

      {/* 3. Entrance Steps on Front Facade (+Z South) */}
      <group position={[0.1, 0, W / 2 + plinthExt]}>
        {/* Step 1 (Bottom) */}
        <mesh position={[0, 0.10, 0.45]} receiveShadow castShadow>
          <boxGeometry args={[1.8, 0.18, 0.35]} />
          <meshStandardMaterial color="#434c5e" roughness={0.88} />
        </mesh>
        {/* Step 2 (Middle) */}
        <mesh position={[0, 0.22, 0.18]} receiveShadow castShadow>
          <boxGeometry args={[1.6, 0.16, 0.35]} />
          <meshStandardMaterial color="#434c5e" roughness={0.88} />
        </mesh>
      </group>
    </group>
  );
};
