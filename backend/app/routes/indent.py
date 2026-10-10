from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import EmergencyIndentOut, EmergencyIndentCreate, EmergencyIndentStatusUpdate
from app.models import EmergencyIndent, PHC, Medicine
from app.services.indent_generator import calculate_emergency_indent_quantity

router = APIRouter(prefix="/indents", tags=["Emergency Indents"])

@router.get("", response_model=List[EmergencyIndentOut])
def list_indents(
    phc_id: Optional[int] = Query(None, description="Filter indents by PHC ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status: PENDING, APPROVED, REJECTED, DISPATCHED"),
    db: Session = Depends(get_db)
):
    """Lists emergency indents submitted by PHCs."""
    query = db.query(EmergencyIndent).join(PHC).join(Medicine)

    if phc_id:
        query = query.filter(EmergencyIndent.phc_id == phc_id)
    if status_filter:
        query = query.filter(EmergencyIndent.status == status_filter.upper())

    return query.order_by(EmergencyIndent.created_at.desc()).all()

@router.post("", response_model=EmergencyIndentOut, status_code=status.HTTP_201_CREATED)
def create_emergency_indent(
    payload: EmergencyIndentCreate, 
    db: Session = Depends(get_db)
):
    """
    Generates and records an emergency indent when local stock is depleted or redistribution is insufficient.
    Calculates required quantity based on daily burn rate and target coverage days.
    """
    calc = calculate_emergency_indent_quantity(
        db, 
        phc_id=payload.phc_id, 
        medicine_id=payload.medicine_id, 
        target_coverage_days=payload.target_coverage_days or 30
    )

    if calc["requested_quantity"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current available stock is adequate. Emergency indent not required at this time."
        )

    indent = EmergencyIndent(
        phc_id=payload.phc_id,
        medicine_id=payload.medicine_id,
        requested_quantity=calc["requested_quantity"],
        target_coverage_days=calc["target_coverage_days"],
        current_stock=calc["current_stock"],
        burn_rate=calc["burn_rate"],
        status="PENDING",
        reason=payload.reason or calc["explanation"]
    )

    db.add(indent)
    db.commit()
    db.refresh(indent)

    return indent

@router.patch("/{indent_id}/status", response_model=EmergencyIndentOut)
def update_indent_status(
    indent_id: int, 
    payload: EmergencyIndentStatusUpdate, 
    db: Session = Depends(get_db)
):
    """
    Updates the approval status of an emergency indent (APPROVED, REJECTED, DISPATCHED).
    Requires authorized human decision-maker review.
    """
    indent = db.query(EmergencyIndent).filter(EmergencyIndent.id == indent_id).first()
    if not indent:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Emergency indent not found.")

    allowed_statuses = ["PENDING", "APPROVED", "REJECTED", "DISPATCHED"]
    new_status = payload.status.upper()
    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invalid status '{payload.status}'. Allowed values: {', '.join(allowed_statuses)}"
        )

    indent.status = new_status
    db.commit()
    db.refresh(indent)

    return indent
