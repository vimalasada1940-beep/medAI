from typing import Dict, Any
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.models import DailyConsumption
from app.services.burn_rate import calculate_burn_rate_from_list
from app.config import settings

def detect_consumption_acceleration(
    db: Session,
    phc_id: int,
    medicine_id: int,
    threshold_ratio: float = None
) -> Dict[str, Any]:
    """
    Compares consumption in the latest 7 days vs the prior 7 days.
    If ratio (recent_burn_rate / prior_burn_rate) >= threshold_ratio (default 1.5),
    flags consumption acceleration.
    """
    if threshold_ratio is None:
        threshold_ratio = settings.ACCELERATION_THRESHOLD_RATIO

    today = date.today()
    recent_start = today - timedelta(days=6)
    prior_start = today - timedelta(days=13)
    prior_end = today - timedelta(days=7)

    # Recent 7 days consumption
    recent_records = db.query(DailyConsumption).filter(
        DailyConsumption.phc_id == phc_id,
        DailyConsumption.medicine_id == medicine_id,
        DailyConsumption.record_date >= recent_start,
        DailyConsumption.record_date <= today
    ).all()

    # Prior 7 days consumption
    prior_records = db.query(DailyConsumption).filter(
        DailyConsumption.phc_id == phc_id,
        DailyConsumption.medicine_id == medicine_id,
        DailyConsumption.record_date >= prior_start,
        DailyConsumption.record_date <= prior_end
    ).all()

    recent_burn = calculate_burn_rate_from_list([r.quantity_consumed for r in recent_records], 7)
    prior_burn = calculate_burn_rate_from_list([r.quantity_consumed for r in prior_records], 7)

    if prior_burn == 0.0:
        ratio = 1.0 if recent_burn == 0.0 else round(recent_burn, 2)
    else:
        ratio = round(recent_burn / prior_burn, 2)

    is_accelerating = (ratio >= threshold_ratio) and (recent_burn > 5.0)

    explanation = (
        f"Recent 7-day daily burn rate ({recent_burn} units/day) is {ratio}x compared to "
        f"prior 7-day rate ({prior_burn} units/day)."
    )

    return {
        "phc_id": phc_id,
        "medicine_id": medicine_id,
        "recent_burn_rate": recent_burn,
        "prior_burn_rate": prior_burn,
        "acceleration_ratio": ratio,
        "is_accelerating": is_accelerating,
        "explanation": explanation
    }
