import React, { useEffect, useRef } from 'react';
import { useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { useShelterStore } from '../../store/shelterStore';
import { ShelterModel } from '../../digitalTwin/models/ShelterModel';
import { SolarSystem3D } from '../../digitalTwin/scene/SolarSystem3D';
import { Compass3D } from '../../digitalTwin/scene/Compass3D';
import { EnvironmentScene } from '../../digitalTwin/scene/EnvironmentScene';
import { HeatFlowParticles } from '../../digitalTwin/scene/HeatFlowParticles';
import { SolarPositionData } from '../../types';

interface ShelterSceneProps {
  solarData?: SolarPositionData;
  thermalColors?: Record<string, string>;
}

export const ShelterScene: React.FC<ShelterSceneProps> = ({
  solarData,
  thermalColors = {},
}) => {
  const { currentDesign, activeViewMode, cameraPreset, componentVisibility, simHour } = useShelterStore();
  const { camera } = useThree();
  const controlsRef = useRef<any>(null);

  const { length_m: L, width_m: W, height_m: H } = currentDesign.geometry;
  const centerY = (0.35 + H) / 2;

  // Handle Camera Presets in Y-UP coordinates
  useEffect(() => {
    if (!controlsRef.current) return;

    controlsRef.current.target.set(0, centerY, 0);

    if (cameraPreset === 'isometric') {
      camera.position.set(L * 1.3, H * 1.4, W * 1.5);
    } else if (cameraPreset === 'front') {
      camera.position.set(0, H * 0.7, W * 2.3);
    } else if (cameraPreset === 'side') {
      camera.position.set(L * 2.3, H * 0.7, 0);
    } else if (cameraPreset === 'top') {
      camera.position.set(0, Math.max(L, W) * 2.5, 0.001);
    } else if (cameraPreset === 'north') {
      camera.position.set(0, H * 0.7, -W * 2.3);
    }

    controlsRef.current.update();
  }, [cameraPreset, L, W, H, centerY, camera]);

  return (
    <>
      <OrbitControls
        ref={controlsRef}
        makeDefault
        minDistance={3.0}
        maxDistance={40}
        maxPolarAngle={Math.PI / 2 - 0.02} // Prevent camera going below ground
        dampingFactor={0.06}
      />

      {/* 1. Environment & Site Ground Disc */}
      <EnvironmentScene geometry={currentDesign.geometry} />

      {/* 2. NOAA Astronomical Sun & Trajectory */}
      {componentVisibility.sun_path && (
        <SolarSystem3D solarData={solarData} timeHour={simHour} />
      )}

      {/* 3. 3D Cardinal Compass (Aligned to True North) */}
      {componentVisibility.compass && (
        <Compass3D radius={Math.max(L, W) * 1.3} />
      )}

      {/* 4. High-Quality Architectural Parametric Shelter */}
      <ShelterModel
        geometry={currentDesign.geometry}
        materials={currentDesign.materials}
        viewMode={activeViewMode}
        thermalColors={thermalColors}
        componentVisibility={componentVisibility}
      />

      {/* 5. Conceptual Streamlines & Heat Flux */}
      <HeatFlowParticles geometry={currentDesign.geometry} viewMode={activeViewMode} />
    </>
  );
};
