"""
Loan / EMI Tracker Route
CRUD + amortization schedule + dashboard summary (total outstanding, monthly EMI burden).
"""
import math
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Loan, User
from app.schemas import LoanCreate, LoanResponse
from app.services.auth import get_current_user

router = APIRouter(prefix="/loans", tags=["loans"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _compute_emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Standard reducing-balance EMI formula."""
    if annual_rate == 0:
        return round(principal / tenure_months, 2)
    r = annual_rate / 12 / 100  # monthly rate
    emi = principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)
    return round(emi, 2)


def _amortization(principal: float, annual_rate: float, tenure_months: int, start: date):
    """Returns list of monthly amortization rows."""
    if annual_rate == 0:
        emi = round(principal / tenure_months, 2)
        balance = principal
        rows = []
        for i in range(1, tenure_months + 1):
            interest = 0.0
            principal_paid = min(emi, balance)
            balance = max(0.0, balance - principal_paid)
            rows.append({
                "month": i,
                "emi": emi,
                "principal_paid": round(principal_paid, 2),
                "interest_paid": 0.0,
                "balance": round(balance, 2),
            })
        return rows

    r = annual_rate / 12 / 100
    emi = _compute_emi(principal, annual_rate, tenure_months)
    balance = principal
    rows = []
    for i in range(1, tenure_months + 1):
        interest = round(balance * r, 2)
        principal_paid = round(emi - interest, 2)
        balance = max(0.0, round(balance - principal_paid, 2))
        rows.append({
            "month": i,
            "emi": emi,
            "principal_paid": principal_paid,
            "interest_paid": interest,
            "balance": balance,
        })
    return rows


# ─── GET summary ───────────────────────────────────────────────────────────────
@router.get("/summary")
def get_loan_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    loans = db.query(Loan).filter(
        Loan.user_id == current_user.id,
        Loan.is_active == True
    ).all()

    total_outstanding = sum(l.outstanding_amount for l in loans)
    monthly_emi_burden = sum(l.emi_amount for l in loans)
    total_principal = sum(l.principal_amount for l in loans)
    total_paid = total_principal - total_outstanding

    return {
        "active_loans": len(loans),
        "total_outstanding": round(total_outstanding, 2),
        "monthly_emi_burden": round(monthly_emi_burden, 2),
        "total_principal": round(total_principal, 2),
        "total_paid_so_far": round(total_paid, 2),
    }


# ─── GET all loans ─────────────────────────────────────────────────────────────
@router.get("/", response_model=list[LoanResponse])
def list_loans(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return (
        db.query(Loan)
        .filter(Loan.user_id == current_user.id)
        .order_by(Loan.start_date.desc())
        .all()
    )


# ─── CREATE ───────────────────────────────────────────────────────────────────
@router.post("/", response_model=LoanResponse)
def create_loan(
    data: LoanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Auto-compute EMI if not provided properly
    emi = data.emi_amount or _compute_emi(data.principal_amount, data.interest_rate, data.tenure_months)
    loan = Loan(
        user_id=current_user.id,
        name=data.name,
        loan_type=data.loan_type,
        principal_amount=data.principal_amount,
        interest_rate=data.interest_rate,
        tenure_months=data.tenure_months,
        start_date=data.start_date,
        emi_amount=emi,
        outstanding_amount=data.outstanding_amount,
        lender_name=data.lender_name,
        is_active=data.is_active,
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan


# ─── UPDATE ───────────────────────────────────────────────────────────────────
@router.put("/{loan_id}", response_model=LoanResponse)
def update_loan(
    loan_id: int,
    data: LoanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.user_id == current_user.id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    loan.name = data.name
    loan.loan_type = data.loan_type
    loan.principal_amount = data.principal_amount
    loan.interest_rate = data.interest_rate
    loan.tenure_months = data.tenure_months
    loan.start_date = data.start_date
    loan.emi_amount = data.emi_amount or _compute_emi(data.principal_amount, data.interest_rate, data.tenure_months)
    loan.outstanding_amount = data.outstanding_amount
    loan.lender_name = data.lender_name
    loan.is_active = data.is_active
    db.commit()
    db.refresh(loan)
    return loan


# ─── DELETE ───────────────────────────────────────────────────────────────────
@router.delete("/{loan_id}")
def delete_loan(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.user_id == current_user.id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    db.delete(loan)
    db.commit()
    return {"detail": "Deleted"}


# ─── GET amortization schedule ────────────────────────────────────────────────
@router.get("/{loan_id}/schedule")
def get_amortization_schedule(
    loan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.user_id == current_user.id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    schedule = _amortization(
        loan.principal_amount,
        loan.interest_rate,
        loan.tenure_months,
        loan.start_date,
    )
    total_interest = sum(row["interest_paid"] for row in schedule)
    return {
        "loan_name": loan.name,
        "emi": loan.emi_amount,
        "total_interest_outflow": round(total_interest, 2),
        "total_repayment": round(loan.principal_amount + total_interest, 2),
        "schedule": schedule,
    }


# ─── EMI Calculator (no auth, utility endpoint) ───────────────────────────────
@router.get("/calculate-emi")
def calculate_emi(principal: float, annual_rate: float, tenure_months: int):
    emi = _compute_emi(principal, annual_rate, tenure_months)
    r = annual_rate / 12 / 100
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    return {
        "emi": emi,
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "principal": principal,
    }


# ─── Debt Payoff Simulator (Snowball vs Avalanche) ────────────────────────────
@router.get("/payoff-simulation")
def payoff_simulation(
    extra_payment: float = 0.0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Compare Snowball (smallest balance first) vs Avalanche (highest rate first)
    strategies for paying off all active loans with an optional extra monthly payment.
    Returns month-by-month balance data for charting.
    """
    loans = db.query(Loan).filter(
        Loan.user_id == current_user.id,
        Loan.is_active == True,
    ).all()

    if not loans:
        return {"months": 0, "strategies": {}}

    def simulate(strategy: str):
        # Work with mutable copies
        debts = [
            {
                "name": l.name,
                "balance": l.outstanding_amount,
                "rate": l.interest_rate,
                "min_payment": l.emi_amount,
            }
            for l in loans
        ]

        # Sort order determines which debt gets the extra payment
        if strategy == "snowball":
            debts.sort(key=lambda d: d["balance"])
        else:  # avalanche
            debts.sort(key=lambda d: d["rate"], reverse=True)

        total_min = sum(d["min_payment"] for d in debts)
        months_elapsed = 0
        total_interest = 0.0
        # Chart data: list of total remaining balance per month
        balance_over_time = []

        while any(d["balance"] > 0 for d in debts) and months_elapsed < 600:
            months_elapsed += 1
            extra_left = extra_payment

            for debt in debts:
                if debt["balance"] <= 0:
                    continue
                monthly_rate = debt["rate"] / 12 / 100
                interest = round(debt["balance"] * monthly_rate, 2)
                total_interest += interest

                payment = debt["min_payment"] + extra_left
                extra_left = 0  # extra goes to first debt in priority

                if payment >= debt["balance"] + interest:
                    # Loan paid off — redirect leftover to next
                    extra_left = payment - (debt["balance"] + interest)
                    debt["balance"] = 0.0
                else:
                    debt["balance"] = round(debt["balance"] + interest - payment, 2)

            total_remaining = sum(d["balance"] for d in debts)
            balance_over_time.append(round(total_remaining, 2))

        return {
            "months_to_payoff": months_elapsed,
            "total_interest_paid": round(total_interest, 2),
            "total_paid": round(
                sum(l.outstanding_amount for l in loans) + total_interest, 2
            ),
            "payoff_date": (
                __import__("datetime").date.today()
                + __import__("datetime").timedelta(days=months_elapsed * 30)
            ).isoformat(),
            "balance_over_time": balance_over_time,
        }

    snowball = simulate("snowball")
    avalanche = simulate("avalanche")

    interest_saved = round(snowball["total_interest_paid"] - avalanche["total_interest_paid"], 2)
    months_saved = snowball["months_to_payoff"] - avalanche["months_to_payoff"]

    return {
        "loan_count": len(loans),
        "total_outstanding": round(sum(l.outstanding_amount for l in loans), 2),
        "extra_payment": extra_payment,
        "snowball": snowball,
        "avalanche": avalanche,
        "avalanche_advantage": {
            "interest_saved": interest_saved,
            "months_saved": months_saved,
        },
    }
