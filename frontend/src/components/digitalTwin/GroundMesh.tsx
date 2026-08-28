import React from 'react';
import { GeometryParams } from '../../types';

interface GroundMeshProps {
  geometry: GeometryParams;
  explodedOffset?: number;
}

export const GroundMesh: React.FC<GroundMeshProps> = ({
  geometry,
  explodedOffset = 0,
}) => {
  const { length_m: L, width_m: W } = geometry;
  const groundRadius = Math.max(L, W) * 2.2;

  return (
    <group position={[0, 0, 0]}>
      {/* Foundation Concrete Plinth Slab */}
      <mesh position={[0, 0, 0.1 - explodedOffset * 0.2]} receiveShadow castShadow>
        <boxGeometry args={[L + 0.4, W + 0.4, 0.2]} />
        <meshStandardMaterial color="#57606f" roughness={0.92} metalness={0.05} />
      </mesh>

      {/* Circular Site Podium Disc */}
      <mesh position={[0, 0, -0.01]} receiveShadow>
        <cylinderGeometry args={[groundRadius, groundRadius, 0.02, 64]} />
        <meshStandardMaterial color="#161b22" roughness={0.95} metalness={0.0} />
      </mesh>

      {/* Subtle Circular Terrain Ring */}
      <mesh position={[0, 0, -0.005]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[groundRadius - 0.08, groundRadius, 64]} />
        <meshBasicMaterial color="#30363d" opacity={0.5} transparent />
      </mesh>
    </group>
  );
};
