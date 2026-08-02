"""
Investment Portfolio Route
Full CRUD + portfolio summary with returns, XIRR-approximation, and
allocation breakdown by type.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Investment, User
from app.schemas import InvestmentCreate, InvestmentResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/investments", tags=["investments"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ─── GET portfolio summary ─────────────────────────────────────────────────────
@router.get("/summary")
def get_portfolio_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    investments = (
        db.query(Investment)
        .filter(Investment.user_id == current_user.id)
        .all()
    )

    total_invested = sum(i.invested_amount for i in investments)
    total_current = sum(i.current_value for i in investments)
    total_gain = total_current - total_invested
    gain_pct = (total_gain / total_invested * 100) if total_invested > 0 else 0.0

    # Allocation by type
    allocation: dict = {}
    for inv in investments:
        allocation[inv.investment_type] = allocation.get(inv.investment_type, 0.0) + inv.current_value

    # Top performer
    top = None
    if investments:
        def _return_pct(i):
            if i.invested_amount > 0:
                return (i.current_value - i.invested_amount) / i.invested_amount * 100
            return 0.0
        top = max(investments, key=_return_pct)

    return {
        "total_invested": round(total_invested, 2),
        "total_current_value": round(total_current, 2),
        "total_gain_loss": round(total_gain, 2),
        "overall_return_pct": round(gain_pct, 2),
        "allocation": {k: round(v, 2) for k, v in allocation.items()},
        "top_performer": {
            "name": top.name,
            "investment_type": top.investment_type,
            "return_pct": round(
                (top.current_value - top.invested_amount) / top.invested_amount * 100
                if top.invested_amount > 0 else 0.0, 2
            ),
        } if top else None,
        "count": len(investments),
    }


# ─── GET all investments ───────────────────────────────────────────────────────
@router.get("/", response_model=list[InvestmentResponse])
def list_investments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Investment)
        .filter(Investment.user_id == current_user.id)
        .order_by(Investment.purchase_date.desc())
        .all()
    )


# ─── CREATE ───────────────────────────────────────────────────────────────────
@router.post("/", response_model=InvestmentResponse)
def create_investment(
    data: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inv = Investment(
        user_id=current_user.id,
        name=data.name,
        investment_type=data.investment_type,
        invested_amount=data.invested_amount,
        current_value=data.current_value,
        units=data.units,
        purchase_price=data.purchase_price,
        current_price=data.current_price,
        purchase_date=data.purchase_date,
        notes=data.notes,
    )
    db.add(inv)
    db.commit()
    db.refresh(inv)
    return inv


# ─── UPDATE ───────────────────────────────────────────────────────────────────
@router.put("/{inv_id}", response_model=InvestmentResponse)
def update_investment(
    inv_id: int,
    data: InvestmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inv = db.query(Investment).filter(
        Investment.id == inv_id,
        Investment.user_id == current_user.id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")

    inv.name = data.name
    inv.investment_type = data.investment_type
    inv.invested_amount = data.invested_amount
    inv.current_value = data.current_value
    inv.units = data.units
    inv.purchase_price = data.purchase_price
    inv.current_price = data.current_price
    inv.purchase_date = data.purchase_date
    inv.notes = data.notes
    db.commit()
    db.refresh(inv)
    return inv


# ─── DELETE ───────────────────────────────────────────────────────────────────
@router.delete("/{inv_id}")
def delete_investment(
    inv_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    inv = db.query(Investment).filter(
        Investment.id == inv_id,
        Investment.user_id == current_user.id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Investment not found")
    db.delete(inv)
    db.commit()
    return {"detail": "Deleted"}
