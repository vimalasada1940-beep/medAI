import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import TransferCard from '../components/TransferCard';
import { ArrowRightLeft, ShieldCheck, CheckCircle, Clock } from 'lucide-react';

export default function Redistribution({ selectedPhcId }) {
  const [recommendations, setRecommendations] = useState([]);
  const [existingRequests, setExistingRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('recommendations');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [recs, reqs] = await Promise.all([
        api.getRedistributionRecommendations(selectedPhcId),
        api.getRedistributionRequests(selectedPhcId)
      ]);
      setRecommendations(recs);
      setExistingRequests(reqs);
    } catch (err) {
      console.error("Redistribution data fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedPhcId]);

  const handleCreateRequest = async (payload) => {
    await api.createRedistributionRequest(payload);
    alert("✅ Transfer request submitted successfully for authorized officer review!");
    fetchData();
  };

  return (
    <div>
      <h1 className="page-title">Inter-PHC Smart Redistribution Engine</h1>
      <p className="page-subtitle">Matches high-risk recipient PHCs with nearby donor PHCs holding safe surplus stock</p>

      {/* Tabs */}
      <div style={{ display: 'flex', gap: '1rem', borderBottom: '1px solid var(--border-color)', marginBottom: '1.5rem' }}>
        <button
          className={`nav-item-btn ${activeTab === 'recommendations' ? 'active' : ''}`}
          style={{ width: 'auto', padding: '0.65rem 1.25rem', borderRadius: 'var(--radius-md) var(--radius-md) 0 0' }}
          onClick={() => setActiveTab('recommendations')}
        >
          <ShieldCheck size={18} />
          Recommended Safe Transfers ({recommendations.length})
        </button>
        <button
          className={`nav-item-btn ${activeTab === 'requests' ? 'active' : ''}`}
          style={{ width: 'auto', padding: '0.65rem 1.25rem', borderRadius: 'var(--radius-md) var(--radius-md) 0 0' }}
          onClick={() => setActiveTab('requests')}
        >
          <Clock size={18} />
          Existing Transfer Requests ({existingRequests.length})
        </button>
      </div>

      {loading ? (
        <div className="loading-box">Running spatial optimization algorithm...</div>
      ) : activeTab === 'recommendations' ? (
        recommendations && recommendations.length > 0 ? (
          <div>
            {recommendations.map((rec, idx) => (
              <TransferCard key={idx} rec={rec} onRequestTransfer={handleCreateRequest} />
            ))}
          </div>
        ) : (
          <div className="empty-box">
            <CheckCircle size={48} color="#10b981" style={{ marginBottom: '1rem' }} />
            <h3>No Active Redistribution Needed</h3>
            <p>All PHCs currently have balanced stock levels above safety thresholds, or no nearby donor has surplus.</p>
          </div>
        )
      ) : (
        /* Existing Requests Tab */
        existingRequests && existingRequests.length > 0 ? (
          <div className="table-container">
            <table className="custom-table">
              <thead>
                <tr>
                  <th>Request ID</th>
                  <th>Medicine</th>
                  <th>Donor PHC</th>
                  <th>Recipient PHC</th>
                  <th>Proposed Qty</th>
                  <th>Distance</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {existingRequests.map(req => (
                  <tr key={req.id}>
                    <td>#{req.id}</td>
                    <td style={{ fontWeight: 600 }}>{req.medicine?.name}</td>
                    <td style={{ color: '#10b981' }}>{req.donor_phc?.name}</td>
                    <td style={{ color: '#ef4444' }}>{req.recipient_phc?.name}</td>
                    <td style={{ fontWeight: 700 }}>{req.proposed_quantity} units</td>
                    <td>{req.distance_km} km</td>
                    <td>
                      <span style={{ background: 'rgba(56, 189, 248, 0.15)', color: '#38bdf8', padding: '0.2rem 0.6rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 700 }}>
                        {req.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="empty-box">No existing transfer requests found.</div>
        )
      )}
    </div>
  );
}
