import re
from datetime import datetime, date

CATEGORY_KEYWORDS = {
    "Shopping": ["amazon", "flipkart", "myntra"],
    "Food": ["zomato", "swiggy"],
    "Travel": ["uber", "ola"],
    "Fuel": ["petrol"],
    "UPI": ["phonepe", "gpay", "paytm", "upi"],
    "Cash": ["atm"],
    "Income": ["salary"]
}

# Keywords in description that strongly indicate income/credit
_CREDIT_KEYWORDS = [
    "SALARY", "CREDIT", "DEPOSIT", "INTEREST", "REFUND", "DIVIDEND",
    "CASHBACK", "REVERSAL", "CREDITED", "CR/", "/CR/", "/CR",
    "NEFT CR", "IMPS CR", "RTGS CR", "BY TRANSFER", "BY CLG",
    "INT.PD", "INT PD", "INT PAID",
]

# Keywords that strongly indicate expense/debit
_DEBIT_KEYWORDS = [
    "WITHDRAWAL", "DEBIT", "DEDUCTED", "DEBITED", "PURCHASE",
    "ATM WDL", "ATM CASH", "POS/", "PAYMENT", "DR/", "/DR/", "/DR",
    "NEFT DR", "IMPS DR", "TO TRANSFER", "BY CHQ", "EMI",
    "CHARGE", "FEE", "PENALTY",
]

# Column header patterns used to detect table structure
_DEBIT_COL_HEADERS = re.compile(
    r"\b(withdrawal|debit|dr|withdrawn|debit\s*amount|withdrawal\s*amt)\b",
    re.IGNORECASE,
)
_CREDIT_COL_HEADERS = re.compile(
    r"\b(deposit|credit|cr|deposited|credit\s*amount|deposit\s*amt)\b",
    re.IGNORECASE,
)
_BALANCE_COL_HEADERS = re.compile(
    r"\b(balance|closing\s*bal|running\s*bal|available\s*bal)\b",
    re.IGNORECASE,
)


def categorize_transaction(description: str) -> str:
    desc = description.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(keyword in desc for keyword in keywords):
            return category
    return "Others"


def parse_date_string(date_str: str) -> date:
    """
    Safely parse a date string with dots, slashes, or dashes (e.g. 28.08.22, 28/08/2022)
    into a datetime.date object.
    """
    clean_date_str = re.sub(r"\s+", "", date_str).replace(".", "-").replace("/", "-")
    try:
        parts = clean_date_str.split("-")
        if len(parts) == 3:
            if len(parts[2]) == 4:
                return datetime.strptime(clean_date_str, "%d-%m-%Y").date()
            else:
                return datetime.strptime(clean_date_str, "%d-%m-%y").date()
    except (ValueError, IndexError):
        pass
    return date.today()


def _detect_type_from_indicator(indicator: str | None) -> str | None:
    """Return 'income' or 'expense' from a CR/DR indicator string, or None."""
    if not indicator:
        return None
    ind = indicator.strip().upper().rstrip("/")
    if ind in ("CR", "C"):
        return "income"
    if ind in ("DR", "D"):
        return "expense"
    return None


def _detect_type_from_description(description: str) -> str | None:
    """
    Keyword-based heuristic on the description text.
    Returns 'income', 'expense', or None if unclear.
    """
    desc_upper = description.upper()

    # Check for explicit CR/DR markers in the text
    if re.search(r"\bCR\b", desc_upper) or desc_upper.endswith("/CR") or "/CR/" in desc_upper:
        return "income"
    if re.search(r"\bDR\b", desc_upper) or desc_upper.endswith("/DR") or "/DR/" in desc_upper:
        return "expense"

    for kw in _CREDIT_KEYWORDS:
        if kw in desc_upper:
            return "income"
    for kw in _DEBIT_KEYWORDS:
        if kw in desc_upper:
            return "expense"

    return None


def _clean_description(desc: str) -> str:
    """Remove trailing CR/DR indicators from description text."""
    desc = desc.strip()
    # Remove trailing CR/DR markers that got appended
    desc = re.sub(r"\s+(CR|DR|CR/|DR/)\s*$", "", desc, flags=re.IGNORECASE)
    # Collapse whitespace
    desc = re.sub(r"\s+", " ", desc)
    return desc.strip()


def _is_header_or_junk(description: str) -> bool:
    """Return True if the description looks like a header or false-positive."""
    desc_lower = description.lower()
    junk_phrases = [
        "brought forward", "carried forward", "opening balance",
        "closing balance", "statement summary", "page no",
        "date particulars", "transaction details",
    ]
    return any(phrase in desc_lower for phrase in junk_phrases)


def _parse_amount_str(amount_str: str) -> float | None:
    """Parse an amount string like '1,23,456.78' or '500.00' into a float."""
    if not amount_str:
        return None
    cleaned = amount_str.replace(",", "").replace(" ", "").strip()
    # Remove currency symbols
    cleaned = re.sub(r"[₹$€£]", "", cleaned)
    if not cleaned:
        return None
    try:
        val = abs(float(cleaned))
        return val if val > 0 else None
    except ValueError:
        return None


# ---------------------------------------------------------------------------
#  Strategy 1: Table-based extraction via pdfplumber
# ---------------------------------------------------------------------------

def extract_from_tables(pdf_path: str) -> list:
    """
    Use pdfplumber to extract structured tables from the PDF.
    Detects column headers for debit/credit/balance and maps values accordingly.
    """
    try:
        import pdfplumber
    except ImportError:
        return []

    transactions = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                if not tables:
                    continue

                for table in tables:
                    if not table or len(table) < 2:
                        continue

                    # --- Detect column roles from header row ---
                    header_row = table[0]
                    if not header_row:
                        continue

                    date_col = -1
                    desc_col = -1
                    debit_col = -1
                    credit_col = -1
                    balance_col = -1

                    for idx, cell in enumerate(header_row):
                        if cell is None:
                            continue
                        cell_text = str(cell).strip()
                        cell_lower = cell_text.lower()

                        if any(kw in cell_lower for kw in ["date", "txn date", "value date", "trans date"]):
                            if date_col == -1:
                                date_col = idx
                        elif any(kw in cell_lower for kw in ["narration", "description", "particular", "detail", "remark"]):
                            desc_col = idx
                        elif _DEBIT_COL_HEADERS.search(cell_text):
                            debit_col = idx
                        elif _CREDIT_COL_HEADERS.search(cell_text):
                            credit_col = idx
                        elif _BALANCE_COL_HEADERS.search(cell_text):
                            balance_col = idx

                    # We need at minimum a date column and at least one amount column
                    has_separate_cols = debit_col >= 0 and credit_col >= 0
                    has_any_amount = debit_col >= 0 or credit_col >= 0
                    if date_col < 0 or not has_any_amount:
                        continue

                    # --- Process data rows ---
                    for row in table[1:]:
                        if not row or len(row) <= max(date_col, desc_col if desc_col >= 0 else 0):
                            continue

                        # Parse date
                        date_cell = str(row[date_col] or "").strip()
                        if not re.search(r"\d{2}\s*[./-]\s*\d{2}\s*[./-]\s*\d{2,4}", date_cell):
                            continue
                        date_match = re.search(r"(\d{2}\s*[./-]\s*\d{2}\s*[./-]\s*\d{2,4})", date_cell)
                        if not date_match:
                            continue
                        date_obj = parse_date_string(date_match.group(1))

                        # Parse description
                        desc = ""
                        if desc_col >= 0 and desc_col < len(row):
                            desc = str(row[desc_col] or "").strip()
                        if not desc:
                            # Try to find description from non-date, non-amount columns
                            for idx, cell in enumerate(row):
                                if idx in (date_col, debit_col, credit_col, balance_col):
                                    continue
                                cell_val = str(cell or "").strip()
                                if cell_val and len(cell_val) > 3:
                                    desc = cell_val
                                    break

                        desc = _clean_description(desc)
                        if not desc or _is_header_or_junk(desc):
                            continue

                        # Parse amounts from debit/credit columns
                        debit_amt = None
                        credit_amt = None

                        if debit_col >= 0 and debit_col < len(row):
                            debit_amt = _parse_amount_str(str(row[debit_col] or ""))
                        if credit_col >= 0 and credit_col < len(row):
                            credit_amt = _parse_amount_str(str(row[credit_col] or ""))

                        # Determine transaction type and amount
                        if has_separate_cols:
                            if credit_amt and not debit_amt:
                                amount = credit_amt
                                tx_type = "income"
                            elif debit_amt and not credit_amt:
                                amount = debit_amt
                                tx_type = "expense"
                            elif debit_amt and credit_amt:
                                # Both present — unusual; take the larger as the primary
                                if credit_amt >= debit_amt:
                                    amount = credit_amt
                                    tx_type = "income"
                                else:
                                    amount = debit_amt
                                    tx_type = "expense"
                            else:
                                # Neither has a value — skip
                                continue
                        else:
                            # Only one amount column detected
                            amount = debit_amt or credit_amt
                            if not amount:
                                continue
                            # Try to determine type from description
                            tx_type = _detect_type_from_description(desc) or "expense"

                        transactions.append({
                            "date": date_obj,
                            "description": desc,
                            "amount": amount,
                            "category": categorize_transaction(desc),
                            "transaction_type": tx_type,
                        })

    except Exception as e:
        print(f"[parser] Table extraction failed: {e}")

    return transactions


# ---------------------------------------------------------------------------
#  Strategy 2: Multi-amount regex extraction from raw text
# ---------------------------------------------------------------------------

def extract_from_text(text: str) -> list:
    """
    Regex-based extraction that handles:
    - Single amount with optional CR/DR indicator
    - Multiple amounts per line (debit col | credit col | balance col)
    """
    transactions = []

    # Date pattern component
    DATE_RE = r"(\d{2}\s*[./-]\s*\d{2}\s*[./-]\s*\d{2,4})"
    # Single amount
    AMT_RE = r"[\d,]+\.\d{2}"
    # CR/DR indicator
    IND_RE = r"(?:CR|DR|CR/|DR/|\bC\b|\bD\b)"

    # ── Detect if the text has a columnar format ──
    # Look for header lines that suggest separate debit/credit columns
    has_separate_columns = False
    header_area = text[:2000].upper()
    if (re.search(r"\b(WITHDRAWAL|DEBIT|DR)\b", header_area) and
            re.search(r"\b(DEPOSIT|CREDIT|CR)\b", header_area)):
        has_separate_columns = True

    # ── Pattern A: Line with multiple amounts (columnar) ──
    # Date ... description ... amount1 ... amount2 [... amount3]
    # The amounts correspond to: debit, credit, balance (in various orders)
    if has_separate_columns:
        # Match date, then description, then 2-3 amounts at end of line
        multi_amt_pattern = (
            DATE_RE + r"\s+"               # date
            r"(.*?)\s+"                    # description (non-greedy)
            r"(" + AMT_RE + r")\s+"        # first amount
            r"(" + AMT_RE + r")"           # second amount
            r"(?:\s+(" + AMT_RE + r"))?"   # optional third amount (balance)
        )

        for match in re.finditer(multi_amt_pattern, text, re.MULTILINE | re.IGNORECASE):
            date_obj = parse_date_string(match.group(1))
            desc = _clean_description(match.group(2))

            if not desc or _is_header_or_junk(desc):
                continue

            amt1 = _parse_amount_str(match.group(3))
            amt2 = _parse_amount_str(match.group(4))
            amt3 = _parse_amount_str(match.group(5)) if match.group(5) else None

            if amt3 is not None:
                # Three amounts: debit | credit | balance
                # The actual transaction amount is whichever of amt1/amt2 is non-zero
                if amt1 and not amt2:
                    # Debit column has value
                    transactions.append({
                        "date": date_obj,
                        "description": desc,
                        "amount": amt1,
                        "category": categorize_transaction(desc),
                        "transaction_type": "expense",
                    })
                    continue
                elif amt2 and not amt1:
                    # Credit column has value
                    transactions.append({
                        "date": date_obj,
                        "description": desc,
                        "amount": amt2,
                        "category": categorize_transaction(desc),
                        "transaction_type": "income",
                    })
                    continue

            # Two amounts: could be amount + balance, or debit + credit
            # Heuristic: if one is much larger, it's likely the balance
            if amt1 and amt2:
                # Use description keywords as tiebreaker
                desc_type = _detect_type_from_description(desc)
                if desc_type == "income":
                    # The actual amount is the smaller of the two (the larger is balance)
                    amount = min(amt1, amt2)
                    tx_type = "income"
                elif desc_type == "expense":
                    amount = min(amt1, amt2)
                    tx_type = "expense"
                else:
                    # Default: first amount is transaction, second is balance
                    amount = amt1
                    tx_type = "expense"

                transactions.append({
                    "date": date_obj,
                    "description": desc,
                    "amount": amount,
                    "category": categorize_transaction(desc),
                    "transaction_type": tx_type,
                })

    # ── Pattern B: Single amount with optional CR/DR indicator ──
    if not transactions:
        single_pattern = (
            DATE_RE + r"\s+"
            r"(.*?)\s+"
            r"(-?" + AMT_RE + r")"
            r"\s*(" + IND_RE + r")?"
        )

        for match in re.finditer(single_pattern, text, re.DOTALL | re.IGNORECASE):
            date_obj = parse_date_string(match.group(1))
            desc = match.group(2).strip()
            desc = re.sub(r"\s+", " ", desc)  # Flatten multi-line spacing
            indicator = match.group(4)
            amount_str = match.group(3).replace(",", "")

            try:
                amount = abs(float(amount_str))
            except ValueError:
                continue

            if _is_header_or_junk(desc):
                continue

            # Determine transaction type from indicator first, then description
            tx_type = _detect_type_from_indicator(indicator)
            if tx_type is None:
                tx_type = _detect_type_from_description(desc)
            if tx_type is None:
                # Check if original amount was negative (some statements use negative for debit)
                if amount_str.startswith("-"):
                    tx_type = "expense"
                else:
                    tx_type = "expense"  # Default to expense

            # Clean description — remove CR/DR indicator if it was appended
            desc = _clean_description(desc)
            if not desc:
                continue

            transactions.append({
                "date": date_obj,
                "description": desc,
                "amount": amount,
                "category": categorize_transaction(desc),
                "transaction_type": tx_type,
            })

    # ── Fallback: line-by-line for fragmented PDFs ──
    if not transactions:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            line = line.strip()
            match = re.search(DATE_RE + r"\s+(.*)", line)
            if match:
                date_obj = parse_date_string(match.group(1))
                desc = match.group(2).strip()

                # Check next 1-2 lines for the amount
                for offset in [1, 2]:
                    if i + offset < len(lines):
                        next_line = lines[i + offset].strip()
                        amt_match = re.match(
                            r"^(-?" + AMT_RE + r")\s*(" + IND_RE + r")?$",
                            next_line, re.IGNORECASE,
                        )
                        if amt_match:
                            try:
                                amt = abs(float(amt_match.group(1).replace(",", "")))
                                indicator = amt_match.group(2)

                                tx_type = _detect_type_from_indicator(indicator)
                                if tx_type is None:
                                    tx_type = _detect_type_from_description(desc)
                                if tx_type is None:
                                    tx_type = "expense"

                                clean_desc = _clean_description(desc)
                                if not clean_desc or _is_header_or_junk(clean_desc):
                                    break

                                transactions.append({
                                    "date": date_obj,
                                    "description": clean_desc,
                                    "amount": amt,
                                    "category": categorize_transaction(clean_desc),
                                    "transaction_type": tx_type,
                                })
                                break
                            except ValueError:
                                pass

    return transactions


# ---------------------------------------------------------------------------
#  Main entry point
# ---------------------------------------------------------------------------

def extract_transactions(text: str, pdf_path: str | None = None) -> list:
    """
    Extract transactions from bank statement text (and optionally the PDF file).

    Returns a list of dicts, each with:
        - date (datetime.date)
        - description (str)
        - amount (float)
        - category (str)
        - transaction_type ("income" | "expense")

    Strategies tried in order:
        1. Table extraction via pdfplumber (if pdf_path provided)
        2. Multi-amount regex on raw text
        3. Single-amount regex with CR/DR indicator
        4. Line-by-line fallback
    """
    transactions = []

    # Strategy 1: Table extraction (most reliable for columnar statements)
    if pdf_path:
        transactions = extract_from_tables(pdf_path)
        if transactions:
            print("=" * 60)
            print(f"[parser] Strategy: TABLE EXTRACTION")
            print(f"[parser] Transactions Found: {len(transactions)}")
            for tx in transactions[:5]:
                print(f"  {tx['date']} | {tx['transaction_type']:7s} | {tx['amount']:>12,.2f} | {tx['description'][:50]}")
            if len(transactions) > 5:
                print(f"  ... and {len(transactions) - 5} more")
            print("=" * 60)
            return transactions

    # Strategy 2 & 3 & 4: Text-based extraction
    transactions = extract_from_text(text)

    strategy = "TEXT REGEX" if transactions else "NONE"
    print("=" * 60)
    print(f"[parser] Strategy: {strategy}")
    print(f"[parser] Transactions Found: {len(transactions)}")
    for tx in transactions[:5]:
        print(f"  {tx['date']} | {tx['transaction_type']:7s} | {tx['amount']:>12,.2f} | {tx['description'][:50]}")
    if len(transactions) > 5:
        print(f"  ... and {len(transactions) - 5} more")
    print("=" * 60)

    return transactions