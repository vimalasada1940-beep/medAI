import React from 'react';
import { Activity, ShieldAlert } from 'lucide-react';

export default function Header({ currentPage, selectedPhcId }) {
  const getPageTitle = () => {
    switch (currentPage) {
      case 'dashboard': return 'Executive Overview';
      case 'inventory': return 'Live Medicine Inventories';
      case 'alerts': return 'Early Warning Stock Alerts';
      case 'redistribution': return 'Inter-PHC Smart Redistribution';
      case 'indents': return 'Emergency Procurement Indents';
      default: return 'Overview';
    }
  };

  const getPhcName = (id) => {
    const names = {
      1: 'Rampur PHC',
      2: 'Bilaspur CHC',
      3: 'Shahabad SDH',
      4: 'Suar RHC',
      5: 'Milak PHU'
    };
    return names[id] || 'All District PHCs';
  };

  return (
    <header className="header">
      <div className="header-title-group">
        <Activity size={24} color="#38bdf8" />
        <h2 style={{ fontSize: '1.2rem', fontWeight: 600 }}>{getPageTitle()}</h2>
        <span className="current-phc-badge">
          {getPhcName(selectedPhcId)}
        </span>
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fbbf24', fontSize: '0.8rem' }}>
        <ShieldAlert size={16} />
        <span>Student Decision-Support Prototype (Human Authorization Required)</span>
      </div>
    </header>
  );
}
