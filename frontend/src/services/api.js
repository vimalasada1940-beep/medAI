// MediPulse Backend API Client Service
// Uses native browser fetch API

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

async function handleResponse(response) {
  if (!response.ok) {
    let errorMsg = `HTTP Error ${response.status}: ${response.statusText}`;
    try {
      const errJson = await response.json();
      if (errJson.detail) {
        errorMsg = errJson.detail;
      } else if (errJson.message) {
        errorMsg = errJson.message;
      }
    } catch (e) {
      // Ignore json parse error
    }
    throw new Error(errorMsg);
  }
  return await response.json();
}

export const api = {
  // 1. Health Check
  getHealth: async () => {
    const res = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(res);
  },

  // 2. Dashboard Summary
  getDashboardSummary: async () => {
    const res = await fetch(`${API_BASE_URL}/dashboard/summary`);
    return handleResponse(res);
  },

  // 3. Inventory Records
  getInventory: async (phcId = null, riskLevel = null) => {
    let url = `${API_BASE_URL}/inventory`;
    const params = new URLSearchParams();
    if (phcId) params.append('phc_id', phcId);
    if (riskLevel) params.append('risk_level', riskLevel);

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    const res = await fetch(url);
    return handleResponse(res);
  },

  // 4. Stock Alerts
  getAlerts: async (phcId = null, riskLevel = null) => {
    let url = `${API_BASE_URL}/alerts`;
    const params = new URLSearchParams();
    if (phcId) params.append('phc_id', phcId);
    if (riskLevel) params.append('risk_level', riskLevel);

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    const res = await fetch(url);
    return handleResponse(res);
  },

  refreshAlerts: async () => {
    const res = await fetch(`${API_BASE_URL}/alerts/refresh`, {
      method: 'POST'
    });
    return handleResponse(res);
  },

  // 5. Redistribution Recommendations & Requests
  getRedistributionRecommendations: async (recipientPhcId = null) => {
    let url = `${API_BASE_URL}/redistribution/recommendations`;
    if (recipientPhcId) {
      url += `?recipient_phc_id=${recipientPhcId}`;
    }
    const res = await fetch(url);
    return handleResponse(res);
  },

  getRedistributionRequests: async (phcId = null) => {
    let url = `${API_BASE_URL}/redistribution/requests`;
    if (phcId) {
      url += `?phc_id=${phcId}`;
    }
    const res = await fetch(url);
    return handleResponse(res);
  },

  createRedistributionRequest: async (payload) => {
    const res = await fetch(`${API_BASE_URL}/redistribution/requests`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  // 6. Emergency Indents
  getIndents: async (phcId = null, status = null) => {
    let url = `${API_BASE_URL}/indents`;
    const params = new URLSearchParams();
    if (phcId) params.append('phc_id', phcId);
    if (status) params.append('status', status);

    if (params.toString()) {
      url += `?${params.toString()}`;
    }

    const res = await fetch(url);
    return handleResponse(res);
  },

  createIndent: async (payload) => {
    const res = await fetch(`${API_BASE_URL}/indents`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    return handleResponse(res);
  },

  updateIndentStatus: async (indentId, status) => {
    const res = await fetch(`${API_BASE_URL}/indents/${indentId}/status`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status })
    });
    return handleResponse(res);
  },

  // 7. CSV Data Ingestion
  uploadCsv: async (file, csvType = 'auto') => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE_URL}/ingestion/csv?csv_type=${csvType}`, {
      method: 'POST',
      body: formData
    });
    return handleResponse(res);
  }
};

