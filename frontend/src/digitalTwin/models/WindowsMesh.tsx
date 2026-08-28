import React from 'react';
import { GeometryParams } from '../../types';
import { getPBRMaterial } from '../materials/materialLibrary';

interface WindowsMeshProps {
  geometry: GeometryParams;
  glazingMatId: string;
}

export const WindowsMesh: React.FC<WindowsMeshProps> = ({
  geometry,
  glazingMatId,
}) => {
  const { length_m: L, width_m: W, height_m: H, wwr_pct } = geometry;
  const plinthHeight = 0.35;
  const glass = getPBRMaterial(glazingMatId);
  const frame = getPBRMaterial('frame_aluminum');

  const winW = Math.max(1.0, Math.min(1.8, (L * (wwr_pct / 100)) / 1.2));
  const winH = 1.1;
  const winY = plinthHeight + 0.9 + winH / 2;

  return (
    <group>
      {/* 1. FRONT WINDOW (SOUTH: +Z) */}
      <group position={[L / 4 + 0.1, winY, W / 2 + 0.01]}>
        {/* Transparent Glazing Glass Pane */}
        <mesh castShadow>
          <boxGeometry args={[winW, winH, 0.02]} />
          <meshPhysicalMaterial
            color={glass.color}
            roughness={glass.roughness}
            metalness={glass.metalness}
            transmission={0.85}
            thickness={0.05}
            opacity={glass.opacity || 0.45}
            transparent={true}
          />
        </mesh>

        {/* Outer Aluminum Frame */}
        <mesh>
          <boxGeometry args={[winW + 0.08, winH + 0.08, 0.06]} />
          <meshStandardMaterial color={frame.color} metalness={frame.metalness} roughness={frame.roughness} wireframe />
        </mesh>

        {/* Horizontal & Vertical Muntin Dividers */}
        <mesh>
          <boxGeometry args={[winW, 0.03, 0.03]} />
          <meshStandardMaterial color="#2e3440" metalness={0.7} roughness={0.3} />
        </mesh>
        <mesh>
          <boxGeometry args={[0.03, winH, 0.03]} />
          <meshStandardMaterial color="#2e3440" metalness={0.7} roughness={0.3} />
        </mesh>

        {/* Exterior Window Sill Ledge */}
        <mesh position={[0, -winH / 2 - 0.03, 0.04]}>
          <boxGeometry args={[winW + 0.16, 0.05, 0.12]} />
          <meshStandardMaterial color="#4c566a" roughness={0.7} />
        </mesh>
      </group>

      {/* 2. BACK CROSS-VENTILATION WINDOW (NORTH: -Z) */}
      <group position={[0, winY, -W / 2 - 0.01]}>
        {/* Transparent Glazing Glass Pane */}
        <mesh castShadow>
          <boxGeometry args={[winW, winH, 0.02]} />
          <meshPhysicalMaterial
            color={glass.color}
            roughness={glass.roughness}
            metalness={glass.metalness}
            transmission={0.85}
            thickness={0.05}
            opacity={glass.opacity || 0.45}
            transparent={true}
          />
        </mesh>
        {/* Outer Aluminum Frame */}
        <mesh>
          <boxGeometry args={[winW + 0.08, winH + 0.08, 0.06]} />
          <meshStandardMaterial color={frame.color} metalness={frame.metalness} roughness={frame.roughness} wireframe />
        </mesh>
        {/* Sill Ledge */}
        <mesh position={[0, -winH / 2 - 0.03, -0.04]}>
          <boxGeometry args={[winW + 0.16, 0.05, 0.12]} />
          <meshStandardMaterial color="#4c566a" roughness={0.7} />
        </mesh>
      </group>
    </group>
  );
};
