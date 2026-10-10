import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import StockTable from '../components/StockTable';
import { Search, Filter } from 'lucide-react';

export default function Inventory({ selectedPhcId }) {
  const [inventories, setInventories] = useState([]);
  const [riskFilter, setRiskFilter] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const data = await api.getInventory(selectedPhcId, riskFilter || null);
      setInventories(data);
    } catch (err) {
      console.error("Inventory fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, [selectedPhcId, riskFilter]);

  const filteredItems = inventories.filter(item => {
    if (!searchTerm) return true;
    const term = searchTerm.toLowerCase();
    return (
      item.medicine?.name.toLowerCase().includes(term) ||
      item.medicine?.code.toLowerCase().includes(term) ||
      item.phc?.name.toLowerCase().includes(term)
    );
  });

  return (
    <div>
      <h1 className="page-title">Primary Health Centre Medicine Inventories</h1>
      <p className="page-subtitle">Track available stock, 7-day daily burn rate, and stock-out estimates across PHCs</p>

      {/* Search and Risk Filter Controls */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ display: 'flex', alignItems: 'center', background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-md)', padding: '0.5rem 0.85rem', width: '320px' }}>
          <Search size={18} color="var(--text-muted)" style={{ marginRight: '0.5rem' }} />
          <input
            type="text"
            placeholder="Search medicine or PHC..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-main)', outline: 'none', width: '100%', fontSize: '0.9rem' }}
          />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Filter size={16} color="var(--text-muted)" />
          <span style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Filter Risk:</span>
          {['', 'HIGH', 'MEDIUM', 'LOW'].map(level => (
            <button
              key={level}
              className="btn-action"
              style={{
                background: riskFilter === level ? 'var(--primary)' : 'var(--bg-card)',
                color: riskFilter === level ? '#fff' : 'var(--text-muted)',
                border: '1px solid var(--border-color)',
                fontSize: '0.8rem',
                padding: '0.35rem 0.75rem'
              }}
              onClick={() => setRiskFilter(level)}
            >
              {level === '' ? 'ALL' : level}
            </button>
          ))}
        </div>
      </div>

      <StockTable items={filteredItems} loading={loading} />
    </div>
  );
}
