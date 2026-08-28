import React from 'react';
import { GeometryParams } from '../../types';

interface PorchMeshProps {
  geometry: GeometryParams;
  explodedOffset?: number;
}

export const PorchMesh: React.FC<PorchMeshProps> = ({
  geometry,
  explodedOffset = 0,
}) => {
  const { length_m: L, width_m: W, height_m: H, overhang_m } = geometry;
  const plinthHeight = 0.35;
  const porchDepth = Math.max(0.9, Math.min(1.6, overhang_m * 1.5 || 1.0));
  const porchWidth = Math.min(2.4, Math.max(1.6, L * 0.35));
  const doorX = -L / 4; // Centered around the entrance door
  const colRadius = 0.06;
  const colHeight = H;

  const yOffset = -explodedOffset * 0.2;

  return (
    <group position={[doorX, yOffset, W / 2 + porchDepth / 2]}>
      {/* 1. Porch Concrete Floor Slab (Flush against facade wall at Z = W/2) */}
      <mesh position={[0, plinthHeight / 2, 0]} receiveShadow castShadow>
        <boxGeometry args={[porchWidth, plinthHeight, porchDepth]} />
        <meshStandardMaterial color="#475569" roughness={0.88} metalness={0.05} />
      </mesh>

      {/* 2. Left Structural Column */}
      <mesh position={[-porchWidth / 2 + 0.15, plinthHeight + colHeight / 2, porchDepth / 2 - 0.12]} castShadow>
        <cylinderGeometry args={[colRadius, colRadius, colHeight, 16]} />
        <meshStandardMaterial color="#1e293b" roughness={0.4} metalness={0.7} />
      </mesh>

      {/* 3. Right Structural Column */}
      <mesh position={[porchWidth / 2 - 0.15, plinthHeight + colHeight / 2, porchDepth / 2 - 0.12]} castShadow>
        <cylinderGeometry args={[colRadius, colRadius, colHeight, 16]} />
        <meshStandardMaterial color="#1e293b" roughness={0.4} metalness={0.7} />
      </mesh>

      {/* 4. Canopy Header Beam */}
      <mesh position={[0, plinthHeight + colHeight, porchDepth / 2 - 0.12]} castShadow>
        <boxGeometry args={[porchWidth + 0.1, 0.12, 0.12]} />
        <meshStandardMaterial color="#1e293b" roughness={0.4} metalness={0.7} />
      </mesh>
    </group>
  );
};
