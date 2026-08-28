import React from 'react';
import { GeometryParams } from '../../types';
import { getPBRMaterial } from '../materials/materialLibrary';

interface DoorMeshProps {
  geometry: GeometryParams;
}

export const DoorMesh: React.FC<DoorMeshProps> = ({ geometry }) => {
  const { width_m: W, door_width_m, door_height_m } = geometry;
  const plinthHeight = 0.35;
  const dW = door_width_m || 0.9;
  const dH = door_height_m || 2.1;
  const doorMat = getPBRMaterial('door_timber_composite');

  return (
    <group position={[0.1, plinthHeight + dH / 2, W / 2 + 0.02]}>
      {/* Outer Door Frame Jamb */}
      <mesh>
        <boxGeometry args={[dW + 0.08, dH + 0.08, 0.08]} />
        <meshStandardMaterial color="#2e3440" roughness={0.4} metalness={0.7} />
      </mesh>

      {/* Main Solid Timber Door Leaf */}
      <mesh castShadow>
        <boxGeometry args={[dW, dH, 0.05]} />
        <meshStandardMaterial
          color={doorMat.color}
          roughness={doorMat.roughness}
          metalness={doorMat.metalness}
        />
      </mesh>

      {/* Decorative Door Panel Reveals */}
      <mesh position={[0, dH * 0.2, 0.03]}>
        <boxGeometry args={[dW * 0.75, dH * 0.35, 0.01]} />
        <meshStandardMaterial color="#4c566a" roughness={0.6} />
      </mesh>
      <mesh position={[0, -dH * 0.2, 0.03]}>
        <boxGeometry args={[dW * 0.75, dH * 0.35, 0.01]} />
        <meshStandardMaterial color="#4c566a" roughness={0.6} />
      </mesh>

      {/* Brass Lever Handle Hardware */}
      <group position={[dW / 2 - 0.12, 0, 0.04]}>
        <mesh castShadow>
          <sphereGeometry args={[0.03, 16, 16]} />
          <meshStandardMaterial color="#f59e0b" roughness={0.2} metalness={0.9} />
        </mesh>
        <mesh position={[-0.04, 0, 0]} rotation={[0, 0, Math.PI / 2]}>
          <cylinderGeometry args={[0.01, 0.01, 0.08, 8]} />
          <meshStandardMaterial color="#f59e0b" roughness={0.2} metalness={0.9} />
        </mesh>
      </group>
    </group>
  );
};
