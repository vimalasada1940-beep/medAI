import React from 'react';
import { AlertCircle, AlertTriangle, CheckCircle } from 'lucide-react';

export default function RiskBadge({ level }) {
  const normalized = (level || 'LOW').toUpperCase();

  if (normalized === 'HIGH') {
    return (
      <span className="risk-badge high">
        <AlertCircle size={12} /> HIGH (≤3d)
      </span>
    );
  }

  if (normalized === 'MEDIUM') {
    return (
      <span className="risk-badge medium">
        <AlertTriangle size={12} /> MEDIUM (4-7d)
      </span>
    );
  }

  return (
    <span className="risk-badge low">
      <CheckCircle size={12} /> LOW (&gt;7d)
    </span>
  );
}
