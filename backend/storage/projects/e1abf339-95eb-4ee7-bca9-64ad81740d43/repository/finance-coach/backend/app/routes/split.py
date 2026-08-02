from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app import models, schemas
from app.services.auth import get_current_user

router = APIRouter(prefix="/splits", tags=["splits"])


@router.get("/", response_model=List[schemas.SharedExpenseResponse])
def get_splits(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(models.SharedExpense).filter(
        models.SharedExpense.user_id == current_user.id
    ).order_by(models.SharedExpense.created_at.desc()).all()


@router.post("/", response_model=schemas.SharedExpenseResponse)
def create_split(
    data: schemas.SharedExpenseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    split = models.SharedExpense(
        user_id=current_user.id,
        description=data.description,
        total_amount=data.total_amount,
        friend_name=data.friend_name,
        amount_owed=data.amount_owed,
        is_settled=False
    )
    db.add(split)
    db.commit()
    db.refresh(split)
    return split


@router.put("/{split_id}/settle", response_model=schemas.SharedExpenseResponse)
def settle_split(
    split_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    split = db.query(models.SharedExpense).filter(
        models.SharedExpense.id == split_id,
        models.SharedExpense.user_id == current_user.id
    ).first()
    if not split:
        raise HTTPException(status_code=404, detail="Split not found")
    split.is_settled = True
    db.commit()
    db.refresh(split)
    return split


@router.delete("/{split_id}")
def delete_split(
    split_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    split = db.query(models.SharedExpense).filter(
        models.SharedExpense.id == split_id,
        models.SharedExpense.user_id == current_user.id
    ).first()
    if not split:
        raise HTTPException(status_code=404, detail="Split not found")
    db.delete(split)
    db.commit()
    return {"detail": "Split expense deleted"}