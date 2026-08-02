from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Transaction, User
from app.services.auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def compute_new_regime_tax(taxable_income: float) -> dict:
    """
    Compute Indian Income Tax under New Regime (FY 2025-26).
    Slabs:
        0 – 3,00,000       : 0%
        3,00,001 – 7,00,000 : 5%
        7,00,001 – 10,00,000: 10%
        10,00,001 – 12,00,000: 15%
        12,00,001 – 15,00,000: 20%
        Above 15,00,000     : 30%
    Standard deduction: ₹75,000 (new regime FY25-26)
    """
    standard_deduction = 75_000.0
    net_taxable = max(0.0, taxable_income - standard_deduction)

    slabs = [
        (300_000,  0.00),
        (400_000,  0.05),
        (300_000,  0.10),
        (200_000,  0.15),
        (300_000,  0.20),
        (float("inf"), 0.30),
    ]

    tax = 0.0
    remaining = net_taxable
    slab_breakdown = []

    limits = [300_000, 700_000, 1_000_000, 1_200_000, 1_500_000]
    labels = ["₹0 – ₹3L", "₹3L – ₹7L", "₹7L – ₹10L", "₹10L – ₹12L", "₹12L – ₹15L", "Above ₹15L"]
    rates  = [0.0, 0.05, 0.10, 0.15, 0.20, 0.30]
    prev   = 0

    for i, (limit, rate) in enumerate(zip(limits + [None], rates)):
        if remaining <= 0:
            break
        if limit is not None:
            slab_size = limit - prev
        else:
            slab_size = remaining
        taxed = min(remaining, slab_size)
        slab_tax = taxed * rate
        tax += slab_tax
        if taxed > 0:
            slab_breakdown.append({
                "slab": labels[i],
                "rate": f"{int(rate * 100)}%",
                "income_in_slab": round(taxed, 2),
                "tax": round(slab_tax, 2)
            })
        remaining -= taxed
        if limit is not None:
            prev = limit

    # Rebate u/s 87A: If net taxable <= 7,00,000 → full rebate (no tax)
    rebate = 0.0
    if net_taxable <= 700_000:
        rebate = tax
        tax = 0.0

    # Health & Education cess: 4% on tax
    cess = tax * 0.04
    total_tax = tax + cess

    effective_rate = (total_tax / taxable_income * 100) if taxable_income > 0 else 0.0

    return {
        "gross_income": round(taxable_income, 2),
        "standard_deduction": standard_deduction,
        "net_taxable_income": round(net_taxable, 2),
        "rebate_87A": round(rebate, 2),
        "base_tax": round(tax, 2),
        "cess_4pct": round(cess, 2),
        "total_tax_liability": round(total_tax, 2),
        "effective_tax_rate": round(effective_rate, 2),
        "slab_breakdown": slab_breakdown,
        "regime": "New Regime FY 2025-26",
    }


@router.get("/tax/estimate")
def estimate_tax(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Estimates income tax for the logged-in user based on all income transactions.
    Uses Indian New Tax Regime slabs for FY 2025-26.
    """
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    total_income = sum(
        t.amount for t in transactions
        if t.transaction_type == "income" or t.category.lower() == "income"
    )

    tax_data = compute_new_regime_tax(total_income)

    monthly_avg = total_income / 12 if total_income > 0 else 0.0
    tax_data["monthly_avg_income"] = round(monthly_avg, 2)
    tax_data["total_transactions"] = len(transactions)

    tips = []
    if tax_data["total_tax_liability"] > 0:
        tips.append("Consider investing in NPS (National Pension System) under Section 80CCD(1B) for additional ₹50,000 deduction if switching to old regime.")
        tips.append("Tax-saving FDs, ELSS Mutual Funds, and PPF can help reduce taxable income under the old regime.")
    else:
        tips.append("Great news! Your income falls within the tax-free zone under the New Regime (rebate u/s 87A).")
        tips.append("Keep saving and investing to build long-term wealth tax-efficiently.")

    tax_data["tips"] = tips
    return tax_data
