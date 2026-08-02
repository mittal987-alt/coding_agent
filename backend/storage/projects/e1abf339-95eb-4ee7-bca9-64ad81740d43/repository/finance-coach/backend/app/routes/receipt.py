"""
Receipt photo scan.
Runs OCR on a single receipt photo and guesses description/amount/date/
category from the text. Returns a preview only -- nothing is saved to the
database here. The frontend uses this to pre-fill the existing Add
Transaction modal so the user reviews and confirms before it's created.
"""
import os
import re
import tempfile
from datetime import date, datetime
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, Category
from app.services.auth import get_current_user

router = APIRouter()
reader = None

def get_reader():
    global reader
    if reader is None:
        import easyocr
        reader = easyocr.Reader(['en'])
    return reader


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


AMOUNT_KEYWORDS = re.compile(
    r"(total|amount due|grand total|net amount|amount payable|net payable|balance due)",
    re.IGNORECASE
)
NUMBER_PATTERN = re.compile(r"\d{1,3}(?:[,.]\d{3})*(?:\.\d{1,2})?")

DATE_PATTERNS = [
    (re.compile(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b"), "iso"),
    (re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b"), "dmy_slash"),
    (re.compile(r"\b(\d{1,2})-(\d{1,2})-(\d{4})\b"), "dmy_dash"),
]

CATEGORY_KEYWORDS = {
    "food": ["restaurant", "cafe", "food", "eatery", "diner", "kitchen", "pizza", "burger", "bakery"],
    "fuel": ["petrol", "diesel", "fuel", "gas station", "hpcl", "iocl", "bpcl"],
    "shopping": ["mart", "store", "mall", "supermarket", "retail", "bazaar", "outlet"],
    "travel": ["taxi", "cab", "uber", "ola", "airlines", "railway", "metro", "flight"],
}


def _guess_amount(lines: List[str]) -> float:
    candidates: List[float] = []
    for line in lines:
        if AMOUNT_KEYWORDS.search(line):
            for n in NUMBER_PATTERN.findall(line):
                try:
                    candidates.append(float(n.replace(",", "")))
                except ValueError:
                    pass
    if candidates:
        # If a line mentions "total" more than once (subtotal, tax, total),
        # the largest such match is usually the final amount.
        return max(candidates)

    all_nums: List[float] = []
    for line in lines:
        for n in NUMBER_PATTERN.findall(line):
            try:
                all_nums.append(float(n.replace(",", "")))
            except ValueError:
                pass
    return max(all_nums) if all_nums else 0.0


def _guess_date(text: str) -> str:
    for pattern, kind in DATE_PATTERNS:
        m = pattern.search(text)
        if not m:
            continue
        try:
            if kind == "iso":
                d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            elif kind == "dmy_slash":
                d = datetime.strptime(m.group(0), "%d/%m/%Y").date()
            else:
                d = datetime.strptime(m.group(0), "%d-%m-%Y").date()
            return d.isoformat()
        except ValueError:
            continue
    return date.today().isoformat()


def _guess_merchant(lines: List[str]) -> str:
    for line in lines:
        cleaned = line.strip()
        # Skip lines that are just numbers/amounts -- want the merchant name,
        # usually one of the first readable lines on a receipt.
        if len(cleaned) >= 3 and not NUMBER_PATTERN.fullmatch(cleaned):
            return cleaned[:100]
    return "Receipt purchase"


def _guess_category(text: str, user_categories: List[str]) -> str:
    lower = text.lower()
    for cat_key, keywords in CATEGORY_KEYWORDS.items():
        if any(k in lower for k in keywords):
            for uc in user_categories:
                if uc.lower() == cat_key or cat_key in uc.lower():
                    return uc
    if "Others" in user_categories:
        return "Others"
    return user_categories[0] if user_categories else "Others"


@router.post("/receipts/scan")
async def scan_receipt(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not file.filename or not file.filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        return {"success": False, "message": "Please upload a JPG, PNG, or WEBP photo of the receipt."}

    contents = await file.read()
    tmp_path = None
    try:
        suffix = os.path.splitext(file.filename)[1] or ".jpg"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        ocr_reader = get_reader()
        results = ocr_reader.readtext(tmp_path, detail=0)
        lines = [r.strip() for r in results if r.strip()]
        full_text = "\n".join(lines)

        if not full_text:
            return {"success": False, "message": "Couldn't read any text from this photo. Try a clearer, well-lit shot."}

        user_categories = [c.name for c in db.query(Category).filter(Category.user_id == current_user.id).all()]

        return {
            "success": True,
            "description": _guess_merchant(lines),
            "amount": _guess_amount(lines),
            "transaction_date": _guess_date(full_text),
            "category": _guess_category(full_text, user_categories),
            "raw_text": full_text[:800],
        }
    except Exception as e:
        return {"success": False, "message": f"Server error: {str(e)}"}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
