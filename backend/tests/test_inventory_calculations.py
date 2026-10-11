import pytest
from app.services.inventory_calculations import (
    calculate_clinical_urgency,
    calculate_record_metrics
)

def test_clinical_urgency_depleted_stock():
    # Depleted stock (0 units) should always be CRITICAL urgency (score 10)
    res = calculate_clinical_urgency(category="Antibiotics", days_remaining=0.0, available_stock=0)
    assert res["clinical_urgency"] == "CRITICAL"
    assert res["urgency_score"] == 10

def test_clinical_urgency_critical_medicine_low_coverage():
    # Antibiotics with 2 days coverage (<= 3 days) -> CRITICAL (score 9)
    res = calculate_clinical_urgency(category="Antibiotics", days_remaining=2.0, available_stock=100)
    assert res["clinical_urgency"] == "CRITICAL"
    assert res["urgency_score"] == 9

def test_clinical_urgency_routine_medicine_moderate_coverage():
    # Gastrointestinal with 5 days coverage (4 to 7 days) -> MODERATE (score 5)
    res = calculate_clinical_urgency(category="Gastrointestinal", days_remaining=5.0, available_stock=250)
    assert res["clinical_urgency"] == "MODERATE"
    assert res["urgency_score"] == 5

def test_clinical_urgency_adequate_stock():
    # Stable stock (> 7 days) -> ROUTINE
    res = calculate_clinical_urgency(category="Cardiovascular", days_remaining=30.0, available_stock=1500)
    assert res["clinical_urgency"] == "ROUTINE"
    assert res["urgency_score"] <= 3

def test_calculations_from_fallback():
    # Test calculation values logic
    from app.services.stockout_prediction import predict_days_to_stockout
    stock = 150
    burn = 50.0 # units_sold_today
    seven_day_demand = round(burn * 7.0, 2)
    assert seven_day_demand == 350.0

    stockout = predict_days_to_stockout(stock, burn)
    assert stockout["days_remaining"] == 3.0
    assert stockout["risk_level"] == "HIGH"
