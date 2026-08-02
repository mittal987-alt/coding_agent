from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
from datetime import datetime

from app.database import SessionLocal
from app.models import Transaction, User, Budget, SavingsGoal, UploadedDocument
from app.services.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


LEVELS = [
    (0,    "💰 Finance Newbie"),
    (100,  "📊 Budget Beginner"),
    (300,  "🏦 Savings Starter"),
    (600,  "💼 Money Manager"),
    (1000, "📈 Investment Pro"),
    (1500, "🏆 Finance Master"),
    (2500, "👑 Wealth Wizard"),
]

BADGES = [
    {
        "id": "first_transaction",
        "name": "First Step",
        "icon": "🎯",
        "description": "Logged your first transaction",
        "xp": 10
    },
    {
        "id": "ten_transactions",
        "name": "Getting Started",
        "icon": "📝",
        "description": "Logged 10+ transactions",
        "xp": 25
    },
    {
        "id": "fifty_transactions",
        "name": "Data Driven",
        "icon": "📊",
        "description": "Logged 50+ transactions",
        "xp": 75
    },
    {
        "id": "first_budget",
        "name": "Budget Setter",
        "icon": "💰",
        "description": "Created your first budget",
        "xp": 20
    },
    {
        "id": "all_budgets_met",
        "name": "Budget Champion",
        "icon": "🏆",
        "description": "Stayed within all budgets this month",
        "xp": 100
    },
    {
        "id": "first_goal",
        "name": "Goal Setter",
        "icon": "🎯",
        "description": "Created your first savings goal",
        "xp": 20
    },
    {
        "id": "goal_completed",
        "name": "Goal Crusher",
        "icon": "🌟",
        "description": "Completed a savings goal",
        "xp": 150
    },
    {
        "id": "saver_50pct",
        "name": "Super Saver",
        "icon": "💎",
        "description": "Saved 50%+ of income this month",
        "xp": 120
    },
    {
        "id": "pdf_uploaded",
        "name": "Statement Pro",
        "icon": "📄",
        "description": "Uploaded a bank statement PDF",
        "xp": 30
    },
    {
        "id": "streak_7",
        "name": "Week Warrior",
        "icon": "🔥",
        "description": "7-day spending streak tracked",
        "xp": 50
    },
    {
        "id": "streak_30",
        "name": "Monthly Master",
        "icon": "⚡",
        "description": "30-day consistent tracking streak",
        "xp": 200
    },
]


@router.get("/gamification/stats")
def get_gamification_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes XP, level, streak, and earned badges for the user.
    """
    today = date.today()
    current_month = today.strftime("%Y-%m")

    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == current_user.id).all()
    pdf_uploaded = db.query(UploadedDocument).filter(UploadedDocument.user_id == current_user.id).count() > 0

    total_tx = len(transactions)

    # Current month stats
    monthly_income = sum(
        t.amount for t in transactions
        if t.transaction_type == "income" and str(t.transaction_date)[:7] == current_month
    )
    monthly_expense = sum(
        t.amount for t in transactions
        if t.transaction_type == "expense" and str(t.transaction_date)[:7] == current_month
    )

    # Budget discipline check
    category_spend = {}
    for t in transactions:
        if t.transaction_type == "expense" and str(t.transaction_date)[:7] == current_month:
            category_spend[t.category] = category_spend.get(t.category, 0.0) + t.amount

    all_budgets_met = len(budgets) > 0 and all(
        category_spend.get(b.category, 0.0) <= b.amount for b in budgets
    )

    completed_goals = [g for g in goals if g.current_amount >= g.target_amount]
    savings_rate = (1 - monthly_expense / monthly_income) if monthly_income > 0 else 0.0

    # ── Streak Calculation ───────────────────────────────────────
    # Count consecutive days from today backwards that have any transaction
    tx_dates = set()
    for t in transactions:
        tx_date = t.transaction_date
        if isinstance(tx_date, str):
            try:
                tx_date = datetime.strptime(tx_date, "%Y-%m-%d").date()
            except ValueError:
                continue
        tx_dates.add(tx_date)

    streak = 0
    check_date = today
    while check_date in tx_dates:
        streak += 1
        check_date -= timedelta(days=1)

    # ── Badge Evaluation ─────────────────────────────────────────
    earned_badges = []
    total_xp = 0

    badge_conditions = {
        "first_transaction": total_tx >= 1,
        "ten_transactions": total_tx >= 10,
        "fifty_transactions": total_tx >= 50,
        "first_budget": len(budgets) >= 1,
        "all_budgets_met": all_budgets_met,
        "first_goal": len(goals) >= 1,
        "goal_completed": len(completed_goals) >= 1,
        "saver_50pct": savings_rate >= 0.5,
        "pdf_uploaded": pdf_uploaded,
        "streak_7": streak >= 7,
        "streak_30": streak >= 30,
    }

    for badge in BADGES:
        earned = badge_conditions.get(badge["id"], False)
        if earned:
            total_xp += badge["xp"]
        earned_badges.append({**badge, "earned": earned})

    # ── Level Calculation ────────────────────────────────────────
    current_level_name = LEVELS[0][1]
    next_level_xp = LEVELS[1][0]
    prev_level_xp = 0

    for i, (xp_threshold, level_name) in enumerate(LEVELS):
        if total_xp >= xp_threshold:
            current_level_name = level_name
            prev_level_xp = xp_threshold
            if i + 1 < len(LEVELS):
                next_level_xp = LEVELS[i + 1][0]
            else:
                next_level_xp = xp_threshold  # Max level

    xp_progress = total_xp - prev_level_xp
    xp_needed = next_level_xp - prev_level_xp
    progress_pct = min(100, round(xp_progress / xp_needed * 100)) if xp_needed > 0 else 100

    return {
        "total_xp": total_xp,
        "level": current_level_name,
        "next_level_xp": next_level_xp,
        "xp_progress": xp_progress,
        "xp_needed": xp_needed,
        "progress_pct": progress_pct,
        "streak_days": streak,
        "badges": earned_badges,
        "earned_badge_count": sum(1 for b in earned_badges if b["earned"]),
        "total_badge_count": len(BADGES),
        "stats": {
            "total_transactions": total_tx,
            "budgets_set": len(budgets),
            "goals_set": len(goals),
            "goals_completed": len(completed_goals),
            "savings_rate_pct": round(savings_rate * 100, 1)
        }
    }
