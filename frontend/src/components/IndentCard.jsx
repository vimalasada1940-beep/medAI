import React, { useState } from 'react';
import { FileText, CheckCircle2, XCircle, Truck, Clock } from 'lucide-react';

export default function IndentCard({ indent, onUpdateStatus }) {
  const [loading, setLoading] = useState(false);

  const getStatusBadge = (status) => {
    switch (status) {
      case 'APPROVED':
        return <span style={{ background: 'rgba(16, 185, 129, 0.15)', color: '#10b981', padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 700 }}>APPROVED</span>;
      case 'REJECTED':
        return <span style={{ background: 'rgba(239, 68, 68, 0.15)', color: '#ef4444', padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 700 }}>REJECTED</span>;
      case 'DISPATCHED':
        return <span style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 700 }}>DISPATCHED</span>;
      default:
        return <span style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 700 }}>PENDING REVIEW</span>;
    }
  };

  const handleAction = async (newStatus) => {
    if (!window.confirm(`Are you sure you want to change indent #${indent.id} status to ${newStatus}?`)) {
      return;
    }

    setLoading(true);
    try {
      await onUpdateStatus(indent.id, newStatus);
    } catch (err) {
      alert(`Status update failed: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: 'var(--radius-lg)',
      padding: '1.25rem',
      marginBottom: '1rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={18} color="#38bdf8" />
            <h4 style={{ fontSize: '1.05rem', fontWeight: 600 }}>{indent.medicine?.name || `Medicine #${indent.medicine_id}`}</h4>
          </div>
          <div style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            {indent.phc?.name || `PHC #${indent.phc_id}`}
          </div>
        </div>
        {getStatusBadge(indent.status)}
      </div>

      <div style={{ background: 'var(--bg-dark)', padding: '0.85rem 1rem', borderRadius: 'var(--radius-md)', display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.5rem', margin: '0.85rem 0' }}>
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>REQUESTED INDENT</span>
          <strong style={{ fontSize: '1.1rem', color: '#38bdf8' }}>{indent.requested_quantity} units</strong>
        </div>
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>CURRENT STOCK</span>
          <span style={{ fontWeight: 600 }}>{indent.current_stock} units</span>
        </div>
        <div>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block' }}>DAILY BURN RATE</span>
          <span style={{ fontWeight: 600 }}>{indent.burn_rate} / day</span>
        </div>
      </div>

      <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem', fontStyle: 'italic' }}>
        "{indent.reason}"
      </p>

      {indent.status === 'PENDING' && (
        <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'flex-end' }}>
          <button 
            className="btn-action btn-danger"
            onClick={() => handleAction('REJECTED')}
            disabled={loading}
          >
            <XCircle size={15} /> Reject
          </button>
          <button 
            className="btn-action btn-teal"
            onClick={() => handleAction('APPROVED')}
            disabled={loading}
          >
            <CheckCircle2 size={15} /> Approve Indent
          </button>
        </div>
      )}

      {indent.status === 'APPROVED' && (
        <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
          <button 
            className="btn-action btn-primary"
            onClick={() => handleAction('DISPATCHED')}
            disabled={loading}
          >
            <Truck size={15} /> Mark Dispatched
          </button>
        </div>
      )}
    </div>
  );
}
