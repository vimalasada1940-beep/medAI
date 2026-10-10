from typing import List
from datetime import date, timedelta
from sqlalchemy.orm import Session

def calculate_burn_rate_from_list(quantities: List[int], days: int = 7) -> float:
    """
    Calculates average daily consumption (burn rate) from a list of daily consumption integers.
    Safely handles zero or empty lists.
    """
    if not quantities or days <= 0:
        return 0.0

    total_consumption = sum(quantities)
    # Average across the number of days evaluated
    burn_rate = total_consumption / float(days)
    return round(max(0.0, burn_rate), 2)

def calculate_phc_medicine_burn_rate(
    db: Session, 
    phc_id: int, 
    medicine_id: int, 
    window_days: int = 7
) -> float:
    """
    Queries database for daily consumption records over the last `window_days`
    for a given PHC and medicine, computing the average daily burn rate.
    """
    from app.models import DailyConsumption
    end_date = date.today()
    start_date = end_date - timedelta(days=window_days - 1)

    records = db.query(DailyConsumption).filter(
        DailyConsumption.phc_id == phc_id,
        DailyConsumption.medicine_id == medicine_id,
        DailyConsumption.record_date >= start_date,
        DailyConsumption.record_date <= end_date
    ).all()

    if not records:
        return 0.0

    quantities = [r.quantity_consumed for r in records]
    # If fewer records exist than window_days, average over total window_days to prevent skew
    return calculate_burn_rate_from_list(quantities, days=window_days)
