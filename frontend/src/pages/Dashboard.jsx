import React, { useEffect, useState } from 'react';
import { Building2, AlertOctagon, ArrowRightLeft, FileText, Pill, RefreshCw } from 'lucide-react';
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

  useEffect(() => {
    loadDashboardData();
  }, [selectedPhcId]);

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <div>
          <h1 className="page-title">Executive PHC Inventory Dashboard</h1>
          <p className="page-subtitle">Real-time early warning stock monitoring and smart redistribution analytics</p>
        </div>
        <button 
          className="btn-action btn-primary"
          onClick={loadDashboardData}
          style={{ gap: '0.5rem' }}
        >
          <RefreshCw size={16} /> Refresh Metrics
        </button>
      </div>

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
