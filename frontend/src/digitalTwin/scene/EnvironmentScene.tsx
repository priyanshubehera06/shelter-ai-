import React from 'react';
import { GeometryParams } from '../../types';

interface EnvironmentSceneProps {
  geometry: GeometryParams;
}

export const EnvironmentScene: React.FC<EnvironmentSceneProps> = ({ geometry }) => {
  const { length_m: L, width_m: W } = geometry;
  const radius = Math.max(L, W) * 2.5;

  return (
    <group position={[0, 0, 0]}>
      {/* Daylight & Ambient Lighting */}
      <ambientLight intensity={0.7} />
      <hemisphereLight args={['#ffffff', '#1e293b', 0.45]} />

      {/* Studio Circular Ground Disc (X-Z plane at Y = -0.01) */}
      <mesh position={[0, -0.01, 0]} receiveShadow>
        <cylinderGeometry args={[radius, radius, 0.02, 64]} />
        <meshStandardMaterial color="#0f172a" roughness={0.95} metalness={0.0} />
      </mesh>

      {/* Concentric Orientation Guide Rings */}
      <mesh position={[0, 0.002, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[radius * 0.95, radius, 64]} />
        <meshBasicMaterial color="#1e293b" opacity={0.5} transparent />
      </mesh>

      <mesh position={[0, 0.002, 0]} rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[radius * 0.65, radius * 0.66, 64]} />
        <meshBasicMaterial color="#1e293b" opacity={0.3} transparent />
      </mesh>
    </group>
  );
};
