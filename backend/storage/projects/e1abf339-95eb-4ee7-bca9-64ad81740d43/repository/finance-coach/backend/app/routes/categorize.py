from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from app.models import Category, User
from app.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.auth import get_current_user

router = APIRouter()

# Seeded the first time a user fetches their categories with none yet.
# These mirror the category options that used to be hardcoded across the
# app (transaction modal, budgets, subscriptions, reminders, recurring).
DEFAULT_CATEGORIES = [
    ("Food", "#0F6E56"),
    ("Travel", "#BA7517"),
    ("Shopping", "#378ADD"),
    ("Fuel", "#D85A30"),
    ("UPI", "#7C6FDB"),
    ("Cash", "#7C8B6F"),
    ("Income", "#0F6E56"),
    ("Utilities", "#5B8FA8"),
    ("Entertainment", "#B0522D"),
    ("Rent", "#8B5E3C"),
    ("Credit Card", "#C24E28"),
    ("Insurance", "#4E6E8E"),
    ("Subscription", "#7C6FDB"),
    ("Others", "#8A8F98"),
]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    categories = (
        db.query(Category)
        .filter(Category.user_id == current_user.id)
        .order_by(Category.name)
        .all()
    )

    if not categories:
        for name, color in DEFAULT_CATEGORIES:
            db.add(Category(user_id=current_user.id, name=name, color=color))
        db.commit()
        categories = (
            db.query(Category)
            .filter(Category.user_id == current_user.id)
            .order_by(Category.name)
            .all()
        )

    return categories


@router.post("/categories", response_model=CategoryResponse)
def create_category(
    data: CategoryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    existing = (
        db.query(Category)
        .filter(
            Category.user_id == current_user.id,
            Category.name.ilike(data.name.strip())
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="A category with this name already exists")

    category = Category(
        user_id=current_user.id,
        name=data.name.strip(),
        color=data.color or "#8a8f98"
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    data: CategoryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    if data.name is not None:
        category.name = data.name.strip()
    if data.color is not None:
        category.color = data.color

    db.commit()
    db.refresh(category)
    return category


@router.delete("/categories/{category_id}")
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a category from the user's list. This does NOT touch any
    existing transactions/budgets/subscriptions/reminders already tagged
    with this category's name -- those fields are plain strings, so they
    simply keep displaying the old label even after it's removed from
    the manageable list.
    """
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"message": "Category deleted"}