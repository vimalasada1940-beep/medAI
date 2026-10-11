import pytest
from app.services.stockout_prediction import predict_days_to_stockout

def test_high_risk_stockout():
    # 150 stock / 75 burn = 2.0 days <= 3.0 -> HIGH risk
    res = predict_days_to_stockout(available_stock=150, burn_rate=75.0)
    assert res["days_remaining"] == 2.0
    assert res["risk_level"] == "HIGH"
    assert res["status_label"] == "CRITICAL"

def test_medium_risk_stockout():
    # 250 stock / 50 burn = 5.0 days -> MEDIUM risk (4 to 7 days)
    res = predict_days_to_stockout(available_stock=250, burn_rate=50.0)
    assert res["days_remaining"] == 5.0
    assert res["risk_level"] == "MEDIUM"
    assert res["status_label"] == "WARNING"

def test_low_risk_stockout():
    # 1200 stock / 30 burn = 40.0 days > 7.0 -> LOW risk
    res = predict_days_to_stockout(available_stock=1200, burn_rate=30.0)
    assert res["days_remaining"] == 40.0
    assert res["risk_level"] == "LOW"
    assert res["status_label"] == "STABLE"

def test_zero_burn_rate_safety():
    res = predict_days_to_stockout(available_stock=500, burn_rate=0.0)
    assert res["days_remaining"] is None
    assert res["risk_level"] == "LOW"
    assert res["status_label"] == "NO_BURN"

def test_zero_stock():
    res = predict_days_to_stockout(available_stock=0, burn_rate=50.0)
    assert res["days_remaining"] == 0.0
    assert res["risk_level"] == "HIGH"
    assert res["status_label"] == "DEPLETED"

def test_feature_columns_validation():
    from app.ml.feature_engineering import verify_feature_columns, REQUIRED_FEATURE_COLUMNS, FeatureValidationError
    
    # Missing columns should raise FeatureValidationError
    with pytest.raises(FeatureValidationError) as excinfo:
        verify_feature_columns(["day_of_week", "day_of_month"])
    assert "Missing required ML feature columns" in str(excinfo.value)

    # All required columns should pass without error
    full_features = {col: 1 for col in REQUIRED_FEATURE_COLUMNS}
    verify_feature_columns(full_features)

def test_missing_model_error_handling():
    from app.ml.predict_demand import load_trained_model, MLModelNotFoundError
    
    with pytest.raises(MLModelNotFoundError) as excinfo:
        load_trained_model(model_path="non_existent_model_file.pkl")
    assert "Trained model file not found" in str(excinfo.value)

