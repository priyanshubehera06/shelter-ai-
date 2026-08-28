import React from 'react';
import { GeometryParams } from '../../types';

interface HeatFlowParticlesProps {
  geometry: GeometryParams;
  viewMode?: string;
}

export const HeatFlowParticles: React.FC<HeatFlowParticlesProps> = ({ geometry, viewMode }) => {
  const { length_m: L, width_m: W, height_m: H } = geometry;
  const plinthHeight = 0.35;
  const winY = plinthHeight + 0.9 + 0.55;

  if (viewMode === 'ventilation') {
    return (
      <group position={[0, winY, 0]}>
        {/* Wind Ingress Streamline Tubes passing from South (+Z) through to North (-Z) */}
        <mesh position={[L / 4 + 0.1, 0, W / 2 + 1.0]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.05, 0.05, 1.8, 16]} />
          <meshBasicMaterial color="#38bdf8" opacity={0.7} transparent />
        </mesh>
        <mesh position={[0, 0, 0]} rotation={[0, Math.PI / 4, 0]}>
          <cylinderGeometry args={[0.06, 0.06, L * 0.7, 16]} />
          <meshBasicMaterial color="#38bdf8" opacity={0.4} transparent />
        </mesh>
        <mesh position={[0, 0, -W / 2 - 1.0]} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.05, 0.05, 1.8, 16]} />
          <meshBasicMaterial color="#38bdf8" opacity={0.7} transparent />
        </mesh>
      </group>
    );
  }

  if (viewMode === 'heat_flow') {
    return (
      <group position={[0, plinthHeight + H + 0.6, 0]}>
        {/* Solar Radiation Heat Influx Conduction Arrows on Roof */}
        {[-L / 3, 0, L / 3].map((x, idx) => (
          <group key={idx} position={[x, 0, 0]} rotation={[Math.PI, 0, 0]}>
            <coneGeometry args={[0.14, 0.35, 16]} />
            <meshBasicMaterial color="#ef4444" opacity={0.8} transparent />
          </group>
        ))}
      </group>
    );
  }

  return null;
};
