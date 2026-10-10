import csv
import io
from datetime import datetime, date
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models import DailyConsumption, PHC, Medicine

def parse_and_ingest_consumption_csv(db: Session, file_content: str) -> Dict[str, Any]:
    """
    Parses CSV content containing daily consumption logs and ingests them into PostgreSQL.
    CSV Format Expected: phc_code, medicine_code, record_date, quantity_consumed
    Validates negative quantities, invalid dates, and missing PHC/Medicine codes.
    """
    f = io.StringIO(file_content)
    reader = csv.DictReader(f)

    inserted_count = 0
    updated_count = 0
    errors = []

    # Map PHC & Medicine codes to DB IDs
    phcs = {p.code: p.id for p in db.query(PHC).all()}
    medicines = {m.code: m.id for m in db.query(Medicine).all()}

    for row_idx, row in enumerate(reader, start=1):
        phc_code = row.get("phc_code", "").strip()
        med_code = row.get("medicine_code", "").strip()
        date_str = row.get("record_date", "").strip()
        qty_str = row.get("quantity_consumed", "").strip()

        if not phc_code or not med_code or not date_str or not qty_str:
            errors.append(f"Row {row_idx}: Missing required fields.")
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

        # Check existing record
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
        "inserted_records": inserted_count,
        "updated_records": updated_count,
        "errors": errors,
        "notice": "Ingested synthetic demonstration records successfully."
    }
