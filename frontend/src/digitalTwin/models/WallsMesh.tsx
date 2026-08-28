import React from 'react';
import { GeometryParams } from '../../types';
import { getPBRMaterial } from '../materials/materialLibrary';

interface WallsMeshProps {
  geometry: GeometryParams;
  materialId: string;
  viewMode?: string;
  explodedOffset?: number;
  thermalColors?: Record<string, string>;
}

export const WallsMesh: React.FC<WallsMeshProps> = ({
  geometry,
  materialId,
  viewMode = 'architectural',
  explodedOffset = 0,
  thermalColors = {},
}) => {
  const { length_m: L, width_m: W, height_m: H, wall_thickness_cm, door_width_m, door_height_m } = geometry;
  const plinthHeight = 0.35;
  const T = Math.max(0.18, wall_thickness_cm / 100.0);
  const pbr = getPBRMaterial(materialId);

  const getWallColor = (wallKey: string) => {
    if (viewMode === 'thermal_heatmap' && thermalColors[wallKey]) {
      return thermalColors[wallKey];
    }
    return pbr.color;
  };

  const baseY = plinthHeight + H / 2 + explodedOffset * 0.2;

  // Front Wall Door & Window Dimensions
  const dW = door_width_m || 0.9;
  const dH = door_height_m || 2.1;
  const winW = 1.3;
  const winH = 1.1;
  const winBottom = 0.9;

  return (
    <group position={[0, baseY, 0]}>
      {/* 1. FRONT WALL (SOUTH: +Z) */}
      <group position={[0, 0, W / 2 - T / 2]}>
        {/* Left Wall Segment */}
        <mesh position={[-L / 2 + (L / 2 - dW / 2 - 0.2) / 2, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[L / 2 - dW / 2 - 0.2, H, T]} />
          <meshStandardMaterial
            color={getWallColor('south')}
            roughness={pbr.roughness}
            metalness={pbr.metalness}
          />
        </mesh>

        {/* Lintel Header Beam above Entrance Door */}
        <mesh position={[0.1, H / 2 - (H - dH) / 2, 0]} castShadow receiveShadow>
          <boxGeometry args={[dW + 0.2, H - dH, T]} />
          <meshStandardMaterial
            color={getWallColor('south')}
            roughness={pbr.roughness}
            metalness={pbr.metalness}
          />
        </mesh>

        {/* Right Wall Segment with Window Cutout */}
        {/* Under Window */}
        <mesh position={[L / 4 + 0.1, -H / 2 + winBottom / 2, 0]} castShadow receiveShadow>
          <boxGeometry args={[winW + 0.2, winBottom, T]} />
          <meshStandardMaterial color={getWallColor('south')} roughness={pbr.roughness} metalness={pbr.metalness} />
        </mesh>
        {/* Over Window */}
        <mesh position={[L / 4 + 0.1, H / 2 - (H - winBottom - winH) / 2, 0]} castShadow receiveShadow>
          <boxGeometry args={[winW + 0.2, H - winBottom - winH, T]} />
          <meshStandardMaterial color={getWallColor('south')} roughness={pbr.roughness} metalness={pbr.metalness} />
        </mesh>
        {/* Far Right Wall Corner Piece */}
        <mesh position={[L / 2 - (L / 4 - winW / 2) / 2, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[Math.max(0.4, L / 4 - winW / 2), H, T]} />
          <meshStandardMaterial color={getWallColor('south')} roughness={pbr.roughness} metalness={pbr.metalness} />
        </mesh>
      </group>

      {/* 2. BACK WALL (NORTH: -Z) */}
      <group position={[0, 0, -W / 2 + T / 2]}>
        {/* Solid Back Wall with Cross-Vent Window Cutout */}
        {/* Left North Segment */}
        <mesh position={[-L / 3, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[L / 3, H, T]} />
          <meshStandardMaterial color={getWallColor('north')} roughness={pbr.roughness} metalness={pbr.metalness} />
        </mesh>
        {/* Center North Segment (Window Under/Over) */}
        <mesh position={[0, -H / 2 + winBottom / 2, 0]} castShadow receiveShadow>
          <boxGeometry args={[winW, winBottom, T]} />
          <meshStandardMaterial color={getWallColor('north')} roughness={pbr.roughness} metalness={pbr.metalness} />
        </mesh>
        <mesh position={[0, H / 2 - (H - winBottom - winH) / 2, 0]} castShadow receiveShadow>
          <boxGeometry args={[winW, H - winBottom - winH, T]} />
          <meshStandardMaterial color={getWallColor('north')} roughness={pbr.roughness} metalness={pbr.metalness} />
        </mesh>
        {/* Right North Segment */}
        <mesh position={[L / 3, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[L / 3, H, T]} />
          <meshStandardMaterial color={getWallColor('north')} roughness={pbr.roughness} metalness={pbr.metalness} />
        </mesh>
      </group>

      {/* 3. EAST WALL (+X) */}
      <mesh position={[L / 2 - T / 2, 0, 0]} castShadow receiveShadow>
        <boxGeometry args={[T, H, W - T * 2]} />
        <meshStandardMaterial
          color={getWallColor('east')}
          roughness={pbr.roughness}
          metalness={pbr.metalness}
        />
      </mesh>

      {/* 4. WEST WALL (-X) */}
      <mesh position={[-L / 2 + T / 2, 0, 0]} castShadow receiveShadow>
        <boxGeometry args={[T, H, W - T * 2]} />
        <meshStandardMaterial
          color={getWallColor('west')}
          roughness={pbr.roughness}
          metalness={pbr.metalness}
        />
      </mesh>

      {/* 5. INTERIOR PARTITION WALL (when length >= 5.5m) */}
      {L >= 5.5 && (
        <mesh position={[-0.2, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[T * 0.7, H, W * 0.6]} />
          <meshStandardMaterial
            color={pbr.color}
            roughness={pbr.roughness}
            metalness={pbr.metalness}
          />
        </mesh>
      )}
    </group>
  );
};
