"""
Nightly scheduler — runs a set of jobs automatically once a day, for every
user, without anyone needing to open the app:

  1. Auto-run all due recurring transactions (reuses app.routes.recurring)
  2. Build a "Daily Brief" per user: yesterday's spend/income + category
     breakdown, and today's bills due (subscriptions + reminders)
  3. Refresh alerts/overspending checks per user right after, so alerts
     are current the moment someone opens the app rather than computed
     live on every request (reuses app.routes.alerts)

Requires APScheduler:  pip install apscheduler
"""
import json
import logging
from datetime import date, timedelta

from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, Transaction, Subscription, PaymentReminder, DailyBrief
from app.routes.recurring import trigger_due_all_users, trigger_due_for_user
from app.routes.alerts import compute_alerts

logger = logging.getLogger("scheduler")

scheduler = BackgroundScheduler()


def build_brief_for_user(db: Session, user_id: int, recurring_triggered_count: int = 0) -> DailyBrief:
    """Computes and upserts today's DailyBrief row for one user."""
    today = date.today()
    yesterday = today - timedelta(days=1)

    y_txs = db.query(Transaction).filter(
        Transaction.user_id == user_id,
        Transaction.transaction_date == yesterday
    ).all()
    yesterday_expense = sum(t.amount for t in y_txs if t.transaction_type == "expense")
    yesterday_income = sum(t.amount for t in y_txs if t.transaction_type == "income")

    category_breakdown: dict = {}
    for t in y_txs:
        if t.transaction_type == "expense":
            category_breakdown[t.category] = category_breakdown.get(t.category, 0.0) + t.amount

    subs_due = db.query(Subscription).filter(
        Subscription.user_id == user_id,
        Subscription.next_due_date == today
    ).all()
    reminders_due = db.query(PaymentReminder).filter(
        PaymentReminder.user_id == user_id,
        PaymentReminder.is_paid == False,
        PaymentReminder.due_date == today
    ).all()
    bills_due_today = (
        [{"name": s.name, "amount": s.amount, "source": "subscription"} for s in subs_due]
        + [{"name": r.name, "amount": r.amount, "source": "reminder"} for r in reminders_due]
    )

    alerts_result = compute_alerts(user_id, db)

    brief = db.query(DailyBrief).filter(
        DailyBrief.user_id == user_id,
        DailyBrief.brief_date == today
    ).first()
    if not brief:
        brief = DailyBrief(user_id=user_id, brief_date=today)
        db.add(brief)

    brief.yesterday_spend = yesterday_expense
    brief.yesterday_income = yesterday_income
    brief.category_breakdown = json.dumps(category_breakdown)
    brief.bills_due_today = json.dumps(bills_due_today)
    brief.recurring_triggered_count = recurring_triggered_count
    brief.alerts_critical_count = alerts_result["critical_count"]
    brief.alerts_warning_count = alerts_result["warning_count"]

    return brief


def run_daily_jobs():
    """The scheduled job. Runs all three automations for every user."""
    db = SessionLocal()
    try:
        logger.info("Running nightly finance jobs...")

        # Job 1: auto-run due recurring transactions for everyone, in one pass
        triggered_counts = trigger_due_all_users(db)

        # Job 2 + 3: daily brief + fresh alerts, per user
        users = db.query(User).all()
        for user in users:
            build_brief_for_user(db, user.id, triggered_counts.get(user.id, 0))

        db.commit()
        logger.info(f"Nightly jobs complete. {len(users)} briefs generated, "
                    f"{sum(triggered_counts.values())} recurring transaction(s) triggered.")
    except Exception:
        db.rollback()
        logger.exception("Nightly finance jobs failed")
    finally:
        db.close()


def generate_brief_now(db: Session, user_id: int) -> DailyBrief:
    """Manually regenerate today's brief for one user (used by the
    POST /daily-brief/generate endpoint, e.g. for testing without waiting
    for the nightly run)."""
    triggered = trigger_due_for_user(db, user_id)
    brief = build_brief_for_user(db, user_id, triggered)
    db.commit()
    return brief


def start_scheduler():
    """Call once on FastAPI startup. Runs daily at 00:05 server time."""
    if scheduler.running:
        return
    scheduler.add_job(run_daily_jobs, "cron", hour=0, minute=5, id="daily_jobs", replace_existing=True)
    scheduler.start()
    logger.info("Scheduler started — daily jobs will run at 00:05.")