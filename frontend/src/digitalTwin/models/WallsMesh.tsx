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
  const { length_m: L, width_m: W, height_m: H, wall_thickness_cm, door_width_m, door_height_m, wwr_pct } = geometry;
  const plinthHeight = 0.35;
  const T = Math.max(0.20, wall_thickness_cm / 100.0);
  const pbr = getPBRMaterial(materialId);

  const getWallColor = (wallKey: string) => {
    if (viewMode === 'thermal_heatmap' && thermalColors[wallKey]) {
      return thermalColors[wallKey];
    }
    return pbr.color;
  };

  const baseY = plinthHeight + H / 2 + explodedOffset * 0.2;

  // Door position and size
  const dW = door_width_m || 0.9;
  const dH = Math.min(H - 0.2, door_height_m || 2.1);
  const doorX = -L / 4; // Centered on left side of facade

  // Window position and size
  const winW = Math.max(1.0, Math.min(1.8, (L * (wwr_pct / 100)) / 1.2));
  const winH = Math.min(1.2, H - 1.3);
  const winSill = 0.9; // Sill height from floor
  const winX = L / 4; // Centered on right side of facade

  // Front Wall X-coordinates (Left to Right: -L/2 to +L/2)
  const f_x0 = -L / 2;
  const f_x1 = doorX - dW / 2;
  const f_x2 = doorX + dW / 2;
  const f_x3 = winX - winW / 2;
  const f_x4 = winX + winW / 2;
  const f_x5 = L / 2;

  // Segment widths
  const w_left = f_x1 - f_x0;
  const w_mid = f_x3 - f_x2;
  const w_right = f_x5 - f_x4;

  // Back Wall (North) X-coordinates (Window in center at x=0)
  const b_winX = 0;
  const b_x0 = -L / 2;
  const b_x1 = b_winX - winW / 2;
  const b_x2 = b_winX + winW / 2;
  const b_x3 = L / 2;

  const b_w_left = b_x1 - b_x0;
  const b_w_right = b_x3 - b_x2;

  return (
    <group position={[0, baseY, 0]}>
      {/* 1. FRONT WALL (SOUTH: +Z) — 100% Continuous & Airtight */}
      <group position={[0, 0, W / 2 - T / 2]}>
        {/* 1a. Far Left Solid Column */}
        {w_left > 0.05 && (
          <mesh position={[(f_x0 + f_x1) / 2, 0, 0]} castShadow receiveShadow>
            <boxGeometry args={[w_left, H, T]} />
            <meshStandardMaterial
              color={getWallColor('south')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}

        {/* 1b. Lintel Header Beam above Door */}
        {H > dH && (
          <mesh position={[doorX, H / 2 - (H - dH) / 2, 0]} castShadow receiveShadow>
            <boxGeometry args={[dW, H - dH, T]} />
            <meshStandardMaterial
              color={getWallColor('south')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}

        {/* 1c. Center Solid Column between Door and Window */}
        {w_mid > 0.05 && (
          <mesh position={[(f_x2 + f_x3) / 2, 0, 0]} castShadow receiveShadow>
            <boxGeometry args={[w_mid, H, T]} />
            <meshStandardMaterial
              color={getWallColor('south')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}

        {/* 1d. Wall Below Front Window (Spandrel) */}
        {winSill > 0.05 && (
          <mesh position={[winX, -H / 2 + winSill / 2, 0]} castShadow receiveShadow>
            <boxGeometry args={[winW, winSill, T]} />
            <meshStandardMaterial
              color={getWallColor('south')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}

        {/* 1e. Wall Above Front Window (Lintel) */}
        {H - (winSill + winH) > 0.05 && (
          <mesh position={[winX, H / 2 - (H - (winSill + winH)) / 2, 0]} castShadow receiveShadow>
            <boxGeometry args={[winW, H - (winSill + winH), T]} />
            <meshStandardMaterial
              color={getWallColor('south')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}

        {/* 1f. Far Right Solid Column */}
        {w_right > 0.05 && (
          <mesh position={[(f_x4 + f_x5) / 2, 0, 0]} castShadow receiveShadow>
            <boxGeometry args={[w_right, H, T]} />
            <meshStandardMaterial
              color={getWallColor('south')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}
      </group>

      {/* 2. BACK WALL (NORTH: -Z) — 100% Continuous & Airtight */}
      <group position={[0, 0, -W / 2 + T / 2]}>
        {/* 2a. Left Solid Segment */}
        {b_w_left > 0.05 && (
          <mesh position={[(b_x0 + b_x1) / 2, 0, 0]} castShadow receiveShadow>
            <boxGeometry args={[b_w_left, H, T]} />
            <meshStandardMaterial
              color={getWallColor('north')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}

        {/* 2b. Wall Below Back Window (Spandrel) */}
        {winSill > 0.05 && (
          <mesh position={[b_winX, -H / 2 + winSill / 2, 0]} castShadow receiveShadow>
            <boxGeometry args={[winW, winSill, T]} />
            <meshStandardMaterial
              color={getWallColor('north')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}

        {/* 2c. Wall Above Back Window (Lintel) */}
        {H - (winSill + winH) > 0.05 && (
          <mesh position={[b_winX, H / 2 - (H - (winSill + winH)) / 2, 0]} castShadow receiveShadow>
            <boxGeometry args={[winW, H - (winSill + winH), T]} />
            <meshStandardMaterial
              color={getWallColor('north')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}

        {/* 2d. Right Solid Segment */}
        {b_w_right > 0.05 && (
          <mesh position={[(b_x2 + b_x3) / 2, 0, 0]} castShadow receiveShadow>
            <boxGeometry args={[b_w_right, H, T]} />
            <meshStandardMaterial
              color={getWallColor('north')}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
        )}
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
        <mesh position={[0, 0, 0]} castShadow receiveShadow>
          <boxGeometry args={[T * 0.8, H, W - T * 2 - 1.2]} />
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
