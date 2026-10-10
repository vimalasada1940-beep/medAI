from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import StockAlertOut
from app.services.alert_service import get_active_alerts, refresh_alerts

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.get("", response_model=List[StockAlertOut])
def list_alerts(
    phc_id: Optional[int] = Query(None, description="Filter alerts by PHC ID"),
    risk_level: Optional[str] = Query(None, description="Filter alerts by risk level: HIGH, MEDIUM, LOW"),
    db: Session = Depends(get_db)
):
    """Retrieves active (unresolved) stock depletion and acceleration alerts."""
    refresh_alerts(db) # Auto-refresh to ensure latest status
    alerts = get_active_alerts(db, phc_id=phc_id, risk_level=risk_level)
    return alerts

@router.post("/refresh")
def trigger_alert_refresh(db: Session = Depends(get_db)):
    """Triggers an explicit recalculation and refresh of stock alerts across all PHCs."""
    count = refresh_alerts(db)
    return {
        "status": "SUCCESS",
        "active_alerts_count": count,
        "message": f"Successfully evaluated inventory and updated {count} active stock alerts."
    }
