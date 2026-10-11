"""
MediPulse Inventory & Demand Calculations Service
Computes units_sold_today, 7-day demand, stockout days, stockout risk, and clinical urgency.
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.services.stockout_prediction import predict_days_to_stockout
from app.ml.predict_demand import predict_phc_medicine_demand

CRITICAL_THERAPEUTIC_CATEGORIES = {
    "antibiotics",
    "cardiovascular",
    "anti-diabetic",
    "respiratory",
    "emergency",
    "vaccines",
    "analgesics & antipyretics"
}

def calculate_clinical_urgency(
    category: Optional[str],
    days_remaining: Optional[float],
    available_stock: int
) -> Dict[str, Any]:
    """
    Calculates clinical urgency based on therapeutic category,
    current stock level, and days remaining before stock depletion.

    Levels:
    - CRITICAL (Score: 9-10): Depleted stock or <= 3 days of life-saving medicine.
    - HIGH (Score: 7-8): <= 3 days of routine medicine, or 4-7 days of critical medicine.
    - MODERATE (Score: 4-6): 4-7 days of routine medicine.
    - ROUTINE (Score: 1-3): > 7 days or stable inventory.
    """
    cat = (category or "").strip().lower()
    is_critical_cat = any(crit in cat for crit in CRITICAL_THERAPEUTIC_CATEGORIES)

    if available_stock <= 0:
        return {
            "clinical_urgency": "CRITICAL",
            "urgency_score": 10,
            "explanation": f"Immediate patient care risk: Stock is depleted (0 units available) for {category or 'medicine'}."
        }

    if days_remaining is not None and days_remaining <= 3.0:
        if is_critical_cat:
            return {
                "clinical_urgency": "CRITICAL",
                "urgency_score": 9,
                "explanation": f"Critical clinical urgency: Only {days_remaining} days remaining of essential medicine ({category})."
            }
        else:
            return {
                "clinical_urgency": "HIGH",
                "urgency_score": 8,
                "explanation": f"High clinical urgency: Stock-out imminent in {days_remaining} days for {category}."
            }

    if days_remaining is not None and days_remaining <= 7.0:
        if is_critical_cat:
            return {
                "clinical_urgency": "HIGH",
                "urgency_score": 7,
                "explanation": f"High clinical urgency: Vulnerable coverage ({days_remaining} days) for essential medicine ({category})."
            }
        else:
            return {
                "clinical_urgency": "MODERATE",
                "urgency_score": 5,
                "explanation": f"Moderate clinical urgency: Stock coverage is {days_remaining} days for {category}."
            }

    return {
        "clinical_urgency": "ROUTINE",
        "urgency_score": 2,
        "explanation": f"Routine clinical urgency: Adequate stock coverage ({days_remaining if days_remaining is not None else 'N/A'} days)."
    }

def calculate_record_metrics(
    db: Session,
    phc_id: int,
    medicine_id: int,
    available_stock: int,
    daily_burn_fallback: Optional[float] = None,
    category: Optional[str] = None
) -> Dict[str, Any]:
    """
    Performs full suite of prediction and inventory calculations for an inventory record:
    1. Predicts 'units_sold_today'
    2. Calculates seven-day demand
    3. Calculates days of stock remaining
    4. Calculates stock-out risk
    5. Calculates clinical urgency
    """
    from app.models import Medicine

    # 1. Predict units_sold_today
    pred_res = predict_phc_medicine_demand(db, phc_id, medicine_id, forecast_days=7)
    predicted_daily = float(pred_res.get("predicted_daily_demand", 0.0))

    if predicted_daily <= 0.0 and daily_burn_fallback is not None and daily_burn_fallback > 0.0:
        predicted_daily = float(daily_burn_fallback)

    units_sold_today = round(max(0.0, predicted_daily), 2)

    # 2. Calculate seven-day demand
    seven_day_demand = round(units_sold_today * 7.0, 2)

    # 3. Calculate days of stock remaining
    stockout_info = predict_days_to_stockout(available_stock, units_sold_today)
    days_remaining = stockout_info["days_remaining"]

    # 4. Calculate stock-out risk
    risk_level = stockout_info["risk_level"]
    status_label = stockout_info["status_label"]

    # 5. Calculate clinical urgency
    if not category:
        med = db.query(Medicine).filter(Medicine.id == medicine_id).first()
        category = med.category if med else "General"

    urgency_info = calculate_clinical_urgency(category, days_remaining, available_stock)

    return {
        "phc_id": phc_id,
        "medicine_id": medicine_id,
        "available_stock": available_stock,
        "units_sold_today": units_sold_today,
        "seven_day_demand": seven_day_demand,
        "days_remaining": days_remaining,
        "risk_level": risk_level,
        "status_label": status_label,
        "clinical_urgency": urgency_info["clinical_urgency"],
        "urgency_score": urgency_info["urgency_score"],
        "urgency_explanation": urgency_info["explanation"],
        "prediction_method": pred_res.get("method", "Baseline"),
        "is_prediction_reliable": pred_res.get("is_reliable", False)
    }
