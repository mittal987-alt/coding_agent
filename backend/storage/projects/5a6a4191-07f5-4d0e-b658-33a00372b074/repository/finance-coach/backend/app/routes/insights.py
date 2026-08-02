from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import calendar

from app.database import SessionLocal
from app.models import Transaction, User, Budget
from app.services.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/insights")
def insights(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    food = sum(
        t.amount
        for t in transactions
        if t.category == "Food" and t.transaction_type == "expense"
    )

    travel = sum(
        t.amount
        for t in transactions
        if t.category == "Travel" and t.transaction_type == "expense"
    )

    shopping = sum(
        t.amount
        for t in transactions
        if t.category == "Shopping" and t.transaction_type == "expense"
    )

    insights = []

    # Historical high expense checks
    if food > 5000:
        insights.append(
            f"⚠ Food spending is high: ₹{food:,.2f}"
        )

    if shopping > 5000:
        insights.append(
            f"⚠ Shopping spending is high: ₹{shopping:,.2f}"
        )

    if travel > 2000:
        insights.append(
            f"⚠ Travel spending is high: ₹{travel:,.2f}"
        )

    # --- Predictive Burn Rate and Forecasting Logic ---
    today = datetime.now().date()
    current_month_txs = []
    
    for t in transactions:
        tx_date = t.transaction_date
        if isinstance(tx_date, str):
            try:
                tx_date = datetime.strptime(tx_date, "%Y-%m-%d").date()
            except ValueError:
                continue
        
        if tx_date.year == today.year and tx_date.month == today.month:
            current_month_txs.append(t)

    current_month_expenses = sum(t.amount for t in current_month_txs if t.transaction_type == "expense")
    current_month_income = sum(t.amount for t in current_month_txs if t.transaction_type == "income")
    
    days_passed = today.day
    num_days = calendar.monthrange(today.year, today.month)[1]
    
    daily_burn = 0.0
    projected_expenses = 0.0
    
    if days_passed > 0:
        daily_burn = current_month_expenses / days_passed
        projected_expenses = daily_burn * num_days

    # Alert if projected monthly expenses exceed monthly income
    if projected_expenses > 0 and current_month_income > 0 and projected_expenses > current_month_income:
        insights.append(
            f"🔮 Based on your daily burn rate of ₹{daily_burn:,.2f}/day, your projected expenses (₹{projected_expenses:,.2f}) will exceed your income of ₹{current_month_income:,.2f} this month."
        )

    # Check budgets projections
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    for b in budgets:
        cat_spent_current = sum(
            t.amount 
            for t in current_month_txs 
            if t.category == b.category and t.transaction_type == "expense"
        )
        if days_passed > 0 and cat_spent_current > 0:
            projected_cat_spent = (cat_spent_current / days_passed) * num_days
            if projected_cat_spent > b.amount:
                overrun = projected_cat_spent - b.amount
                insights.append(
                    f"🔮 Projected spending for **{b.category}** (₹{projected_cat_spent:,.2f}) is set to exceed its budget of ₹{b.amount:,.2f} by ₹{overrun:,.2f}."
                )

    if not insights:
        insights.append(
            "✅ Spending looks healthy"
        )

    return {
        "food": food,
        "travel": travel,
        "shopping": shopping,
        "insights": insights,
        "predictions": {
            "projected_expense": projected_expenses,
            "days_remaining": num_days - days_passed,
            "burn_rate_daily": daily_burn,
            "current_month_income": current_month_income
        }
    }