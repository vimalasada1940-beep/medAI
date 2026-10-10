import React from 'react';

export default function StatCard({ title, value, icon: Icon, color = '#0284c7', subtext }) {
  return (
    <div className="stat-card">
      <div>
        <div className="stat-title">{title}</div>
        <div className="stat-value">{value}</div>
        {subtext && <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>{subtext}</div>}
      </div>
      <div 
        className="stat-icon-wrapper" 
        style={{ background: `${color}20`, color: color }}
      >
        <Icon size={24} />
      </div>
    </div>
  );
}
