import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import IndentCard from '../components/IndentCard';
import { PlusCircle, FileText, CheckCircle2 } from 'lucide-react';

export default function EmergencyIndents({ selectedPhcId }) {
  const [indents, setIndents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showNewModal, setShowNewModal] = useState(false);
  
  // New Indent form state
  const [phcIdInput, setPhcIdInput] = useState(selectedPhcId || 1);
  const [medIdInput, setMedIdInput] = useState(1);
  const [targetDaysInput, setTargetDaysInput] = useState(30);
  const [reasonInput, setReasonInput] = useState('Critical stock depletion early warning indent');

  const fetchIndents = async () => {
    setLoading(true);
    try {
      const data = await api.getIndents(selectedPhcId);
      setIndents(data);
    } catch (err) {
      console.error("Indents fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIndents();
  }, [selectedPhcId]);

  const handleUpdateStatus = async (indentId, newStatus) => {
    await api.updateIndentStatus(indentId, newStatus);
    fetchIndents();
  };

  const handleCreateIndentSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.createIndent({
        phc_id: Number(phcIdInput),
        medicine_id: Number(medIdInput),
        target_coverage_days: Number(targetDaysInput),
        reason: reasonInput
      });
      alert("✅ Emergency procurement indent generated successfully!");
      setShowNewModal(false);
      fetchIndents();
    } catch (err) {
      alert(`Indent creation failed: ${err.message}`);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 className="page-title">Emergency Procurement Indents</h1>
          <p className="page-subtitle">Generated when inter-PHC stock redistribution is insufficient to meet target coverage</p>
        </div>
        <button 
          className="btn-action btn-primary"
          onClick={() => setShowNewModal(true)}
        >
          <PlusCircle size={18} /> Generate Emergency Indent
        </button>
      </div>

      {loading ? (
        <div className="loading-box">Loading emergency indents...</div>
      ) : indents && indents.length > 0 ? (
        <div>
          {indents.map(indent => (
            <IndentCard key={indent.id} indent={indent} onUpdateStatus={handleUpdateStatus} />
          ))}
        </div>
      ) : (
        <div className="empty-box">
          <CheckCircle2 size={48} color="#10b981" style={{ marginBottom: '1rem' }} />
          <h3>No Pending Emergency Indents</h3>
          <p>No emergency procurement requests are currently active for the selected health centre.</p>
        </div>
      )}

      {/* Modal for Creating New Emergency Indent */}
      {showNewModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(15, 23, 42, 0.85)', backdropFilter: 'blur(4px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100
        }}>
          <div style={{
            background: 'var(--bg-card)', border: '1px solid var(--border-color)',
            borderRadius: 'var(--radius-lg)', padding: '1.75rem', maxWidth: '520px', width: '90%'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#38bdf8', marginBottom: '1.25rem' }}>
              <FileText size={24} />
              <h3 style={{ fontSize: '1.2rem' }}>Generate Emergency Indent</h3>
            </div>

            <form onSubmit={handleCreateIndentSubmit}>
              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Select PHC</label>
                <select 
                  className="phc-select"
                  value={phcIdInput}
                  onChange={(e) => setPhcIdInput(e.target.value)}
                >
                  <option value="1">PHC-001: Rampur Primary Health Centre</option>
                  <option value="2">PHC-002: Bilaspur Community Health</option>
                  <option value="3">PHC-003: Shahabad Sub-District Hosp</option>
                  <option value="4">PHC-004: Suar Rural Health Centre</option>
                  <option value="5">PHC-005: Milak Primary Health Unit</option>
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Select Medicine</label>
                <select 
                  className="phc-select"
                  value={medIdInput}
                  onChange={(e) => setMedIdInput(e.target.value)}
                >
                  <option value="1">MED-PAR-500: Paracetamol 500mg</option>
                  <option value="2">MED-AMO-500: Amoxicillin 500mg</option>
                  <option value="3">MED-ORS-21G: Oral Rehydration Salts</option>
                  <option value="4">MED-MET-500: Metformin 500mg</option>
                  <option value="5">MED-AML-005: Amlodipine 5mg</option>
                  <option value="6">MED-AZI-250: Azithromycin 250mg</option>
                </select>
              </div>

              <div style={{ marginBottom: '1rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Target Coverage (Days)</label>
                <input 
                  type="number" 
                  className="phc-select"
                  value={targetDaysInput}
                  onChange={(e) => setTargetDaysInput(e.target.value)}
                  min="7" max="90"
                />
              </div>

              <div style={{ marginBottom: '1.5rem' }}>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.35rem' }}>Reason / Justification</label>
                <textarea 
                  className="phc-select"
                  style={{ height: '70px', resize: 'none' }}
                  value={reasonInput}
                  onChange={(e) => setReasonInput(e.target.value)}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }}>
                <button 
                  type="button"
                  className="btn-action" 
                  style={{ background: 'var(--bg-card-hover)', color: 'var(--text-main)' }}
                  onClick={() => setShowNewModal(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  className="btn-action btn-primary"
                >
                  Submit Emergency Indent
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
