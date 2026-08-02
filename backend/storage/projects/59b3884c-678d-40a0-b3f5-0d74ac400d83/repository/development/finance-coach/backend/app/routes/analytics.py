from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from app.database import SessionLocal
from app.models import Transaction, User, Budget, SavingsGoal
from app.services.auth import get_current_user

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/analytics/trends")
def get_monthly_trends(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns monthly income vs expenses for the last 6 months (or all available months).
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    if not transactions:
        return []

    # Sort transactions chronologically
    transactions.sort(key=lambda t: t.transaction_date)

    monthly_data = {}
    
    # Process transactions and accumulate income / expenses
    for t in transactions:
        # Date string formatting: e.g. "2026-06-12"
        # We parse the date (usually a date object in sqlalchemy, but let's be safe)
        tx_date = t.transaction_date
        if isinstance(tx_date, str):
            try:
                tx_date = datetime.strptime(tx_date, "%Y-%m-%d").date()
            except ValueError:
                continue

        # Create unique key like "2026-06" for sorting, and human readable "Jun 2026"
        sort_key = tx_date.strftime("%Y-%m")
        display_month = tx_date.strftime("%b %Y")

        if sort_key not in monthly_data:
            monthly_data[sort_key] = {
                "month": display_month,
                "income": 0.0,
                "expense": 0.0
            }

        amount = float(t.amount)
        if t.transaction_type == "income" or t.category.lower() == "income":
            monthly_data[sort_key]["income"] += amount
        else:
            monthly_data[sort_key]["expense"] += amount

    # Sort by the sort_key (YYYY-MM)
    sorted_keys = sorted(monthly_data.keys())
    
    # Return last 6 months of records
    trend_results = [monthly_data[k] for k in sorted_keys[-6:]]
    return trend_results


@router.get("/analytics/health-score")
def get_health_score(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes a 0-100 Financial Health Score from:
      - Savings Rate (40 pts): (income - expense) / income
      - Budget Discipline (40 pts): fraction of budgets not exceeded
      - Goals Activity (20 pts): at least one active savings goal
    """
    today = date.today()
    current_month = today.strftime("%Y-%m")

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()

    # Monthly income and expense
    monthly_income = sum(
        t.amount for t in transactions
        if (t.transaction_type == "income" or t.category.lower() == "income")
        and str(t.transaction_date)[:7] == current_month
    )
    monthly_expense = sum(
        t.amount for t in transactions
        if t.transaction_type != "income" and t.category.lower() != "income"
        and str(t.transaction_date)[:7] == current_month
    )

    # --- Savings Rate Score (0-40) ---
    if monthly_income > 0:
        savings_rate = max(0.0, (monthly_income - monthly_expense) / monthly_income)
        savings_score = min(40, round(savings_rate * 40 * 2))  # scaled so 50%+ savings = full 40
    else:
        savings_score = 0

    # --- Budget Discipline Score (0-40) ---
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    budget_score = 40  # start with full marks
    budget_tips = []
    if budgets:
        within_count = 0
        for b in budgets:
            spent = sum(
                t.amount for t in transactions
                if t.category == b.category
                and t.transaction_type != "income"
                and str(t.transaction_date)[:7] == current_month
            )
            if spent <= b.amount:
                within_count += 1
            else:
                budget_tips.append(f"Over budget on {b.category} by ₹{round(spent - b.amount):,}")
        budget_score = round((within_count / len(budgets)) * 40)

    # --- Goals Activity Score (0-20) ---
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == current_user.id).all()
    active_goals = [g for g in goals if g.current_amount < g.target_amount]
    goals_score = 20 if active_goals else (10 if goals else 0)

    total_score = savings_score + budget_score + goals_score

    # Generate advice string
    advice_parts = []
    if savings_score < 20:
        advice_parts.append("Try to save at least 20% of your income this month.")
    if budget_tips:
        advice_parts.extend(budget_tips[:2])
    if goals_score == 0:
        advice_parts.append("Create a savings goal to boost your score by 20 points!")

    advice = " ".join(advice_parts) if advice_parts else "Great work! Keep maintaining your spending habits."

    return {
        "score": total_score,
        "savings_score": savings_score,
        "budget_score": budget_score,
        "goals_score": goals_score,
        "advice": advice,
        "monthly_income": monthly_income,
        "monthly_expense": monthly_expense
    }
