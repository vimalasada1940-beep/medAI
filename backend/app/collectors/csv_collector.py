import csv
import io
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.models import DailyConsumption, Inventory, PHC, Medicine
from app.ml.feature_engineering import REQUIRED_FEATURE_COLUMNS

REQUIRED_CONSUMPTION_COLUMNS = ["phc_code", "medicine_code", "record_date", "quantity_consumed"]
REQUIRED_INVENTORY_COLUMNS = ["phc_code", "medicine_code", "available_stock"]

class CSVValidationError(ValueError):
    """Raised when CSV structure, required columns, or required model features are missing or invalid."""
    def __init__(self, message: str, missing_columns: List[str] = None, detected_columns: List[str] = None):
        super().__init__(message)
        self.message = message
        self.missing_columns = missing_columns or []
        self.detected_columns = detected_columns or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": "VALIDATION_ERROR",
            "message": self.message,
            "missing_columns": self.missing_columns,
            "detected_columns": self.detected_columns
        }

def validate_csv_columns(fieldnames: Optional[List[str]], expected_type: str = "auto") -> str:
    """
    Validates CSV header field names against required project schemas.
    Raises CSVValidationError with explicit details if required fields are absent.
    Returns the detected schema type ('consumption' or 'inventory').
    """
    if not fieldnames:
        raise CSVValidationError(
            message="CSV file header is empty or could not be parsed.",
            missing_columns=["header_row"],
            detected_columns=[]
        )

    # Normalize fields (lowercase, strip whitespace, strip UTF-8 BOM)
    normalized = [f.strip().lower().lstrip("\ufeff") for f in fieldnames if f]


    has_cons = all(col in normalized for col in REQUIRED_CONSUMPTION_COLUMNS)
    has_inv = all(col in normalized for col in REQUIRED_INVENTORY_COLUMNS)

    if expected_type == "consumption":
        missing = [c for c in REQUIRED_CONSUMPTION_COLUMNS if c not in normalized]
        if missing:
            raise CSVValidationError(
                message=f"CSV missing required consumption column(s): {missing}. Required columns: {REQUIRED_CONSUMPTION_COLUMNS}",
                missing_columns=missing,
                detected_columns=normalized
            )
        return "consumption"

    if expected_type == "inventory":
        missing = [c for c in REQUIRED_INVENTORY_COLUMNS if c not in normalized]
        if missing:
            raise CSVValidationError(
                message=f"CSV missing required inventory column(s): {missing}. Required columns: {REQUIRED_INVENTORY_COLUMNS}",
                missing_columns=missing,
                detected_columns=normalized
            )
        return "inventory"

    # Auto-detection
    if has_cons:
        return "consumption"
    if has_inv:
        return "inventory"

    # Neither matched - construct explicit missing columns error
    missing_inv = [c for c in REQUIRED_INVENTORY_COLUMNS if c not in normalized]
    missing_cons = [c for c in REQUIRED_CONSUMPTION_COLUMNS if c not in normalized]
    raise CSVValidationError(
        message=(
            f"CSV columns do not match required schemas. "
            f"For inventory upload, missing: {missing_inv} (expected: {REQUIRED_INVENTORY_COLUMNS}). "
            f"For daily consumption upload, missing: {missing_cons} (expected: {REQUIRED_CONSUMPTION_COLUMNS})."
        ),
        missing_columns=missing_inv,
        detected_columns=normalized
    )

def parse_and_ingest_consumption_csv(db: Session, file_content: str) -> Dict[str, Any]:
    """
    Parses and validates CSV content containing daily consumption logs and ingests into PostgreSQL.
    CSV Format Expected: phc_code, medicine_code, record_date, quantity_consumed
    """
    f = io.StringIO(file_content.strip())
    reader = csv.DictReader(f)

    validate_csv_columns(reader.fieldnames, expected_type="consumption")

    inserted_count = 0
    updated_count = 0
    errors = []

    phcs = {p.code: p.id for p in db.query(PHC).all()}
    medicines = {m.code: m.id for m in db.query(Medicine).all()}

    for row_idx, row in enumerate(reader, start=1):
        clean_row = {str(k).strip().lower().lstrip("\ufeff"): (str(v).strip() if v is not None else "") for k, v in row.items() if k is not None}
        phc_code = clean_row.get("phc_code", "")
        med_code = clean_row.get("medicine_code", "")
        date_str = clean_row.get("record_date", "")
        qty_str = clean_row.get("quantity_consumed", "")

        if not phc_code or not med_code or not date_str or not qty_str:
            errors.append(f"Row {row_idx}: Missing required consumption fields.")
            continue

        if phc_code not in phcs:
            errors.append(f"Row {row_idx}: PHC code '{phc_code}' not found in database.")
            continue

        if med_code not in medicines:
            errors.append(f"Row {row_idx}: Medicine code '{med_code}' not found in database.")
            continue

        try:
            qty = int(qty_str)
            if qty < 0:
                errors.append(f"Row {row_idx}: Quantity consumed cannot be negative ({qty}).")
                continue
        except ValueError:
            errors.append(f"Row {row_idx}: Invalid quantity integer '{qty_str}'.")
            continue

        try:
            rec_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            errors.append(f"Row {row_idx}: Invalid date format '{date_str}' (expected YYYY-MM-DD).")
            continue

        phc_id = phcs[phc_code]
        med_id = medicines[med_code]

        existing = db.query(DailyConsumption).filter(
            DailyConsumption.phc_id == phc_id,
            DailyConsumption.medicine_id == med_id,
            DailyConsumption.record_date == rec_date
        ).first()

        if existing:
            existing.quantity_consumed = qty
            updated_count += 1
        else:
            new_record = DailyConsumption(
                phc_id=phc_id,
                medicine_id=med_id,
                record_date=rec_date,
                quantity_consumed=qty
            )
            db.add(new_record)
            inserted_count += 1

    db.commit()

    return {
        "status": "SUCCESS" if not errors else "PARTIAL_SUCCESS",
        "csv_type": "daily_consumption",
        "inserted_records": inserted_count,
        "updated_records": updated_count,
        "errors": errors,
        "notice": "Ingested consumption records into PostgreSQL successfully."
    }

def parse_and_ingest_inventory_csv(db: Session, file_content: str) -> Dict[str, Any]:
    """
    Parses and validates CSV content containing PHC inventory records and upserts into PostgreSQL.
    CSV Format Expected: phc_code, medicine_code, available_stock
    Optional fields: unit_cost, batch_number, expiry_date, daily_burn_rate
    """
    f = io.StringIO(file_content.strip())
    reader = csv.DictReader(f)

    validate_csv_columns(reader.fieldnames, expected_type="inventory")

    inserted_count = 0
    updated_count = 0
    errors = []
    processed_records = []


    phcs = {p.code: p.id for p in db.query(PHC).all()}
    medicines = {m.code: m.id for m in db.query(Medicine).all()}

    for row_idx, row in enumerate(reader, start=1):
        clean_row = {str(k).strip().lower().lstrip("\ufeff"): (str(v).strip() if v is not None else "") for k, v in row.items() if k is not None}
        phc_code = clean_row.get("phc_code", "")
        med_code = clean_row.get("medicine_code", "")
        stock_str = clean_row.get("available_stock", "")

        if not phc_code or not med_code or not stock_str:
            errors.append(f"Row {row_idx}: Missing required inventory fields.")
            continue

        if phc_code not in phcs:
            errors.append(f"Row {row_idx}: PHC code '{phc_code}' not found in database.")
            continue

        if med_code not in medicines:
            errors.append(f"Row {row_idx}: Medicine code '{med_code}' not found in database.")
            continue

        try:
            stock = int(stock_str)
            if stock < 0:
                errors.append(f"Row {row_idx}: Available stock cannot be negative ({stock}).")
                continue
        except ValueError:
            errors.append(f"Row {row_idx}: Invalid stock integer '{stock_str}'.")
            continue

        phc_id = phcs[phc_code]
        med_id = medicines[med_code]
        batch_num = clean_row.get("batch_number") or None
        cost_str = clean_row.get("unit_cost", "0.0")
        try:
            unit_cost = float(cost_str)
        except ValueError:
            unit_cost = 0.0

        exp_date = None
        exp_str = clean_row.get("expiry_date", "")
        if exp_str:
            try:
                exp_date = datetime.strptime(exp_str, "%Y-%m-%d").date()
            except ValueError:
                pass

        inv = db.query(Inventory).filter(
            Inventory.phc_id == phc_id,
            Inventory.medicine_id == med_id
        ).first()

        if inv:
            inv.available_stock = stock
            if batch_num:
                inv.batch_number = batch_num
            if exp_date:
                inv.expiry_date = exp_date
            if unit_cost > 0:
                inv.unit_cost = unit_cost
            updated_count += 1
        else:
            inv = Inventory(
                phc_id=phc_id,
                medicine_id=med_id,
                available_stock=stock,
                reserved_stock=0,
                unit_cost=unit_cost,
                batch_number=batch_num,
                expiry_date=exp_date
            )
            db.add(inv)
            inserted_count += 1

        # Calculate Batch 5 prediction and inventory metrics for the record
        try:
            from app.services.inventory_calculations import calculate_record_metrics
            fallback_burn = None
            if "daily_burn_rate" in clean_row:
                try:
                    fallback_burn = float(clean_row["daily_burn_rate"])
                except ValueError:
                    pass

            metrics = calculate_record_metrics(
                db=db,
                phc_id=phc_id,
                medicine_id=med_id,
                available_stock=stock,
                daily_burn_fallback=fallback_burn
            )
            processed_records.append({
                "phc_code": phc_code,
                "medicine_code": med_code,
                "available_stock": stock,
                "units_sold_today": metrics["units_sold_today"],
                "seven_day_demand": metrics["seven_day_demand"],
                "days_remaining": metrics["days_remaining"],
                "risk_level": metrics["risk_level"],
                "status_label": metrics["status_label"],
                "clinical_urgency": metrics["clinical_urgency"],
                "urgency_score": metrics["urgency_score"]
            })
        except Exception as metric_err:
            errors.append(f"Row {row_idx}: Calculation warning - {metric_err}")

    db.commit()

    return {
        "status": "SUCCESS" if not errors else "PARTIAL_SUCCESS",
        "csv_type": "inventory",
        "inserted_records": inserted_count,
        "updated_records": updated_count,
        "records": processed_records,
        "errors": errors,
        "notice": "Ingested inventory records into PostgreSQL and calculated demand/risk metrics successfully."
    }


def parse_and_validate_csv(db: Session, file_content: str) -> Dict[str, Any]:
    """
    Unified entry point for CSV parsing:
    Detects header schema, validates required columns, and processes the file.
    """
    f = io.StringIO(file_content.strip())
    reader = csv.DictReader(f)
    detected_type = validate_csv_columns(reader.fieldnames, expected_type="auto")

    if detected_type == "consumption":
        return parse_and_ingest_consumption_csv(db, file_content)
    else:
        return parse_and_ingest_inventory_csv(db, file_content)
