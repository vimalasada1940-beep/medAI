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
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
