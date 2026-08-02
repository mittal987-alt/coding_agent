from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date, timedelta
import calendar

from app.database import SessionLocal
from app.models import User, Account, SavingsGoal, SharedExpense, Investment, Transaction
from app.services.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/networth")
def get_net_worth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes the user's net worth:
    Assets  = Account balances + Savings Goals (current amounts saved)
    Liabilities = Unsettled shared expenses (money owed to user)
    Net Worth = Total Assets - Total Liabilities
    """
    # ── Assets ──────────────────────────────────────────────────
    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    account_total = sum(a.balance for a in accounts)

    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == current_user.id).all()
    goals_saved = sum(g.current_amount for g in goals)

    investments = db.query(Investment).filter(Investment.user_id == current_user.id).all()
    investments_total = sum(i.current_value for i in investments)

    total_assets = account_total + goals_saved + investments_total

    # ── Liabilities (money owed BY user to others via splits) ────
    # In our model, amount_owed = friend owes user. So liabilities = 0 from splits.
    # We treat total SharedExpense total_amount - amount_owed as user's share spent.
    shared_expenses = db.query(SharedExpense).filter(
        SharedExpense.user_id == current_user.id,
        SharedExpense.is_settled == False
    ).all()

    # User's share = total_amount - amount_owed (friend's share)
    user_share_unsettled = sum(
        max(0.0, s.total_amount - s.amount_owed) for s in shared_expenses
    )

    total_liabilities = user_share_unsettled

    net_worth = total_assets - total_liabilities

    # Breakdown for UI
    asset_breakdown = []
    for a in accounts:
        asset_breakdown.append({
            "name": a.name,
            "type": a.account_type,
            "amount": round(a.balance, 2),
            "category": "account"
        })
    for g in goals:
        if g.current_amount > 0:
            asset_breakdown.append({
                "name": g.name,
                "type": "Savings Goal",
                "amount": round(g.current_amount, 2),
                "category": "goal"
            })
    for inv in investments:
        if inv.current_value > 0:
            asset_breakdown.append({
                "name": inv.name,
                "type": inv.investment_type,
                "amount": round(inv.current_value, 2),
                "category": "investment"
            })

    liability_breakdown = []
    for s in shared_expenses:
        user_share = max(0.0, s.total_amount - s.amount_owed)
        if user_share > 0:
            liability_breakdown.append({
                "name": s.description,
                "type": "Unsettled Split",
                "amount": round(user_share, 2),
                "friend": s.friend_name,
                "category": "split"
            })

    return {
        "total_assets": round(total_assets, 2),
        "total_liabilities": round(total_liabilities, 2),
        "net_worth": round(net_worth, 2),
        "account_total": round(account_total, 2),
        "goals_saved": round(goals_saved, 2),
        "investments_total": round(investments_total, 2),
        "asset_breakdown": asset_breakdown,
        "liability_breakdown": liability_breakdown,
    }


@router.get("/networth/history")
def get_net_worth_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes a 6-month historical net worth trend dynamically by working backward
    from current account balances using transaction logs.
    """
    today = date.today()

    accounts = db.query(Account).filter(Account.user_id == current_user.id).all()
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == current_user.id).all()
    investments = db.query(Investment).filter(Investment.user_id == current_user.id).all()
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()

    # Calculate end dates for each of the last 6 months
    months = []
    curr = today
    for _ in range(6):
        last_day = calendar.monthrange(curr.year, curr.month)[1]
        months.append(date(curr.year, curr.month, last_day))

        # Move to previous month's end
        first_of_curr = curr.replace(day=1)
        prev_month_end = first_of_curr - timedelta(days=1)
        curr = prev_month_end

    months.reverse() # chronological order

    account_balances = {a.id: a.balance for a in accounts if a.id is not None}
    total_investments = sum(i.current_value for i in investments)
    total_goals = sum(g.current_amount for g in goals)

    sorted_txs = sorted(transactions, key=lambda t: t.transaction_date, reverse=True)
    months_desc = sorted(months, reverse=True)

    temp_balances = dict(account_balances)
    tx_index = 0
    history_map = {}

    for m_end in months_desc:
        # Undo transactions that occurred after this month's end
        while tx_index < len(sorted_txs):
            tx = sorted_txs[tx_index]
            tx_date = tx.transaction_date
            if isinstance(tx_date, str):
                try:
                    from datetime import datetime
                    tx_date = datetime.strptime(tx_date, "%Y-%m-%d").date()
                except ValueError:
                    tx_index += 1
                    continue

            if tx_date > m_end:
                if tx.account_id in temp_balances:
                    if tx.transaction_type == "income":
                        temp_balances[tx.account_id] -= tx.amount
                    else:
                        temp_balances[tx.account_id] += tx.amount
                tx_index += 1
            else:
                break

        assets = sum(temp_balances.values()) + total_investments + total_goals
        history_map[m_end.strftime("%b %Y")] = max(0.0, round(assets, 2))

    return [
        {"month": label, "net_worth": history_map.get(label, 0.0)}
        for label in [m.strftime("%b %Y") for m in months]
    ]
