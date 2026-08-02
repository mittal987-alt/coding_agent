from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models import Subscription, User, Transaction
from app.schemas import SubscriptionCreate, SubscriptionResponse
from app.services.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/subscriptions", response_model=List[SubscriptionResponse])
def get_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.id)
        .all()
    )


@router.post("/subscriptions", response_model=SubscriptionResponse)
def create_subscription(
    sub_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_sub = Subscription(
        user_id=current_user.id,
        name=sub_data.name,
        amount=sub_data.amount,
        category=sub_data.category,
        billing_cycle=sub_data.billing_cycle,
        next_due_date=sub_data.next_due_date
    )
    db.add(new_sub)
    db.commit()
    db.refresh(new_sub)
    return new_sub


@router.put("/subscriptions/{sub_id}", response_model=SubscriptionResponse)
def update_subscription(
    sub_id: int,
    sub_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = (
        db.query(Subscription)
        .filter(Subscription.id == sub_id, Subscription.user_id == current_user.id)
        .first()
    )

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    sub.name = sub_data.name
    sub.amount = sub_data.amount
    sub.category = sub_data.category
    sub.billing_cycle = sub_data.billing_cycle
    sub.next_due_date = sub_data.next_due_date

    db.commit()
    db.refresh(sub)
    return sub


@router.delete("/subscriptions/{sub_id}")
def delete_subscription(
    sub_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sub = (
        db.query(Subscription)
        .filter(Subscription.id == sub_id, Subscription.user_id == current_user.id)
        .first()
    )

    if not sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subscription not found"
        )

    db.delete(sub)
    db.commit()
    return {"message": "Subscription deleted successfully"}


@router.get("/subscriptions/detect")
def detect_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Scans transaction history to identify recurring expenses.
    Groups transactions by description, checks chronological intervals,
    and returns list of suggested subscriptions.
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id, Transaction.transaction_type == "expense")
        .all()
    )

    # Group by cleaned lowercase description
    groups = {}
    for tx in transactions:
        desc = tx.description.strip().lower()
        if not desc:
            continue
        # simple grouping by matching description
        if desc not in groups:
            groups[desc] = []
        groups[desc].append(tx)

    suggestions = []
    # Check already registered subscriptions to avoid duplicate suggestions
    existing_subs = db.query(Subscription).filter(Subscription.user_id == current_user.id).all()
    existing_names = {s.name.lower().strip() for s in existing_subs}

    for desc, tx_list in groups.items():
        if len(tx_list) < 2:
            continue

        # Skip if this description already matches a registered subscription name
        if any(existing_name in desc for existing_name in existing_names):
            continue

        # Sort by date
        tx_list.sort(key=lambda x: x.transaction_date)

        # Calculate differences between consecutive transactions
        intervals = []
        for i in range(len(tx_list) - 1):
            diff = (tx_list[i+1].transaction_date - tx_list[i].transaction_date).days
            intervals.append(diff)

        # Check if intervals correspond to monthly recurring pattern (~25 to 35 days)
        # We can also check if the amount is similar (within 10% range)
        avg_interval = sum(intervals) / len(intervals)
        is_monthly = 25 <= avg_interval <= 35
        
        # Check amount consistency
        amounts = [tx.amount for tx in tx_list]
        avg_amount = sum(amounts) / len(amounts)
        amount_variance = all(abs(amt - avg_amount) / avg_amount <= 0.15 for amt in amounts) if avg_amount > 0 else False

        if is_monthly and amount_variance:
            latest_tx = tx_list[-1]
            
            # Suggest next due date as latest_date + 30 days
            suggested_due = latest_tx.transaction_date + timedelta(days=30)
            
            # Capitalize name nicely
            name = latest_tx.description.title()
            
            suggestions.append({
                "name": name,
                "amount": latest_tx.amount,
                "category": latest_tx.category,
                "billing_cycle": "Monthly",
                "next_due_date": suggested_due.isoformat()
            })

    return suggestions
