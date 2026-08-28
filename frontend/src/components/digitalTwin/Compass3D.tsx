import React from 'react';
import { Text } from '@react-three/drei';

interface Compass3DProps {
  radius?: number;
}

export const Compass3D: React.FC<Compass3DProps> = ({ radius = 7.0 }) => {
  return (
    <group position={[-radius * 0.8, -radius * 0.8, 0.05]}>
      {/* Base Ring */}
      <mesh rotation={[-Math.PI / 2, 0, 0]}>
        <ringGeometry args={[0.7, 0.8, 32]} />
        <meshBasicMaterial color="#30363d" />
      </mesh>

      {/* Red North Arrow */}
      <mesh position={[0, 0.4, 0.02]} rotation={[0, 0, 0]}>
        <coneGeometry args={[0.18, 0.5, 16]} />
        <meshBasicMaterial color="#e74c3c" />
      </mesh>

      {/* North Label */}
      <Text
        position={[0, 0.85, 0.02]}
        fontSize={0.28}
        color="#e74c3c"
        anchorX="center"
        anchorY="middle"
      >
        N
      </Text>

      {/* East Pointer */}
      <mesh position={[0.4, 0, 0.02]} rotation={[0, 0, -Math.PI / 2]}>
        <coneGeometry args={[0.12, 0.35, 16]} />
        <meshBasicMaterial color="#7f8c8d" />
      </mesh>

      <Text
        position={[0.8, 0, 0.02]}
        fontSize={0.22}
        color="#bdc3c7"
        anchorX="center"
        anchorY="middle"
      >
        E
      </Text>
    </group>
  );
};
