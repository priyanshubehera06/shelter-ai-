import React, { Suspense } from 'react';
import { useGLTF } from '@react-three/drei';
import { GeometryParams, MaterialSelection } from '../../types';
import { FoundationMesh } from './FoundationMesh';
import { PorchMesh } from './PorchMesh';
import { WallsMesh } from './WallsMesh';
import { RoofMesh } from './RoofMesh';
import { WindowsMesh } from './WindowsMesh';
import { DoorMesh } from './DoorMesh';
import { ShadingElements } from './ShadingElements';

interface ShelterModelProps {
  geometry: GeometryParams;
  materials: MaterialSelection;
  viewMode?: 'architectural' | 'solar_shading' | 'thermal_heatmap' | 'ventilation' | 'exploded' | 'heat_flow';
  thermalColors?: Record<string, string>;
  glbUrl?: string;
  componentVisibility?: {
    roof: boolean;
    walls: boolean;
    windows: boolean;
    door: boolean;
    shading: boolean;
    ground: boolean;
    compass: boolean;
    sun_path: boolean;
  };
}

/**
 * Optional GLB Mesh Loader component with auto-cloning & shadows
 */
const GLBModel: React.FC<{ url: string }> = ({ url }) => {
  const { scene } = useGLTF(url);
  return (
    <primitive
      object={scene.clone()}
      castShadow
      receiveShadow
      position={[0, 0, 0]}
    />
  );
};

export const ShelterModel: React.FC<ShelterModelProps> = ({
  geometry,
  materials,
  viewMode = 'architectural',
  thermalColors = {},
  glbUrl,
  componentVisibility = {
    roof: true,
    walls: true,
    windows: true,
    door: true,
    shading: true,
    ground: true,
    compass: true,
    sun_path: true,
  },
}) => {
  // Rotate around vertical Y-axis for True Azimuth Orientation
  const orientationRad = (geometry.orientation_deg * Math.PI) / 180.0;
  const isExploded = viewMode === 'exploded';
  const explodedOffset = isExploded ? 0.8 : 0;

  return (
    <group rotation={[0, -orientationRad, 0]}>
      {/* If an external GLB model URL is passed, render with Suspense fallback */}
      {glbUrl ? (
        <Suspense fallback={null}>
          <GLBModel url={glbUrl} />
        </Suspense>
      ) : (
        /* High-Precision Parametric PBR Procedural Shelter */
        <>
          {/* 1. Foundation Concrete Plinth Slab */}
          {componentVisibility.ground && (
            <FoundationMesh geometry={geometry} explodedOffset={explodedOffset} />
          )}

          {/* 2. Entrance Porch & Veranda Columns */}
          <PorchMesh geometry={geometry} explodedOffset={explodedOffset} />

          {/* 3. Exterior & Partition Walls */}
          {componentVisibility.walls && (
            <WallsMesh
              geometry={geometry}
              materialId={materials.wall_mat_id}
              viewMode={viewMode}
              explodedOffset={explodedOffset}
              thermalColors={thermalColors}
            />
          )}

          {/* 4. Glazing Windows & Muntin Frames */}
          {componentVisibility.windows && (
            <WindowsMesh geometry={geometry} glazingMatId={materials.glazing_mat_id} />
          )}

          {/* 5. Entrance Solid Timber Door */}
          {componentVisibility.door && <DoorMesh geometry={geometry} />}

          {/* 6. Solar Shading Louvers */}
          {componentVisibility.shading && <ShadingElements geometry={geometry} />}

          {/* 7. Parametric Multi-Variant Roof System */}
          {componentVisibility.roof && (
            <RoofMesh
              geometry={geometry}
              materialId={materials.roof_mat_id}
              viewMode={viewMode}
              explodedOffset={explodedOffset}
              thermalColors={thermalColors}
            />
          )}
        </>
      )}
    </group>
  );
};
