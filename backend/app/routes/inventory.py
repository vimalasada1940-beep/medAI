from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas import InventoryOut, InventoryCreate
from app.models import Inventory, PHC, Medicine
from app.services.inventory_calculations import calculate_record_metrics
from app.services.alert_service import refresh_alerts

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=List[InventoryOut])
def list_inventories(
    phc_id: Optional[int] = Query(None, description="Filter by PHC ID"),
    medicine_id: Optional[int] = Query(None, description="Filter by Medicine ID"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level: HIGH, MEDIUM, LOW"),
    db: Session = Depends(get_db)
):
    """
    Returns PHC medicine inventory records with calculated daily demand predictions,
    estimated days remaining, stock-out risk, and clinical urgency.
    """
    query = db.query(Inventory).join(PHC).join(Medicine)

    if phc_id:
        query = query.filter(Inventory.phc_id == phc_id)
    if medicine_id:
        query = query.filter(Inventory.medicine_id == medicine_id)

    records = query.all()
    results = []

    for inv in records:
        metrics = calculate_record_metrics(
            db=db,
            phc_id=inv.phc_id,
            medicine_id=inv.medicine_id,
            available_stock=inv.available_stock,
            category=inv.medicine.category if inv.medicine else None
        )

        # Filter by risk level if requested
        if risk_level and metrics["risk_level"] != risk_level.upper():
            continue

        inv_out = InventoryOut(
            id=inv.id,
            phc_id=inv.phc_id,
            medicine_id=inv.medicine_id,
            available_stock=inv.available_stock,
            reserved_stock=inv.reserved_stock,
            unit_cost=float(inv.unit_cost or 0.0),
            batch_number=inv.batch_number,
            expiry_date=inv.expiry_date,
            last_updated=inv.last_updated,
            phc=inv.phc,
            medicine=inv.medicine,
            burn_rate=metrics["units_sold_today"],
            days_remaining=metrics["days_remaining"],
            risk_level=metrics["risk_level"],
            status_label=metrics["status_label"],
            units_sold_today=metrics["units_sold_today"],
            seven_day_demand=metrics["seven_day_demand"],
            clinical_urgency=metrics["clinical_urgency"],
            urgency_score=metrics["urgency_score"]
        )
        results.append(inv_out)

    return results

@router.get("/{inventory_id}", response_model=InventoryOut)
def get_inventory_item(inventory_id: int, db: Session = Depends(get_db)):
    """Retrieves a single inventory item by ID."""
    inv = db.query(Inventory).filter(Inventory.id == inventory_id).first()
    if not inv:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Inventory record not found.")

    metrics = calculate_record_metrics(
        db=db,
        phc_id=inv.phc_id,
        medicine_id=inv.medicine_id,
        available_stock=inv.available_stock,
        category=inv.medicine.category if inv.medicine else None
    )

    return InventoryOut(
        id=inv.id,
        phc_id=inv.phc_id,
        medicine_id=inv.medicine_id,
        available_stock=inv.available_stock,
        reserved_stock=inv.reserved_stock,
        unit_cost=float(inv.unit_cost or 0.0),
        batch_number=inv.batch_number,
        expiry_date=inv.expiry_date,
        last_updated=inv.last_updated,
        phc=inv.phc,
        medicine=inv.medicine,
        burn_rate=metrics["units_sold_today"],
        days_remaining=metrics["days_remaining"],
        risk_level=metrics["risk_level"],
        status_label=metrics["status_label"],
        units_sold_today=metrics["units_sold_today"],
        seven_day_demand=metrics["seven_day_demand"],
        clinical_urgency=metrics["clinical_urgency"],
        urgency_score=metrics["urgency_score"]
    )

@router.post("", response_model=InventoryOut, status_code=status.HTTP_201_CREATED)
def create_or_update_inventory(payload: InventoryCreate, db: Session = Depends(get_db)):
    """Creates a new inventory entry or updates existing stock levels, persisting to PostgreSQL."""
    if payload.available_stock < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Available stock cannot be negative.")

    phc = db.query(PHC).filter(PHC.id == payload.phc_id).first()
    med = db.query(Medicine).filter(Medicine.id == payload.medicine_id).first()
    if not phc or not med:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid PHC or Medicine ID specified.")

    inv = db.query(Inventory).filter(
        Inventory.phc_id == payload.phc_id,
        Inventory.medicine_id == payload.medicine_id
    ).first()

    if inv:
        inv.available_stock = payload.available_stock
        inv.reserved_stock = payload.reserved_stock
        inv.unit_cost = payload.unit_cost
        inv.batch_number = payload.batch_number
        inv.expiry_date = payload.expiry_date
    else:
        inv = Inventory(**payload.model_dump())
        db.add(inv)

    db.commit()
    db.refresh(inv)

    # Persist updated alerts & predictions to PostgreSQL
    refresh_alerts(db)

    metrics = calculate_record_metrics(
        db=db,
        phc_id=inv.phc_id,
        medicine_id=inv.medicine_id,
        available_stock=inv.available_stock,
        category=med.category
    )

    return InventoryOut(
        id=inv.id,
        phc_id=inv.phc_id,
        medicine_id=inv.medicine_id,
        available_stock=inv.available_stock,
        reserved_stock=inv.reserved_stock,
        unit_cost=float(inv.unit_cost or 0.0),
        batch_number=inv.batch_number,
        expiry_date=inv.expiry_date,
        last_updated=inv.last_updated,
        phc=inv.phc,
        medicine=inv.medicine,
        burn_rate=metrics["units_sold_today"],
        days_remaining=metrics["days_remaining"],
        risk_level=metrics["risk_level"],
        status_label=metrics["status_label"],
        units_sold_today=metrics["units_sold_today"],
        seven_day_demand=metrics["seven_day_demand"],
        clinical_urgency=metrics["clinical_urgency"],
        urgency_score=metrics["urgency_score"]
    )

