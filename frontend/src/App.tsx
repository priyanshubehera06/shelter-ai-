import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from './components/layout/AppLayout';
import { HomePage } from './pages/HomePage';
import { LocationClimatePage } from './pages/LocationClimatePage';
import { ShelterDesignLabPage } from './pages/ShelterDesignLabPage';
import { MaterialRecommendationsPage } from './pages/MaterialRecommendationsPage';
import { DigitalTwinPage } from './pages/DigitalTwinPage';
import { WhatIfLabPage } from './pages/WhatIfLabPage';
import { OptimizationPage } from './pages/OptimizationPage';
import { ResultsPage } from './pages/ResultsPage';

export const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<AppLayout />}>
          {/* Core Thermal Engineering Workflow Routes */}
          <Route index element={<HomePage />} />
          <Route path="climate" element={<LocationClimatePage />} />
          <Route path="design" element={<ShelterDesignLabPage />} />
          <Route path="materials" element={<MaterialRecommendationsPage />} />
          <Route path="simulate" element={<DigitalTwinPage />} />
          <Route path="compare" element={<WhatIfLabPage />} />
          <Route path="optimization" element={<OptimizationPage />} />
          <Route path="optimize" element={<OptimizationPage />} />
          <Route path="results" element={<ResultsPage />} />

          {/* Backward compatibility redirects */}
          <Route path="location" element={<Navigate to="/climate" replace />} />
          <Route path="digital-twin" element={<Navigate to="/simulate" replace />} />
          <Route path="what-if" element={<Navigate to="/compare" replace />} />
          <Route path="recommendations" element={<Navigate to="/materials" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
};

export default App;
