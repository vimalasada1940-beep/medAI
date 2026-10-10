# MediPulse System Architecture 🏗️

## High-Level Architecture Overview
MediPulse follows a clean 3-tier web application architecture:

```
[ React + Vite SPA Frontend ]
          │  (REST API calls via fetch)
          ▼
[ FastAPI Backend Service ] ──▶ [ scikit-learn ML Engine ]
          │  (SQLAlchemy ORM)
          ▼
[ PostgreSQL Database (pgAdmin) ]
```

---

## Component Layers

### 1. Frontend Tier (React 18 + Vite)
- **Framework**: React 18 with Vite bundling.
- **Styling**: Custom CSS design system with CSS tokens, dark mode palette, and glassmorphism.
- **Charts**: Recharts Area & Line visualizations for 7-day burn trajectory.
- **API Client**: Modular native `fetch` service layer (`src/services/api.js`).

### 2. Backend Tier (FastAPI + Python 3.11/3.12)
- **App Entry**: `app/main.py` with CORS, `/api/v1` router composition, and global error handling.
- **Services**:
  - `burn_rate.py`: Computes 7-day average daily burn rate.
  - `acceleration.py`: Compares recent 7-day vs prior 7-day burn rate ratio.
  - `stockout_prediction.py`: Classifies risk thresholds (HIGH, MEDIUM, LOW).
  - `redistribution_engine.py`: Spatial Haversine donor matching with safety stock buffer enforcement.
  - `indent_generator.py`: Calculates 30-day target coverage emergency indents.
  - `alert_service.py`: Scans DB and manages stock alert records.

### 3. Machine Learning Tier (scikit-learn + joblib)
- **Feature Engineering**: Time features (`day_of_week`, `day_of_month`, `is_weekend`) + lag features (`lag_1d`, `lag_7d`, `rolling_7d_avg`) preventing future data leakage.
- **Model**: `RandomForestRegressor(n_estimators=100)`.
- **Artifact**: Saved as `backend/artifacts/demand_model.joblib`.

### 4. Database Tier (PostgreSQL)
- Relational schema defined in `backend/database/schema.sql`.
- ORM models in `backend/app/models.py`.
