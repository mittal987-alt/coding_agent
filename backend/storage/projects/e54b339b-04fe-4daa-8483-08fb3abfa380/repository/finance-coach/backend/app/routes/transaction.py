from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from app.database import SessionLocal
from app.models import Transaction, User, Account
from app.schemas import TransactionCreate, TransactionUpdate, BulkTransactionIds, BulkRecategorize
from app.services.auth import get_current_user
from app.services.currency_service import convert_currency_logic
from app.services.embeddings import get_embedding
import json

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_owned_account(db: Session, account_id: int, user_id: int) -> Account:
    account = db.query(Account).filter(
        Account.id == account_id,
        Account.user_id == user_id
    ).first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return account


def _apply_to_balance(account: Account, amount: float, transaction_type: str) -> None:
    """Income adds to the account balance, expense subtracts from it.
    `amount` is always the INR-converted value -- accounts are always INR."""
    if transaction_type == "income":
        account.balance += amount
    else:
        account.balance -= amount


def _reverse_from_balance(account: Account, amount: float, transaction_type: str) -> None:
    """Undoes a previously-applied transaction's effect on the balance."""
    if transaction_type == "income":
        account.balance -= amount
    else:
        account.balance += amount


async def _resolve_currency(amount: float, currency: Optional[str]):
    """
    Given an amount entered in `currency`, returns the tuple used to store
    the transaction: (amount_in_inr, currency, original_amount, exchange_rate).
    INR is the app's home currency -- everything downstream (budgets, goals,
    account balances, dashboards) assumes `amount` is INR.
    """
    currency = (currency or "INR").upper()
    if currency == "INR":
        return amount, "INR", None, 1.0

    result = await convert_currency_logic(amount, currency, "INR")
    return result["converted"], currency, amount, result["rate"]


@router.get("/transactions")
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
        .all()
    )


@router.post("/transactions")
async def create_transaction(
    tx_data: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    final_amount, currency, original_amount, exchange_rate = await _resolve_currency(
        tx_data.amount, tx_data.currency
    )

    new_tx = Transaction(
        user_id=current_user.id,
        transaction_date=tx_data.transaction_date,
        description=tx_data.description,
        amount=final_amount,
        currency=currency,
        original_amount=original_amount,
        exchange_rate=exchange_rate,
        category=tx_data.category,
        transaction_type=tx_data.transaction_type,
        account_id=tx_data.account_id,
        receipt_image_url=tx_data.receipt_image_url,
    )
    
    embed_text = f"Date: {new_tx.transaction_date}, Desc: {new_tx.description}, Amt: {new_tx.amount}, Cat: {new_tx.category}, Type: {new_tx.transaction_type}"
    embedding_vector = await get_embedding(embed_text)
    if embedding_vector:
        new_tx.embedding = json.dumps(embedding_vector)

    db.add(new_tx)

    if tx_data.account_id is not None:
        account = _get_owned_account(db, tx_data.account_id, current_user.id)
        _apply_to_balance(account, final_amount, tx_data.transaction_type)

    db.commit()
    db.refresh(new_tx)
    return new_tx


@router.delete("/transactions/bulk")
def bulk_delete_transactions(
    data: BulkTransactionIds,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deletes multiple transactions at once, reversing each one's effect
    on its linked account (if any) exactly like a single delete would."""
    txs = db.query(Transaction).filter(
        Transaction.id.in_(data.ids),
        Transaction.user_id == current_user.id
    ).all()

    for tx in txs:
        if tx.account_id is not None:
            account = db.query(Account).filter(
                Account.id == tx.account_id,
                Account.user_id == current_user.id
            ).first()
            if account:
                _reverse_from_balance(account, tx.amount, tx.transaction_type)
        db.delete(tx)

    db.commit()
    return {"deleted": len(txs)}


@router.put("/transactions/bulk/category")
def bulk_recategorize_transactions(
    data: BulkRecategorize,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sets the same category on multiple transactions at once. Doesn't
    touch amount/account/type, so no balance recalculation is needed."""
    txs = db.query(Transaction).filter(
        Transaction.id.in_(data.ids),
        Transaction.user_id == current_user.id
    ).all()

    for tx in txs:
        tx.category = data.category

    db.commit()
    return {"updated": len(txs)}


@router.put("/transactions/{tx_id}")
async def update_transaction(
    tx_id: int,
    tx_data: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == tx_id, Transaction.user_id == current_user.id)
        .first()
    )

    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Undo this transaction's old effect on whichever account it used to be linked to.
    # tx.amount is always already INR, so no conversion needed to reverse it.
    if tx.account_id is not None:
        old_account = db.query(Account).filter(
            Account.id == tx.account_id,
            Account.user_id == current_user.id
        ).first()
        if old_account:
            _reverse_from_balance(old_account, tx.amount, tx.transaction_type)

    final_amount, currency, original_amount, exchange_rate = await _resolve_currency(
        tx_data.amount, tx_data.currency
    )

    tx.transaction_date = tx_data.transaction_date
    tx.description = tx_data.description
    tx.amount = final_amount
    tx.currency = currency
    tx.original_amount = original_amount
    tx.exchange_rate = exchange_rate
    tx.category = tx_data.category
    tx.transaction_type = tx_data.transaction_type
    tx.account_id = tx_data.account_id

    embed_text = f"Date: {tx.transaction_date}, Desc: {tx.description}, Amt: {tx.amount}, Cat: {tx.category}, Type: {tx.transaction_type}"
    embedding_vector = await get_embedding(embed_text)
    if embedding_vector:
        tx.embedding = json.dumps(embedding_vector)

    # Apply the (possibly new) transaction to whichever account it's now linked to
    if tx_data.account_id is not None:
        new_account = _get_owned_account(db, tx_data.account_id, current_user.id)
        _apply_to_balance(new_account, final_amount, tx_data.transaction_type)

    db.commit()
    db.refresh(tx)
    return tx


@router.delete("/transactions/{tx_id}")
def delete_transaction(
    tx_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    tx = (
        db.query(Transaction)
        .filter(Transaction.id == tx_id, Transaction.user_id == current_user.id)
        .first()
    )

    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    if tx.account_id is not None:
        account = db.query(Account).filter(
            Account.id == tx.account_id,
            Account.user_id == current_user.id
        ).first()
        if account:
            _reverse_from_balance(account, tx.amount, tx.transaction_type)

    db.delete(tx)
    db.commit()
    return {"message": "Transaction deleted successfully"}


@router.post("/seed")
def seed(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    t1 = Transaction(
        user_id=current_user.id,
        transaction_date=date(2026, 6, 1),
        description="Salary",
        amount=50000,
        category="Income",
        transaction_type="income"
    )

    t2 = Transaction(
        user_id=current_user.id,
        transaction_date=date(2026, 6, 3),
        description="Amazon",
        amount=2500,
        category="Shopping",
        transaction_type="expense"
    )

    t3 = Transaction(
        user_id=current_user.id,
        transaction_date=date(2026, 6, 5),
        description="Zomato",
        amount=600,
        category="Food",
        transaction_type="expense"
    )

    db.add(t1)
    db.add(t2)
    db.add(t3)

    db.commit()

    return {
        "message": "Transactions inserted successfully"
    }