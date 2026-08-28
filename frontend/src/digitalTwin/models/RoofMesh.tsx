import React, { useMemo } from 'react';
import * as THREE from 'three';
import { GeometryParams } from '../../types';
import { getPBRMaterial } from '../materials/materialLibrary';

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
  const plinthHeight = 0.35;
  const pbr = getPBRMaterial(materialId);

  const roofColor = viewMode === 'thermal_heatmap' && thermalColors['roof']
    ? thermalColors['roof']
    : pbr.color;

  const pitchRad = (Math.max(5, roof_pitch_deg) * Math.PI) / 180.0;
  const extL = L + 2 * overhang_m;
  const extW = W + 2 * overhang_m;
  const roofThickness = 0.10;

  // Height of gable ridge apex above wall plate
  const deltaY = roof_type === 'pitched'
    ? (W / 2.0) * Math.tan(pitchRad)
    : roof_type === 'monoslope'
    ? W * Math.tan(pitchRad)
    : roof_type === 'hipped'
    ? (W / 2.0) * Math.tan(pitchRad)
    : 0.12;

  const baseY = plinthHeight + H + explodedOffset * 0.8;

  // Gable Half Slope Box Geometry
  const gablePitchGeom = useMemo(() => {
    const slopeDepth = Math.sqrt((extW / 2) ** 2 + deltaY ** 2);
    return new THREE.BoxGeometry(extL, roofThickness, slopeDepth);
  }, [extL, extW, deltaY]);

  // Monoslope Box Geometry
  const monoslopeGeom = useMemo(() => {
    const slopeDepth = Math.sqrt(extW ** 2 + deltaY ** 2);
    return new THREE.BoxGeometry(extL, roofThickness, slopeDepth);
  }, [extL, extW, deltaY]);

  // Flat Slab Box Geometry
  const flatGeom = useMemo(() => {
    return new THREE.BoxGeometry(extL, roofThickness, extW);
  }, [extL, extW]);

  // Triangular Gable End Wall Prism Geometry (East & West)
  const gableEndPrismGeom = useMemo(() => {
    const shape = new THREE.Shape();
    shape.moveTo(-W / 2, 0);
    shape.lineTo(0, deltaY);
    shape.lineTo(W / 2, 0);
    shape.closePath();

    const extrudeSettings = {
      steps: 1,
      depth: 0.18,
      bevelEnabled: false,
    };
    return new THREE.ExtrudeGeometry(shape, extrudeSettings);
  }, [W, deltaY]);

  return (
    <group position={[0, baseY, 0]}>
      {/* 1. GABLE (PITCHED) ROOF */}
      {roof_type === 'pitched' && (
        <group>
          {/* South Slope (towards +Z) */}
          <mesh
            geometry={gablePitchGeom}
            position={[0, deltaY / 2, extW / 4]}
            rotation={[pitchRad, 0, 0]}
            castShadow
            receiveShadow
          >
            <meshStandardMaterial
              color={roofColor}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>

          {/* North Slope (towards -Z) */}
          <mesh
            geometry={gablePitchGeom}
            position={[0, deltaY / 2, -extW / 4]}
            rotation={[-pitchRad, 0, 0]}
            castShadow
            receiveShadow
          >
            <meshStandardMaterial
              color={roofColor}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>

          {/* Ridge Cap Trim */}
          <mesh position={[0, deltaY + 0.05, 0]} castShadow>
            <boxGeometry args={[extL + 0.04, 0.08, 0.20]} />
            <meshStandardMaterial color="#2e3440" roughness={0.3} metalness={0.8} />
          </mesh>

          {/* East Triangular Gable End Wall */}
          <mesh
            geometry={gableEndPrismGeom}
            position={[L / 2 - 0.18, 0, 0]}
            rotation={[0, Math.PI / 2, 0]}
            castShadow
          >
            <meshStandardMaterial color={pbr.color} roughness={pbr.roughness} metalness={pbr.metalness} />
          </mesh>

          {/* West Triangular Gable End Wall */}
          <mesh
            geometry={gableEndPrismGeom}
            position={[-L / 2, 0, 0]}
            rotation={[0, Math.PI / 2, 0]}
            castShadow
          >
            <meshStandardMaterial color={pbr.color} roughness={pbr.roughness} metalness={pbr.metalness} />
          </mesh>
        </group>
      )}

      {/* 2. MONOSLOPE (SINGLE SHED) ROOF */}
      {roof_type === 'monoslope' && (
        <group>
          <mesh
            geometry={monoslopeGeom}
            position={[0, deltaY / 2, 0]}
            rotation={[pitchRad, 0, 0]}
            castShadow
            receiveShadow
          >
            <meshStandardMaterial
              color={roofColor}
              roughness={pbr.roughness}
              metalness={pbr.metalness}
            />
          </mesh>
          {/* Top Ridge Fascia */}
          <mesh position={[0, deltaY + 0.04, -extW / 2 + 0.05]} castShadow>
            <boxGeometry args={[extL, 0.12, 0.10]} />
            <meshStandardMaterial color="#2e3440" roughness={0.3} metalness={0.8} />
          </mesh>
        </group>
      )}

      {/* 3. HIPPED (4-SLOPE) ROOF */}
      {roof_type === 'hipped' && (
        <group position={[0, deltaY / 2, 0]}>
          {/* South Facet */}
          <mesh
            position={[0, 0, extW / 4]}
            rotation={[pitchRad, 0, 0]}
            castShadow
            receiveShadow
          >
            <boxGeometry args={[extL * 0.82, roofThickness, extW / 2]} />
            <meshStandardMaterial color={roofColor} roughness={pbr.roughness} metalness={pbr.metalness} />
          </mesh>
          {/* North Facet */}
          <mesh
            position={[0, 0, -extW / 4]}
            rotation={[-pitchRad, 0, 0]}
            castShadow
            receiveShadow
          >
            <boxGeometry args={[extL * 0.82, roofThickness, extW / 2]} />
            <meshStandardMaterial color={roofColor} roughness={pbr.roughness} metalness={pbr.metalness} />
          </mesh>
          {/* East Facet */}
          <mesh
            position={[extL / 3, 0, 0]}
            rotation={[0, 0, -pitchRad]}
            castShadow
          >
            <boxGeometry args={[extL / 3, roofThickness, extW * 0.7]} />
            <meshStandardMaterial color={roofColor} roughness={pbr.roughness} metalness={pbr.metalness} />
          </mesh>
          {/* West Facet */}
          <mesh
            position={[-extL / 3, 0, 0]}
            rotation={[0, 0, pitchRad]}
            castShadow
          >
            <boxGeometry args={[extL / 3, roofThickness, extW * 0.7]} />
            <meshStandardMaterial color={roofColor} roughness={pbr.roughness} metalness={pbr.metalness} />
          </mesh>
        </group>
      )}

      {/* 4. FLAT SLAB ROOF */}
      {roof_type === 'flat' && (
        <group>
          <mesh geometry={flatGeom} position={[0, 0.05, 0]} castShadow receiveShadow>
            <meshStandardMaterial color={roofColor} roughness={pbr.roughness} metalness={pbr.metalness} />
          </mesh>
          {/* Perimeter Parapet Walls */}
          <mesh position={[0, 0.25, extW / 2 - 0.05]} castShadow>
            <boxGeometry args={[extL, 0.35, 0.12]} />
            <meshStandardMaterial color="#475569" roughness={0.9} />
          </mesh>
          <mesh position={[0, 0.25, -extW / 2 + 0.05]} castShadow>
            <boxGeometry args={[extL, 0.35, 0.12]} />
            <meshStandardMaterial color="#475569" roughness={0.9} />
          </mesh>
          <mesh position={[extL / 2 - 0.05, 0.25, 0]} castShadow>
            <boxGeometry args={[0.12, 0.35, extW - 0.24]} />
            <meshStandardMaterial color="#475569" roughness={0.9} />
          </mesh>
          <mesh position={[-extL / 2 + 0.05, 0.25, 0]} castShadow>
            <boxGeometry args={[0.12, 0.35, extW - 0.24]} />
            <meshStandardMaterial color="#475569" roughness={0.9} />
          </mesh>
        </group>
      )}
    </group>
  );
};
