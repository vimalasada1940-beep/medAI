from typing import List
from sqlalchemy.orm import Session
from app.models import Inventory, StockAlert, PHC, Medicine
from app.services.burn_rate import calculate_phc_medicine_burn_rate
from app.services.stockout_prediction import predict_days_to_stockout
from app.services.acceleration import detect_consumption_acceleration

def refresh_alerts(db: Session) -> int:
    """
    Scans all PHC inventories in the database, recalculates burn rates and risk levels,
    and updates the stock_alerts table. Resolves alerts if stock is restored.
    Returns the count of active high/medium alerts.
    """
    inventories = db.query(Inventory).all()
    created_or_updated = 0

    for inv in inventories:
        phc_id = inv.phc_id
        med_id = inv.medicine_id
        
        phc = inv.phc
        med = inv.medicine

        burn_rate = calculate_phc_medicine_burn_rate(db, phc_id, med_id)
        prediction = predict_days_to_stockout(inv.available_stock, burn_rate)
        acceleration = detect_consumption_acceleration(db, phc_id, med_id)

        risk_level = prediction["risk_level"]
        days_rem = prediction["days_remaining"]

        # Check existing unresolved alert
        existing_alert = db.query(StockAlert).filter(
            StockAlert.phc_id == phc_id,
            StockAlert.medicine_id == med_id,
            StockAlert.is_resolved == False
        ).first()

        if risk_level in ["HIGH", "MEDIUM"]:
            msg = (
                f"{med.name} stock level at {phc.name} is {risk_level} risk! "
                f"Available stock: {inv.available_stock} units, daily burn rate: {burn_rate}. "
                f"{prediction['explanation']}"
            )

            if acceleration["is_accelerating"]:
                msg += f" WARNING: Rapid consumption acceleration detected ({acceleration['acceleration_ratio']}x increase)."

            if existing_alert:
                existing_alert.risk_level = risk_level
                existing_alert.days_remaining = days_rem
                existing_alert.burn_rate = burn_rate
                existing_alert.message = msg
            else:
                new_alert = StockAlert(
                    phc_id=phc_id,
                    medicine_id=med_id,
                    alert_type="STOCKOUT_RISK",
                    risk_level=risk_level,
                    days_remaining=days_rem,
                    burn_rate=burn_rate,
                    message=msg,
                    is_resolved=False
                )
                db.add(new_alert)
            created_or_updated += 1
        else:
            # Resolve alert if risk level dropped to LOW
            if existing_alert:
                existing_alert.is_resolved = True

    db.commit()
    return created_or_updated

def get_active_alerts(
    db: Session, 
    phc_id: int = None, 
    risk_level: str = None
) -> List[StockAlert]:
    """Queries active (unresolved) alerts filtered by optional PHC ID or risk level."""
    query = db.query(StockAlert).filter(StockAlert.is_resolved == False)
    
    if phc_id:
        query = query.filter(StockAlert.phc_id == phc_id)
    if risk_level:
        query = query.filter(StockAlert.risk_level == risk_level.upper())

    return query.order_by(StockAlert.created_at.desc()).all()
