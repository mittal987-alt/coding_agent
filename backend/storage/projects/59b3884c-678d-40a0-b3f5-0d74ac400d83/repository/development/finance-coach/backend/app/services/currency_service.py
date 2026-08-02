"""
Currency Service
Provides a live exchange rate lookup (with offline fallback) and a
list of supported currencies.
"""
import httpx
from typing import Optional

# ─── Offline fallback rates (relative to INR as base) ─────────────────────────
FALLBACK_RATES_TO_INR: dict[str, float] = {
    "USD": 83.50,
    "EUR": 90.20,
    "GBP": 105.80,
    "AED": 22.73,
    "SGD": 61.90,
    "AUD": 54.20,
    "CAD": 61.10,
    "JPY": 0.555,
    "CHF": 93.60,
    "CNY": 11.50,
    "HKD": 10.70,
    "NZD": 50.10,
    "SAR": 22.27,
    "MYR": 17.80,
    "THB": 2.35,
    "INR": 1.0,
}

SUPPORTED_CURRENCIES = [
    {"code": "INR", "name": "Indian Rupee", "symbol": "₹"},
    {"code": "USD", "name": "US Dollar", "symbol": "$"},
    {"code": "EUR", "name": "Euro", "symbol": "€"},
    {"code": "GBP", "name": "British Pound", "symbol": "£"},
    {"code": "AED", "name": "UAE Dirham", "symbol": "د.إ"},
    {"code": "SGD", "name": "Singapore Dollar", "symbol": "S$"},
    {"code": "AUD", "name": "Australian Dollar", "symbol": "A$"},
    {"code": "CAD", "name": "Canadian Dollar", "symbol": "C$"},
    {"code": "JPY", "name": "Japanese Yen", "symbol": "¥"},
    {"code": "CHF", "name": "Swiss Franc", "symbol": "CHF"},
    {"code": "CNY", "name": "Chinese Yuan", "symbol": "¥"},
    {"code": "HKD", "name": "Hong Kong Dollar", "symbol": "HK$"},
    {"code": "NZD", "name": "New Zealand Dollar", "symbol": "NZ$"},
    {"code": "SAR", "name": "Saudi Riyal", "symbol": "﷼"},
    {"code": "MYR", "name": "Malaysian Ringgit", "symbol": "RM"},
    {"code": "THB", "name": "Thai Baht", "symbol": "฿"},
]

async def fetch_live_rate(from_currency: str, to_currency: str = "INR") -> Optional[float]:
    """Try to get a live rate from the free exchangerate-api.com API."""
    try:
        url = f"https://open.er-api.com/v6/latest/{from_currency}"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("rates", {}).get(to_currency)
    except Exception:
        pass
    return None

async def convert_currency_logic(amount: float, from_currency: str, to_currency: str = "INR"):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()

    if from_currency == to_currency:
        return {"from": from_currency, "to": to_currency, "amount": amount, "converted": amount, "rate": 1.0, "source": "same_currency"}

    # Try live rate first
    rate = await fetch_live_rate(from_currency, to_currency)
    source = "live"

    if rate is None:
        # Fallback: convert both via INR
        from_rate = FALLBACK_RATES_TO_INR.get(from_currency)
        to_rate = FALLBACK_RATES_TO_INR.get(to_currency)
        if from_rate is None or to_rate is None:
            raise ValueError(f"Unsupported currency: {from_currency} or {to_currency}")
        rate = from_rate / to_rate
        source = "offline_fallback"

    converted = round(amount * rate, 2)
    return {
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "rate": round(rate, 6),
        "converted": converted,
        "source": source,
    }

async def get_all_rates_logic():
    """Returns all supported currency rates vs INR (live + fallback)."""
    live_rates = {}
    try:
        url = "https://open.er-api.com/v6/latest/INR"
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                all_rates = data.get("rates", {})
                for c in SUPPORTED_CURRENCIES:
                    code = c["code"]
                    if code in all_rates and all_rates[code] > 0:
                        live_rates[code] = round(1 / all_rates[code], 4)  # convert to INR per unit
    except Exception:
        pass

    rates = []
    for c in SUPPORTED_CURRENCIES:
        code = c["code"]
        rate_inr = live_rates.get(code) or FALLBACK_RATES_TO_INR.get(code, 1.0)
        rates.append({
            "code": code,
            "name": c["name"],
            "symbol": c["symbol"],
            "rate_inr": rate_inr,
            "source": "live" if code in live_rates else "fallback",
        })

    return {"rates": rates, "base": "INR"}
