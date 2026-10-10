import React, { useState } from 'react';
import { ArrowRight, ShieldCheck, Navigation, AlertTriangle } from 'lucide-react';

export default function TransferCard({ rec, onRequestTransfer }) {
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleConfirm = async () => {
    setLoading(true);
    try {
      await onRequestTransfer({
        donor_phc_id: rec.donor_phc.id,
        recipient_phc_id: rec.recipient_phc.id,
        medicine_id: rec.medicine.id,
        proposed_quantity: rec.recommended_transfer_quantity,
        reason: rec.explanation
      });
      setShowConfirmModal(false);
    } catch (err) {
      alert(`Transfer request failed: ${err.message}`);
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
      marginBottom: '1.25rem'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h4 style={{ fontSize: '1.05rem', fontWeight: 600, color: '#38bdf8' }}>
          {rec.medicine.name}
        </h4>
        <span style={{ background: 'var(--teal-light)', color: '#2dd4bf', padding: '0.25rem 0.65rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
          <ShieldCheck size={14} /> Safety Validated
        </span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', alignItems: 'center', gap: '1rem', background: 'var(--bg-dark)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '1rem' }}>
        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>DONOR PHC (SURPLUS)</div>
          <div style={{ fontWeight: 600, color: '#10b981' }}>{rec.donor_phc.name}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Available: {rec.donor_available_stock} units (Safety: {rec.donor_safety_stock})
          </div>
        </div>

        <div style={{ textAlign: 'center' }}>
          <div style={{ background: 'var(--primary)', color: '#fff', borderRadius: '9999px', width: '36px', height: '36px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.25rem auto' }}>
            <ArrowRight size={18} />
          </div>
          <div style={{ fontSize: '0.75rem', fontWeight: 700, color: '#38bdf8' }}>
            {rec.recommended_transfer_quantity} units
          </div>
        </div>

        <div>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>RECIPIENT PHC (NEED)</div>
          <div style={{ fontWeight: 600, color: '#ef4444' }}>{rec.recipient_phc.name}</div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Stock: {rec.recipient_available_stock} units ({rec.recipient_days_remaining}d rem)
          </div>
        </div>
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          <Navigation size={14} />
          <span>Distance: {rec.distance_km} km</span>
        </div>

        <button 
          className="btn-action btn-teal"
          onClick={() => setShowConfirmModal(true)}
        >
          Propose Transfer
        </button>
      </div>

      {/* Confirmation Modal */}
      {showConfirmModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.85)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100
        }}>
          <div style={{
            background: 'var(--bg-card)', border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-lg)', padding: '1.75rem', maxWidth: '500px', width: '90%'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#f59e0b', marginBottom: '1rem' }}>
              <AlertTriangle size={24} />
              <h3 style={{ fontSize: '1.15rem' }}>Authorize Transfer Proposal</h3>
            </div>

            <p style={{ fontSize: '0.9rem', color: 'var(--text-main)', marginBottom: '1rem', lineHeight: '1.5' }}>
              Are you sure you want to submit a proposed transfer of <strong>{rec.recommended_transfer_quantity} units</strong> of <strong>{rec.medicine.name}</strong> from <strong>{rec.donor_phc.name}</strong> to <strong>{rec.recipient_phc.name}</strong>?
            </p>

            <div style={{ background: 'var(--bg-dark)', padding: '0.85rem', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
              🔒 <strong>Human Authorization Notice:</strong> This action creates a transfer request record. No automated physical dispatch occurs without authorized officer approval.
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
              <button 
                className="btn-action" 
                style={{ background: 'var(--bg-card-hover)', color: 'var(--text-main)' }}
                onClick={() => setShowConfirmModal(false)}
                disabled={loading}
              >
                Cancel
              </button>
              <button 
                className="btn-action btn-primary"
                onClick={handleConfirm}
                disabled={loading}
              >
                {loading ? 'Submitting...' : 'Confirm Request'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
