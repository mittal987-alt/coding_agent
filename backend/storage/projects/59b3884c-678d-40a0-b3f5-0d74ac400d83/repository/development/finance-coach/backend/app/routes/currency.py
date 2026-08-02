"""
Multi-Currency Support Route
Provides a live exchange rate lookup (with offline fallback) and a
list of supported currencies. Transactions can be stored with original
currency/amount and auto-converted to INR.
"""
from fastapi import APIRouter, HTTPException

from app.services.currency_service import SUPPORTED_CURRENCIES, convert_currency_logic, get_all_rates_logic

router = APIRouter(prefix="/currency", tags=["currency"])


# ─── List all supported currencies ────────────────────────────────────────────
@router.get("/supported")
def list_currencies():
    return SUPPORTED_CURRENCIES


# ─── Convert amount ───────────────────────────────────────────────────────────
@router.get("/convert")
async def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str = "INR"
):
    try:
        return await convert_currency_logic(amount, from_currency, to_currency)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ─── Get current rates (all currencies → INR) ────────────────────────────────
@router.get("/rates")
async def get_rates():
    """Returns all supported currency rates vs INR (live + fallback)."""
    return await get_all_rates_logic()
