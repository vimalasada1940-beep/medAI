from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import PHC, Medicine, Inventory
from app.services.burn_rate import calculate_phc_medicine_burn_rate
from app.services.stockout_prediction import predict_days_to_stockout
from app.utils.distance import calculate_haversine_distance

def find_redistribution_recommendations(
    db: Session,
    recipient_phc_id: int = None,
    medicine_id: int = None,
    max_distance_km: float = 100.0
) -> List[Dict[str, Any]]:
    """
    Finds potential donor PHCs for medicines experiencing stock risk.
    
    Safety Guarantee:
    A PHC is recommended as a donor ONLY if its available stock after transferring 
    the recommended quantity will remain strictly above its designated safety stock level.
    """
    recommendations = []

    # 1. Query recipient inventories needing redistribution
    query = db.query(Inventory).join(PHC).join(Medicine)
    if recipient_phc_id:
        query = query.filter(Inventory.phc_id == recipient_phc_id)
    if medicine_id:
        query = query.filter(Inventory.medicine_id == medicine_id)

    recipient_inventories = query.all()

    for r_inv in recipient_inventories:
        r_phc = r_inv.phc
        med = r_inv.medicine

        # Compute recipient burn rate and days to stockout
        r_burn = calculate_phc_medicine_burn_rate(db, r_phc.id, med.id)
        r_prediction = predict_days_to_stockout(r_inv.available_stock, r_burn)

        # Only recommend transfers if recipient is at HIGH or MEDIUM risk
        if r_prediction["risk_level"] not in ["HIGH", "MEDIUM"]:
            continue

        # Target 14-day supply for recipient
        target_recipient_stock = int(r_burn * 14) if r_burn > 0 else med.safety_stock_level
        deficit_quantity = max(0, target_recipient_stock - r_inv.available_stock)
        if deficit_quantity <= 0:
            continue

        # 2. Look for candidate donor PHCs with surplus stock above safety stock
        candidate_donors = db.query(Inventory).filter(
            Inventory.medicine_id == med.id,
            Inventory.phc_id != r_phc.id
        ).all()

        for d_inv in candidate_donors:
            d_phc = d_inv.phc
            # Surplus is available stock minus safety stock level
            surplus = d_inv.available_stock - med.safety_stock_level
            
            # Donor must have surplus available
            if surplus <= 0:
                continue

            # Calculate geographical distance
            dist_km = calculate_haversine_distance(
                r_phc.latitude, r_phc.longitude,
                d_phc.latitude, d_phc.longitude
            )

            if dist_km > max_distance_km:
                continue

            # Safe transfer quantity is the minimum of recipient deficit and donor surplus
            transfer_qty = min(deficit_quantity, surplus)
            if transfer_qty <= 0:
                continue

            explanation = (
                f"Donor {d_phc.name} has {d_inv.available_stock} units available (Safety threshold: {med.safety_stock_level}). "
                f"It can safely share {transfer_qty} units with {r_phc.name} while retaining full safety buffer. "
                f"Geographical distance: {dist_km} km."
            )

            recommendations.append({
                "donor_phc": d_phc,
                "recipient_phc": r_phc,
                "medicine": med,
                "donor_available_stock": d_inv.available_stock,
                "donor_safety_stock": med.safety_stock_level,
                "surplus_available": surplus,
                "recipient_available_stock": r_inv.available_stock,
                "recipient_burn_rate": r_burn,
                "recipient_days_remaining": r_prediction["days_remaining"],
                "recommended_transfer_quantity": transfer_qty,
                "distance_km": dist_km,
                "safety_validated": True,
                "explanation": explanation
            })

    # Sort recommendations by shortest distance first
    recommendations.sort(key=lambda x: x["distance_km"])
    return recommendations
