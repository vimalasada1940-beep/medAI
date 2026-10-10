import React from 'react';
import { LayoutDashboard, Pill, AlertTriangle, ArrowRightLeft, FileText } from 'lucide-react';
import logo from '../assets/logo.svg';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'inventory', label: 'Medicine Inventory', icon: Pill },
  { id: 'alerts', label: 'Stock Alerts', icon: AlertTriangle },
  { id: 'redistribution', label: 'Smart Redistribution', icon: ArrowRightLeft },
  { id: 'indents', label: 'Emergency Indents', icon: FileText },
];

export default function Sidebar({ currentPage, setCurrentPage, selectedPhcId, setSelectedPhcId }) {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo-area">
        <img src={logo} alt="MediPulse Logo" className="sidebar-logo" />
        <div>
          <h1 className="brand-name">MediPulse</h1>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>
            PHC Early Warning System
          </span>
        </div>
      </div>

      <nav className="nav-list">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              className={`nav-item-btn ${isActive ? 'active' : ''}`}
              onClick={() => setCurrentPage(item.id)}
            >
              <Icon size={19} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="phc-filter-box">
        <div className="phc-label">Select Active PHC</div>
        <select
          className="phc-select"
          value={selectedPhcId || ''}
          onChange={(e) => setSelectedPhcId(e.target.value ? Number(e.target.value) : null)}
        >
          <option value="">All PHCs (District View)</option>
          <option value="1">PHC-001: Rampur Primary Health Centre</option>
          <option value="2">PHC-002: Bilaspur Community Health</option>
          <option value="3">PHC-003: Shahabad Sub-District Hosp</option>
          <option value="4">PHC-004: Suar Rural Health Centre</option>
          <option value="5">PHC-005: Milak Primary Health Unit</option>
        </select>
      </div>
    </aside>
  );
}
