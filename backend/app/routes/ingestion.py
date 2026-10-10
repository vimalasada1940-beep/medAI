from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.collectors.csv_collector import parse_and_ingest_consumption_csv

router = APIRouter(prefix="/ingestion", tags=["Data Ingestion"])

@router.post("/csv")
async def upload_consumption_csv(
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    """
    Ingests daily consumption CSV logs into PostgreSQL database.
    Validates CSV fields, negative quantities, and date formatting.
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

    result = parse_and_ingest_consumption_csv(db, decoded)
    return result
