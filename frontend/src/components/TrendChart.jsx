import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function TrendChart({ data }) {
  // Sample fallback synthetic trend data if empty
  const sampleData = data && data.length > 0 ? data : [
    { day: 'Day 1', Paracetamol: 75, Amoxicillin: 50, Metformin: 60 },
    { day: 'Day 2', Paracetamol: 78, Amoxicillin: 48, Metformin: 58 },
    { day: 'Day 3', Paracetamol: 72, Amoxicillin: 52, Metformin: 62 },
    { day: 'Day 4', Paracetamol: 80, Amoxicillin: 55, Metformin: 65 },
    { day: 'Day 5', Paracetamol: 85, Amoxicillin: 53, Metformin: 70 },
    { day: 'Day 6', Paracetamol: 90, Amoxicillin: 60, Metformin: 75 },
    { day: 'Day 7', Paracetamol: 92, Amoxicillin: 62, Metformin: 78 },
  ];

  return (
    <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius-lg)', padding: '1.5rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <div>
          <h3 style={{ fontSize: '1.1rem', fontWeight: 600 }}>7-Day Daily Consumption & Burn Trajectory</h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Synthetic consumption trends for primary health center medicines</p>
        </div>
      </div>

      <div style={{ width: '100%', height: 280 }}>
        <ResponsiveContainer>
          <AreaChart data={sampleData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="colorPara" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorAmox" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#38bdf8" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="day" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip 
              contentStyle={{ background: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#f8fafc' }}
            />
            <Area type="monotone" dataKey="Paracetamol" stroke="#ef4444" fillOpacity={1} fill="url(#colorPara)" strokeWidth={2} />
            <Area type="monotone" dataKey="Amoxicillin" stroke="#38bdf8" fillOpacity={1} fill="url(#colorAmox)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
