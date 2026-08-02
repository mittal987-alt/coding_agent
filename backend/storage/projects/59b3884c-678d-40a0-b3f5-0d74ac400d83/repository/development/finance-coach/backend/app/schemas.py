from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List, Dict, Any

from datetime import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class TransactionCreate(BaseModel):
    transaction_date: date
    description: str
    amount: float
    category: str
    transaction_type: str
    account_id: Optional[int] = None
    currency: Optional[str] = "INR"  # if not INR, amount is converted to INR server-side on save
    receipt_image_url: Optional[str] = None

class TransactionUpdate(BaseModel):
    transaction_date: date
    description: str
    amount: float
    category: str
    transaction_type: str
    account_id: Optional[int] = None
    currency: Optional[str] = "INR"
    receipt_image_url: Optional[str] = None

class BulkTransactionIds(BaseModel):
    ids: List[int]

class BulkRecategorize(BaseModel):
    ids: List[int]
    category: str

class BudgetCreate(BaseModel):
    category: str
    amount: float

class BudgetResponse(BaseModel):
    id: int
    category: str
    amount: float

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str

class SavingsGoalCreate(BaseModel):
    name: str
    target_amount: float
    current_amount: float = 0.0
    target_date: date

class SavingsGoalResponse(BaseModel):
    id: int
    name: str
    target_amount: float
    current_amount: float
    target_date: date

    class Config:
        from_attributes = True

class SubscriptionCreate(BaseModel):
    name: str
    amount: float
    category: str
    billing_cycle: str
    next_due_date: date

class SubscriptionResponse(BaseModel):
    id: int
    name: str
    amount: float
    category: str
    billing_cycle: str
    next_due_date: date

    class Config:
        from_attributes = True

class AccountCreate(BaseModel):
    name: str
    account_type: str
    balance: float = 0.0

class AccountResponse(BaseModel):
    id: int
    name: str
    account_type: str
    balance: float

    class Config:
        from_attributes = True

class SharedExpenseCreate(BaseModel):
    description: str
    total_amount: float
    friend_name: str
    amount_owed: float

class SharedExpenseResponse(BaseModel):
    id: int
    description: str
    total_amount: float
    friend_name: str
    amount_owed: float
    is_settled: bool

    class Config:
        from_attributes = True

class PaymentReminderCreate(BaseModel):
    name: str
    amount: float
    due_date: date
    category: str = "Others"
    is_recurring: Optional[bool] = False
    recurrence_frequency: Optional[str] = None  # "daily" | "weekly" | "monthly" | "yearly"

class PaymentReminderUpdate(BaseModel):
    name: Optional[str] = None
    amount: Optional[float] = None
    due_date: Optional[date] = None
    category: Optional[str] = None
    is_paid: Optional[bool] = None
    is_recurring: Optional[bool] = None
    recurrence_frequency: Optional[str] = None


class PaymentReminderResponse(BaseModel):
    id: int
    name: str
    amount: float
    due_date: date
    category: str
    is_paid: bool
    days_left: Optional[int] = None
    urgency: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Recurring Transactions ───────────────────────────────────────────────────

class RecurringTransactionCreate(BaseModel):
    description: str
    amount: float
    category: str
    transaction_type: str   # income / expense
    frequency: str          # daily / weekly / monthly / yearly
    next_date: date
    is_active: bool = True
    currency: Optional[str] = "INR"

class RecurringTransactionResponse(BaseModel):
    id: int
    description: str
    amount: float
    category: str
    transaction_type: str
    frequency: str
    next_date: date
    is_active: bool
    currency: str = "INR"
    original_amount: Optional[float] = None
    exchange_rate: float = 1.0

    class Config:
        from_attributes = True


# ─── Investment Portfolio ─────────────────────────────────────────────────────

class InvestmentCreate(BaseModel):
    name: str
    investment_type: str    # Stocks, Mutual Fund, FD, PPF, Gold, Crypto, Others
    invested_amount: float
    current_value: float
    units: Optional[float] = None
    purchase_price: Optional[float] = None
    current_price: Optional[float] = None
    purchase_date: date
    notes: Optional[str] = None

class InvestmentResponse(BaseModel):
    id: int
    name: str
    investment_type: str
    invested_amount: float
    current_value: float
    units: Optional[float] = None
    purchase_price: Optional[float] = None
    current_price: Optional[float] = None
    purchase_date: date
    notes: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Loan / EMI Tracker ───────────────────────────────────────────────────────

class LoanCreate(BaseModel):
    name: str
    loan_type: str          # Home, Car, Personal, Education, Business, Others
    principal_amount: float
    interest_rate: float    # Annual % rate
    tenure_months: int
    start_date: date
    emi_amount: float
    outstanding_amount: float
    lender_name: Optional[str] = None
    is_active: bool = True

class LoanResponse(BaseModel):
    id: int
    name: str
    loan_type: str
    principal_amount: float
    interest_rate: float
    tenure_months: int
    start_date: date
    emi_amount: float
    outstanding_amount: float
    lender_name: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


# --- Categories ---

class CategoryCreate(BaseModel):
    name: str
    color: Optional[str] = "#8a8f98"

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None

class CategoryResponse(BaseModel):
    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


# --- Daily Brief (scheduler-generated) ---

class DailyBriefResponse(BaseModel):
    brief_date: Optional[date] = None
    yesterday_spend: float = 0.0
    yesterday_income: float = 0.0
    category_breakdown: Dict[str, float] = {}
    bills_due_today: List[Dict[str, Any]] = []
    recurring_triggered_count: int = 0
    alerts_critical_count: int = 0
    alerts_warning_count: int = 0
    generated: bool = True