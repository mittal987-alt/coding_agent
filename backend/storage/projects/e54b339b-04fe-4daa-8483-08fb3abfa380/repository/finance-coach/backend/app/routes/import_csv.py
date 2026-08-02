"""
Multi-Bank CSV / Excel Import Route
Parses bank statement CSVs from HDFC, SBI, ICICI, Axis, Kotak, and
generic formats. Auto-detects the bank format, maps columns, and
bulk-inserts transactions.
"""
import csv
import io

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Transaction, User
from app.services.auth import get_current_user
from app.services.csv_service import detect_format, parse_csv_rows

router = APIRouter(prefix="/import", tags=["import"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/csv")
async def import_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a bank statement CSV.
    Supported banks: HDFC, SBI, ICICI, Axis, Kotak, Generic.
    Returns count of transactions imported.
    """
    if not file.filename.lower().endswith((".csv", ".txt")):
        raise HTTPException(status_code=400, detail="Only .csv or .txt files are accepted.")

    content = await file.read()
    try:
        text = content.decode("utf-8-sig")   # handles BOM
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.reader(io.StringIO(text))
    all_rows = [row for row in reader if any(cell.strip() for cell in row)]

    if len(all_rows) < 2:
        raise HTTPException(status_code=400, detail="CSV file is empty or has no data rows.")

    headers = all_rows[0]
    data_rows = all_rows[1:]

    bank_format = detect_format(headers)
    parsed = parse_csv_rows(bank_format, data_rows, headers)

    if not parsed:
        raise HTTPException(status_code=422, detail=f"Could not parse any transactions (detected format: {bank_format}). Check file format.")

    inserted = 0
    for row in parsed:
        tx = Transaction(
            user_id=current_user.id,
            transaction_date=row["date"],
            description=row["desc"][:255],
            amount=row["amount"],
            category=row["category"],
            transaction_type=row["type"],
        )
        db.add(tx)
        inserted += 1

    db.commit()

    return {
        "success": True,
        "bank_format_detected": bank_format,
        "transactions_imported": inserted,
        "message": f"Successfully imported {inserted} transactions from {bank_format} format.",
    }


@router.post("/csv/preview")
async def preview_csv(file: UploadFile = File(...)):
    """Returns first 10 parsed rows for preview without saving."""
    content = await file.read()
    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    reader = csv.reader(io.StringIO(text))
    all_rows = [row for row in reader if any(cell.strip() for cell in row)]

    if len(all_rows) < 2:
        return {"rows": [], "bank_format": "UNKNOWN", "total_rows": 0}

    headers = all_rows[0]
    data_rows = all_rows[1:]
    
    bank_format = detect_format(headers)
    parsed = parse_csv_rows(bank_format, data_rows, headers)

    return {
        "bank_format": bank_format,
        "total_rows": len(parsed),
        "preview": [
            {
                "date": str(r["date"]),
                "description": r["desc"],
                "amount": r["amount"],
                "type": r["type"],
                "category": r["category"],
            }
            for r in parsed[:10]
        ],
    }
