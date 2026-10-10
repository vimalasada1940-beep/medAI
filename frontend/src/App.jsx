import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';

import Dashboard from './pages/Dashboard';
import Inventory from './pages/Inventory';
import Alerts from './pages/Alerts';
import Redistribution from './pages/Redistribution';
import EmergencyIndents from './pages/EmergencyIndents';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [selectedPhcId, setSelectedPhcId] = useState(null);

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard selectedPhcId={selectedPhcId} setCurrentPage={setCurrentPage} />;
      case 'inventory':
        return <Inventory selectedPhcId={selectedPhcId} />;
      case 'alerts':
        return <Alerts selectedPhcId={selectedPhcId} />;
      case 'redistribution':
        return <Redistribution selectedPhcId={selectedPhcId} />;
      case 'indents':
        return <EmergencyIndents selectedPhcId={selectedPhcId} />;
      default:
        return <Dashboard selectedPhcId={selectedPhcId} setCurrentPage={setCurrentPage} />;
    }
  };

  return (
    <div className="app-container">
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        selectedPhcId={selectedPhcId}
        setSelectedPhcId={setSelectedPhcId}
      />
      <div className="main-content">
        <Header currentPage={currentPage} selectedPhcId={selectedPhcId} />
        <main className="page-wrapper">
          <div className="disclaimer-banner">
            ⚠️ <strong>Student Decision-Support Prototype Notice:</strong> Demonstrates stock monitoring, burn rate forecasting, and redistribution recommendations using synthetic data. Never presents real government health data. Transfers and indents require authorized human review.
          </div>
          {renderPage()}
        </main>
      </div>
    </div>
  );
}
