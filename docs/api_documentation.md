# MediPulse REST API Reference 📡

Base URL: `http://localhost:8000/api/v1`

---

## Endpoints Summary

### 1. Health Check
- **`GET /health`** or **`GET /api/v1/health`**
  - **Response**: `200 OK`
  ```json
  {
    "status": "healthy",
    "app_name": "MediPulse",
    "environment": "development",
    "prototype_disclaimer": "Student decision-support prototype."
  }
  ```

### 2. Dashboard Overview
- **`GET /api/v1/dashboard/summary`**
  - **Response**: `200 OK`
  ```json
  {
    "total_phcs": 5,
    "total_medicines": 6,
    "medicines_at_risk": 4,
    "high_risk_stockouts": 3,
    "pending_redistributions": 0,
    "pending_indents": 0,
    "synthetic_notice": "DEMONSTRATION ONLY: Synthetic data for student prototype."
  }
  ```

### 3. Inventory API
- **`GET /api/v1/inventory?phc_id=1&risk_level=HIGH`**
  - Returns inventory list with calculated `burn_rate` and `days_remaining`.
- **`GET /api/v1/inventory/{inventory_id}`**
- **`POST /api/v1/inventory`**

### 4. Stock Alerts API
- **`GET /api/v1/alerts?risk_level=HIGH`**
- **`POST /api/v1/alerts/refresh`**

### 5. Smart Redistribution API
- **`GET /api/v1/redistribution/recommendations?recipient_phc_id=1`**
  - Calculates inter-PHC recommendations ensuring donor safety stock buffer.
- **`GET /api/v1/redistribution/requests`**
- **`POST /api/v1/redistribution/requests`**

### 6. Emergency Indents API
- **`GET /api/v1/indents?status=PENDING`**
- **`POST /api/v1/indents`**
- **`PATCH /api/v1/indents/{indent_id}/status`**
  - Accepts payload `{"status": "APPROVED"}` or `{"status": "REJECTED"}`.

### 7. Data Ingestion API
- **`POST /api/v1/ingestion/csv`**
  - Multipart form upload of daily consumption CSV logs.
