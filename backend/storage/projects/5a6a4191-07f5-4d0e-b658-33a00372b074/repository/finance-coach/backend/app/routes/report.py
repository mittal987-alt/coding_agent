import csv
import io

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.services.auth import get_current_user

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/csv")
def export_csv(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.user_id == current_user.id)
        .order_by(models.Transaction.transaction_date.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Date",
        "Description",
        "Category",
        "Type",
        "Amount"
    ])

    for t in transactions:
        writer.writerow([
            t.transaction_date,
            t.description,
            t.category,
            t.transaction_type,
            t.amount,
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=finance_report.csv"
        },
    )