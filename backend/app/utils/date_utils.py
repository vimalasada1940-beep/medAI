from datetime import datetime, date, timedelta, timezone
from typing import List, Tuple

def get_utc_now() -> datetime:
    """Returns the current date and time in UTC timezone."""
    return datetime.now(timezone.utc)

def get_recent_date_range(days: int = 7) -> Tuple[date, date]:
    """
    Returns a tuple of (start_date, end_date) representing the last N days 
    ending yesterday (or today).
    """
    end_d = date.today()
    start_d = end_d - timedelta(days=days - 1)
    return start_d, end_d

def get_comparison_windows(days: int = 7) -> Tuple[Tuple[date, date], Tuple[date, date]]:
    """
    Returns two date ranges:
    1. Recent window: (today - 7d, today)
    2. Prior window: (today - 14d, today - 7d)
    Used for comparing consumption acceleration.
    """
    today = date.today()
    recent_start = today - timedelta(days=days - 1)
    recent_end = today

    prior_start = today - timedelta(days=(days * 2) - 1)
    prior_end = today - timedelta(days=days)

    return (recent_start, recent_end), (prior_start, prior_end)
