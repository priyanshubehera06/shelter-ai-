import React, { useMemo } from 'react';
import * as THREE from 'three';
import { Text } from '@react-three/drei';
import { SolarPositionData } from '../../types';

interface SolarSystem3DProps {
  solarData?: SolarPositionData;
  timeHour?: number;
}

export const SolarSystem3D: React.FC<SolarSystem3DProps> = ({ solarData, timeHour = 12 }) => {
  if (!solarData) return null;

  const { is_daylight, altitude_deg, azimuth_deg } = solarData;

  const R = 18.0;
  const altRad = (Math.max(0, altitude_deg) * Math.PI) / 180.0;
  const azRad = (azimuth_deg * Math.PI) / 180.0;

  // True Astronomical NOAA 3D Coordinates in Y-UP Three.js system
  const sunX = R * Math.cos(altRad) * Math.sin(azRad);
  const sunY = Math.max(0.5, R * Math.sin(altRad));
  const sunZ = -R * Math.cos(altRad) * Math.cos(azRad);

  // Generate 24-hr Diurnal Solar Arc Curve in Y-UP
  const splineGeom = useMemo(() => {
    const points: THREE.Vector3[] = [];
    for (let h = 5.5; h <= 18.5; h += 0.5) {
      // Approximate diurnal altitude and azimuth curve
      const solarNoonHour = 12.2;
      const hourAngle = ((h - solarNoonHour) * 15.0 * Math.PI) / 180.0;
      const decRad = (20.0 * Math.PI) / 180.0; // summer solstice declination
      const latRad = (21.46 * Math.PI) / 180.0; // Sambalpur latitude

      const sinAlt = Math.sin(latRad) * Math.sin(decRad) + Math.cos(latRad) * Math.cos(decRad) * Math.cos(hourAngle);
      const alt = Math.asin(Math.max(0, sinAlt));

      const cosAz = (Math.sin(decRad) - Math.sin(latRad) * Math.sin(alt)) / (Math.cos(latRad) * Math.cos(alt) + 0.0001);
      const az = hourAngle < 0 ? Math.PI - Math.acos(Math.max(-1, Math.min(1, cosAz))) : Math.PI + Math.acos(Math.max(-1, Math.min(1, cosAz)));

      if (alt >= 0) {
        const px = R * Math.cos(alt) * Math.sin(az);
        const py = R * Math.sin(alt);
        const pz = -R * Math.cos(alt) * Math.cos(az);
        points.push(new THREE.Vector3(px, py, pz));
      }
    }

    if (points.length < 2) return null;
    const curve = new THREE.CatmullRomCurve3(points);
    return new THREE.TubeGeometry(curve, 64, 0.06, 8, false);
  }, [R]);

  return (
    <group>
      {/* 24-Hr Diurnal Spline Arc Tube */}
      {splineGeom && (
        <mesh geometry={splineGeom}>
          <meshBasicMaterial color="#f59e0b" opacity={0.35} transparent />
        </mesh>
      )}

      {/* Dynamic Sun Sphere and Directional Light */}
      {is_daylight && (
        <group position={[sunX, sunY, sunZ]}>
          {/* Glowing Sun Core */}
          <mesh>
            <sphereGeometry args={[0.55, 32, 32]} />
            <meshBasicMaterial color="#fbbf24" />
          </mesh>
          {/* Glowing Corona */}
          <mesh>
            <sphereGeometry args={[0.9, 16, 16]} />
            <meshBasicMaterial color="#f59e0b" opacity={0.25} transparent />
          </mesh>

          {/* Directional Sunlight with Soft Shadows */}
          <directionalLight
            castShadow
            intensity={2.2}
            shadow-mapSize={[2048, 2048]}
            shadow-camera-near={0.5}
            shadow-camera-far={60}
            shadow-camera-left={-12}
            shadow-camera-right={12}
            shadow-camera-top={12}
            shadow-camera-bottom={-12}
            shadow-bias={-0.0005}
          />

          {/* Solar Coordinates Floating Annotation */}
          <Text
            position={[0, 1.2, 0]}
            fontSize={0.4}
            color="#fbbf24"
            anchorX="center"
            anchorY="middle"
          >
            {`${String(Math.floor(timeHour)).padStart(2, '0')}:00 (${altitude_deg}° Alt, ${azimuth_deg}° Az)`}
          </Text>
        </group>
      )}
    </group>
  );
};
