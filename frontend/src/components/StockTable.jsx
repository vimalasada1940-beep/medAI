import React from 'react';
import RiskBadge from './RiskBadge';

export default function StockTable({ items, loading }) {
  if (loading) {
    return <div className="loading-box">Loading live inventory records...</div>;
  }

  if (!items || items.length === 0) {
    return <div className="empty-box">No inventory records found for the selected PHC.</div>;
  }

  return (
    <div className="table-container">
      <table className="custom-table">
        <thead>
          <tr>
            <th>Health Centre (PHC)</th>
            <th>Medicine Name</th>
            <th>Category</th>
            <th>Available Stock</th>
            <th>Daily Burn Rate</th>
            <th>Days Remaining</th>
            <th>Risk Level</th>
            <th>Clinical Urgency</th>
          </tr>
        </thead>
        <tbody>
          {items.map((item) => (
            <tr key={item.id}>
              <td style={{ fontWeight: 600 }}>{item.phc?.name || `PHC #${item.phc_id}`}</td>
              <td>
                <div style={{ fontWeight: 600 }}>{item.medicine?.name || `MED #${item.medicine_id}`}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{item.medicine?.code}</div>
              </td>
              <td>{item.medicine?.category || 'General'}</td>
              <td style={{ fontWeight: 700, fontSize: '1rem' }}>
                {item.available_stock.toLocaleString()} {item.medicine?.unit || 'units'}
              </td>
              <td>{item.burn_rate} / day</td>
              <td style={{ fontWeight: 600, color: item.days_remaining <= 3 ? '#ef4444' : (item.days_remaining <= 7 ? '#f59e0b' : '#10b981') }}>
                {item.days_remaining !== null ? `${item.days_remaining} days` : 'No Burn Rate'}
              </td>
              <td>
                <RiskBadge level={item.risk_level} />
              </td>
              <td>
                <span style={{
                  padding: '0.2rem 0.55rem',
                  borderRadius: '4px',
                  fontSize: '0.75rem',
                  fontWeight: 700,
                  background: item.clinical_urgency === 'CRITICAL' ? 'rgba(239, 68, 68, 0.2)' : (item.clinical_urgency === 'HIGH' ? 'rgba(245, 158, 11, 0.2)' : (item.clinical_urgency === 'MODERATE' ? 'rgba(56, 189, 248, 0.2)' : 'rgba(16, 185, 129, 0.15)')),
                  color: item.clinical_urgency === 'CRITICAL' ? '#ef4444' : (item.clinical_urgency === 'HIGH' ? '#f59e0b' : (item.clinical_urgency === 'MODERATE' ? '#38bdf8' : '#10b981')),
                  border: `1px solid ${item.clinical_urgency === 'CRITICAL' ? '#ef4444' : (item.clinical_urgency === 'HIGH' ? '#f59e0b' : (item.clinical_urgency === 'MODERATE' ? '#38bdf8' : '#10b981'))}`
                }}>
                  {item.clinical_urgency || 'ROUTINE'}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>

  );
}
