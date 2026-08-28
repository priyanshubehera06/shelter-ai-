import React, { useEffect, useRef, useState } from 'react';
import { Canvas, useThree } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';
import * as THREE from 'three';
import { useShelterStore } from '../../store/shelterStore';
import { fetchDigitalTwinConfig } from '../../api/endpoints';
import { EnvironmentScene } from '../../digitalTwin/scene/EnvironmentScene';
import { SolarSystem3D } from '../../digitalTwin/scene/SolarSystem3D';
import { Compass3D } from '../../digitalTwin/scene/Compass3D';
import { HeatFlowParticles } from '../../digitalTwin/scene/HeatFlowParticles';
import { ShelterModel } from '../../digitalTwin/models/ShelterModel';
import { DigitalTwinConfigResponse } from '../../types';

interface SceneContentProps {
  telemetry: DigitalTwinConfigResponse | null;
}

const SceneContent: React.FC<SceneContentProps> = ({ telemetry }) => {
  const { currentDesign, activeViewMode, cameraPreset, componentVisibility, simHour } = useShelterStore();
  const { camera } = useThree();
  const controlsRef = useRef<any>(null);

  const { length_m: L, width_m: W, height_m: H } = currentDesign.geometry;
  const centerY = (0.35 + H) / 2;

  // Thermal Surface Colors extraction from Sol-Air calculations
  const thermalColors: Record<string, string> = {};
  if (telemetry) {
    telemetry.components.forEach((c) => {
      if (c.name.includes('South')) thermalColors['south'] = c.thermal_color_hex || '#b58d6b';
      if (c.name.includes('North')) thermalColors['north'] = c.thermal_color_hex || '#b58d6b';
      if (c.name.includes('East')) thermalColors['east'] = c.thermal_color_hex || '#b58d6b';
      if (c.name.includes('West')) thermalColors['west'] = c.thermal_color_hex || '#b58d6b';
      if (c.name.includes('Roof')) thermalColors['roof'] = c.thermal_color_hex || '#34495e';
    });
  }

  // Camera Presets in Standard Y-UP Coordinate System
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

      {/* 1. Environment & Circular Ground Site Disc */}
      <EnvironmentScene geometry={currentDesign.geometry} />

      {/* 2. Astronomical NOAA Sun & 24h Spline Trajectory */}
      {componentVisibility.sun_path && (
        <SolarSystem3D solarData={telemetry?.solar} timeHour={simHour} />
      )}

      {/* 3. 3D Cardinal Orientation Compass (True North) */}
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

      {/* 5. Conceptual Airflow & Heat Flux Vectors */}
      <HeatFlowParticles geometry={currentDesign.geometry} viewMode={activeViewMode} />
    </>
  );
};

export const Viewport3D: React.FC = () => {
  const { currentDesign, selectedLocationId, selectedMonth, simHour, activeViewMode } = useShelterStore();
  const [telemetry, setTelemetry] = useState<DigitalTwinConfigResponse | null>(null);

  useEffect(() => {
    fetchDigitalTwinConfig({
      geometry: currentDesign.geometry,
      materials: currentDesign.materials,
      hour_of_day: simHour,
      location_id: selectedLocationId,
      month: selectedMonth,
      view_mode: activeViewMode,
    })
      .then((data) => setTelemetry(data))
      .catch((err) => console.error('Failed to load 3D telemetry:', err));
  }, [currentDesign, simHour, selectedLocationId, selectedMonth, activeViewMode]);

  return (
    <div className="relative flex-1 h-full w-full bg-[#0a0d12] overflow-hidden select-none">
      {/* 3D Canvas with Y-UP Default Camera */}
      <Canvas
        shadows
        camera={{ position: [8, 6, 9], fov: 45 }}
        className="w-full h-full cursor-grab active:cursor-grabbing"
      >
        <SceneContent telemetry={telemetry} />
      </Canvas>

      {/* Floating Interaction Hint */}
      <div className="absolute top-3 left-1/2 -translate-x-1/2 pointer-events-none px-3 py-1 bg-[#11161f]/80 backdrop-blur-md rounded-full border border-[#232c3d] text-[10px] font-medium text-slate-400">
        🖱️ Drag to rotate • Scroll to zoom • Right-click drag to pan
      </div>
    </div>
  );
};
