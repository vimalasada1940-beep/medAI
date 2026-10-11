import os
import pickle
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
try:
    import pandas as pd
except ImportError:
    pd = None

from sqlalchemy.orm import Session
from app.models import DailyConsumption, Inventory
from app.ml.feature_engineering import (
    REQUIRED_FEATURE_COLUMNS,
    FeatureValidationError,
    verify_feature_columns,
    extract_time_features,
    build_lag_and_rolling_features,
    prepare_feature_matrix
)
from app.services.burn_rate import calculate_phc_medicine_burn_rate

class MLModelNotFoundError(FileNotFoundError):
    """Raised when the trained ML model file (.pkl or .joblib) is not found or empty."""
    pass

class PreprocessingError(ValueError):
    """Raised when required preprocessing fails or input records are malformed."""
    pass

def get_model_candidate_paths() -> List[str]:
    """Returns candidate filepaths for the trained demand forecast model."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    return [
        os.path.join(base_dir, 'ml', 'medipulse_demand.pkl'),
        os.path.join(base_dir, 'app', 'artifacts', 'medipulse_demand.pkl'),
        os.path.join(base_dir, 'artifacts', 'medipulse_demand.pkl'),
        os.path.join(base_dir, 'app', 'artifacts', 'medipulse_demand_model.pkl'),
        os.path.join(base_dir, 'artifacts', 'medipulse_demand_model.pkl'),
        os.path.join(base_dir, 'ml', 'model.pkl'),
        os.path.join(base_dir, 'ml', 'demand_model.pkl'),
        os.path.join(base_dir, 'artifacts', 'demand_model.pkl'),
        os.path.join(base_dir, 'artifacts', 'demand_model.joblib'),
        os.path.join(base_dir, 'app', 'artifacts', 'demand_model.joblib'),
        os.path.abspath(os.path.join(base_dir, '..', 'ml', 'model.pkl')),
    ]



def load_trained_model(model_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads trained demand forecasting model (.pkl or .joblib).
    Searches backend/ml/ and backend/artifacts/ by default.
    Raises MLModelNotFoundError if no valid non-empty model file is found.
    Raises ValueError if the model file is corrupted or cannot be loaded.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    candidates = [model_path] if model_path else get_model_candidate_paths()

    found_path = None
    for p in candidates:
        if p and os.path.exists(p) and os.path.getsize(p) > 0:
            found_path = p
            break

    if not found_path:
        expected_pkl = os.path.join(base_dir, 'ml', 'model.pkl')
        expected_joblib = os.path.join(base_dir, 'artifacts', 'demand_model.joblib')
        raise MLModelNotFoundError(
            f"Trained model file not found or is 0 bytes. "
            f"Please place your trained '.pkl' model at: '{expected_pkl}' "
            f"(or '.joblib' at: '{expected_joblib}'). "
            f"Checked locations: {[os.path.normpath(c) for c in candidates if c]}"
        )

    # Attempt loading based on extension
    data = None
    try:
        if found_path.endswith('.pkl'):
            with open(found_path, 'rb') as f:
                data = pickle.load(f)
        else:
            try:
                import joblib
                data = joblib.load(found_path)
            except Exception as j_err:
                # Fallback to pickle
                with open(found_path, 'rb') as f:
                    data = pickle.load(f)
    except Exception as e:
        raise ValueError(
            f"Failed to load model file at '{found_path}': {type(e).__name__} - {str(e)}. "
            f"Ensure file is a valid pickled estimator compatible with your Python environment."
        )

    # Standardize output
    if isinstance(data, dict):
        model = data.get("model", data)
        feature_cols = data.get("feature_cols", REQUIRED_FEATURE_COLUMNS)
        metrics = data.get("metrics", {})
    else:
        model = data
        feature_cols = REQUIRED_FEATURE_COLUMNS
        metrics = {}

    return {
        "model": model,
        "feature_cols": feature_cols,
        "metrics": metrics,
        "model_path": found_path,
        "format": "pkl" if found_path.endswith('.pkl') else "joblib"
    }

def predict_phc_medicine_demand(
    db: Session,
    phc_id: int,
    medicine_id: int,
    forecast_days: int = 7
) -> Dict[str, Any]:
    """
    Predicts demand for a given PHC and medicine over the next `forecast_days`.
    If data is insufficient (< 7 historical consumption entries) or model artifact is missing,
    returns an understandable reliability warning with explicit missing file details.
    """
    model_data = None
    model_load_error = None

    try:
        model_data = load_trained_model()
    except MLModelNotFoundError as e:
        model_load_error = str(e)
    except Exception as e:
        model_load_error = f"Error loading model: {str(e)}"

    # Query historical daily consumption for this PHC & medicine
    records = db.query(DailyConsumption).filter(
        DailyConsumption.phc_id == phc_id,
        DailyConsumption.medicine_id == medicine_id
    ).order_by(DailyConsumption.record_date.asc()).all()

    historical_burn = calculate_phc_medicine_burn_rate(db, phc_id, medicine_id)

    # 1. Fallback if model is missing or data is insufficient
    if len(records) < 7 or model_data is None:
        predicted_daily_demand = historical_burn
        predicted_total_demand = round(historical_burn * forecast_days, 2)
        
        reason = []
        if len(records) < 7:
            reason.append(f"Insufficient historical data ({len(records)} entries, minimum 7 required)")
        if model_load_error:
            reason.append(model_load_error)

        return {
            "phc_id": phc_id,
            "medicine_id": medicine_id,
            "forecast_days": forecast_days,
            "predicted_daily_demand": predicted_daily_demand,
            "predicted_total_demand": predicted_total_demand,
            "is_reliable": False,
            "reliability_notice": (
                "⚠️ " + "; ".join(reason) + ". "
                f"Falling back to 7-day average daily burn rate ({historical_burn} units/day)."
            ),
            "error_detail": model_load_error,
            "method": "7-Day Moving Average Baseline"
        }

    # 2. ML Model Inference
    model = model_data["model"]
    feature_cols = model_data.get("feature_cols", REQUIRED_FEATURE_COLUMNS)

    df_raw = pd.DataFrame([{
        "record_date": r.record_date,
        "quantity_consumed": r.quantity_consumed
    } for r in records])

    try:
        df_feat = extract_time_features(df_raw, "record_date")
        df_feat = build_lag_and_rolling_features(df_feat, "quantity_consumed")
        verify_feature_columns(df_feat, feature_cols)
        X, _ = prepare_feature_matrix(df_feat, "quantity_consumed", verify=True)
    except Exception as prep_err:
        raise PreprocessingError(f"ML Preprocessing or feature verification failed: {str(prep_err)}")

    latest_X = X.iloc[-1:].copy()
    try:
        pred_val = model.predict(latest_X)[0]
    except Exception as inf_err:
        raise ValueError(f"Model inference failed on input features {list(latest_X.columns)}: {str(inf_err)}")

    pred_val = max(0.0, float(pred_val))
    total_pred = round(pred_val * forecast_days, 2)

    return {
        "phc_id": phc_id,
        "medicine_id": medicine_id,
        "forecast_days": forecast_days,
        "predicted_daily_demand": round(pred_val, 2),
        "predicted_total_demand": total_pred,
        "is_reliable": True,
        "reliability_notice": f"✅ Demand forecast generated via {model_data['format'].upper()} model ({os.path.basename(model_data['model_path'])}).",
        "method": f"{type(model).__name__} ML Model"
    }

