import React from 'react';
import { GeometryParams } from '../../types';
import { getMaterialProps } from './MaterialLibrary';

interface GlazingAndDoorMeshProps {
  geometry: GeometryParams;
  glazingMatId: string;
}

export const GlazingAndDoorMesh: React.FC<GlazingAndDoorMeshProps> = ({
  geometry,
  glazingMatId,
}) => {
  const { length_m: L, width_m: W, height_m: H, door_width_m, door_height_m } = geometry;
  const glassProps = getMaterialProps(glazingMatId);
  const doorProps = getMaterialProps('door_timber_composite');

  return (
    <group>
      {/* Entrance Door (Front South Facade: -Y) */}
      <group position={[0.1, -W / 2 + 0.05, door_height_m / 2]}>
        <mesh castShadow>
          <boxGeometry args={[door_width_m, 0.05, door_height_m]} />
          <meshStandardMaterial
            color={doorProps.color}
            roughness={doorProps.roughness}
            metalness={doorProps.metalness}
          />
        </mesh>
        {/* Door handle */}
        <mesh position={[door_width_m / 2 - 0.12, -0.04, 0]}>
          <sphereGeometry args={[0.035, 16, 16]} />
          <meshStandardMaterial color="#f1c40f" metalness={0.9} roughness={0.2} />
        </mesh>
      </group>

      {/* Front Window Glazing Pane (South: -Y) */}
      <group position={[-L / 4, -W / 2 + 0.02, H * 0.55]}>
        <mesh castShadow>
          <boxGeometry args={[1.2, 0.03, 1.0]} />
          <meshStandardMaterial
            color={glassProps.color}
            roughness={glassProps.roughness}
            metalness={glassProps.metalness}
            opacity={glassProps.opacity || 0.65}
            transparent={true}
          />
        </mesh>
        {/* Window Aluminum Frame */}
        <mesh>
          <boxGeometry args={[1.26, 0.04, 1.06]} />
          <meshStandardMaterial color="#2d3436" metalness={0.8} roughness={0.3} wireframe />
        </mesh>
      </group>

      {/* Back Window Glazing Pane (North: +Y) for Cross Ventilation */}
      <group position={[L / 4, W / 2 - 0.02, H * 0.55]}>
        <mesh castShadow>
          <boxGeometry args={[1.2, 0.03, 1.0]} />
          <meshStandardMaterial
            color={glassProps.color}
            roughness={glassProps.roughness}
            metalness={glassProps.metalness}
            opacity={glassProps.opacity || 0.65}
            transparent={true}
          />
        </mesh>
        <mesh>
          <boxGeometry args={[1.26, 0.04, 1.06]} />
          <meshStandardMaterial color="#2d3436" metalness={0.8} roughness={0.3} wireframe />
        </mesh>
      </group>
    </group>
  );
};
