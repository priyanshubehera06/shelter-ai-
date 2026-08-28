import React from 'react';
import { Text } from '@react-three/drei';

interface Compass3DProps {
  radius?: number;
}

export const Compass3D: React.FC<Compass3DProps> = ({ radius = 6.5 }) => {
  return (
    <group position={[-radius * 0.85, 0.03, radius * 0.85]}>
      {/* Outer Dial Ring on X-Z Plane */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.7, 0.8, 32]} />
        <meshBasicMaterial color="#334155" />
      </mesh>

      {/* North Pointer (Red Cone Arrow along -Z) */}
      <mesh position={[0, 0.02, -0.4]} rotation={[-Math.PI / 2, 0, 0]}>
        <coneGeometry args={[0.16, 0.45, 16]} />
        <meshBasicMaterial color="#ef4444" />
      </mesh>
      <Text
        position={[0, 0.02, -0.85]}
        rotation={[-Math.PI / 2, 0, 0]}
        fontSize={0.28}
        color="#ef4444"
        anchorX="center"
        anchorY="middle"
      >
        N (0°)
      </Text>

      {/* East Pointer (+X) */}
      <mesh position={[0.4, 0.02, 0]} rotation={[0, 0, -Math.PI / 2]}>
        <coneGeometry args={[0.12, 0.35, 16]} />
        <meshBasicMaterial color="#64748b" />
      </mesh>
      <Text
        position={[0.85, 0.02, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        fontSize={0.22}
        color="#94a3b8"
        anchorX="center"
        anchorY="middle"
      >
        E (90°)
      </Text>

      {/* South Pointer (+Z) */}
      <mesh position={[0, 0.02, 0.4]} rotation={[Math.PI / 2, 0, 0]}>
        <coneGeometry args={[0.12, 0.35, 16]} />
        <meshBasicMaterial color="#64748b" />
      </mesh>
      <Text
        position={[0, 0.02, 0.85]}
        rotation={[-Math.PI / 2, 0, 0]}
        fontSize={0.22}
        color="#94a3b8"
        anchorX="center"
        anchorY="middle"
      >
        S (180°)
      </Text>

      {/* West Pointer (-X) */}
      <mesh position={[-0.4, 0.02, 0]} rotation={[0, 0, Math.PI / 2]}>
        <coneGeometry args={[0.12, 0.35, 16]} />
        <meshBasicMaterial color="#64748b" />
      </mesh>
      <Text
        position={[-0.85, 0.02, 0]}
        rotation={[-Math.PI / 2, 0, 0]}
        fontSize={0.22}
        color="#94a3b8"
        anchorX="center"
        anchorY="middle"
      >
        W (270°)
      </Text>
    </group>
  );
};
