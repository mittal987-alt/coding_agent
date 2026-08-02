from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
from calendar import monthrange

from app.database import SessionLocal
from app.models import PaymentReminder, User
from app.schemas import PaymentReminderCreate, PaymentReminderResponse, PaymentReminderUpdate
from app.services.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _advance_date(d: date, frequency: str) -> date:
    """Advance a date by one cycle of the given frequency."""
    if frequency == "daily":
        return d + timedelta(days=1)
    if frequency == "weekly":
        return d + timedelta(weeks=1)
    if frequency == "yearly":
        try:
            return d.replace(year=d.year + 1)
        except ValueError:
            # Feb 29 on a non-leap year
            return d.replace(year=d.year + 1, day=28)
    # default: monthly
    month = d.month + 1
    year = d.year
    if month > 12:
        month = 1
        year += 1
    day = min(d.day, monthrange(year, month)[1])
    return d.replace(year=year, month=month, day=day)


def _to_response(r: PaymentReminder) -> dict:
    today = date.today()
    days_left = (r.due_date - today).days
    urgency = "overdue" if days_left < 0 else ("urgent" if days_left <= 3 else ("soon" if days_left <= 7 else "ok"))
    return {
        "id": r.id,
        "name": r.name,
        "amount": r.amount,
        "due_date": r.due_date,
        "category": r.category,
        "is_paid": r.is_paid,
        "days_left": days_left,
        "urgency": urgency,
        "is_recurring": getattr(r, "is_recurring", False),
        "recurrence_frequency": getattr(r, "recurrence_frequency", None),
    }


@router.get("/reminders", response_model=List[PaymentReminderResponse])
def get_reminders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminders = (
        db.query(PaymentReminder)
        .filter(PaymentReminder.user_id == current_user.id)
        .order_by(PaymentReminder.due_date)
        .all()
    )
    return [_to_response(r) for r in reminders]


@router.post("/reminders", response_model=PaymentReminderResponse)
def create_reminder(
    data: PaymentReminderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminder = PaymentReminder(
        user_id=current_user.id,
        name=data.name,
        amount=data.amount,
        due_date=data.due_date,
        category=data.category,
        is_paid=False,
        is_recurring=getattr(data, "is_recurring", False) or False,
        recurrence_frequency=getattr(data, "recurrence_frequency", None),
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return _to_response(reminder)


@router.put("/reminders/{reminder_id}", response_model=PaymentReminderResponse)
def update_reminder(
    reminder_id: int,
    data: PaymentReminderUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Edit a reminder's fields — used for snoozing/rescheduling (due_date),
    renaming, changing amount/category, or toggling recurrence."""
    reminder = (
        db.query(PaymentReminder)
        .filter(PaymentReminder.id == reminder_id, PaymentReminder.user_id == current_user.id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(reminder, field, value)

    db.commit()
    db.refresh(reminder)
    return _to_response(reminder)


@router.put("/reminders/{reminder_id}/snooze/{days}", response_model=PaymentReminderResponse)
def snooze_reminder(
    reminder_id: int,
    days: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Push a reminder's due date forward by a number of days."""
    reminder = (
        db.query(PaymentReminder)
        .filter(PaymentReminder.id == reminder_id, PaymentReminder.user_id == current_user.id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    reminder.due_date = reminder.due_date + timedelta(days=days)
    db.commit()
    db.refresh(reminder)
    return _to_response(reminder)


@router.put("/reminders/{reminder_id}/pay")
def mark_reminder_paid(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminder = (
        db.query(PaymentReminder)
        .filter(PaymentReminder.id == reminder_id, PaymentReminder.user_id == current_user.id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")

    reminder.is_paid = True
    db.commit()

    # If this reminder recurs, spawn the next occurrence automatically.
    if getattr(reminder, "is_recurring", False) and getattr(reminder, "recurrence_frequency", None):
        next_due = _advance_date(reminder.due_date, reminder.recurrence_frequency)
        next_reminder = PaymentReminder(
            user_id=current_user.id,
            name=reminder.name,
            amount=reminder.amount,
            due_date=next_due,
            category=reminder.category,
            is_paid=False,
            is_recurring=True,
            recurrence_frequency=reminder.recurrence_frequency,
        )
        db.add(next_reminder)
        db.commit()
        return {"message": f"Marked as paid. Next '{reminder.name}' scheduled for {next_due.isoformat()}."}

    return {"message": "Marked as paid"}


@router.delete("/reminders/{reminder_id}")
def delete_reminder(
    reminder_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    reminder = (
        db.query(PaymentReminder)
        .filter(PaymentReminder.id == reminder_id, PaymentReminder.user_id == current_user.id)
        .first()
    )
    if not reminder:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reminder not found")
    db.delete(reminder)
    db.commit()
    return {"message": "Reminder deleted"}