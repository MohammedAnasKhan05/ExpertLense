import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import OverviewPage from './pages/OverviewPage';
import AnalysisPage from './pages/AnalysisPage';
import ComparisonPage from './pages/ComparisonPage';
import ThemesPage from './pages/ThemesPage';
import ResearchPage from './pages/ResearchPage';
import SourcesPage from './pages/SourcesPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<OverviewPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/comparison" element={<ComparisonPage />} />
            <Route path="/themes" element={<ThemesPage />} />
            <Route path="/research" element={<ResearchPage />} />
            <Route path="/sources" element={<SourcesPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
