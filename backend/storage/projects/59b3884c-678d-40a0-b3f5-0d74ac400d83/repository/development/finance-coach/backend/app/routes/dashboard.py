from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Transaction, User
from app.services.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/dashboard")
def dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    income = sum(
        t.amount
        for t in transactions
        if t.transaction_type == "income"
    )

    expense = sum(
        t.amount
        for t in transactions
        if t.transaction_type == "expense"
    )

    savings = income - expense

    return {
        "income": income,
        "expense": expense,
        "savings": savings,
        "total_transactions": len(transactions)
    }