from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from datetime import datetime

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


@router.get("/analytics/daily-spend")
def get_daily_spend_heatmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns daily expense totals for the past 90 days for rendering
    a GitHub-style spending heatmap.
    Format: [{date: "YYYY-MM-DD", amount: float, level: 0-4}]
    """
    today = date.today()
    start_date = today - timedelta(days=89)  # 90 days window

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == current_user.id,
            Transaction.transaction_type == "expense"
        )
        .all()
    )

    # Build a map of date -> total spend
    spend_map: dict[str, float] = {}
    for t in transactions:
        tx_date = t.transaction_date
        if isinstance(tx_date, str):
            try:
                tx_date = datetime.strptime(tx_date, "%Y-%m-%d").date()
            except ValueError:
                continue
        if start_date <= tx_date <= today:
            key = tx_date.isoformat()
            spend_map[key] = spend_map.get(key, 0.0) + t.amount

    # Determine intensity levels (0-4) based on quartiles of non-zero values
    amounts = [v for v in spend_map.values() if v > 0]
    if amounts:
        amounts_sorted = sorted(amounts)
        n = len(amounts_sorted)
        q1 = amounts_sorted[n // 4]
        q2 = amounts_sorted[n // 2]
        q3 = amounts_sorted[3 * n // 4]
        max_amt = amounts_sorted[-1]
    else:
        q1 = q2 = q3 = max_amt = 1

    def get_level(amount: float) -> int:
        if amount == 0:
            return 0
        elif amount <= q1:
            return 1
        elif amount <= q2:
            return 2
        elif amount <= q3:
            return 3
        else:
            return 4

    # Generate all 90 days
    result = []
    current = start_date
    while current <= today:
        key = current.isoformat()
        amount = spend_map.get(key, 0.0)
        result.append({
            "date": key,
            "amount": round(amount, 2),
            "level": get_level(amount),
            "day_of_week": current.weekday(),  # 0=Mon, 6=Sun
            "week": (current - start_date).days // 7
        })
        current += timedelta(days=1)

    total_spend = sum(spend_map.values())
    avg_daily = total_spend / 90

    return {
        "days": result,
        "total_spend_90d": round(total_spend, 2),
        "avg_daily_spend": round(avg_daily, 2),
        "max_day_spend": round(max_amt if amounts else 0, 2),
        "active_days": len(amounts),
    }
