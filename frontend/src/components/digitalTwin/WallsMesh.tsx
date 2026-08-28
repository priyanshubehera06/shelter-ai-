import React from 'react';
import { GeometryParams } from '../../types';
import { getMaterialProps } from './MaterialLibrary';

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
  const { length_m: L, width_m: W, height_m: H, wall_thickness_cm } = geometry;
  const T = wall_thickness_cm / 100.0;
  const defaultMat = getMaterialProps(materialId);

  const getWallColor = (wallKey: string) => {
    if (viewMode === 'thermal_heatmap' && thermalColors[wallKey]) {
      return thermalColors[wallKey];
    }
    return defaultMat.color;
  };

  const yOffset = explodedOffset * 0.2;

  return (
    <group position={[0, 0, H / 2 + yOffset]}>
      {/* Front Wall (South: -Y) with Door cutout and Window */}
      <group position={[0, -W / 2 + T / 2, 0]}>
        {/* Left piece */}
        <mesh position={[(-L / 2 + (L / 2 - 0.7)) / 2, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[L / 2 - 0.7, T, H]} />
          <meshStandardMaterial
            color={getWallColor('south')}
            roughness={defaultMat.roughness}
            metalness={defaultMat.metalness}
          />
        </mesh>
        {/* Right piece */}
        <mesh position={[(L / 2 - (L / 2 - 0.7)) / 2 + 0.6, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[L / 2 - 0.7, T, H]} />
          <meshStandardMaterial
            color={getWallColor('south')}
            roughness={defaultMat.roughness}
            metalness={defaultMat.metalness}
          />
        </mesh>
        {/* Top Header over Door */}
        <mesh position={[0.1, 0, H / 2 - (H - 2.1) / 2]} castShadow receiveShadow>
          <boxGeometry args={[1.2, T, H - 2.1]} />
          <meshStandardMaterial
            color={getWallColor('south')}
            roughness={defaultMat.roughness}
            metalness={defaultMat.metalness}
          />
        </mesh>
      </group>

      {/* Back Wall (North: +Y) */}
      <mesh position={[0, W / 2 - T / 2, 0]} castShadow receiveShadow>
        <boxGeometry args={[L, T, H]} />
        <meshStandardMaterial
          color={getWallColor('north')}
          roughness={defaultMat.roughness}
          metalness={defaultMat.metalness}
        />
      </mesh>

      {/* East Wall (+X) */}
      <mesh position={[L / 2 - T / 2, 0, 0]} castShadow receiveShadow>
        <boxGeometry args={[T, W - 2 * T, H]} />
        <meshStandardMaterial
          color={getWallColor('east')}
          roughness={defaultMat.roughness}
          metalness={defaultMat.metalness}
        />
      </mesh>

      {/* West Wall (-X) */}
      <mesh position={[-L / 2 + T / 2, 0, 0]} castShadow receiveShadow>
        <boxGeometry args={[T, W - 2 * T, H]} />
        <meshStandardMaterial
          color={getWallColor('west')}
          roughness={defaultMat.roughness}
          metalness={defaultMat.metalness}
        />
      </mesh>
    </group>
  );
};
