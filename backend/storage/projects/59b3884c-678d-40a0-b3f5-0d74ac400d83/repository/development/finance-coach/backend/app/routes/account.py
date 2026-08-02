from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.services.auth import get_current_user
from app.models import Transaction

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=List[schemas.AccountResponse])
def get_accounts(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.Account).filter(models.Account.user_id == current_user.id).all()


@router.post("/", response_model=schemas.AccountResponse)
def create_account(
    data: schemas.AccountCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account = models.Account(
        user_id=current_user.id,
        name=data.name,
        account_type=data.account_type,
        balance=data.balance
    )
    db.add(account)
    db.commit()
    db.refresh(account)
    return account


@router.put("/{account_id}", response_model=schemas.AccountResponse)
def update_account(
    account_id: int,
    data: schemas.AccountCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account = db.query(models.Account).filter(
        models.Account.id == account_id,
        models.Account.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    account.name = data.name
    account.account_type = data.account_type
    account.balance = data.balance
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}")
def delete_account(
    account_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    account = db.query(models.Account).filter(
        models.Account.id == account_id,
        models.Account.user_id == current_user.id
    ).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # Unlink transactions so the FK constraint is not violated
    db.query(Transaction).filter(
        Transaction.account_id == account_id,
        Transaction.user_id == current_user.id
    ).update({"account_id": None}, synchronize_session=False)

    db.delete(account)
    db.commit()
    return {"detail": "Account deleted"}