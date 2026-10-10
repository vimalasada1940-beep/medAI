import React from 'react';
import { AlertCircle, Clock, MapPin } from 'lucide-react';
import RiskBadge from './RiskBadge';

export default function AlertCard({ alert }) {
  const isHigh = alert.risk_level === 'HIGH';

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: `1px solid ${isHigh ? 'rgba(239, 68, 68, 0.4)' : 'rgba(245, 158, 11, 0.4)'}`,
      borderRadius: 'var(--radius-lg)',
      padding: '1.25rem',
      marginBottom: '1rem',
      boxShadow: 'var(--shadow-sm)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertCircle size={20} color={isHigh ? '#ef4444' : '#f59e0b'} />
          <h4 style={{ fontSize: '1rem', fontWeight: 600 }}>{alert.medicine?.name || `Medicine #${alert.medicine_id}`}</h4>
        </div>
        <RiskBadge level={alert.risk_level} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <MapPin size={14} />
          <span>{alert.phc?.name || `PHC #${alert.phc_id}`}</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
          <Clock size={14} />
          <span>Daily Burn: {alert.burn_rate} units/day</span>
        </div>
      </div>

      <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', lineHeight: '1.4' }}>
        {alert.message}
      </p>
    </div>
  );
}
