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
  const winH = Math.min(1.2, H - 1.3);
  const winSill = 0.9;
  const winY = plinthHeight + winSill + winH / 2;
  const winX = L / 4; // Matches front window aperture in WallsMesh

  return (
    <group>
      {/* 1. FRONT WINDOW (SOUTH: +Z) */}
      <group position={[winX, winY, W / 2 + 0.01]}>
        {/* Transparent Glazing Glass Pane */}
        <mesh castShadow>
          <boxGeometry args={[winW - 0.04, winH - 0.04, 0.02]} />
          <meshPhysicalMaterial
            color={glass.color}
            roughness={glass.roughness}
            metalness={glass.metalness}
            transmission={0.9}
            thickness={0.06}
            opacity={glass.opacity || 0.45}
            transparent={true}
          />
        </mesh>

        {/* Outer Frame Casing (Solid Aluminum, NO Wireframe) */}
        <mesh>
          <boxGeometry args={[winW, winH, 0.05]} />
          <meshStandardMaterial
            color="#1e293b"
            metalness={0.8}
            roughness={0.2}
          />
        </mesh>

        {/* Architectural Cross-Muntin Dividers */}
        <mesh position={[0, 0, 0.01]}>
          <boxGeometry args={[winW - 0.04, 0.025, 0.02]} />
          <meshStandardMaterial color="#334155" metalness={0.7} roughness={0.3} />
        </mesh>
        <mesh position={[0, 0, 0.01]}>
          <boxGeometry args={[0.025, winH - 0.04, 0.02]} />
          <meshStandardMaterial color="#334155" metalness={0.7} roughness={0.3} />
        </mesh>

        {/* Exterior Window Sill Ledge */}
        <mesh position={[0, -winH / 2 - 0.025, 0.05]}>
          <boxGeometry args={[winW + 0.1, 0.04, 0.12]} />
          <meshStandardMaterial color="#475569" roughness={0.7} />
        </mesh>
      </group>

      {/* 2. BACK CROSS-VENTILATION WINDOW (NORTH: -Z) */}
      <group position={[0, winY, -W / 2 - 0.01]}>
        {/* Transparent Glazing Glass Pane */}
        <mesh castShadow>
          <boxGeometry args={[winW - 0.04, winH - 0.04, 0.02]} />
          <meshPhysicalMaterial
            color={glass.color}
            roughness={glass.roughness}
            metalness={glass.metalness}
            transmission={0.9}
            thickness={0.06}
            opacity={glass.opacity || 0.45}
            transparent={true}
          />
        </mesh>

        {/* Outer Frame Casing */}
        <mesh>
          <boxGeometry args={[winW, winH, 0.05]} />
          <meshStandardMaterial color="#1e293b" metalness={0.8} roughness={0.2} />
        </mesh>

        {/* Cross-Muntin */}
        <mesh position={[0, 0, -0.01]}>
          <boxGeometry args={[winW - 0.04, 0.025, 0.02]} />
          <meshStandardMaterial color="#334155" metalness={0.7} roughness={0.3} />
        </mesh>
        <mesh position={[0, 0, -0.01]}>
          <boxGeometry args={[0.025, winH - 0.04, 0.02]} />
          <meshStandardMaterial color="#334155" metalness={0.7} roughness={0.3} />
        </mesh>

        {/* Sill Ledge */}
        <mesh position={[0, -winH / 2 - 0.025, -0.05]}>
          <boxGeometry args={[winW + 0.1, 0.04, 0.12]} />
          <meshStandardMaterial color="#475569" roughness={0.7} />
        </mesh>
      </group>
    </group>
  );
};
