from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models import Budget, User
from app.schemas import BudgetCreate, BudgetResponse
from app.services.auth import get_current_user
from app.services.embeddings import get_embedding
import json

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/budgets", response_model=List[BudgetResponse])
def get_budgets(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id)
        .all()
    )


@router.post("/budgets", response_model=BudgetResponse)
async def set_budget(
    budget_data: BudgetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if budget already exists for this category
    existing_budget = (
        db.query(Budget)
        .filter(
            Budget.user_id == current_user.id,
            Budget.category == budget_data.category
        )
        .first()
    )

    if existing_budget:
        existing_budget.amount = budget_data.amount
        
        embed_text = f"Category: {existing_budget.category}, Budget Limit: {existing_budget.amount}"
        embedding_vector = await get_embedding(embed_text)
        if embedding_vector:
            existing_budget.embedding = json.dumps(embedding_vector)

        db.commit()
        db.refresh(existing_budget)
        return existing_budget

    new_budget = Budget(
        user_id=current_user.id,
        category=budget_data.category,
        amount=budget_data.amount
    )
    
    embed_text = f"Category: {new_budget.category}, Budget Limit: {new_budget.amount}"
    embedding_vector = await get_embedding(embed_text)
    if embedding_vector:
        new_budget.embedding = json.dumps(embedding_vector)

    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget


@router.delete("/budgets/{budget_id}")
def delete_budget(
    budget_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    budget = (
        db.query(Budget)
        .filter(Budget.id == budget_id, Budget.user_id == current_user.id)
        .first()
    )

    if not budget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Budget not found"
        )

    db.delete(budget)
    db.commit()
    return {"message": "Budget deleted successfully"}
