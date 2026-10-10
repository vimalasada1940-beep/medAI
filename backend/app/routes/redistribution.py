from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import RedistributionRecommendationOut, RedistributionRequestOut, RedistributionRequestCreate
from app.models import RedistributionRequest, PHC, Medicine, Inventory
from app.services.redistribution_engine import find_redistribution_recommendations
from app.utils.distance import calculate_haversine_distance

router = APIRouter(prefix="/redistribution", tags=["Redistribution"])

@router.get("/recommendations", response_model=List[RedistributionRecommendationOut])
def get_redistribution_recommendations(
    recipient_phc_id: Optional[int] = Query(None, description="Filter recommendations for specific recipient PHC"),
    medicine_id: Optional[int] = Query(None, description="Filter recommendations for specific medicine"),
    db: Session = Depends(get_db)
):
    """
    Computes inter-PHC stock redistribution recommendations.
    Ensures donor stock remains strictly above safety stock after any proposed transfer.
    """
    recommendations = find_redistribution_recommendations(
        db, 
        recipient_phc_id=recipient_phc_id, 
        medicine_id=medicine_id
    )
    return recommendations

@router.get("/requests", response_model=List[RedistributionRequestOut])
def list_redistribution_requests(
    phc_id: Optional[int] = Query(None, description="Filter requests by donor or recipient PHC ID"),
    db: Session = Depends(get_db)
):
    """Lists existing redistribution transfer requests."""
    query = db.query(RedistributionRequest).join(
        PHC, RedistributionRequest.donor_phc_id == PHC.id
    ).join(Medicine)

    if phc_id:
        query = query.filter(
            (RedistributionRequest.donor_phc_id == phc_id) | 
            (RedistributionRequest.recipient_phc_id == phc_id)
        )

    return query.order_by(RedistributionRequest.requested_at.desc()).all()

@router.post("/requests", response_model=RedistributionRequestOut, status_code=status.HTTP_201_CREATED)
def create_redistribution_request(
    payload: RedistributionRequestCreate, 
    db: Session = Depends(get_db)
):
    """
    Submits a proposed inter-PHC stock transfer request for human approval.
    Requires explicit authorization before any real stock movement occurs.
    """
    if payload.donor_phc_id == payload.recipient_phc_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Donor PHC and Recipient PHC cannot be the same health centre."
        )

    donor_phc = db.query(PHC).filter(PHC.id == payload.donor_phc_id).first()
    recipient_phc = db.query(PHC).filter(PHC.id == payload.recipient_phc_id).first()
    medicine = db.query(Medicine).filter(Medicine.id == payload.medicine_id).first()

    if not donor_phc or not recipient_phc or not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid PHC or Medicine ID specified.")

    donor_inv = db.query(Inventory).filter(
        Inventory.phc_id == payload.donor_phc_id,
        Inventory.medicine_id == payload.medicine_id
    ).first()

    if not donor_inv or (donor_inv.available_stock - medicine.safety_stock_level) < payload.proposed_quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Safety Violation: Donor {donor_phc.name} cannot safely transfer {payload.proposed_quantity} units without dropping below safety stock ({medicine.safety_stock_level})."
        )

    dist_km = calculate_haversine_distance(
        donor_phc.latitude, donor_phc.longitude,
        recipient_phc.latitude, recipient_phc.longitude
    )

    req = RedistributionRequest(
        donor_phc_id=payload.donor_phc_id,
        recipient_phc_id=payload.recipient_phc_id,
        medicine_id=payload.medicine_id,
        proposed_quantity=payload.proposed_quantity,
        distance_km=dist_km,
        status="PROPOSED",
        reason=payload.reason
    )

    db.add(req)
    db.commit()
    db.refresh(req)

    return req
