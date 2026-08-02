"""
CSV Service
Handles parsing and normalizing bank statement CSVs into transaction dictionaries.
"""
import re
from datetime import date, datetime
from typing import Optional

_DATE_FORMATS = [
    "%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d %b %Y",
    "%d/%m/%y", "%d-%m-%y", "%m/%d/%Y", "%d.%m.%Y",
    "%d %B %Y",
]

def _parse_date(s: str) -> Optional[date]:
    s = s.strip()
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

def _clean_amount(s: str) -> Optional[float]:
    """Remove commas, currency symbols, and parse float."""
    if not s:
        return None
    cleaned = re.sub(r"[^\d.\-]", "", s.replace(",", ""))
    try:
        return float(cleaned)
    except ValueError:
        return None

def detect_format(headers: list[str]) -> str:
    h = [h.strip().lower() for h in headers]
    joined = " ".join(h)
    if "narration" in joined and "chq" in joined:
        return "HDFC"
    if "txn date" in joined or "transaction date" in joined:
        if "debit" in joined and "credit" in joined:
            return "SBI"
    if "value date" in joined and "remarks" in joined:
        return "ICICI"
    if "tran date" in joined and "particular" in joined:
        return "AXIS"
    return "GENERIC"

def _parse_hdfc(rows, headers) -> list[dict]:
    parsed = []
    h = [x.strip().lower() for x in headers]
    for row in rows:
        try:
            d = _parse_date(row[h.index("date")] if "date" in h else row[0])
            desc = row[h.index("narration")] if "narration" in h else row[1]
            withdraw = _clean_amount(row[h.index("withdrawal amt.(inr)")] if "withdrawal amt.(inr)" in h else row[4])
            deposit = _clean_amount(row[h.index("deposit amt.(inr)")] if "deposit amt.(inr)" in h else row[5])
            if d and desc:
                if deposit and deposit > 0:
                    parsed.append({"date": d, "desc": desc.strip(), "amount": deposit, "type": "income", "category": "Income"})
                if withdraw and withdraw > 0:
                    parsed.append({"date": d, "desc": desc.strip(), "amount": withdraw, "type": "expense", "category": "Others"})
        except (IndexError, ValueError):
            continue
    return parsed

def _parse_sbi(rows, headers) -> list[dict]:
    parsed = []
    h = [x.strip().lower() for x in headers]
    for row in rows:
        try:
            date_val = row[0] if len(row) > 0 else ""
            desc = row[2] if len(row) > 2 else ""
            debit = _clean_amount(row[4]) if len(row) > 4 else None
            credit = _clean_amount(row[5]) if len(row) > 5 else None
            d = _parse_date(date_val)
            if d and desc.strip():
                if credit and credit > 0:
                    parsed.append({"date": d, "desc": desc.strip(), "amount": credit, "type": "income", "category": "Income"})
                if debit and debit > 0:
                    parsed.append({"date": d, "desc": desc.strip(), "amount": debit, "type": "expense", "category": "Others"})
        except (IndexError, ValueError):
            continue
    return parsed

def _parse_generic(rows, headers) -> list[dict]:
    parsed = []
    h = [x.strip().lower() for x in headers]

    def _find(candidates):
        for c in candidates:
            if c in h:
                return h.index(c)
        return None

    date_idx = _find(["date", "txn date", "transaction date", "tran date", "value date"])
    desc_idx = _find(["description", "narration", "particulars", "remarks", "particular", "details"])
    debit_idx = _find(["debit", "withdrawal", "withdrawal amt.(inr)", "withdrawals(dr)", "debit amount"])
    credit_idx = _find(["credit", "deposit", "deposit amt.(inr)", "deposits(cr)", "credit amount"])
    amount_idx = _find(["amount", "amt"])

    for row in rows:
        try:
            if date_idx is None or len(row) <= (date_idx or 0):
                continue
            d = _parse_date(row[date_idx])
            desc = row[desc_idx].strip() if desc_idx is not None and len(row) > desc_idx else "Transaction"

            if not d:
                continue

            if amount_idx is not None and len(row) > amount_idx:
                amt = _clean_amount(row[amount_idx])
                if amt and amt != 0:
                    tx_type = "income" if amt > 0 else "expense"
                    parsed.append({"date": d, "desc": desc, "amount": abs(amt), "type": tx_type, "category": "Income" if amt > 0 else "Others"})
            else:
                credit = _clean_amount(row[credit_idx]) if credit_idx is not None and len(row) > credit_idx else None
                debit = _clean_amount(row[debit_idx]) if debit_idx is not None and len(row) > debit_idx else None
                if credit and credit > 0:
                    parsed.append({"date": d, "desc": desc, "amount": credit, "type": "income", "category": "Income"})
                if debit and debit > 0:
                    parsed.append({"date": d, "desc": desc, "amount": debit, "type": "expense", "category": "Others"})
        except (IndexError, ValueError, AttributeError):
            continue
    return parsed

def parse_csv_rows(bank_format: str, data_rows: list[list[str]], headers: list[str]) -> list[dict]:
    if bank_format == "HDFC":
        return _parse_hdfc(data_rows, headers)
    elif bank_format == "SBI":
        return _parse_sbi(data_rows, headers)
    else:
        return _parse_generic(data_rows, headers)
