"""
Recurring Transactions Route
Supports CRUD + manual trigger to fire all due recurring transactions
into the actual transactions table.
"""
from datetime import date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import RecurringTransaction, Transaction, User
from app.schemas import RecurringTransactionCreate, RecurringTransactionResponse
from app.services.auth import get_current_user
from app.services.currency_service import convert_currency_logic

router = APIRouter(prefix="/recurring", tags=["recurring"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _advance_date(d: date, frequency: str) -> date:
    if frequency == "daily":
        return d + timedelta(days=1)
    elif frequency == "weekly":
        return d + timedelta(weeks=1)
    elif frequency == "monthly":
        # Move to same day next month
        month = d.month + 1 if d.month < 12 else 1
        year = d.year + (1 if d.month == 12 else 0)
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        return d.replace(year=year, month=month, day=min(d.day, max_day))
    elif frequency == "yearly":
        return d.replace(year=d.year + 1)
    return d


async def _resolve_currency(amount: float, currency: Optional[str]):
    """Same pattern as transaction.py -- converts to INR, the app's home
    currency. Returns (amount_in_inr, currency, original_amount, exchange_rate)."""
    currency = (currency or "INR").upper()
    if currency == "INR":
        return amount, "INR", None, 1.0
    result = await convert_currency_logic(amount, currency, "INR")
    return result["converted"], currency, amount, result["rate"]


def trigger_due_for_user(db: Session, user_id: int) -> int:
    """
    Checks all active recurring transactions for one user whose
    next_date <= today, creates actual Transaction records, and advances
    their next_date. Returns the number created. Shared by the manual
    /recurring/trigger route and the nightly scheduler.

    rec.amount is already stored in INR (converted at create/update time),
    so no currency conversion is needed here -- the currency metadata is
    just copied across for display purposes.
    """
    today = date.today()
    due = db.query(RecurringTransaction).filter(
        RecurringTransaction.user_id == user_id,
        RecurringTransaction.is_active == True,
        RecurringTransaction.next_date <= today,
    ).all()

    created_count = 0
    for rec in due:
        tx = Transaction(
            user_id=user_id,
            transaction_date=rec.next_date,
            description=f"[Auto] {rec.description}",
            amount=rec.amount,
            currency=rec.currency,
            original_amount=rec.original_amount,
            exchange_rate=rec.exchange_rate,
            category=rec.category,
            transaction_type=rec.transaction_type,
        )
        db.add(tx)
        rec.next_date = _advance_date(rec.next_date, rec.frequency)
        created_count += 1

    return created_count


def trigger_due_all_users(db: Session) -> dict:
    """
    Same as trigger_due_for_user but across every user in one pass --
    used by the nightly scheduler so it doesn't need one query per user.
    Returns {user_id: count_created}.
    """
    today = date.today()
    due = db.query(RecurringTransaction).filter(
        RecurringTransaction.is_active == True,
        RecurringTransaction.next_date <= today,
    ).all()

    counts: dict = {}
    for rec in due:
        tx = Transaction(
            user_id=rec.user_id,
            transaction_date=rec.next_date,
            description=f"[Auto] {rec.description}",
            amount=rec.amount,
            currency=rec.currency,
            original_amount=rec.original_amount,
            exchange_rate=rec.exchange_rate,
            category=rec.category,
            transaction_type=rec.transaction_type,
        )
        db.add(tx)
        rec.next_date = _advance_date(rec.next_date, rec.frequency)
        counts[rec.user_id] = counts.get(rec.user_id, 0) + 1

    return counts


# --- GET all recurring transactions ---
@router.get("/", response_model=list[RecurringTransactionResponse])
def list_recurring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(RecurringTransaction)
        .filter(RecurringTransaction.user_id == current_user.id)
        .order_by(RecurringTransaction.next_date)
        .all()
    )


# --- CREATE ---
@router.post("/", response_model=RecurringTransactionResponse)
async def create_recurring(
    data: RecurringTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    final_amount, currency, original_amount, exchange_rate = await _resolve_currency(
        data.amount, data.currency
    )
    rec = RecurringTransaction(
        user_id=current_user.id,
        description=data.description,
        amount=final_amount,
        currency=currency,
        original_amount=original_amount,
        exchange_rate=exchange_rate,
        category=data.category,
        transaction_type=data.transaction_type,
        frequency=data.frequency,
        next_date=data.next_date,
        is_active=data.is_active,
    )
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


# --- UPDATE ---
@router.put("/{rec_id}", response_model=RecurringTransactionResponse)
async def update_recurring(
    rec_id: int,
    data: RecurringTransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = db.query(RecurringTransaction).filter(
        RecurringTransaction.id == rec_id,
        RecurringTransaction.user_id == current_user.id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")

    final_amount, currency, original_amount, exchange_rate = await _resolve_currency(
        data.amount, data.currency
    )

    rec.description = data.description
    rec.amount = final_amount
    rec.currency = currency
    rec.original_amount = original_amount
    rec.exchange_rate = exchange_rate
    rec.category = data.category
    rec.transaction_type = data.transaction_type
    rec.frequency = data.frequency
    rec.next_date = data.next_date
    rec.is_active = data.is_active
    db.commit()
    db.refresh(rec)
    return rec


# --- DELETE ---
@router.delete("/{rec_id}")
def delete_recurring(
    rec_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    rec = db.query(RecurringTransaction).filter(
        RecurringTransaction.id == rec_id,
        RecurringTransaction.user_id == current_user.id
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recurring transaction not found")
    db.delete(rec)
    db.commit()
    return {"detail": "Deleted"}


# --- TRIGGER: fire all due recurring transactions for the logged-in user ---
@router.post("/trigger")
def trigger_recurring(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    created_count = trigger_due_for_user(db, current_user.id)
    db.commit()
    return {"triggered": created_count, "message": f"Created {created_count} transaction(s) from recurring schedule."}