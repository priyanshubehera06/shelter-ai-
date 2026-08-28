import React, { useMemo } from 'react';
import * as THREE from 'three';
import { GeometryParams } from '../../types';
import { getMaterialProps } from './MaterialLibrary';

interface RoofMeshProps {
  geometry: GeometryParams;
  materialId: string;
  viewMode?: string;
  explodedOffset?: number;
  thermalColors?: Record<string, string>;
}

export const RoofMesh: React.FC<RoofMeshProps> = ({
  geometry,
  materialId,
  viewMode = 'architectural',
  explodedOffset = 0,
  thermalColors = {},
}) => {
  const { length_m: L, width_m: W, height_m: H, roof_type, roof_pitch_deg, overhang_m } = geometry;
  const matProps = getMaterialProps(materialId);

  const roofColor = viewMode === 'thermal_heatmap' && thermalColors['roof']
    ? thermalColors['roof']
    : matProps.color;

  const pitchRad = (roof_pitch_deg * Math.PI) / 180.0;
  const deltaZ = roof_type === 'pitched'
    ? (W / 2.0) * Math.tan(pitchRad)
    : roof_type === 'monoslope'
    ? W * Math.tan(pitchRad)
    : 0.15;

  const baseZ = H + explodedOffset;

  // Generate Roof Geometries
  const roofGeom = useMemo(() => {
    const extL = L + 2 * overhang_m;
    const extW = W + 2 * overhang_m;
    const t = 0.08;

    if (roof_type === 'flat') {
      return new THREE.BoxGeometry(extL, extW, t);
    } else if (roof_type === 'monoslope') {
      // Slanted single plane
      const geom = new THREE.BoxGeometry(extL, Math.sqrt(extW * extW + deltaZ * deltaZ), t);
      return geom;
    } else {
      // Pitched Gable roof with 2 slope planes
      const slopeW = Math.sqrt((extW / 2) ** 2 + deltaZ ** 2);
      const geom = new THREE.BoxGeometry(extL, slopeW, t);
      return geom;
    }
  }, [L, W, deltaZ, roof_type, overhang_m]);

  const slopeW = Math.sqrt(((W + 2 * overhang_m) / 2) ** 2 + deltaZ ** 2);
  const extW = W + 2 * overhang_m;

  return (
    <group position={[0, 0, baseZ]}>
      {roof_type === 'pitched' ? (
        <group position={[0, 0, deltaZ / 2]}>
          {/* South Pitch Slope */}
          <mesh
            geometry={roofGeom}
            position={[0, -extW / 4, 0]}
            rotation={[pitchRad, 0, 0]}
            castShadow
            receiveShadow
          >
            <meshStandardMaterial
              color={roofColor}
              roughness={matProps.roughness}
              metalness={matProps.metalness}
            />
          </mesh>

          {/* North Pitch Slope */}
          <mesh
            geometry={roofGeom}
            position={[0, extW / 4, 0]}
            rotation={[-pitchRad, 0, 0]}
            castShadow
            receiveShadow
          >
            <meshStandardMaterial
              color={roofColor}
              roughness={matProps.roughness}
              metalness={matProps.metalness}
            />
          </mesh>

          {/* Fascia Ridge Cap */}
          <mesh position={[0, 0, deltaZ / 2 + 0.04]} castShadow>
            <boxGeometry args={[L + 2 * overhang_m + 0.05, 0.15, 0.06]} />
            <meshStandardMaterial color="#2c3e50" roughness={0.3} metalness={0.8} />
          </mesh>
        </group>
      ) : roof_type === 'monoslope' ? (
        <mesh
          geometry={roofGeom}
          position={[0, 0, deltaZ / 2]}
          rotation={[pitchRad, 0, 0]}
          castShadow
          receiveShadow
        >
          <meshStandardMaterial
            color={roofColor}
            roughness={matProps.roughness}
            metalness={matProps.metalness}
          />
        </mesh>
      ) : (
        <mesh
          geometry={roofGeom}
          position={[0, 0, 0.05]}
          castShadow
          receiveShadow
        >
          <meshStandardMaterial
            color={roofColor}
            roughness={matProps.roughness}
            metalness={matProps.metalness}
          />
        </mesh>
      )}
    </group>
  );
};
