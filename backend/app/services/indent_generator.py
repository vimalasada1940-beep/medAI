from typing import Dict, Any
from sqlalchemy.orm import Session
from app.models import Inventory, Medicine, PHC
from app.services.burn_rate import calculate_phc_medicine_burn_rate
from app.config import settings

def calculate_emergency_indent_quantity(
    db: Session,
    phc_id: int,
    medicine_id: int,
    target_coverage_days: int = None
) -> Dict[str, Any]:
    """
    Computes recommended emergency indent quantity for a PHC experiencing stock depletion
    or when local redistribution is insufficient.
    
    Formula:
    target_required = burn_rate * target_coverage_days
    indent_qty = max(0, target_required - (available_stock + reserved_stock))
    """
    if target_coverage_days is None:
        target_coverage_days = settings.DEFAULT_TARGET_COVERAGE_DAYS

    inv = db.query(Inventory).filter(
        Inventory.phc_id == phc_id,
        Inventory.medicine_id == medicine_id
    ).first()

    med = db.query(Medicine).filter(Medicine.id == medicine_id).first()
    phc = db.query(PHC).filter(PHC.id == phc_id).first()

    if not inv or not med or not phc:
        raise ValueError("Invalid PHC or Medicine record specified for indent generation.")

    burn_rate = calculate_phc_medicine_burn_rate(db, phc_id, medicine_id)

    if burn_rate > 0.0:
        target_stock = int(burn_rate * target_coverage_days)
    else:
        # Fallback to 1.5x safety stock level if burn rate is zero
        target_stock = int(med.safety_stock_level * 1.5)

    effective_current_stock = inv.available_stock + inv.reserved_stock
    indent_qty = max(0, target_stock - effective_current_stock)

    explanation = (
        f"Calculated emergency indent for {med.name} at {phc.name}: "
        f"Daily burn rate is {burn_rate} units/day. Target {target_coverage_days}-day coverage requires {target_stock} units. "
        f"Current available ({inv.available_stock}) plus reserved ({inv.reserved_stock}) stock is {effective_current_stock} units. "
        f"Recommended emergency indent quantity: {indent_qty} units."
    )

    return {
        "phc_id": phc_id,
        "medicine_id": medicine_id,
        "burn_rate": burn_rate,
        "current_stock": inv.available_stock,
        "reserved_stock": inv.reserved_stock,
        "target_coverage_days": target_coverage_days,
        "target_stock_required": target_stock,
        "requested_quantity": indent_qty,
        "explanation": explanation
    }
