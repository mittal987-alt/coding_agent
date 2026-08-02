from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date
import calendar
from typing import List
from pydantic import BaseModel

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


@router.get("/budget/plan")
def get_budget_plan(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Analyzes last month's spending per category and generates AI-suggested
    budgets for next month:
    - Overspent categories: suggest 10% reduction from actual
    - Under-budget categories: suggest 5% growth from budget limit
    - Unbudgeted categories: suggest capping at actual spend
    """
    today = date.today()

    # Last month calculation
    if today.month == 1:
        last_month_year = today.year - 1
        last_month = 12
    else:
        last_month_year = today.year
        last_month = today.month - 1

    last_month_str = f"{last_month_year}-{last_month:02d}"

    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()

    budget_map = {b.category: b.amount for b in budgets}

    # Compute last-month actuals per category
    last_month_spend = {}
    last_month_income = 0.0
    for t in transactions:
        tx_date_str = str(t.transaction_date)[:7]
        if tx_date_str == last_month_str:
            if t.transaction_type == "income":
                last_month_income += t.amount
            else:
                last_month_spend[t.category] = last_month_spend.get(t.category, 0.0) + t.amount

    # All unique categories (from budget + from last month)
    all_categories = set(budget_map.keys()) | set(last_month_spend.keys())
    all_categories.discard("income")
    all_categories.discard("Income")

    plan = []
    for cat in sorted(all_categories):
        actual = last_month_spend.get(cat, 0.0)
        budget_limit = budget_map.get(cat, 0.0)

        if budget_limit > 0 and actual > budget_limit:
            # Overspent: suggest cutting 10% from actual
            suggested = round(actual * 0.90, 2)
            status = "overspent"
            advice = f"You overspent by ₹{actual - budget_limit:,.0f}. Aim to cut 10%."
        elif budget_limit > 0 and actual <= budget_limit:
            # Under budget: suggest 5% growth from current limit
            suggested = round(budget_limit * 1.05, 2)
            status = "under_budget"
            advice = f"Well within budget. Slight growth of 5% suggested."
        else:
            # No existing budget: cap at actual spend
            suggested = round(actual, 2)
            status = "unbudgeted"
            advice = f"No budget set. Suggesting to cap at last month's actual."

        plan.append({
            "category": cat,
            "last_month_actual": round(actual, 2),
            "current_budget": round(budget_limit, 2),
            "suggested_budget": suggested,
            "status": status,
            "advice": advice
        })

    # Sort: overspent first, then unbudgeted, then under_budget
    order = {"overspent": 0, "unbudgeted": 1, "under_budget": 2}
    plan.sort(key=lambda x: order.get(x["status"], 3))

    total_suggested = sum(p["suggested_budget"] for p in plan)
    savings_buffer = last_month_income - total_suggested if last_month_income > 0 else 0.0

    return {
        "last_month": f"{calendar.month_name[last_month]} {last_month_year}",
        "last_month_income": round(last_month_income, 2),
        "plan": plan,
        "total_suggested_budget": round(total_suggested, 2),
        "projected_savings": round(savings_buffer, 2),
    }


# ─── Apply suggested plan: bulk-upsert budgets ────────────────────────────────
class BudgetEntry(BaseModel):
    category: str
    suggested_budget: float


class ApplyPlanRequest(BaseModel):
    plan: List[BudgetEntry]


@router.post("/budget/plan/apply")
def apply_budget_plan(
    body: ApplyPlanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bulk-applies the AI-suggested budget plan.
    For each category in the plan:
      - If a budget already exists for that category, update its amount.
      - Otherwise, create a new budget row.
    """
    upserted = 0
    for entry in body.plan:
        existing = (
            db.query(Budget)
            .filter(Budget.user_id == current_user.id, Budget.category == entry.category)
            .first()
        )
        if existing:
            existing.amount = entry.suggested_budget
        else:
            db.add(Budget(
                user_id=current_user.id,
                category=entry.category,
                amount=entry.suggested_budget
            ))
        upserted += 1

    db.commit()
    return {
        "message": f"Applied {upserted} budget(s) from plan.",
        "upserted": upserted
    }
