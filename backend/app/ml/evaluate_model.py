import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from typing import Dict, Any

def evaluate_demand_model(
    model, 
    X_test: pd.DataFrame, 
    y_test: pd.Series,
    y_train: pd.Series
) -> Dict[str, Any]:
    """
    Evaluates trained scikit-learn model against a dummy baseline (mean predictor).
    Returns dictionary with MAE, RMSE, and R^2 score.
    """
    # 1. Model Predictions
    y_pred = model.predict(X_test)
    y_pred = np.clip(y_pred, a_min=0, a_max=None) # Non-negative constraint

    model_mae = mean_absolute_error(y_test, y_pred)
    model_rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    model_r2 = r2_score(y_test, y_pred)

    # 2. Baseline Predictor (Historical Mean)
    baseline_mean = y_train.mean()
    baseline_pred = np.full_like(y_test, fill_value=baseline_mean)

    baseline_mae = mean_absolute_error(y_test, baseline_pred)
    baseline_rmse = np.sqrt(mean_squared_error(y_test, baseline_pred))

    metrics = {
        "model_mae": round(float(model_mae), 2),
        "model_rmse": round(float(model_rmse), 2),
        "model_r2": round(float(model_r2), 4),
        "baseline_mae": round(float(baseline_mae), 2),
        "baseline_rmse": round(float(baseline_rmse), 2),
        "improvement_over_baseline_pct": round(float(((baseline_mae - model_mae) / baseline_mae) * 100), 2) if baseline_mae > 0 else 0.0
    }

    print("\n--- MediPulse ML Model Evaluation Report ---")
    print(f"Model MAE (Mean Absolute Error) : {metrics['model_mae']}")
    print(f"Model RMSE (Root Mean Sq Error)  : {metrics['model_rmse']}")
    print(f"Model R2 Score                   : {metrics['model_r2']}")
    print(f"Baseline MAE                     : {metrics['baseline_mae']}")
    print(f"Improvement over Baseline        : {metrics['improvement_over_baseline_pct']}%")
    print("-----------------------------------------------\n")

    return metrics
