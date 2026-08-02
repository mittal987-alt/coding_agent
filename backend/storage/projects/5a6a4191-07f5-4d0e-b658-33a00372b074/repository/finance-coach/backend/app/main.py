from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text, inspect
import os
from dotenv import load_dotenv

from app.database import engine
from app.models import Base

# Routers
from app.routes.auth import router as auth_router
from app.routes.insights import router as insights_router
from app.routes.upload import router as upload_router
from app.routes.dashboard import router as dashboard_router
from app.routes.transaction import router as transaction_router
from app.routes.budget import router as budget_router
from app.routes.chat import router as chat_router
from app.routes.goal import router as goal_router
from app.routes.subscription import router as subscription_router
from app.routes.analytics import router as analytics_router
from app.routes.account import router as account_router
from app.routes.split import router as split_router
from app.routes.report import router as report_router
# New Feature Routers
from app.routes.tax import router as tax_router
from app.routes.alerts import router as alerts_router
from app.routes.budget_planner import router as budget_planner_router
from app.routes.networth import router as networth_router
from app.routes.reminders import router as reminders_router
from app.routes.categorize import router as categorize_router
from app.routes.heatmap import router as heatmap_router
from app.routes.gamification import router as gamification_router
# High-Impact Feature Routers
from app.routes.recurring import router as recurring_router
from app.routes.investments import router as investments_router
from app.routes.loans import router as loans_router
from app.routes.currency import router as currency_router
from app.routes.pdf_report import router as pdf_report_router
from app.routes.import_csv import router as import_csv_router
# Daily automation
from app.routes.daily_brief import router as daily_brief_router
from app.services.scheduler import start_scheduler
# Custom categories
from app.routes.categories import router as categories_router
# Full data export/backup
from app.routes.backup import router as backup_router
# Receipt photo scan
from app.routes.receipt import router as receipt_router
# Receipt image storage
from app.routes.receipt_store import router as receipt_store_router
# Gamified challenges
from app.routes.challenges import router as challenges_router

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

try:
    reciept_path = os.path.join(os.path.dirname(__file__), "routes", "reciept.py")
    if os.path.exists(reciept_path):
        os.remove(reciept_path)
except Exception as e:
    print(f"Warning: Could not clean up old reciept.py: {e}")

# Auto-create tables (e.g. budgets table)
Base.metadata.create_all(bind=engine)

# Database schema migrations/patches
from sqlalchemy import text
try:
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE uploaded_documents ADD COLUMN IF NOT EXISTS user_id INTEGER REFERENCES users(id)"))
        conn.execute(text("ALTER TABLE recurring_transactions ADD COLUMN IF NOT EXISTS currency VARCHAR(10) DEFAULT 'INR'"))
        conn.execute(text("ALTER TABLE recurring_transactions ADD COLUMN IF NOT EXISTS original_amount DOUBLE PRECISION"))
        conn.execute(text("ALTER TABLE recurring_transactions ADD COLUMN IF NOT EXISTS exchange_rate DOUBLE PRECISION DEFAULT 1.0"))
        conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS receipt_image_url VARCHAR(500)"))
        conn.execute(text("ALTER TABLE transactions ADD COLUMN IF NOT EXISTS embedding TEXT"))
        conn.execute(text("ALTER TABLE budgets ADD COLUMN IF NOT EXISTS embedding TEXT"))
        conn.commit()
except Exception as e:
    print(f"Warning: Could not alter database tables: {e}")

# Auto-correct incorrectly classified transactions
try:
    with engine.connect() as conn:
        result = conn.execute(text("""
            UPDATE transactions 
            SET transaction_type = 'income'
            WHERE transaction_type = 'expense'
              AND (
                description ~* '\\b(NEFT|IMPS|RTGS|UPI|CHG|INT)?CR\\b'
                OR description ~* '\\b(NEFT|IMPS|RTGS|UPI|CHG|INT)?CR-'
                OR description ~* '/CR/'
                OR description ~* '\\b(SALARY|CREDIT|DEPOSIT|INTEREST|REFUND|DIVIDEND)\\b'
              )
        """))
        conn.commit()
        if result.rowcount > 0:
            print(f"Database Patch: Auto-corrected {result.rowcount} transactions from expense to income.")
except Exception as e:
    print(f"Warning: Could not auto-correct transactions: {e}")

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://ai-w27z.vercel.app",
    "https://ai-frontend-5tom.onrender.com",
    
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(insights_router)
app.include_router(upload_router)
app.include_router(dashboard_router)
app.include_router(transaction_router)
app.include_router(budget_router)
app.include_router(chat_router)
app.include_router(goal_router)
app.include_router(subscription_router)
app.include_router(analytics_router)
app.include_router(account_router)
app.include_router(split_router)
app.include_router(report_router)
# New Feature Routers
app.include_router(tax_router)
app.include_router(alerts_router)
app.include_router(budget_planner_router)
app.include_router(networth_router)
app.include_router(reminders_router)
app.include_router(categorize_router)
app.include_router(heatmap_router)
app.include_router(gamification_router)
# High-Impact Feature Routers
app.include_router(recurring_router)
app.include_router(investments_router)
app.include_router(loans_router)
app.include_router(currency_router)
app.include_router(pdf_report_router)
app.include_router(import_csv_router)
# Daily automation
app.include_router(daily_brief_router)
# Custom categories
app.include_router(categories_router)
# Full data export/backup
app.include_router(backup_router)
# Receipt photo scan
app.include_router(receipt_router)
# Receipt image storage
app.include_router(receipt_store_router)
# Gamified challenges
app.include_router(challenges_router)


@app.on_event("startup")
def on_startup():
    start_scheduler()


@app.get("/")
def root():
    return {
        "message": "Finance AI Coach Backend Running"
    }