<p align="center">
  <h1 align="center">💰 Finance AI Coach</h1>
  <p align="center">
    <strong>Your AI-powered personal finance command center.</strong><br/>
    Analyze bank statements · Track investments · Manage loans · Get AI insights · Gamify your savings
  </p>
  <p align="center">
    <a href="#-features"><img src="https://img.shields.io/badge/Features-30+-blueviolet?style=for-the-badge" alt="Features"></a>
    <a href="#-tech-stack"><img src="https://img.shields.io/badge/Stack-React%20%2B%20FastAPI-00d4aa?style=for-the-badge" alt="Tech Stack"></a>
    <a href="#-getting-started"><img src="https://img.shields.io/badge/Setup-5%20min-orange?style=for-the-badge" alt="Setup"></a>
    <a href="https://github.com/mittal987-alt/ai"><img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"></a>
  </p>
</p>

---

## 📖 Overview

**Finance AI Coach** is a full-stack personal finance platform that goes beyond simple expense tracking. Upload your bank statements and let AI parse, categorize, and analyze every transaction. Set budgets, track investments, manage loans, split bills with friends, scan receipts, and compete in gamified savings challenges — all from a single, beautiful dashboard.

---

## ✨ Features

### 🏦 Core Finance
| Feature | Description |
|---------|-------------|
| **Bank Statement Upload** | Upload PDF bank statements — transactions are auto-extracted, categorized, and stored |
| **Smart Dashboard** | At-a-glance view of income, expenses, savings, and recent transactions |
| **Transaction Management** | Full CRUD with filtering, search, and multi-currency support |
| **Multi-Account Support** | Track Bank, Credit Card, Cash, and UPI Wallet accounts separately |
| **CSV Import** | Bulk-import transactions from any CSV file |

### 🤖 AI & Intelligence
| Feature | Description |
|---------|-------------|
| **AI Chat Assistant** | Ask questions about your finances in natural language (Gemini-powered) |
| **Spending Insights** | Auto-generated category breakdowns and personalized recommendations |
| **Smart Categorization** | AI-powered transaction categorization with embeddings |
| **Daily Brief** | Auto-generated overnight financial snapshot — yesterday's spend, income, category breakdown, and due bills |
| **Smart Alerts** | Budget overrun warnings, unusual spending detection, and critical financial alerts |

### 📊 Planning & Budgets
| Feature | Description |
|---------|-------------|
| **Budget Tracker** | Set category-wise budgets and track adherence in real-time |
| **Budget Planner** | AI-assisted budget planning with recommendations |
| **Savings Goals** | Create goals with target amounts and deadlines, track progress visually |
| **Payment Reminders** | Never miss a bill — supports recurring reminders (daily/weekly/monthly/yearly) |
| **Subscription Manager** | Track all subscriptions, billing cycles, and upcoming renewal dates |

### 💼 Wealth Management
| Feature | Description |
|---------|-------------|
| **Investment Portfolio** | Track Stocks, Mutual Funds, FDs, PPF, Gold, Crypto with P&L analytics |
| **Loan & EMI Tracker** | Manage Home, Car, Personal, Education loans with amortization schedules |
| **Net Worth Dashboard** | Real-time net worth calculation across all accounts, investments, and liabilities |
| **Currency Converter** | Live exchange rates with multi-currency transaction support |
| **Tax Summary** | Estimate tax liability with categorized deductions |

### 🎮 Engagement & Gamification
| Feature | Description |
|---------|-------------|
| **Savings Challenges** | 52-Week Challenge, No-Spend Week, Save 10%, 100-Day Streak |
| **Achievements & Badges** | Unlock achievements for hitting financial milestones |
| **Spending Heatmap** | Calendar-style visualization of daily spending intensity |

### 🔧 Utilities
| Feature | Description |
|---------|-------------|
| **Receipt Scanner** | Upload receipt photos for automatic data extraction |
| **Expense Splitting** | Split bills with friends and track who owes what |
| **PDF Report Export** | Generate downloadable PDF financial reports |
| **Full Data Backup** | Export/import all your financial data |
| **Custom Categories** | Create, rename, and color-code your own spending categories |

### 🔒 Security
- JWT-based authentication (signup, login, protected routes)
- Per-user data isolation — your data is never shared
- Secure file uploads with server-side validation

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | React 19 · TypeScript · Tailwind CSS 4 · MUI 9 · Recharts 3 · Vite 8 |
| **Backend** | FastAPI · Python · SQLAlchemy · Pydantic |
| **Database** | PostgreSQL |
| **AI/ML** | Google Gemini API · Embeddings-based categorization |
| **PDF Processing** | pdfplumber |
| **Scheduling** | APScheduler (nightly daily-brief generation & recurring transactions) |
| **Auth** | JWT (python-jose) · bcrypt |

---

## 📂 Project Structure

```
finance-coach/
├── backend/
│   ├── app/
│   │   ├── main.py                 # FastAPI app entry point & middleware
│   │   ├── database.py             # SQLAlchemy engine & session
│   │   ├── models.py               # 14 ORM models (User → Challenge)
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   ├── routes/                  # 33 API route modules
│   │   │   ├── auth.py             #   signup, login, JWT
│   │   │   ├── upload.py           #   bank statement PDF upload & parse
│   │   │   ├── transaction.py      #   CRUD + search + filters
│   │   │   ├── dashboard.py        #   summary stats
│   │   │   ├── insights.py         #   AI-generated spending insights
│   │   │   ├── chat.py             #   AI financial assistant
│   │   │   ├── budget.py           #   budget CRUD
│   │   │   ├── budget_planner.py   #   AI budget recommendations
│   │   │   ├── goal.py             #   savings goals
│   │   │   ├── subscription.py     #   subscription manager
│   │   │   ├── recurring.py        #   auto-recurring transactions
│   │   │   ├── investments.py      #   portfolio management
│   │   │   ├── loans.py            #   loan & EMI tracker
│   │   │   ├── networth.py         #   net worth calculation
│   │   │   ├── tax.py              #   tax estimation
│   │   │   ├── alerts.py           #   smart financial alerts
│   │   │   ├── reminders.py        #   payment reminders
│   │   │   ├── analytics.py        #   advanced analytics
│   │   │   ├── categorize.py       #   AI categorization
│   │   │   ├── heatmap.py          #   spending heatmap data
│   │   │   ├── gamification.py     #   XP, levels, achievements
│   │   │   ├── challenges.py       #   savings challenges
│   │   │   ├── split.py            #   bill splitting
│   │   │   ├── receipt.py          #   receipt OCR scanning
│   │   │   ├── receipt_store.py    #   receipt image storage
│   │   │   ├── currency.py         #   live exchange rates
│   │   │   ├── categories.py       #   custom categories CRUD
│   │   │   ├── import_csv.py       #   CSV import
│   │   │   ├── pdf_report.py       #   PDF report generation
│   │   │   ├── backup.py           #   full data export/import
│   │   │   ├── daily_brief.py      #   daily financial snapshot
│   │   │   ├── account.py          #   multi-account management
│   │   │   └── report.py           #   reporting endpoints
│   │   └── services/
│   │       ├── parser.py           #   bank statement PDF parser
│   │       ├── auth.py             #   JWT & password utilities
│   │       ├── embeddings.py       #   AI embedding generation
│   │       ├── csv_service.py      #   CSV parsing logic
│   │       ├── currency_service.py #   exchange rate fetching
│   │       ├── pdf_service.py      #   PDF report builder
│   │       └── scheduler.py        #   APScheduler daily jobs
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Router & app shell
│   │   ├── main.tsx                # React entry point
│   │   ├── pages/
│   │   │   ├── dashboard.tsx       # Main dashboard (137 KB of UI!)
│   │   │   ├── Overview.tsx        # Financial overview
│   │   │   ├── Investments.tsx     # Portfolio tracker
│   │   │   ├── Loans.tsx           # Loan & EMI manager
│   │   │   ├── Planner.tsx         # Budget planner
│   │   │   ├── Challenges.tsx      # Gamified savings challenges
│   │   │   ├── RecurringTransactions.tsx
│   │   │   ├── Subscriptions.tsx
│   │   │   ├── Notifications.tsx
│   │   │   ├── DailyBrief.tsx
│   │   │   ├── Goals.tsx
│   │   │   ├── Splits.tsx
│   │   │   ├── Tax.tsx
│   │   │   ├── Calendar.tsx        # Spending heatmap calendar
│   │   │   ├── Accounts.tsx
│   │   │   ├── Achievements.tsx
│   │   │   └── settings.tsx
│   │   ├── components/
│   │   │   ├── Layout.tsx          # App shell, sidebar, navigation
│   │   │   ├── CurrencyWidget.tsx
│   │   │   └── CurrencyConverterWidget.tsx
│   │   └── context/                # React context providers
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

- **Python** 3.10+
- **Node.js** 18+
- **PostgreSQL** 14+
- **Gemini API Key** ([Get one free](https://aistudio.google.com/apikey))

### 1. Clone the Repository

```bash
git clone https://github.com/mittal987-alt/ai.git
cd ai
```

### 2. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

Create a `backend/.env` file:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/finance_coach
GEMINI_API_KEY=your_gemini_api_key_here
```

Start the backend:

```bash
python -m uvicorn app.main:app --reload
```

> Backend runs at **http://127.0.0.1:8000** — API docs at **http://127.0.0.1:8000/docs**

### 3. Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

> Frontend runs at **http://localhost:5173**

---

## 🔌 API Reference

### Authentication
```http
POST   /signup                    # Create a new account
POST   /login                     # Login & receive JWT token
```

### Dashboard & Analytics
```http
GET    /dashboard                 # Summary stats (income, expenses, savings)
GET    /analytics                 # Advanced analytics & trends
GET    /heatmap                   # Daily spending heatmap data
GET    /daily-brief               # Auto-generated daily financial snapshot
```

### Transactions
```http
GET    /transactions              # List with filters & search
POST   /upload-statement          # Upload & parse PDF bank statement
POST   /import-csv                # Bulk import from CSV
POST   /categorize                # AI-powered categorization
```

### Budgets & Planning
```http
GET    /budgets                   # List budgets
POST   /budgets                   # Create a budget
GET    /budget-planner            # AI budget recommendations
```

### Goals & Reminders
```http
GET    /goals                     # List savings goals
POST   /goals                     # Create a savings goal
GET    /reminders                 # List payment reminders
POST   /reminders                 # Create a reminder
```

### Subscriptions & Recurring
```http
GET    /subscriptions             # List subscriptions
POST   /subscriptions             # Add a subscription
GET    /recurring                 # List recurring transactions
POST   /recurring                 # Create a recurring transaction
```

### Wealth Management
```http
GET    /investments               # Portfolio overview
POST   /investments               # Add an investment
GET    /loans                     # Loan list & amortization
POST   /loans                     # Add a loan
GET    /networth                  # Net worth calculation
GET    /tax                       # Tax summary
GET    /currency                  # Live exchange rates
```

### AI Features
```http
POST   /chat                      # AI financial assistant (Gemini)
GET    /insights                  # AI-generated spending insights
GET    /alerts                    # Smart financial alerts
```

### Gamification
```http
GET    /gamification              # XP, level, achievements
GET    /challenges                # Active savings challenges
POST   /challenges                # Start a new challenge
```

### Utilities
```http
POST   /receipt/scan              # OCR receipt scanning
GET    /accounts                  # Multi-account management
POST   /split                     # Split a bill
GET    /report/pdf                # Download PDF report
GET    /backup/export             # Full data export
POST   /backup/import             # Full data import
GET    /categories                # Custom categories
```

---

## 🖥 Screenshots

> *Coming soon — contribute screenshots by opening a PR!*

---

## 🗺 Roadmap

- [ ] Real-time stock price integration
- [ ] Monthly/weekly spending trend charts
- [ ] Push notifications (FCM/Web Push)
- [ ] Mobile app (React Native)
- [ ] Email financial digest reports
- [ ] Multi-bank API integration (Account Aggregator)
- [ ] Mutual fund SIP recommendations
- [ ] Dark mode toggle in settings

---

## 🤝 Contributing

Contributions are welcome! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Aayush Mittal**

B.Tech Student · Full Stack Developer

[![GitHub](https://img.shields.io/badge/GitHub-mittal987--alt-181717?style=flat-square&logo=github)](https://github.com/mittal987-alt)

---

<p align="center">
  Built with ❤️ using React, FastAPI, PostgreSQL, and Gemini AI
</p>
