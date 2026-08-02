from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Date, Boolean, Text
from sqlalchemy.sql import func

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))

    email = Column(String(100), unique=True)
    password = Column(String(255))
    created_at = Column(DateTime(timezone=True),
                        server_default=func.now())
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    transaction_date = Column(Date)
    description = Column(String(255))
    amount = Column(Float)
    currency = Column(String(10), default="INR")
    original_amount = Column(Float, nullable=True)
    exchange_rate = Column(Float, default=1.0)

    category = Column(String(100))
    transaction_type = Column(String(20))  # income/expense
    receipt_image_url = Column(String(500), nullable=True)
    embedding = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    filename = Column(String(255))
    extracted_text = Column(String)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String(100))
    amount = Column(Float)
    embedding = Column(Text, nullable=True)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class SavingsGoal(Base):
    __tablename__ = "savings_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)
    target_date = Column(Date)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    amount = Column(Float)
    category = Column(String(100))
    billing_cycle = Column(String(50))  # e.g., Monthly, Yearly
    next_due_date = Column(Date)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    account_type = Column(String(50))  # Bank, Credit Card, Cash, UPI Wallet
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SharedExpense(Base):
    __tablename__ = "shared_expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String(255))
    total_amount = Column(Float)
    friend_name = Column(String(100))
    amount_owed = Column(Float)  # Amount the friend owes the user
    is_settled = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PaymentReminder(Base):
    __tablename__ = "payment_reminders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    amount = Column(Float)
    is_recurring = Column(Boolean, default=False)
    recurrence_frequency = Column(String, nullable=True)  # "daily" | "weekly" | "monthly" | "yearly"

    due_date = Column(Date)
    category = Column(String(100), default="Others")
    is_paid = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class RecurringTransaction(Base):
    """Auto-generates transactions on a fixed schedule."""
    __tablename__ = "recurring_transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    description = Column(String(255))
    amount = Column(Float)
    currency = Column(String(10), default="INR")
    original_amount = Column(Float, nullable=True)
    exchange_rate = Column(Float, default=1.0)
    category = Column(String(100))
    transaction_type = Column(String(20))  # income / expense
    frequency = Column(String(50))         # daily / weekly / monthly / yearly
    next_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Investment(Base):
    """Investment portfolio: Stocks, MF, FD, PPF, Gold, Crypto, Others."""
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(200))
    investment_type = Column(String(100))  # Stocks, Mutual Fund, FD, PPF, Gold, Crypto, Others
    invested_amount = Column(Float)
    current_value = Column(Float)
    units = Column(Float, nullable=True)
    purchase_price = Column(Float, nullable=True)
    current_price = Column(Float, nullable=True)
    purchase_date = Column(Date)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Loan(Base):
    """Loan / EMI tracker."""
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(200))
    loan_type = Column(String(100))        # Home, Car, Personal, Education, Business, Others
    principal_amount = Column(Float)
    interest_rate = Column(Float)          # Annual rate in %
    tenure_months = Column(Integer)
    start_date = Column(Date)
    emi_amount = Column(Float)
    outstanding_amount = Column(Float)
    lender_name = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Category(Base):
    """
    User-managed categories, shared across transactions, budgets,
    subscriptions, reminders, and recurring transactions. Category fields
    on those tables are plain strings (not foreign keys), so this list is
    purely for populating dropdowns and consistent coloring in the UI --
    deleting or renaming a category here never touches existing records.
    """
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(100))
    color = Column(String(20), default="#8a8f98")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class DailyBrief(Base):
    """
    One row per user per day, generated automatically by the nightly
    scheduler (app/services/scheduler.py). Stores a snapshot so the
    frontend can fetch it instantly instead of recomputing on every load.
    """
    __tablename__ = "daily_briefs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    brief_date = Column(Date)  # the date this brief was generated for

    yesterday_spend = Column(Float, default=0.0)
    yesterday_income = Column(Float, default=0.0)
    category_breakdown = Column(String)  # JSON string: {"Food": 340.0, ...}
    bills_due_today = Column(String)     # JSON string: [{"name": ..., "amount": ..., "source": ...}, ...]

    recurring_triggered_count = Column(Integer, default=0)
    alerts_critical_count = Column(Integer, default=0)
    alerts_warning_count = Column(Integer, default=0)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Challenge(Base):
    """Gamified savings/spending challenges."""
    __tablename__ = "challenges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_type = Column(String(50))   # 52_week | no_spend_week | save_10_pct | 100_day_streak
    started_at = Column(Date)
    current_value = Column(Float, default=0.0)
    target_value = Column(Float, default=0.0)
    is_complete = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())