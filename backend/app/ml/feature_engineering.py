from __future__ import annotations
try:
    import pandas as pd
    import numpy as np
except ImportError:
    pd = None
    np = None
from typing import Tuple, Any, List


def extract_time_features(df: Any, date_column: str = "record_date") -> Any:
    """
    Extracts time-based features from a pandas DataFrame containing a date column.
    Guarantees no future data leakage.
    """
    if pd is None:
        raise ImportError("pandas could not be loaded in the current environment.")
    df = df.copy()

    df[date_column] = pd.to_datetime(df[date_column])
    df = df.sort_values(date_column).reset_index(drop=True)

    df["day_of_week"] = df[date_column].dt.dayofweek
    df["day_of_month"] = df[date_column].dt.day
    df["month"] = df[date_column].dt.month
    df["is_weekend"] = df["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)

    return df

def build_lag_and_rolling_features(
    df: pd.DataFrame, 
    target_column: str = "quantity_consumed",
    group_columns: list = None
) -> pd.DataFrame:
    """
    Generates lag features (lag_1d, lag_7d) and rolling average features (rolling_7d_avg).
    Uses strict past shift (.shift(1)) to prevent data leakage.
    """
    df = df.copy()
    
    if group_columns:
        # Grouped lag calculation (e.g. per phc_id and medicine_id)
        df["lag_1d"] = df.groupby(group_columns)[target_column].shift(1)
        df["lag_7d"] = df.groupby(group_columns)[target_column].shift(7)
        df["rolling_7d_avg"] = (
            df.groupby(group_columns)[target_column]
            .transform(lambda x: x.shift(1).rolling(window=7, min_periods=1).mean())
        )
    else:
        df["lag_1d"] = df[target_column].shift(1)
        df["lag_7d"] = df[target_column].shift(7)
        df["rolling_7d_avg"] = df[target_column].shift(1).rolling(window=7, min_periods=1).mean()

    # Fill NaNs resulting from shifts with forward fill or median
    df["lag_1d"] = df["lag_1d"].fillna(df[target_column].median() if not df[target_column].empty else 0)
    df["lag_7d"] = df["lag_7d"].fillna(df["lag_1d"])
    df["rolling_7d_avg"] = df["rolling_7d_avg"].fillna(df["lag_1d"])

    return df

REQUIRED_FEATURE_COLUMNS = [
    "day_of_week", 
    "day_of_month", 
    "month", 
    "is_weekend", 
    "lag_1d", 
    "lag_7d", 
    "rolling_7d_avg"
]

class FeatureValidationError(ValueError):
    """Raised when one or more required ML feature columns are missing from the input data."""
    pass

def verify_feature_columns(df: Any, required_cols: list = None) -> None:
    """
    Verifies that all required feature columns are present in the DataFrame or dict.
    Raises FeatureValidationError with exact missing column names if any are absent.
    """
    if required_cols is None:
        required_cols = REQUIRED_FEATURE_COLUMNS
    
    if hasattr(df, "columns"):
        available = set(df.columns)
    elif isinstance(df, dict):
        available = set(df.keys())
    elif hasattr(df, "__iter__"):
        available = set(df)
    else:
        available = set()

    missing = [c for c in required_cols if c not in available]
    if missing:
        raise FeatureValidationError(
            f"Missing required ML feature columns: {missing}. Expected columns: {required_cols}"
        )


def load_preprocessing_artifact(artifact_path: str = None):
    """
    Loads a serialized preprocessing artifact (.pkl or .joblib) if available.
    If artifact_path is specified and not found, raises FileNotFoundError.
    If no path is specified, searches backend/ml/ and backend/artifacts/.
    Returns None if no dedicated serialized preprocessor is configured.
    """
    import os
    if artifact_path:
        if not os.path.exists(artifact_path):
            raise FileNotFoundError(f"Preprocessing artifact not found at: {artifact_path}")
        try:
            import pickle
            with open(artifact_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load preprocessing artifact from {artifact_path}: {e}")

    # Check default locations
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    candidates = [
        os.path.join(base_dir, 'ml', 'preprocessing_artifacts.pkl'),
        os.path.join(base_dir, 'app', 'artifacts', 'preprocessing_artifacts.pkl'),
        os.path.join(base_dir, 'artifacts', 'preprocessing_artifacts.pkl'),
        os.path.join(base_dir, 'ml', 'preprocessor.pkl'),
        os.path.join(base_dir, 'artifacts', 'preprocessor.pkl'),
        os.path.join(base_dir, 'ml', 'scaler.pkl'),
        os.path.join(base_dir, 'artifacts', 'scaler.pkl'),
    ]

    for c in candidates:
        if os.path.exists(c) and os.path.getsize(c) > 0:
            try:
                import pickle
                with open(c, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                raise ValueError(f"Failed to load preprocessing artifact from {c}: {e}")
    return None

def prepare_feature_matrix(
    df: pd.DataFrame, 
    target_column: str = "quantity_consumed",
    verify: bool = True
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepares feature matrix X and target vector y for model training or inference.
    If verify is True, verifies that all required feature columns exist.
    """
    feature_cols = REQUIRED_FEATURE_COLUMNS
    
    if verify:
        verify_feature_columns(df, feature_cols)
    else:
        for col in feature_cols:
            if col not in df.columns:
                df[col] = 0

    X = df[feature_cols].copy()
    y = df[target_column].copy() if target_column in df.columns else None

    return X, y

