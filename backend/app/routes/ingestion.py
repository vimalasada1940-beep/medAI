from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.collectors.csv_collector import (
    parse_and_validate_csv, 
    parse_and_ingest_consumption_csv,
    parse_and_ingest_inventory_csv,
    CSVValidationError
)

router = APIRouter(prefix="/ingestion", tags=["Data Ingestion"])

@router.post("/csv")
async def upload_csv_file(
    file: UploadFile = File(...),
    csv_type: str = Query("auto", description="Schema type: auto, consumption, or inventory"),
    db: Session = Depends(get_db)
):
    """
    Ingests daily consumption logs or PHC inventory CSV files into PostgreSQL.
    Validates required columns, positive quantities, and foreign key references.
    Returns HTTP 422 with missing columns if validation fails.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only .csv files are supported."
        )

    content = await file.read()
    try:
        decoded = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to decode file. Ensure file is UTF-8 encoded CSV text."
        )

    try:
        if csv_type == "consumption":
            result = parse_and_ingest_consumption_csv(db, decoded)
        elif csv_type == "inventory":
            result = parse_and_ingest_inventory_csv(db, decoded)
        else:
            result = parse_and_validate_csv(db, decoded)
        return result
    except CSVValidationError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=val_err.to_dict()
        )

