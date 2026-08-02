from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
import calendar

from app.database import SessionLocal
from app.models import Transaction, User, Budget, SavingsGoal, Subscription
from app.services.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def compute_alerts(user_id: int, db: Session) -> dict:
    """
    Aggregates all financial alerts for a user. Extracted from the /alerts
    route so it can be called both by that route (for the logged-in user)
    and by the nightly scheduler (looping over every user) without
    duplicating logic:
    - Budget overruns (critical)
    - Burn rate warning (critical)
    - Subscriptions due in 7 days (warning)
    - Goals behind schedule (warning)
    - Positive tips (info)
    """
    alerts = []
    today = date.today()
    current_month = today.strftime("%Y-%m")

    # ── Fetch data ──────────────────────────────────────────────
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).all()
    subscriptions = db.query(Subscription).filter(Subscription.user_id == user_id).all()

    # ── Current month income & expenses ─────────────────────────
    current_month_txs = []
    for t in transactions:
        tx_date = t.transaction_date
        if isinstance(tx_date, str):
            try:
                tx_date = datetime.strptime(tx_date, "%Y-%m-%d").date()
            except ValueError:
                continue
        if str(tx_date)[:7] == current_month:
            current_month_txs.append(t)

    monthly_income = sum(t.amount for t in current_month_txs if t.transaction_type == "income")
    monthly_expense = sum(t.amount for t in current_month_txs if t.transaction_type == "expense")

    # Category spend map
    category_spend = {}
    for t in current_month_txs:
        if t.transaction_type == "expense":
            category_spend[t.category] = category_spend.get(t.category, 0.0) + t.amount

    # ── 1. Budget Overruns (critical) ────────────────────────────
    for b in budgets:
        spent = category_spend.get(b.category, 0.0)
        if spent > b.amount:
            overrun_pct = ((spent - b.amount) / b.amount * 100)
            alerts.append({
                "type": "critical",
                "icon": "🔴",
                "title": f"Budget Exceeded: {b.category}",
                "message": f"You've spent ₹{spent:,.0f} vs your ₹{b.amount:,.0f} limit — {overrun_pct:.0f}% over budget.",
                "category": "budget"
            })
        elif spent > b.amount * 0.85:
            alerts.append({
                "type": "warning",
                "icon": "🟡",
                "title": f"Budget Warning: {b.category}",
                "message": f"₹{spent:,.0f} spent of ₹{b.amount:,.0f} limit — {(spent/b.amount*100):.0f}% used. Slow down!",
                "category": "budget"
            })

    # ── 2. Burn Rate Warning (critical) ─────────────────────────
    days_passed = today.day
    num_days = calendar.monthrange(today.year, today.month)[1]
    if days_passed > 0 and monthly_expense > 0:
        daily_burn = monthly_expense / days_passed
        projected = daily_burn * num_days
        if monthly_income > 0 and projected > monthly_income:
            shortfall = projected - monthly_income
            alerts.append({
                "type": "critical",
                "icon": "🔥",
                "title": "Burn Rate Alert",
                "message": f"At ₹{daily_burn:,.0f}/day, you'll overspend by ₹{shortfall:,.0f} this month. Cut back now!",
                "category": "spending"
            })

    # ── 3. Subscriptions Due in 7 days (warning) ────────────────
    in_7_days = today + timedelta(days=7)
    for sub in subscriptions:
        due = sub.next_due_date
        if isinstance(due, str):
            try:
                due = datetime.strptime(due, "%Y-%m-%d").date()
            except ValueError:
                continue
        if today <= due <= in_7_days:
            days_left = (due - today).days
            alerts.append({
                "type": "warning",
                "icon": "📅",
                "title": f"Bill Due: {sub.name}",
                "message": f"₹{sub.amount:,.0f} due in {days_left} day{'s' if days_left != 1 else ''}. ({sub.billing_cycle})",
                "category": "subscription"
            })
        elif due < today:
            alerts.append({
                "type": "critical",
                "icon": "⚠️",
                "title": f"Overdue Bill: {sub.name}",
                "message": f"₹{sub.amount:,.0f} payment was due on {due}. Please check your account.",
                "category": "subscription"
            })

    # ── 4. Goals Behind Schedule (warning) ──────────────────────
    for g in goals:
        if g.current_amount >= g.target_amount:
            continue
        target_date = g.target_date
        if isinstance(target_date, str):
            try:
                target_date = datetime.strptime(target_date, "%Y-%m-%d").date()
            except ValueError:
                continue
        days_remaining = (target_date - today).days
        if days_remaining <= 0:
            alerts.append({
                "type": "critical",
                "icon": "🎯",
                "title": f"Goal Overdue: {g.name}",
                "message": f"Target date passed! Still need ₹{(g.target_amount - g.current_amount):,.0f} more.",
                "category": "goal"
            })
        elif days_remaining <= 30:
            alerts.append({
                "type": "warning",
                "icon": "🎯",
                "title": f"Goal Deadline Soon: {g.name}",
                "message": f"Only {days_remaining} days left! Need ₹{(g.target_amount - g.current_amount):,.0f} more to reach ₹{g.target_amount:,.0f}.",
                "category": "goal"
            })

    # ── 5. Positive tips (info) ──────────────────────────────────
    if monthly_income > 0 and monthly_expense < monthly_income * 0.5:
        savings_pct = (1 - monthly_expense / monthly_income) * 100
        alerts.append({
            "type": "info",
            "icon": "✅",
            "title": "Great Savings Rate!",
            "message": f"You're saving {savings_pct:.0f}% of your income this month. Keep it up!",
            "category": "tip"
        })

    if not alerts:
        alerts.append({
            "type": "info",
            "icon": "🌟",
            "title": "All Clear!",
            "message": "No financial alerts right now. Your spending looks healthy!",
            "category": "tip"
        })

    critical_count = sum(1 for a in alerts if a["type"] == "critical")
    warning_count = sum(1 for a in alerts if a["type"] == "warning")

    return {
        "alerts": alerts,
        "total": len(alerts),
        "critical_count": critical_count,
        "warning_count": warning_count,
    }


@router.get("/alerts")
def get_alerts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return compute_alerts(current_user.id, db)