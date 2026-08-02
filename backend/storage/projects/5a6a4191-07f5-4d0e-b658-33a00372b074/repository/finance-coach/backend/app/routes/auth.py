from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.schemas import UserCreate, UserLogin, ChangePasswordRequest
from app.models import (
    User, Transaction, Budget, SavingsGoal, Subscription, Account,
    SharedExpense, PaymentReminder, RecurringTransaction, Investment,
    Loan, DailyBrief,
)
from app.database import SessionLocal
from app.services.auth import get_current_user

from passlib.context import CryptContext
from jose import jwt, JWTError

class UpdateNameRequest(BaseModel):
    name: str

router = APIRouter()

SECRET_KEY = "finance_secret_key"
ALGORITHM = "HS256"

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="login"
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# SIGNUP
# -------------------------
@router.post("/signup")
def signup(
    user: UserCreate,
    db: Session = Depends(get_db)
):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = pwd_context.hash(
        user.password
    )

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User registered successfully"
    }


# -------------------------
# LOGIN
# -------------------------
@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):

    db_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    valid = pwd_context.verify(
        user.password,
        db_user.password
    )

    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = jwt.encode(
        {"sub": db_user.email},
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# -------------------------
# PROFILE
@router.get("/profile")
def profile(
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Authorization token missing")

    token_str = authorization.replace("Bearer ", "")

    try:
        payload = jwt.decode(token_str, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    email = payload["sub"]
    user = db.query(User).filter(User.email == email).first()
    name = user.name if user else ""

    return {"email": email, "name": name}


# -------------------------
# UPDATE NAME
# -------------------------
@router.put("/profile/name")
def update_name(
    data: UpdateNameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.name = data.name.strip()
    db.commit()
    return {"message": "Name updated successfully", "name": current_user.name}


# -------------------------
# CHANGE PASSWORD
# -------------------------
@router.put("/profile/password")
def change_password(
    data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not pwd_context.verify(data.current_password, current_user.password):
        raise HTTPException(
            status_code=401,
            detail="Current password is incorrect"
        )

    current_user.password = pwd_context.hash(data.new_password)
    db.commit()

    return {"message": "Password updated successfully"}


# -------------------------
# DELETE ACCOUNT
# -------------------------
@router.delete("/profile")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Permanently deletes the user and everything owned by them. None of the
    other tables have cascade-delete configured on their user_id foreign
    key, so every table is cleaned up explicitly here first to avoid
    foreign-key violations or orphaned rows.
    """
    user_id = current_user.id

    db.query(Transaction).filter(Transaction.user_id == user_id).delete()
    db.query(Budget).filter(Budget.user_id == user_id).delete()
    db.query(SavingsGoal).filter(SavingsGoal.user_id == user_id).delete()
    db.query(Subscription).filter(Subscription.user_id == user_id).delete()
    db.query(SharedExpense).filter(SharedExpense.user_id == user_id).delete()
    db.query(PaymentReminder).filter(PaymentReminder.user_id == user_id).delete()
    db.query(RecurringTransaction).filter(RecurringTransaction.user_id == user_id).delete()
    db.query(Investment).filter(Investment.user_id == user_id).delete()
    db.query(Loan).filter(Loan.user_id == user_id).delete()
    db.query(DailyBrief).filter(DailyBrief.user_id == user_id).delete()
    # Accounts last among the referencing tables, since Transaction had an
    # additional FK to Account that's already cleared by the delete above.
    db.query(Account).filter(Account.user_id == user_id).delete()

    db.delete(current_user)
    db.commit()

    return {"message": "Account deleted successfully"}