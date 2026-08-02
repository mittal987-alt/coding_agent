"""
Full data export / backup.
Pulls every table scoped to the logged-in user into one JSON payload the
frontend downloads as a file. Read-only -- no import/restore yet.
"""
from datetime import datetime
import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import (
    User, Transaction, Budget, SavingsGoal, Subscription, Account,
    SharedExpense, PaymentReminder, RecurringTransaction, Investment,
    Loan, Category,
)
from app.services.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _dump(rows, fields):
    return [{f: getattr(row, f) for f in fields} for row in rows]


@router.get("/backup/export")
def export_backup(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = current_user.id

    accounts = db.query(Account).filter(Account.user_id == user_id).all()
    transactions = db.query(Transaction).filter(Transaction.user_id == user_id).all()
    budgets = db.query(Budget).filter(Budget.user_id == user_id).all()
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).all()
    subscriptions = db.query(Subscription).filter(Subscription.user_id == user_id).all()
    shared_expenses = db.query(SharedExpense).filter(SharedExpense.user_id == user_id).all()
    reminders = db.query(PaymentReminder).filter(PaymentReminder.user_id == user_id).all()
    recurring = db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id).all()
    investments = db.query(Investment).filter(Investment.user_id == user_id).all()
    loans = db.query(Loan).filter(Loan.user_id == user_id).all()
    categories = db.query(Category).filter(Category.user_id == user_id).all()

    return {
        "exported_at": datetime.utcnow().isoformat(),
        "app": "Finance AI Coach",
        "user": {"name": current_user.name, "email": current_user.email},

        "accounts": _dump(accounts, ["id", "name", "account_type", "balance"]),

        "transactions": _dump(transactions, [
            "id", "transaction_date", "description", "amount", "currency",
            "original_amount", "exchange_rate", "category", "transaction_type", "account_id"
        ]),

        "budgets": _dump(budgets, ["id", "category", "amount"]),

        "savings_goals": _dump(goals, [
            "id", "name", "target_amount", "current_amount", "target_date"
        ]),

        "subscriptions": _dump(subscriptions, [
            "id", "name", "amount", "category", "billing_cycle", "next_due_date"
        ]),

        "shared_expenses": _dump(shared_expenses, [
            "id", "description", "total_amount", "friend_name", "amount_owed", "is_settled"
        ]),

        "payment_reminders": _dump(reminders, [
            "id", "name", "amount", "due_date", "category", "is_paid",
            "is_recurring", "recurrence_frequency"
        ]),

        "recurring_transactions": _dump(recurring, [
            "id", "description", "amount", "currency", "original_amount",
            "exchange_rate", "category", "transaction_type", "frequency",
            "next_date", "is_active"
        ]),

        "investments": _dump(investments, [
            "id", "name", "investment_type", "invested_amount", "current_value",
            "units", "purchase_price", "current_price", "purchase_date", "notes"
        ]),

        "loans": _dump(loans, [
            "id", "name", "loan_type", "principal_amount", "interest_rate",
            "tenure_months", "start_date", "emi_amount", "outstanding_amount",
            "lender_name", "is_active"
        ]),

        "categories": _dump(categories, ["id", "name", "color"]),
    }


@router.post("/backup/import")
def import_backup(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        contents = file.file.read()
        data = json.loads(contents.decode("utf-8"))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON file format.")
    
    if data.get("app") != "Finance AI Coach":
        raise HTTPException(status_code=400, detail="Invalid backup file: wrong app signature.")
        
    user_id = current_user.id
    
    # 1. Clear existing data for this user
    db.query(Transaction).filter(Transaction.user_id == user_id).delete()
    db.query(Budget).filter(Budget.user_id == user_id).delete()
    db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).delete()
    db.query(Subscription).filter(Subscription.user_id == user_id).delete()
    db.query(SharedExpense).filter(SharedExpense.user_id == user_id).delete()
    db.query(PaymentReminder).filter(PaymentReminder.user_id == user_id).delete()
    db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id).delete()
    db.query(Investment).filter(Investment.user_id == user_id).delete()
    db.query(Loan).filter(Loan.user_id == user_id).delete()
    db.query(Category).filter(Category.user_id == user_id).delete()
    # Delete accounts last because transactions have foreign key to accounts
    db.query(Account).filter(Account.user_id == user_id).delete()
    
    db.commit()
    
    # 2. Restore Accounts and build mapping (old_id -> new_id)
    account_map = {}
    if "accounts" in data:
        for acc_data in data["accounts"]:
            old_id = acc_data.get("id")
            new_acc = Account(
                user_id=user_id,
                name=acc_data.get("name"),
                account_type=acc_data.get("account_type"),
                balance=acc_data.get("balance", 0.0)
            )
            db.add(new_acc)
            db.flush() # Generate ID without committing
            if old_id is not None:
                account_map[old_id] = new_acc.id
                
    # 3. Restore Categories
    if "categories" in data:
        for cat_data in data["categories"]:
            new_cat = Category(
                user_id=user_id,
                name=cat_data.get("name"),
                color=cat_data.get("color", "#8a8f98")
            )
            db.add(new_cat)
            
    # 4. Restore Budgets
    if "budgets" in data:
        for b_data in data["budgets"]:
            new_b = Budget(
                user_id=user_id,
                category=b_data.get("category"),
                amount=b_data.get("amount")
            )
            db.add(new_b)
            
    # 5. Restore Savings Goals
    if "savings_goals" in data:
        for sg_data in data["savings_goals"]:
            new_sg = SavingsGoal(
                user_id=user_id,
                name=sg_data.get("name"),
                target_amount=sg_data.get("target_amount"),
                current_amount=sg_data.get("current_amount", 0.0),
                target_date=datetime.strptime(sg_data.get("target_date"), "%Y-%m-%d").date() if sg_data.get("target_date") else None
            )
            db.add(new_sg)
            
    # 6. Restore Subscriptions
    if "subscriptions" in data:
        for sub_data in data["subscriptions"]:
            new_sub = Subscription(
                user_id=user_id,
                name=sub_data.get("name"),
                amount=sub_data.get("amount"),
                category=sub_data.get("category"),
                billing_cycle=sub_data.get("billing_cycle"),
                next_due_date=datetime.strptime(sub_data.get("next_due_date"), "%Y-%m-%d").date() if sub_data.get("next_due_date") else None
            )
            db.add(new_sub)
            
    # 7. Restore Shared Expenses
    if "shared_expenses" in data:
        for se_data in data["shared_expenses"]:
            new_se = SharedExpense(
                user_id=user_id,
                description=se_data.get("description"),
                total_amount=se_data.get("total_amount"),
                friend_name=se_data.get("friend_name"),
                amount_owed=se_data.get("amount_owed"),
                is_settled=se_data.get("is_settled", False)
            )
            db.add(new_se)
            
    # 8. Restore Payment Reminders
    if "payment_reminders" in data:
        for pr_data in data["payment_reminders"]:
            new_pr = PaymentReminder(
                user_id=user_id,
                name=pr_data.get("name"),
                amount=pr_data.get("amount"),
                due_date=datetime.strptime(pr_data.get("due_date"), "%Y-%m-%d").date() if pr_data.get("due_date") else None,
                category=pr_data.get("category", "Others"),
                is_paid=pr_data.get("is_paid", False),
                is_recurring=pr_data.get("is_recurring", False),
                recurrence_frequency=pr_data.get("recurrence_frequency")
            )
            db.add(new_pr)
            
    # 9. Restore Recurring Transactions
    if "recurring_transactions" in data:
        for rt_data in data["recurring_transactions"]:
            new_rt = RecurringTransaction(
                user_id=user_id,
                description=rt_data.get("description"),
                amount=rt_data.get("amount"),
                currency=rt_data.get("currency", "INR"),
                original_amount=rt_data.get("original_amount"),
                exchange_rate=rt_data.get("exchange_rate", 1.0),
                category=rt_data.get("category"),
                transaction_type=rt_data.get("transaction_type"),
                frequency=rt_data.get("frequency"),
                next_date=datetime.strptime(rt_data.get("next_date"), "%Y-%m-%d").date() if rt_data.get("next_date") else None,
                is_active=rt_data.get("is_active", True)
            )
            db.add(new_rt)
            
    # 10. Restore Investments
    if "investments" in data:
        for inv_data in data["investments"]:
            new_inv = Investment(
                user_id=user_id,
                name=inv_data.get("name"),
                investment_type=inv_data.get("investment_type"),
                invested_amount=inv_data.get("invested_amount"),
                current_value=inv_data.get("current_value"),
                units=inv_data.get("units"),
                purchase_price=inv_data.get("purchase_price"),
                current_price=inv_data.get("current_price"),
                purchase_date=datetime.strptime(inv_data.get("purchase_date"), "%Y-%m-%d").date() if inv_data.get("purchase_date") else None,
                notes=inv_data.get("notes")
            )
            db.add(new_inv)
            
    # 11. Restore Loans
    if "loans" in data:
        for loan_data in data["loans"]:
            new_loan = Loan(
                user_id=user_id,
                name=loan_data.get("name"),
                loan_type=loan_data.get("loan_type"),
                principal_amount=loan_data.get("principal_amount"),
                interest_rate=loan_data.get("interest_rate"),
                tenure_months=loan_data.get("tenure_months"),
                start_date=datetime.strptime(loan_data.get("start_date"), "%Y-%m-%d").date() if loan_data.get("start_date") else None,
                emi_amount=loan_data.get("emi_amount"),
                outstanding_amount=loan_data.get("outstanding_amount"),
                lender_name=loan_data.get("lender_name"),
                is_active=loan_data.get("is_active", True)
            )
            db.add(new_loan)
            
    # 12. Restore Transactions with mapped account_id
    if "transactions" in data:
        for tx_data in data["transactions"]:
            old_acc_id = tx_data.get("account_id")
            new_acc_id = account_map.get(old_acc_id) if old_acc_id is not None else None
            new_tx = Transaction(
                user_id=user_id,
                transaction_date=datetime.strptime(tx_data.get("transaction_date"), "%Y-%m-%d").date() if tx_data.get("transaction_date") else None,
                description=tx_data.get("description"),
                amount=tx_data.get("amount"),
                currency=tx_data.get("currency", "INR"),
                original_amount=tx_data.get("original_amount"),
                exchange_rate=tx_data.get("exchange_rate", 1.0),
                category=tx_data.get("category"),
                transaction_type=tx_data.get("transaction_type"),
                account_id=new_acc_id
            )
            db.add(new_tx)

    db.commit()
    return {"success": True, "message": "Backup data successfully imported and restored."}