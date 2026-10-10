import os
import joblib
import pandas as pd
import numpy as np
from datetime import date, timedelta
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from app.models import DailyConsumption, Inventory
from app.ml.feature_engineering import extract_time_features, build_lag_and_rolling_features, prepare_feature_matrix
from app.services.burn_rate import calculate_phc_medicine_burn_rate

def load_trained_model():
    """Loads trained joblib demand model from backend/artifacts/demand_model.joblib."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    model_path = os.path.join(base_dir, 'artifacts', 'demand_model.joblib')

    if not os.path.exists(model_path):
        return None

    try:
        data = joblib.load(model_path)
        return data
    except Exception:
        return None

def predict_phc_medicine_demand(
    db: Session,
    phc_id: int,
    medicine_id: int,
    forecast_days: int = 7
) -> Dict[str, Any]:
    """
    Predicts demand for a given PHC and medicine over the next `forecast_days`.
    If data is insufficient (< 7 historical consumption entries) or model artifact is missing,
    returns an understandable reliability warning instead of ungrounded predictions.
    """
    model_data = load_trained_model()

    # Query historical daily consumption for this PHC & medicine
    records = db.query(DailyConsumption).filter(
        DailyConsumption.phc_id == phc_id,
        DailyConsumption.medicine_id == medicine_id
    ).order_by(DailyConsumption.record_date.asc()).all()

    historical_burn = calculate_phc_medicine_burn_rate(db, phc_id, medicine_id)

    # 1. Check data sufficiency
    if len(records) < 7 or model_data is None:
        predicted_daily_demand = historical_burn
        predicted_total_demand = round(historical_burn * forecast_days, 2)
        
        return {
            "phc_id": phc_id,
            "medicine_id": medicine_id,
            "forecast_days": forecast_days,
            "predicted_daily_demand": predicted_daily_demand,
            "predicted_total_demand": predicted_total_demand,
            "is_reliable": False,
            "reliability_notice": (
                "⚠️ Insufficient historical data or uncalibrated ML model. "
                f"Falling back to 7-day average daily burn rate ({historical_burn} units/day). "
                "Demonstration student prototype notice."
            ),
            "method": "7-Day Moving Average Baseline"
        }

    # 2. ML Model Inference
    model = model_data["model"]
    feature_cols = model_data["feature_cols"]

    df_raw = pd.DataFrame([{
        "record_date": r.record_date,
        "quantity_consumed": r.quantity_consumed
    } for r in records])

    df_feat = extract_time_features(df_raw, "record_date")
    df_feat = build_lag_and_rolling_features(df_feat, "quantity_consumed")
    X, _ = prepare_feature_matrix(df_feat, "quantity_consumed")

    latest_X = X.iloc[-1:].copy()
    pred_val = model.predict(latest_X)[0]
    pred_val = max(0.0, float(pred_val))

    total_pred = round(pred_val * forecast_days, 2)

    return {
        "phc_id": phc_id,
        "medicine_id": medicine_id,
        "forecast_days": forecast_days,
        "predicted_daily_demand": round(pred_val, 2),
        "predicted_total_demand": total_pred,
        "is_reliable": True,
        "reliability_notice": "✅ Demand forecast generated via scikit-learn RandomForestRegressor model.",
        "method": "RandomForestRegressor ML Model"
    }
