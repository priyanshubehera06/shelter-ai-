import React from 'react';
import { DigitalTwinWorkspace } from '../components/digitalTwin/DigitalTwinWorkspace';

export const DigitalTwinPage: React.FC = () => {
  return (
    <div className="h-[calc(100vh-4rem)] -m-6 md:-m-8 overflow-hidden">
      <DigitalTwinWorkspace />
    </div>
  );
};
