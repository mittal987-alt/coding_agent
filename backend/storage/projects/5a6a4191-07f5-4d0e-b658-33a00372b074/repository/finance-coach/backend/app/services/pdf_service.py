"""
PDF Service
Generates professional multi-section PDF reports or fallback HTML reports.
"""
import io
from datetime import date

def generate_pdf_reportlab(user, transactions, budgets, goals, loans, investments) -> bytes:
    """Generate PDF using reportlab if available."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
    from reportlab.lib.units import cm

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    story = []

    # ── Title ──
    title_style = ParagraphStyle(
        "Title", parent=styles["Heading1"],
        fontSize=22, textColor=colors.HexColor("#4F46E5"),
        spaceAfter=6,
    )
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Normal"],
        fontSize=10, textColor=colors.grey, spaceAfter=16,
    )
    story.append(Paragraph("💰 Finance AI Coach — Health Report", title_style))
    story.append(Paragraph(f"Generated: {date.today().strftime('%d %B %Y')}  |  User: {user.name}", sub_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#E2E8F0"), spaceAfter=16))

    # ── Helper styles ──
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13, textColor=colors.HexColor("#1E293B"), spaceAfter=6)
    normal = styles["Normal"]

    def _section(title):
        story.append(Spacer(1, 10))
        story.append(Paragraph(title, h2))
        story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0"), spaceAfter=8))

    def _table(data, col_widths=None):
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E2E8F0")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t)

    # ── 1. Financial Summary ──
    _section("1. Financial Summary")
    income = sum(t.amount for t in transactions if t.transaction_type == "income")
    expense = sum(t.amount for t in transactions if t.transaction_type == "expense")
    savings = income - expense
    savings_rate = (savings / income * 100) if income > 0 else 0

    summary_data = [
        ["Metric", "Amount (₹)"],
        ["Total Income", f"₹{income:,.2f}"],
        ["Total Expenses", f"₹{expense:,.2f}"],
        ["Net Savings", f"₹{savings:,.2f}"],
        ["Savings Rate", f"{savings_rate:.1f}%"],
        ["Transactions Recorded", str(len(transactions))],
    ]
    _table(summary_data, [8*cm, 8*cm])

    # ── 2. Budget vs Actual ──
    if budgets:
        _section("2. Budget vs Actual Spending")
        cat_spend: dict = {}
        for t in transactions:
            if t.transaction_type == "expense":
                cat_spend[t.category] = cat_spend.get(t.category, 0) + t.amount

        bdata = [["Category", "Budget (₹)", "Spent (₹)", "Remaining (₹)", "Status"]]
        for b in budgets:
            spent = cat_spend.get(b.category, 0)
            rem = b.amount - spent
            status = "✓ OK" if rem >= 0 else "⚠ Over"
            bdata.append([b.category, f"₹{b.amount:,.0f}", f"₹{spent:,.0f}", f"₹{rem:,.0f}", status])
        _table(bdata, [4*cm, 3*cm, 3*cm, 3.5*cm, 2*cm])

    # ── 3. Savings Goals ──
    if goals:
        _section("3. Savings Goals Progress")
        gdata = [["Goal", "Target (₹)", "Saved (₹)", "Progress", "Target Date"]]
        for g in goals:
            pct = min(g.current_amount / g.target_amount * 100, 100) if g.target_amount > 0 else 0
            gdata.append([
                g.name,
                f"₹{g.target_amount:,.0f}",
                f"₹{g.current_amount:,.0f}",
                f"{pct:.0f}%",
                str(g.target_date),
            ])
        _table(gdata, [5*cm, 3*cm, 3*cm, 2.5*cm, 3*cm])

    # ── 4. Active Loans ──
    if loans:
        _section("4. Active Loans & EMI Burden")
        ldata = [["Loan", "Type", "Principal (₹)", "Outstanding (₹)", "EMI/mo (₹)", "Rate %"]]
        for l in [x for x in loans if x.is_active]:
            ldata.append([
                l.name, l.loan_type,
                f"₹{l.principal_amount:,.0f}",
                f"₹{l.outstanding_amount:,.0f}",
                f"₹{l.emi_amount:,.0f}",
                f"{l.interest_rate:.1f}%",
            ])
        total_emi = sum(l.emi_amount for l in loans if l.is_active)
        ldata.append(["TOTAL", "", "", "", f"₹{total_emi:,.0f}", ""])
        _table(ldata, [4*cm, 2.5*cm, 3*cm, 3*cm, 2.5*cm, 1.5*cm])

    # ── 5. Investment Portfolio ──
    if investments:
        _section("5. Investment Portfolio")
        total_inv = sum(i.invested_amount for i in investments)
        total_cur = sum(i.current_value for i in investments)
        idata = [["Investment", "Type", "Invested (₹)", "Current Value (₹)", "Return"]]
        for i in investments:
            ret = ((i.current_value - i.invested_amount) / i.invested_amount * 100) if i.invested_amount > 0 else 0
            idata.append([
                i.name, i.investment_type,
                f"₹{i.invested_amount:,.0f}",
                f"₹{i.current_value:,.0f}",
                f"{ret:+.1f}%",
            ])
        overall_ret = ((total_cur - total_inv) / total_inv * 100) if total_inv > 0 else 0
        idata.append(["TOTAL", "", f"₹{total_inv:,.0f}", f"₹{total_cur:,.0f}", f"{overall_ret:+.1f}%"])
        _table(idata, [5*cm, 3*cm, 3*cm, 3*cm, 2*cm])

    # ── Footer ──
    story.append(Spacer(1, 24))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#E2E8F0")))
    story.append(Paragraph(
        "Generated by Finance AI Coach · For personal financial planning only.",
        ParagraphStyle("Footer", parent=normal, fontSize=8, textColor=colors.grey, spaceBefore=6)
    ))

    doc.build(story)
    return buffer.getvalue()

def generate_fallback_html(user, transactions, budgets, goals, loans, investments) -> bytes:
    """Fallback: return an HTML report if reportlab not installed."""
    income = sum(t.amount for t in transactions if t.transaction_type == "income")
    expense = sum(t.amount for t in transactions if t.transaction_type == "expense")
    savings = income - expense
    savings_rate = (savings / income * 100) if income > 0 else 0

    rows = ""
    for t in transactions[:50]:  # limit rows
        rows += f"<tr><td>{t.transaction_date}</td><td>{t.description}</td><td>{t.category}</td><td>{t.transaction_type}</td><td>₹{t.amount:,.2f}</td></tr>"

    html = f"""<!DOCTYPE html><html><head><meta charset='utf-8'>
    <title>Finance Report - {user.name}</title>
    <style>body{{font-family:Arial;margin:30px;}} h1{{color:#4F46E5;}} table{{border-collapse:collapse;width:100%;margin-bottom:20px;}}
    th{{background:#4F46E5;color:white;padding:8px;}} td{{border:1px solid #e2e8f0;padding:7px;}}
    tr:nth-child(even){{background:#f8fafc;}}</style></head><body>
    <h1>💰 Finance AI Coach — Health Report</h1>
    <p>Generated: {date.today()} | User: {user.name}</p>
    <h2>Financial Summary</h2>
    <table><tr><th>Metric</th><th>Amount</th></tr>
    <tr><td>Total Income</td><td>₹{income:,.2f}</td></tr>
    <tr><td>Total Expenses</td><td>₹{expense:,.2f}</td></tr>
    <tr><td>Net Savings</td><td>₹{savings:,.2f}</td></tr>
    <tr><td>Savings Rate</td><td>{savings_rate:.1f}%</td></tr></table>
    <h2>Recent Transactions</h2>
    <table><tr><th>Date</th><th>Description</th><th>Category</th><th>Type</th><th>Amount</th></tr>
    {rows}</table>
    </body></html>"""
    return html.encode("utf-8")
