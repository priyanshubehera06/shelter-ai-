import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { HomePage } from './pages/HomePage';
import { LocationClimatePage } from './pages/LocationClimatePage';
import { ClimateIntelligencePage } from './pages/ClimateIntelligencePage';
import { ShelterDesignLabPage } from './pages/ShelterDesignLabPage';
import { DigitalTwinPage } from './pages/DigitalTwinPage';
import { OptimizationPage } from './pages/OptimizationPage';
import { WhatIfLabPage } from './pages/WhatIfLabPage';
import { ResultsPage } from './pages/ResultsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          <Route index element={<HomePage />} />
          <Route path="location" element={<LocationClimatePage />} />
          <Route path="climate" element={<ClimateIntelligencePage />} />
          <Route path="design" element={<ShelterDesignLabPage />} />
          <Route path="digital-twin" element={<DigitalTwinPage />} />
          <Route path="optimization" element={<OptimizationPage />} />
          <Route path="what-if" element={<WhatIfLabPage />} />
          <Route path="results" element={<ResultsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
