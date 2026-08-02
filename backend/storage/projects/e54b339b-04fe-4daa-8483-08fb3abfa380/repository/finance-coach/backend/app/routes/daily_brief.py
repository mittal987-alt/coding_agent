import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import DailyBrief, User
from app.services.auth import get_current_user
from app.services.scheduler import generate_brief_now

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/daily-brief")
def get_daily_brief(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns the most recently generated Daily Brief for the logged-in
    user. If none exists yet (scheduler hasn't run, or this is a brand new
    account), returns an empty/zeroed response instead of a 404 so the
    frontend can render an empty state cleanly."""
    brief = (
        db.query(DailyBrief)
        .filter(DailyBrief.user_id == current_user.id)
        .order_by(DailyBrief.brief_date.desc())
        .first()
    )
    if not brief:
        return {
            "brief_date": None,
            "yesterday_spend": 0,
            "yesterday_income": 0,
            "category_breakdown": {},
            "bills_due_today": [],
            "recurring_triggered_count": 0,
            "alerts_critical_count": 0,
            "alerts_warning_count": 0,
            "generated": False,
        }

    return {
        "brief_date": brief.brief_date,
        "yesterday_spend": brief.yesterday_spend,
        "yesterday_income": brief.yesterday_income,
        "category_breakdown": json.loads(brief.category_breakdown or "{}"),
        "bills_due_today": json.loads(brief.bills_due_today or "[]"),
        "recurring_triggered_count": brief.recurring_triggered_count,
        "alerts_critical_count": brief.alerts_critical_count,
        "alerts_warning_count": brief.alerts_warning_count,
        "generated": True,
    }


@router.post("/daily-brief/generate")
def generate_daily_brief_now(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually regenerate today's brief right now, for the logged-in user
    only — useful for testing, or for a 'Refresh' button in the UI, without
    waiting for the nightly scheduler."""
    generate_brief_now(db, current_user.id)
    return {"message": "Daily brief regenerated."}