import os
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Transaction, User, Budget
from app.schemas import ChatRequest
from app.services.auth import get_current_user
from app.services.embeddings import get_embedding, cosine_similarity
import json

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def generate_mock_ai_coaching(message: str, user: User, transactions: list, budgets: list) -> str:
    """
    Generate context-aware financial coaching recommendations based on actual user transactions and budgets.
    """
    msg = message.lower()
    total_income = sum(t.amount for t in transactions if t.transaction_type == "income")
    total_expense = sum(t.amount for t in transactions if t.transaction_type == "expense")
    net_savings = total_income - total_expense

    # Category summaries
    categories = {}
    for t in transactions:
        if t.transaction_type == "expense":
            categories[t.category] = categories.get(t.category, 0.0) + t.amount

    # Keyword routing
    if "salary" in msg or "income" in msg:
        return f"Your total recorded income is ₹{total_income:,.2f}. If you have regular direct deposit or salary statements, uploading them helps track your monthly earnings!"
        
    elif "spend" in msg or "expense" in msg or "shopping" in msg or "food" in msg:
        highest_cat = max(categories.keys(), key=lambda k: categories[k]) if categories else "None"
        exp_details = ", ".join([f"₹{amt:,.2f} on {cat}" for cat, amt in categories.items()])
        response = f"Your total expenses amount to ₹{total_expense:,.2f}. "
        if categories:
            response += f"Your top spending area is **{highest_cat}** at ₹{categories[highest_cat]:,.2f}. Here is the breakdown: {exp_details}."
        else:
            response += "No recorded expenses found yet. Try uploading a statement to parse transactions!"
        return response

    elif "budget" in msg or "limit" in msg:
        if not budgets:
            return "You haven't set any category budgets yet. You can set them using the sidebar budget form to start tracking your targets!"
        
        exceeded = []
        for b in budgets:
            spent = categories.get(b.category, 0.0)
            if spent > b.amount:
                exceeded.append(f"**{b.category}** (Spent: ₹{spent:,.2f} / Budget: ₹{b.amount:,.2f})")
        
        budget_details = ", ".join([f"₹{b.amount:,.2f} for {b.category}" for b in budgets])
        response = f"Here are your budget targets: {budget_details}. "
        if exceeded:
            response += f"⚠️ Heads up, you have exceeded your budget for: {', '.join(exceeded)}."
        else:
            response += "✅ Awesome! All your expenses are currently within their budget targets."
        return response

    elif "saving" in msg or "balance" in msg or "left" in msg:
        if net_savings >= 0:
            return f"You're in the green! Your net savings are **₹{net_savings:,.2f}** (Income ₹{total_income:,.2f} - Expenses ₹{total_expense:,.2f}). Keep it up!"
        else:
            return f"⚠️ Warning: You have spent more than you earned this month. Your net balance is **-₹{abs(net_savings):,.2f}** (Income ₹{total_income:,.2f} - Expenses ₹{total_expense:,.2f}). Try setting stricter budget limits."

    elif "hello" in msg or "hi " in msg or "hey" in msg:
        return f"Hello {user.name}! I am your AI Financial Coach. Upload a PDF bank statement or manually add transactions, and ask me to analyze your budgets, expenses, savings, or categories!"

    # Default general chatbot query
    transaction_count = len(transactions)
    return (
        f"Hi {user.name}, I'm parsing your question. I currently track {transaction_count} transaction records for you. "
        f"Your net balance is ₹{net_savings:,.2f} (Income ₹{total_income:,.2f} - Expenses ₹{total_expense:,.2f}). "
        f"Ask me about your 'expenses', 'savings', or 'budgets' to get personalized breakdowns!"
    )


@router.post("/chat")
async def chat_with_coach(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch actual user data for prompt context injection
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )
    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == current_user.id)
        .all()
    )

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        # Fallback to local rule-based intelligence
        ai_response = generate_mock_ai_coaching(request.message, current_user, transactions, budgets)
        return {"response": ai_response}

    # Live Call to Gemini API (using standard HTTP request for robustness)
    user_query_emb = await get_embedding(request.message)

    scored_txs = []
    for t in transactions:
        tx_emb = None
        if t.embedding:
            try:
                tx_emb = json.loads(t.embedding)
            except:
                pass
        
        if not tx_emb:
            embed_text = f"Date: {t.transaction_date}, Desc: {t.description}, Amt: {t.amount}, Cat: {t.category}, Type: {t.transaction_type}"
            tx_emb = await get_embedding(embed_text)
            if tx_emb:
                t.embedding = json.dumps(tx_emb)
                db.commit()
                
        score = cosine_similarity(user_query_emb, tx_emb) if tx_emb and user_query_emb else 0.0
        scored_txs.append((score, t))
        
    scored_budgets = []
    for b in budgets:
        b_emb = None
        if b.embedding:
            try:
                b_emb = json.loads(b.embedding)
            except:
                pass
                
        if not b_emb:
            embed_text = f"Category: {b.category}, Budget Limit: {b.amount}"
            b_emb = await get_embedding(embed_text)
            if b_emb:
                b.embedding = json.dumps(b_emb)
                db.commit()
                
        score = cosine_similarity(user_query_emb, b_emb) if b_emb and user_query_emb else 0.0
        scored_budgets.append((score, b))

    scored_txs.sort(key=lambda x: x[0], reverse=True)
    scored_budgets.sort(key=lambda x: x[0], reverse=True)
    
    top_txs = [item[1] for item in scored_txs[:15]]
    top_budgets = [item[1] for item in scored_budgets[:5]]

    tx_context = []
    for t in top_txs:
        tx_context.append(f"Date: {t.transaction_date}, Desc: {t.description}, Amt: {t.amount}, Cat: {t.category}, Type: {t.transaction_type}")

    budget_context = []
    for b in top_budgets:
        budget_context.append(f"Category: {b.category}, Budget Limit: {b.amount}")

    system_instruction = (
        "You are an expert AI Personal Finance Coach. Below is the most relevant data from the user's financial profile. "
        "Use this context to answer their query accurately. Be polite, encouraging, and provide clear breakdowns when requested. "
        "Always output clean formatting (use bold text, bullets, or emojis where appropriate). "
        f"User name: {current_user.name}\n"
        f"Relevant Transactions:\n" + "\n".join(tx_context) + "\n\n"
        f"Relevant Budgets:\n" + "\n".join(budget_context)
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"System Context:\n{system_instruction}\n\nUser Question: {request.message}"}
                ]
            }
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, timeout=20.0)
            if response.status_code == 200:
                result = response.json()
                text_response = result["candidates"][0]["content"]["parts"][0]["text"]
                return {"response": text_response}
            else:
                # API error, fallback
                fallback_response = generate_mock_ai_coaching(request.message, current_user, transactions, budgets)
                return {"response": f"{fallback_response} (Note: Live AI service returned status {response.status_code}, using offline fallback.)"}
    except Exception as e:
        fallback_response = generate_mock_ai_coaching(request.message, current_user, transactions, budgets)
        return {"response": f"{fallback_response} (Note: Offline fallback active due to request error: {str(e)})"}
