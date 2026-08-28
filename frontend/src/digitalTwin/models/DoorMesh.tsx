import React from 'react';
import { GeometryParams } from '../../types';
import { getPBRMaterial } from '../materials/materialLibrary';

interface DoorMeshProps {
  geometry: GeometryParams;
}

export const DoorMesh: React.FC<DoorMeshProps> = ({ geometry }) => {
  const { length_m: L, width_m: W, height_m: H, door_width_m, door_height_m } = geometry;
  const plinthHeight = 0.35;
  const dW = door_width_m || 0.9;
  const dH = Math.min(H - 0.2, door_height_m || 2.1);
  const doorX = -L / 4; // Matches door opening aperture in WallsMesh
  const doorMat = getPBRMaterial('door_timber_composite');

  return (
    <group position={[doorX, plinthHeight + dH / 2, W / 2 + 0.02]}>
      {/* Outer Door Frame Jamb */}
      <mesh>
        <boxGeometry args={[dW + 0.06, dH + 0.04, 0.06]} />
        <meshStandardMaterial color="#1e293b" roughness={0.3} metalness={0.7} />
      </mesh>

      {/* Main Solid Timber Door Leaf */}
      <mesh castShadow position={[0, 0, 0.01]}>
        <boxGeometry args={[dW - 0.02, dH - 0.02, 0.04]} />
        <meshStandardMaterial
          color={doorMat.color}
          roughness={doorMat.roughness}
          metalness={doorMat.metalness}
        />
      </mesh>

      {/* Decorative Door Panel Reveals */}
      <mesh position={[0, dH * 0.2, 0.035]}>
        <boxGeometry args={[dW * 0.7, dH * 0.35, 0.01]} />
        <meshStandardMaterial color="#334155" roughness={0.6} />
      </mesh>
      <mesh position={[0, -dH * 0.2, 0.035]}>
        <boxGeometry args={[dW * 0.7, dH * 0.35, 0.01]} />
        <meshStandardMaterial color="#334155" roughness={0.6} />
      </mesh>

      {/* Brass Lever Handle Hardware */}
      <group position={[dW / 2 - 0.12, 0, 0.045]}>
        <mesh castShadow>
          <sphereGeometry args={[0.025, 16, 16]} />
          <meshStandardMaterial color="#f59e0b" roughness={0.2} metalness={0.9} />
        </mesh>
        <mesh position={[-0.04, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.008, 0.008, 0.07, 8]} />
          <meshStandardMaterial color="#f59e0b" roughness={0.2} metalness={0.9} />
        </mesh>
      </group>
    </group>
  );
};
