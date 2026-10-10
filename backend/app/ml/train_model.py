import os
import sys
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Ensure parent path in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.ml.feature_engineering import (
    extract_time_features, 
    build_lag_and_rolling_features, 
    prepare_feature_matrix
)
from app.ml.evaluate_model import evaluate_demand_model

def train_and_save_model():
    """
    Trains a scikit-learn demand forecasting model on historical daily consumption features
    and saves the model artifact to backend/artifacts/demand_model.joblib.
    """
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
    data_path = os.path.join(base_dir, 'data', 'raw', 'salesdaily.csv')
    artifacts_dir = os.path.join(base_dir, 'artifacts')
    model_path = os.path.join(artifacts_dir, 'demand_model.joblib')

    os.makedirs(artifacts_dir, exist_ok=True)

    print(f"Loading training data from: {data_path}")

    if not os.path.exists(data_path):
        print("Training data not found. Creating synthetic fallback training data...")
        df = pd.DataFrame({
            "datum": pd.date_range(start="2024-01-01", periods=60, freq="D"),
            "ATC3_units": [45 + (i % 7) * 5 + (i % 3) * 3 for i in range(60)]
        })
    else:
        df = pd.read_csv(data_path)

    date_col = "datum" if "datum" in df.columns else "record_date"
    target_col = "N02BE" if "N02BE" in df.columns else ("ATC3_units" if "ATC3_units" in df.columns else "quantity_consumed")

    if target_col not in df.columns:
        df[target_col] = df.select_dtypes(include=['float64', 'int64']).iloc[:, 0]

    # Feature Engineering
    df_features = extract_time_features(df, date_column=date_col)
    df_features = build_lag_and_rolling_features(df_features, target_column=target_col)
    X, y = prepare_feature_matrix(df_features, target_column=target_col)

    # Train / Test split without shuffling (Time-Series constraint)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

    print(f"Training RandomForestRegressor on {len(X_train)} samples...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluation
    metrics = evaluate_demand_model(model, X_test, y_test, y_train)

    # Save model artifact
    print(f"Saving trained model to {model_path}...")
    joblib.dump({
        "model": model,
        "feature_cols": list(X.columns),
        "metrics": metrics
    }, model_path)

    print("Model training and artifact save completed successfully!")

if __name__ == "__main__":
    train_and_save_model()
