import pandas as pd
import numpy as np
from typing import Tuple

def extract_time_features(df: pd.DataFrame, date_column: str = "record_date") -> pd.DataFrame:
    """
    Extracts time-based features from a pandas DataFrame containing a date column.
    Guarantees no future data leakage.
    """
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

def prepare_feature_matrix(
    df: pd.DataFrame, 
    target_column: str = "quantity_consumed"
) -> Tuple[pd.DataFrame, pd.Series]:
    """
    Prepares feature matrix X and target vector y for scikit-learn model training.
    """
    feature_cols = ["day_of_week", "day_of_month", "month", "is_weekend", "lag_1d", "lag_7d", "rolling_7d_avg"]
    
    # Ensure all feature columns exist
    for col in feature_cols:
        if col not in df.columns:
            df[col] = 0

    X = df[feature_cols].copy()
    y = df[target_column].copy()

    return X, y
