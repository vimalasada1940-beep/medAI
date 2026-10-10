import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import AlertCard from '../components/AlertCard';
import { RefreshCw, ShieldAlert } from 'lucide-react';

export default function Alerts({ selectedPhcId }) {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const data = await api.getAlerts(selectedPhcId);
      setAlerts(data);
    } catch (err) {
      console.error("Alerts fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleManualRefresh = async () => {
    setRefreshing(true);
    try {
      await api.refreshAlerts();
      await fetchAlerts();
    } catch (err) {
      alert(`Refresh failed: ${err.message}`);
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [selectedPhcId]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 className="page-title">Early Warning Stock & Acceleration Alerts</h1>
          <p className="page-subtitle">Automatically triggered when days remaining ≤ 7 days or rapid consumption acceleration is detected</p>
        </div>
        <button 
          className="btn-action btn-primary"
          onClick={handleManualRefresh}
          disabled={refreshing}
        >
          <RefreshCw size={16} className={refreshing ? 'spin' : ''} />
          {refreshing ? 'Scanning DB...' : 'Re-scan Alerts'}
        </button>
      </div>

      {loading ? (
        <div className="loading-box">Loading active stock alerts...</div>
      ) : alerts && alerts.length > 0 ? (
        <div>
          {alerts.map(alert => (
            <AlertCard key={alert.id} alert={alert} />
          ))}
        </div>
      ) : (
        <div className="empty-box">
          <ShieldAlert size={48} color="#10b981" style={{ marginBottom: '1rem' }} />
          <h3>No Active High/Medium Alerts</h3>
          <p>All monitored medicine inventories for this health center have adequate stock levels.</p>
        </div>
      )}
    </div>
  );
}
