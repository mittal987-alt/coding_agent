"""
Gamified Savings Challenges
Four challenge types that users can join and track progress on.
"""
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import SessionLocal
from app.models import Challenge, Transaction, User
from app.services.auth import get_current_user

router = APIRouter(prefix="/challenges", tags=["challenges"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


CHALLENGE_DEFINITIONS = [
    {
        "type": "52_week",
        "name": "52-Week Savings Challenge",
        "icon": "📅",
        "description": "Save ₹Week×100 each week for 52 weeks. Week 1 = ₹100, Week 52 = ₹5,200. Total: ₹1,37,800!",
        "target_value": 52,
        "color": "teal",
    },
    {
        "type": "no_spend_week",
        "name": "No-Spend Week",
        "icon": "🚫",
        "description": "Go 7 consecutive days with zero non-essential expense transactions.",
        "target_value": 7,
        "color": "violet",
    },
    {
        "type": "save_10_pct",
        "name": "Save 10% This Month",
        "icon": "💰",
        "description": "Ensure your savings rate hits at least 10% of income for the current calendar month.",
        "target_value": 10,
        "color": "amber",
    },
    {
        "type": "100_day_streak",
        "name": "100-Day Logging Streak",
        "icon": "🔥",
        "description": "Log at least one transaction every day for 100 consecutive days.",
        "target_value": 100,
        "color": "coral",
    },
]


class JoinChallengeRequest(BaseModel):
    challenge_type: str


def _compute_progress(challenge: Challenge, transactions: list, today: date) -> dict:
    ct = challenge.challenge_type

    if ct == "52_week":
        # Number of full weeks completed since start
        days_elapsed = (today - challenge.started_at).days
        weeks_completed = min(days_elapsed // 7, 52)
        # Total target savings = sum(w*100 for w in 1..52)
        amount_target = sum(w * 100 for w in range(1, 53))
        amount_saved = sum(w * 100 for w in range(1, weeks_completed + 1))
        pct = round((weeks_completed / 52) * 100, 1)
        return {
            "current": weeks_completed,
            "target": 52,
            "pct": pct,
            "label": f"Week {weeks_completed} of 52",
            "sub": f"₹{amount_saved:,.0f} saved of ₹{amount_target:,.0f}",
            "is_complete": weeks_completed >= 52,
        }

    elif ct == "no_spend_week":
        # Count consecutive days from start with 0 expense transactions
        expenses_by_date = {}
        for t in transactions:
            if t.transaction_type == "expense":
                d = t.transaction_date
                expenses_by_date[d] = expenses_by_date.get(d, 0) + 1
        streak = 0
        check = challenge.started_at
        while streak < 7 and check <= today:
            if expenses_by_date.get(check, 0) == 0:
                streak += 1
            else:
                streak = 0
            check += timedelta(days=1)
        pct = round((streak / 7) * 100, 1)
        return {
            "current": streak,
            "target": 7,
            "pct": pct,
            "label": f"{streak} / 7 clean days",
            "sub": "No expense transactions on those days",
            "is_complete": streak >= 7,
        }

    elif ct == "save_10_pct":
        # Check current month income vs expenses
        month_start = today.replace(day=1)
        month_txns = [t for t in transactions if t.transaction_date >= month_start]
        income = sum(t.amount for t in month_txns if t.transaction_type == "income")
        expense = sum(t.amount for t in month_txns if t.transaction_type == "expense")
        savings_rate = round(((income - expense) / income * 100) if income > 0 else 0, 1)
        savings_rate_clamped = max(0.0, savings_rate)
        pct = min(100.0, round((savings_rate_clamped / 10) * 100, 1))
        return {
            "current": savings_rate_clamped,
            "target": 10,
            "pct": pct,
            "label": f"{savings_rate}% savings rate",
            "sub": f"Income ₹{income:,.0f} | Expenses ₹{expense:,.0f}",
            "is_complete": savings_rate >= 10,
        }

    elif ct == "100_day_streak":
        # Count consecutive days from start that have at least 1 transaction
        tx_dates = set(t.transaction_date for t in transactions)
        streak = 0
        check = challenge.started_at
        while check <= today:
            if check in tx_dates:
                streak += 1
            else:
                break
            check += timedelta(days=1)
        streak = min(streak, 100)
        pct = round((streak / 100) * 100, 1)
        return {
            "current": streak,
            "target": 100,
            "pct": pct,
            "label": f"{streak} / 100 days",
            "sub": "Log at least one transaction per day",
            "is_complete": streak >= 100,
        }

    return {"current": 0, "target": 1, "pct": 0, "label": "Unknown", "sub": "", "is_complete": False}


@router.get("/")
def list_challenges(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    today = date.today()
    joined = {c.challenge_type: c for c in db.query(Challenge).filter(Challenge.user_id == current_user.id).all()}
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()

    result = []
    for defn in CHALLENGE_DEFINITIONS:
        entry = dict(defn)
        if defn["type"] in joined:
            ch = joined[defn["type"]]
            progress = _compute_progress(ch, transactions, today)
            entry.update({
                "joined": True,
                "started_at": ch.started_at.isoformat(),
                "is_complete": progress["is_complete"],
                **progress,
            })
        else:
            entry.update({
                "joined": False,
                "started_at": None,
                "is_complete": False,
                "current": 0,
                "target": defn["target_value"],
                "pct": 0,
                "label": "Not started",
                "sub": "",
            })
        result.append(entry)

    return result


@router.post("/join")
def join_challenge(
    req: JoinChallengeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    valid_types = {d["type"] for d in CHALLENGE_DEFINITIONS}
    if req.challenge_type not in valid_types:
        raise HTTPException(status_code=400, detail="Unknown challenge type.")

    existing = db.query(Challenge).filter(
        Challenge.user_id == current_user.id,
        Challenge.challenge_type == req.challenge_type,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already joined this challenge.")

    defn = next(d for d in CHALLENGE_DEFINITIONS if d["type"] == req.challenge_type)
    ch = Challenge(
        user_id=current_user.id,
        challenge_type=req.challenge_type,
        started_at=date.today(),
        target_value=defn["target_value"],
    )
    db.add(ch)
    db.commit()
    return {"message": "Challenge joined!", "challenge_type": req.challenge_type}


@router.delete("/{challenge_type}")
def leave_challenge(
    challenge_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ch = db.query(Challenge).filter(
        Challenge.user_id == current_user.id,
        Challenge.challenge_type == challenge_type,
    ).first()
    if not ch:
        raise HTTPException(status_code=404, detail="Challenge not found.")
    db.delete(ch)
    db.commit()
    return {"message": "Left challenge."}
