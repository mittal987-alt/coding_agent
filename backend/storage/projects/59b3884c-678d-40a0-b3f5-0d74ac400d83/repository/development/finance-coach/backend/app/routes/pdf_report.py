"""
PDF Financial Health Report
Generates a professional multi-section PDF with:
  - Summary stats (income, expense, savings)
  - Budget vs actual per category
  - Savings goals progress
  - Active loans + EMI burden
  - Investment portfolio summary
  - Tax estimate
"""
import io
from datetime import date
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Transaction, Budget, SavingsGoal, Loan, Investment, User
from app.services.auth import get_current_user
from app.services.pdf_service import generate_pdf_reportlab, generate_fallback_html

router = APIRouter(prefix="/report", tags=["report"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/pdf")
def download_pdf_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Downloads a comprehensive PDF financial health report."""
    transactions = db.query(Transaction).filter(Transaction.user_id == current_user.id).all()
    budgets = db.query(Budget).filter(Budget.user_id == current_user.id).all()
    goals = db.query(SavingsGoal).filter(SavingsGoal.user_id == current_user.id).all()
    loans = db.query(Loan).filter(Loan.user_id == current_user.id).all()
    investments = db.query(Investment).filter(Investment.user_id == current_user.id).all()

    try:
        pdf_bytes = generate_pdf_reportlab(current_user, transactions, budgets, goals, loans, investments)
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=finance_report_{date.today()}.pdf"}
        )
    except ImportError:
        # reportlab not installed → return HTML
        html_bytes = generate_fallback_html(current_user, transactions, budgets, goals, loans, investments)
        return StreamingResponse(
            io.BytesIO(html_bytes),
            media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=finance_report_{date.today()}.html"}
        )
