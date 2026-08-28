import React, { useMemo } from 'react';
import * as THREE from 'three';
import { SolarPositionData } from '../../types';

interface SunAndSolarPathProps {
  solarData?: SolarPositionData;
}

export const SunAndSolarPath: React.FC<SunAndSolarPathProps> = ({ solarData }) => {
  if (!solarData) return null;

  const { sun_position_3d, is_daylight, solar_path_spline } = solarData;

  const curvePoints = useMemo(() => {
    if (!solar_path_spline || solar_path_spline.length < 2) return [];
    return solar_path_spline.map((p) => new THREE.Vector3(p[0], p[1], p[2]));
  }, [solar_path_spline]);

  const splineGeometry = useMemo(() => {
    if (curvePoints.length < 2) return null;
    const curve = new THREE.CatmullRomCurve3(curvePoints);
    return new THREE.TubeGeometry(curve, 64, 0.04, 8, false);
  }, [curvePoints]);

  return (
    <group>
      {/* 24-Hr Diurnal Sun Trajectory Spline Tube */}
      {splineGeometry && (
        <mesh geometry={splineGeometry}>
          <meshBasicMaterial color="#f59e0b" opacity={0.4} transparent />
        </mesh>
      )}

      {/* Sun Sphere */}
      {is_daylight && sun_position_3d && (
        <group position={[sun_position_3d[0], sun_position_3d[1], sun_position_3d[2]]}>
          {/* Glowing Sun core */}
          <mesh>
            <sphereGeometry args={[0.55, 32, 32]} />
            <meshBasicMaterial color="#fbbf24" />
          </mesh>
          {/* Sun Halo */}
          <mesh>
            <sphereGeometry args={[0.85, 16, 16]} />
            <meshBasicMaterial color="#f59e0b" opacity={0.25} transparent />
          </mesh>
          {/* Directional Sunlight mapped to NOAA solar position */}
          <directionalLight
            castShadow
            intensity={2.2}
            shadow-mapSize={[2048, 2048]}
            shadow-camera-near={0.5}
            shadow-camera-far={60}
            shadow-camera-left={-10}
            shadow-camera-right={10}
            shadow-camera-top={10}
            shadow-camera-bottom={-10}
            shadow-bias={-0.0005}
          />
        </group>
      )}
    </group>
  );
};
