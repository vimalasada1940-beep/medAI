from typing import Dict, Any, Optional
from app.config import settings

def predict_days_to_stockout(
    available_stock: int,
    burn_rate: float,
    high_threshold: float = None,
    medium_threshold: float = None
) -> Dict[str, Any]:
    """
    Computes days remaining before stock-out based on available stock and daily burn rate.
    
    Risk Threshold Logic:
    - HIGH: days <= 3.0
    - MEDIUM: 4 to 7 days (3.0 < days <= 7.0)
    - LOW: > 7 days or zero burn rate with existing stock
    """
    if high_threshold is None:
        high_threshold = settings.HIGH_RISK_THRESHOLD_DAYS
    if medium_threshold is None:
        medium_threshold = settings.MEDIUM_RISK_THRESHOLD_DAYS

    # Handle zero stock explicitly
    if available_stock <= 0:
        return {
            "days_remaining": 0.0,
            "risk_level": "HIGH",
            "status_label": "DEPLETED",
            "explanation": "Stock is completely depleted (0 units available)."
        }

    # Handle zero or negative burn rate safely
    if burn_rate <= 0.0:
        return {
            "days_remaining": None,
            "risk_level": "LOW",
            "status_label": "NO_BURN",
            "explanation": f"Available stock is {available_stock} units. No recent daily consumption recorded."
        }

    days_remaining = round(available_stock / burn_rate, 2)

    if days_remaining <= high_threshold:
        risk_level = "HIGH"
        status_label = "CRITICAL"
        explanation = f"Critical risk of stock-out within {days_remaining} days (below {high_threshold}-day threshold)."
    elif days_remaining <= medium_threshold:
        risk_level = "MEDIUM"
        status_label = "WARNING"
        explanation = f"Moderate stock warning: estimated stock-out in {days_remaining} days (between {high_threshold} and {medium_threshold} days)."
    else:
        risk_level = "LOW"
        status_label = "STABLE"
        explanation = f"Stock level is adequate. Estimated stock-out in {days_remaining} days."

    return {
        "days_remaining": days_remaining,
        "risk_level": risk_level,
        "status_label": status_label,
        "explanation": explanation
    }
