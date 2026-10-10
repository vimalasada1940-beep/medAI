from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import DashboardSummaryOut
from app.models import PHC, Medicine, StockAlert, RedistributionRequest, EmergencyIndent
from app.services.alert_service import refresh_alerts

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryOut)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Returns live high-level dashboard statistics across all Primary Health Centres (PHCs).
    Calculates total PHCs, medicines at risk, high risk stock-outs, and pending requests.
    """
    # Refresh alerts to ensure live counts
    refresh_alerts(db)

    total_phcs = db.query(PHC).count()
    total_medicines = db.query(Medicine).count()

    active_alerts = db.query(StockAlert).filter(StockAlert.is_resolved == False).all()
    medicines_at_risk = len(set(a.medicine_id for a in active_alerts))
    high_risk_stockouts = len([a for a in active_alerts if a.risk_level == "HIGH"])

    pending_redistributions = db.query(RedistributionRequest).filter(
        RedistributionRequest.status == "PROPOSED"
    ).count()

    pending_indents = db.query(EmergencyIndent).filter(
        EmergencyIndent.status == "PENDING"
    ).count()

    return DashboardSummaryOut(
        total_phcs=total_phcs,
        total_medicines=total_medicines,
        medicines_at_risk=medicines_at_risk,
        high_risk_stockouts=high_risk_stockouts,
        pending_redistributions=pending_redistributions,
        pending_indents=pending_indents,
        synthetic_notice="DEMONSTRATION ONLY: Synthetic data for student decision-support prototype."
    )
