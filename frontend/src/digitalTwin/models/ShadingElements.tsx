import React from 'react';
import { GeometryParams } from '../../types';

interface ShadingElementsProps {
  geometry: GeometryParams;
}

export const ShadingElements: React.FC<ShadingElementsProps> = ({ geometry }) => {
  const { length_m: L, width_m: W, height_m: H, overhang_m } = geometry;
  const plinthHeight = 0.35;
  const winY = plinthHeight + 0.9 + 1.1 + 0.15;
  const shadeDepth = Math.max(0.4, overhang_m * 0.85);

  return (
    <group>
      {/* Front South Window Louver Shading Canopy */}
      <group position={[L / 4 + 0.1, winY, W / 2 + shadeDepth / 2]}>
        {/* Horizontal Shading Fin Plane */}
        <mesh castShadow receiveShadow>
          <boxGeometry args={[1.6, 0.04, shadeDepth]} />
          <meshStandardMaterial color="#434c5e" roughness={0.5} metalness={0.6} />
        </mesh>
        {/* Left Support Bracket */}
        <mesh position={[-0.75, -0.15, -shadeDepth * 0.2]} rotation={[0.4, 0, 0]}>
          <boxGeometry args={[0.03, 0.35, 0.03]} />
          <meshStandardMaterial color="#2e3440" roughness={0.3} metalness={0.8} />
        </mesh>
        {/* Right Support Bracket */}
        <mesh position={[0.75, -0.15, -shadeDepth * 0.2]} rotation={[0.4, 0, 0]}>
          <boxGeometry args={[0.03, 0.35, 0.03]} />
          <meshStandardMaterial color="#2e3440" roughness={0.3} metalness={0.8} />
        </mesh>
      </group>
    </group>
  );
};
