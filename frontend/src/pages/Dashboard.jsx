import React, { useEffect, useState, useRef } from 'react';
import { Building2, AlertOctagon, ArrowRightLeft, FileText, Pill, RefreshCw, Upload, CheckCircle2 } from 'lucide-react';
import { api } from '../services/api';
import StatCard from '../components/StatCard';
import StockTable from '../components/StockTable';
import TrendChart from '../components/TrendChart';
import AlertCard from '../components/AlertCard';

export default function Dashboard({ selectedPhcId, setCurrentPage }) {
  const [summary, setSummary] = useState(null);
  const [inventories, setInventories] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadStatus, setUploadStatus] = useState(null);
  const fileInputRef = useRef(null);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [sumRes, invRes, alertRes] = await Promise.all([
        api.getDashboardSummary(),
        api.getInventory(selectedPhcId),
        api.getAlerts(selectedPhcId, 'HIGH')
      ]);
      setSummary(sumRes);
      setInventories(invRes);
      setAlerts(alertRes);
    } catch (err) {
      console.error("Dashboard data load error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadStatus({ type: 'info', message: `Uploading ${file.name}...` });
    try {
      const res = await api.uploadCsv(file);
      const inserted = res.inserted_records || 0;
      const updated = res.updated_records || 0;
      setUploadStatus({
        type: 'success',
        message: `Successfully ingested CSV! (${inserted} new, ${updated} updated records). Refreshing dashboard...`
      });
      await loadDashboardData();
      setTimeout(() => setUploadStatus(null), 6000);
    } catch (err) {
      setUploadStatus({
        type: 'error',
        message: `CSV Upload Failed: ${err.message}`
      });
    } finally {
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, [selectedPhcId]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
        <div>
          <h1 className="page-title">Executive PHC Inventory Dashboard</h1>
          <p className="page-subtitle">Real-time early warning stock monitoring and smart redistribution analytics</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <input 
            type="file" 
            ref={fileInputRef} 
            onChange={handleFileUpload} 
            accept=".csv" 
            style={{ display: 'none' }} 
          />
          <button 
            className="btn-action"
            onClick={() => fileInputRef.current?.click()}
            style={{ 
              gap: '0.5rem', 
              background: 'rgba(14, 165, 233, 0.15)', 
              color: '#38bdf8', 
              border: '1px solid rgba(56, 189, 248, 0.3)' 
            }}
          >
            <Upload size={16} /> Ingest CSV Log
          </button>
          <button 
            className="btn-action btn-primary"
            onClick={loadDashboardData}
            style={{ gap: '0.5rem' }}
          >
            <RefreshCw size={16} /> Refresh Metrics
          </button>
        </div>
      </div>

      {uploadStatus && (
        <div style={{
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-md)',
          marginBottom: '1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem',
          fontSize: '0.875rem',
          background: uploadStatus.type === 'error' ? 'rgba(239, 68, 68, 0.15)' : (uploadStatus.type === 'success' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(56, 189, 248, 0.15)'),
          color: uploadStatus.type === 'error' ? '#ef4444' : (uploadStatus.type === 'success' ? '#10b981' : '#38bdf8'),
          border: `1px solid ${uploadStatus.type === 'error' ? '#ef4444' : (uploadStatus.type === 'success' ? '#10b981' : '#38bdf8')}`
        }}>
          {uploadStatus.type === 'success' ? <CheckCircle2 size={16} /> : <AlertOctagon size={16} />}
          {uploadStatus.message}
        </div>
      )}


      {/* Top Summary Stat Grid */}
      <div className="stat-grid">
        <StatCard
          title="Total Active PHCs"
          value={summary ? summary.total_phcs : '...'}
          icon={Building2}
          color="#0284c7"
          subtext="Monitoring Health Network"
        />
        <StatCard
          title="Medicines at Risk"
          value={summary ? summary.medicines_at_risk : '...'}
          icon={Pill}
          color="#f59e0b"
          subtext="Depletion or acceleration"
        />
        <StatCard
          title="High Risk Stock-Outs"
          value={summary ? summary.high_risk_stockouts : '...'}
          icon={AlertOctagon}
          color="#ef4444"
          subtext="≤ 3 Days Remaining"
        />
        <StatCard
          title="Pending Transfers / Indents"
          value={summary ? (summary.pending_redistributions + summary.pending_indents) : '...'}
          icon={ArrowRightLeft}
          color="#0d9488"
          subtext="Actionable Recommendations"
        />
      </div>

      {/* 7-Day Stock Consumption Trend Chart */}
      <TrendChart />

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600 }}>Live Inventory Status</h3>
            <button 
              style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 }}
              onClick={() => setCurrentPage('inventory')}
            >
              View All Inventories &rarr;
            </button>
          </div>
          <StockTable items={inventories.slice(0, 5)} loading={loading} />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 600, color: '#ef4444' }}>Critical Alerts</h3>
            <button 
              style={{ background: 'none', border: 'none', color: '#38bdf8', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600 }}
              onClick={() => setCurrentPage('alerts')}
            >
              View All Alerts &rarr;
            </button>
          </div>
          {alerts && alerts.length > 0 ? (
            alerts.slice(0, 3).map(alert => <AlertCard key={alert.id} alert={alert} />)
          ) : (
            <div className="empty-box" style={{ padding: '2rem 1rem' }}>
              No critical high-risk alerts active for selected PHC.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
