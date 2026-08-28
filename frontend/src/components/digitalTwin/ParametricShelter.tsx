import React from 'react';
import { GeometryParams, MaterialSelection } from '../../types';
import { WallsMesh } from './WallsMesh';
import { RoofMesh } from './RoofMesh';
import { GlazingAndDoorMesh } from './GlazingAndDoorMesh';
import { GroundMesh } from './GroundMesh';

interface ParametricShelterProps {
  geometry: GeometryParams;
  materials: MaterialSelection;
  viewMode?: 'architectural' | 'solar_shading' | 'thermal_heatmap' | 'ventilation' | 'exploded';
  thermalColors?: Record<string, string>;
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

export const ParametricShelter: React.FC<ParametricShelterProps> = ({
  geometry,
  materials,
  viewMode = 'architectural',
  thermalColors = {},
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
  const orientationRad = -(geometry.orientation_deg * Math.PI) / 180.0;
  const isExploded = viewMode === 'exploded';
  const explodedOffset = isExploded ? 0.8 : 0;

  return (
    <group rotation={[0, 0, orientationRad]}>
      {/* Foundation & Ground Disc */}
      {componentVisibility.ground && (
        <GroundMesh geometry={geometry} explodedOffset={explodedOffset} />
      )}

      {/* Parametric Structural Walls */}
      {componentVisibility.walls && (
        <WallsMesh
          geometry={geometry}
          materialId={materials.wall_mat_id}
          viewMode={viewMode}
          explodedOffset={explodedOffset}
          thermalColors={thermalColors}
        />
      )}

      {/* Openings: Windows & Doors */}
      {(componentVisibility.windows || componentVisibility.door) && (
        <GlazingAndDoorMesh geometry={geometry} glazingMatId={materials.glazing_mat_id} />
      )}

      {/* Parametric Roof Structure */}
      {componentVisibility.roof && (
        <RoofMesh
          geometry={geometry}
          materialId={materials.roof_mat_id}
          viewMode={viewMode}
          explodedOffset={explodedOffset}
          thermalColors={thermalColors}
        />
      )}
    </group>
  );
};
