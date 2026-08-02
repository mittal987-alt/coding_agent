import React, { useState } from "react";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend
} from "recharts";
import { useFinance } from "../context/FinanceContext";
import { CurrencyConverterWidget } from "../components/CurrencyConverterWidget";
import { API_URL } from "../config";

const Overview: React.FC = () => {
  const {
    data,
    transactions,
    insights,
    userEmail,
    budgets,
    setBudgetCategory,
    budgetCategory,
    setBudgetAmount,
    budgetAmount,
    handleBudgetSubmit,
    handleBudgetDelete,
    trendsData,
    netWorth,
    healthScore,
    heatmapData,
    reminders,
    setShowReminderModal,
    handleReminderPay,
    handleReminderDelete,
    filterSearch,
    setFilterSearch,
    filterCategory,
    setFilterCategory,
    filterType,
    setFilterType,
    handleAutoCategorize,
    isAutoCatting,
    autoCatResult,
    setAutoCatResult,
    setTxModalMode,
    setTxDescription,
    setTxAmount,
    setTxCategory,
    setTxType,
    setTxDate,
    setShowTxModal,
    openEditTxModal,
    handleTxDelete,
    handleBulkDelete,
    handleBulkRecategorize,
    scanReceipt,
    isScanningReceipt,
    trash = [],
    handleRestoreTransaction = async () => { },
    handlePurgeTrash = async () => { },
    filteredTransactions,
    categories
  } = useFinance() as any;

  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [bulkCategory, setBulkCategory] = useState("");
  const [showTrashPanel, setShowTrashPanel] = useState(false);

  const toggleSelect = (id: number) => {
    setSelectedIds(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);
  };

  const toggleSelectAll = (ids: number[]) => {
    setSelectedIds(prev => prev.length === ids.length ? [] : ids);
  };

  // Ledger palette: teal / coral / gold / blue
  const chartColors = ["#0F6E56", "#D85A30", "#BA7517", "#378ADD"];

  const chartData = [
    { name: "Food", value: insights?.food || 0 },
    { name: "Travel", value: insights?.travel || 0 },
    { name: "Shopping", value: insights?.shopping || 0 }
  ].filter(item => item.value > 0);

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <div className="w-10 h-10 border-2 border-stone-300 dark:border-stone-700 border-t-teal-700 dark:border-t-teal-400 rounded-full animate-spin mb-4"></div>
        <p className="text-stone-500 dark:text-stone-400 font-serif text-lg">Opening the ledger…</p>
      </div>
    );
  }

  return (
    <>
      <div className="mb-7">
        <h2 className="font-serif font-bold text-2xl text-stone-900 dark:text-stone-50">Overview</h2>
        <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-0.5">Where your money stands today</p>
      </div>

      {/* Summary Statistics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-5 mb-7">
        <StatCard label="Income" value={data.income} icon="up" accent="teal" sub="Total earnings" />
        <StatCard label="Expenses" value={data.expense} icon="down" accent="coral" sub="Total spending" />
        <StatCard label="Net savings" value={data.savings} icon="check" accent="blue" sub="Remaining balance" />
        <StatCard label="Transactions" value={transactions.length} icon="list" accent="gold" sub="Processed records" isCount />
        <div className="bg-teal-800 dark:bg-teal-950 text-white rounded-xl p-5">
          <div className="flex justify-between items-start mb-3">
            <span className="text-[11px] font-bold uppercase tracking-wider opacity-80">Net worth</span>
            <div className="bg-white/15 text-white p-2 rounded-lg">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.25} stroke="currentColor" className="w-4 h-4">
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.33l-7.5-5-7.5 5V21" />
              </svg>
            </div>
          </div>
          <p className="text-2xl font-mono font-bold">₹{netWorth?.net_worth?.toLocaleString("en-IN") || 0}</p>
          <p className="text-[11px] font-medium mt-1.5 opacity-75">Assets ₹{netWorth?.total_assets?.toLocaleString("en-IN") || 0}</p>
        </div>
      </div>

      {/* Financial Health Score Widget */}
      {userEmail && healthScore && (
        <div className="bg-teal-800 dark:bg-teal-950 rounded-2xl p-6 sm:p-7 mb-7 text-white">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="flex-shrink-0 flex flex-col items-center">
              <div className="relative w-28 h-28">
                <svg viewBox="0 0 36 36" className="w-28 h-28 -rotate-90">
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth="3" />
                  <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#F5C95A" strokeWidth="3" strokeDasharray={`${healthScore.score}, 100`} strokeLinecap="round" />
                </svg>
                <div className="absolute inset-0 flex flex-col items-center justify-center">
                  <span className="text-3xl font-mono font-bold">{healthScore.score}</span>
                  <span className="text-[10px] opacity-70">/ 100</span>
                </div>
              </div>
              <p className="text-[11px] font-bold mt-2 opacity-80 uppercase tracking-widest">
                {healthScore.score >= 80 ? "Excellent" : healthScore.score >= 60 ? "Good" : healthScore.score >= 40 ? "Fair" : "Needs work"}
              </p>
            </div>

            <div className="flex-1 space-y-3 w-full">
              <div>
                <h2 className="text-xl font-serif font-bold mb-1">Financial health score</h2>
                <p className="text-xs text-white/70 font-medium">{healthScore.advice}</p>
              </div>
              <div className="grid grid-cols-3 gap-3 mt-4">
                <div className="bg-white/10 rounded-lg p-3 text-center">
                  <p className="text-2xl font-mono font-bold">{healthScore.savings_score}</p>
                  <p className="text-[10px] font-bold opacity-70 mt-0.5">Savings / 40</p>
                </div>
                <div className="bg-white/10 rounded-lg p-3 text-center">
                  <p className="text-2xl font-mono font-bold">{healthScore.budget_score}</p>
                  <p className="text-[10px] font-bold opacity-70 mt-0.5">Budget / 40</p>
                </div>
                <div className="bg-white/10 rounded-lg p-3 text-center">
                  <p className="text-2xl font-mono font-bold">{healthScore.goals_score}</p>
                  <p className="text-[10px] font-bold opacity-70 mt-0.5">Goals / 20</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Currency Converter Widget */}
      <CurrencyConverterWidget />

      {/* Monthly Trend Area Chart */}
      {userEmail && trendsData && trendsData.length > 0 && (
        <SectionCard title="Cash flow, month by month" desc="Income against expenses over time">
          <div style={{ width: "100%", height: 300 }}>
            <ResponsiveContainer>
              <AreaChart data={trendsData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0F6E56" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#0F6E56" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorExpense" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#D85A30" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#D85A30" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E7E2D6" className="dark:hidden" />
                <CartesianGrid strokeDasharray="3 3" stroke="#2A2A26" className="hidden dark:block" />
                <XAxis dataKey="month" stroke="#A8A296" fontSize={11} tickLine={false} />
                <YAxis stroke="#A8A296" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `₹${val}`} />
                <Tooltip formatter={(value) => [`₹${value}`, ""]} />
                <Legend verticalAlign="top" height={32} />
                <Area name="Income" type="monotone" dataKey="income" stroke="#0F6E56" strokeWidth={2} fillOpacity={1} fill="url(#colorIncome)" />
                <Area name="Expense" type="monotone" dataKey="expense" stroke="#D85A30" strokeWidth={2} fillOpacity={1} fill="url(#colorExpense)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </SectionCard>
      )}

      {/* Dashboard Middle Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-7 mt-7">
        {/* AI Insights */}
        <SectionCard title="AI coach insights" desc="What your data is telling you">
          {insights && insights.insights && insights.insights.length > 0 ? (
            <div className="space-y-3">
              {insights.insights.map((item: string, index: number) => {
                const isWarning = item.includes("⚠") || item.toLowerCase().includes("high") || item.toLowerCase().includes("limit");
                return (
                  <div key={index} className={`flex gap-3 p-3.5 rounded-lg border-l-4 ${isWarning ? "bg-amber-50 dark:bg-amber-950/20 border-amber-500 text-amber-900 dark:text-amber-300" : "bg-teal-50 dark:bg-teal-950/10 border-teal-500 text-teal-900 dark:text-teal-300"}`}>
                    <p className="text-sm font-semibold leading-relaxed">{item.replace("⚠ ", "").replace("✅ ", "")}</p>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState text="No insights yet." sub="Upload a statement or log entries to trigger analysis." />
          )}
        </SectionCard>

        {/* Expense Share */}
        <SectionCard title="Expense share" desc="Where this period's spending went">
          {chartData.length > 0 ? (
            <>
              <div style={{ width: "100%", height: 170 }} className="flex justify-center items-center mb-3">
                <ResponsiveContainer>
                  <PieChart>
                    <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} innerRadius={46} paddingAngle={3}>
                      {chartData.map((_entry, index) => <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />)}
                    </Pie>
                    <Tooltip formatter={(value) => [`₹${value}`, "Spent"]} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="space-y-2.5">
                {chartData.map((category, index) => {
                  const totalSpent = insights?.food + insights?.travel + insights?.shopping || 1;
                  const percentage = (category.value / totalSpent) * 100;
                  return (
                    <div key={category.name} className="flex flex-col gap-1">
                      <div className="flex justify-between items-center text-xs font-bold text-stone-700 dark:text-stone-300">
                        <span className="flex items-center gap-1.5">
                          <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: chartColors[index % chartColors.length] }}></span>
                          {category.name}
                        </span>
                        <span className="font-mono">₹{category.value?.toLocaleString("en-IN")} ({percentage.toFixed(0)}%)</span>
                      </div>
                      <div className="w-full bg-stone-100 dark:bg-stone-800 rounded-full h-1.5">
                        <div className="h-1.5 rounded-full transition-all" style={{ backgroundColor: chartColors[index % chartColors.length], width: `${percentage}%` }}></div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </>
          ) : (
            <EmptyState text="No expenditure records." sub="Check back once a statement is processed." />
          )}
        </SectionCard>

        {/* Category Budgets */}
        <SectionCard title="Category budgets" desc="Targets you've set">
          {budgets.length > 0 ? (
            <div className="space-y-4 mb-5">
              {budgets.map((b: any) => {
                const categorySpent = transactions.filter((t: any) => t.category === b.category && t.transaction_type === "expense").reduce((sum: number, t: any) => sum + t.amount, 0);
                const percentage = Math.min((categorySpent / b.amount) * 100, 100);
                const isExceeded = categorySpent > b.amount;
                const isClose = categorySpent > b.amount * 0.8 && !isExceeded;
                return (
                  <div key={b.id} className="group flex flex-col gap-1">
                    <div className="flex justify-between items-center text-xs font-bold text-stone-700 dark:text-stone-350">
                      <span className="flex items-center gap-1.5">
                        {b.category}
                        <button onClick={() => handleBudgetDelete(b.id)} className="opacity-0 group-hover:opacity-100 text-coral-500 hover:text-coral-600 transition-all font-bold ml-1 cursor-pointer bg-transparent border-none" title="Delete budget">✕</button>
                      </span>
                      <span className="font-mono">₹{categorySpent.toLocaleString("en-IN")} / ₹{b.amount.toLocaleString("en-IN")}</span>
                    </div>
                    <div className="w-full bg-stone-100 dark:bg-stone-850 rounded-full h-2 overflow-hidden">
                      <div className={`h-2 rounded-full transition-all duration-500 ${isExceeded ? "bg-coral-500" : isClose ? "bg-amber-500" : "bg-teal-600"}`} style={{ width: `${percentage}%` }}></div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <EmptyState text="No budgets defined." sub="Use the form below to set target limits." />
          )}

          {userEmail && (
            <form onSubmit={handleBudgetSubmit} className="bg-stone-50 dark:bg-stone-950/40 border border-stone-100 dark:border-stone-850 rounded-lg p-3 mt-2">
              <p className="text-[11px] font-extrabold text-stone-500 dark:text-stone-400 mb-2 uppercase tracking-wide">Set category budget</p>
              <div className="flex gap-2">
                <select
                  value={budgetCategory}
                  onChange={(e) => setBudgetCategory(e.target.value)}
                  className="text-xs w-full bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-md p-1.5 focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200 cursor-pointer"
                >
                  {categories.map((c: any) => <option key={c.id} value={c.name}>{c.name}</option>)}
                </select>
                <input
                  type="number"
                  required
                  value={budgetAmount}
                  onChange={(e) => setBudgetAmount(e.target.value)}
                  placeholder="Amount"
                  className="text-xs w-full bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-md p-1.5 focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200"
                />
                <button type="submit" className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold px-3 py-1.5 rounded-md cursor-pointer transition-all border-none">Save</button>
              </div>
            </form>
          )}
        </SectionCard>
      </div>

      {/* Daily Spending Heatmap & Payment Reminders */}
      {userEmail && (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-7">
          {/* 90-Day Spending Heatmap */}
          <div className="lg:col-span-2">
            <SectionCard
              title="90-day spending heatmap"
              desc="Daily spending intensity, last 3 months"
              action={
                heatmapData && heatmapData.days && (
                  <div className="text-right text-xs">
                    <p className="font-mono font-bold text-stone-700 dark:text-stone-350">Avg ₹{heatmapData.avg_daily_spend?.toLocaleString("en-IN")}/day</p>
                    <p className="font-mono text-stone-450">Total ₹{heatmapData.total_spend_90d?.toLocaleString("en-IN")}</p>
                  </div>
                )
              }
            >
              {heatmapData && heatmapData.days ? (
                <div className="flex flex-col items-start overflow-x-auto pb-2">
                  <div className="flex gap-1">
                    {Array.from({ length: 13 }).map((_, weekIdx) => {
                      const weekDays = heatmapData.days.filter((d: any) => d.week === weekIdx);
                      return (
                        <div key={weekIdx} className="flex flex-col gap-1">
                          {weekIdx === 0 && weekDays.length > 0 && Array.from({ length: weekDays[0].day_of_week }).map((_, padIdx) => (
                            <div key={`pad-${padIdx}`} className="w-3.5 h-3.5 rounded bg-transparent"></div>
                          ))}
                          {weekDays.map((day: any) => {
                            const levelColors = ["bg-stone-100 dark:bg-stone-800", "bg-teal-100 dark:bg-teal-950/60", "bg-teal-300 dark:bg-teal-900/80", "bg-teal-500 dark:bg-teal-700", "bg-teal-700 dark:bg-teal-500"];
                            return <div key={day.date} className={`w-3.5 h-3.5 rounded transition-all cursor-pointer ${levelColors[day.level]}`} title={`${day.date}: ₹${day.amount?.toLocaleString("en-IN")} spent`}></div>;
                          })}
                        </div>
                      );
                    })}
                  </div>
                  <div className="flex justify-between w-full mt-4 text-[10px] text-stone-450 dark:text-stone-500 font-bold px-1">
                    <span>90 days ago</span>
                    <div className="flex items-center gap-1">
                      <span>Less</span>
                      <div className="w-2.5 h-2.5 rounded bg-stone-100 dark:bg-stone-800"></div>
                      <div className="w-2.5 h-2.5 rounded bg-teal-100 dark:bg-teal-950/60"></div>
                      <div className="w-2.5 h-2.5 rounded bg-teal-300 dark:bg-teal-900/80"></div>
                      <div className="w-2.5 h-2.5 rounded bg-teal-500"></div>
                      <div className="w-2.5 h-2.5 rounded bg-teal-700 dark:bg-teal-500"></div>
                      <span>More</span>
                    </div>
                    <span>Today</span>
                  </div>
                </div>
              ) : (
                <EmptyState text="Loading heatmap…" sub="" />
              )}
            </SectionCard>
          </div>

          {/* Bill Reminders */}
          <SectionCard
            title="Bill reminders"
            desc="Upcoming and overdue payments"
            action={
              <button
                onClick={() => setShowReminderModal(true)}
                className="bg-teal-50 hover:bg-teal-100 dark:bg-teal-950/40 dark:hover:bg-teal-900/60 text-teal-700 dark:text-teal-400 text-xs font-bold py-1.5 px-3 rounded-md transition-all cursor-pointer border-none"
              >
                + Add
              </button>
            }
          >
            {reminders && reminders.length > 0 ? (
              <div className="space-y-3 max-h-[280px] overflow-y-auto pr-1">
                {reminders.map((r: any) => {
                  const urgencyStyle: Record<string, string> = {
                    overdue: "bg-coral-50 dark:bg-coral-950/20 border-coral-100 dark:border-coral-900 text-coral-700 dark:text-coral-450",
                    urgent: "bg-amber-50 dark:bg-amber-950/20 border-amber-100 dark:border-amber-900 text-amber-700 dark:text-amber-400",
                    soon: "bg-teal-50 dark:bg-teal-950/20 border-teal-100 dark:border-teal-900 text-teal-700 dark:text-teal-400",
                    ok: "bg-stone-50 dark:bg-stone-800/50 border-stone-100 dark:border-stone-700 text-stone-650 dark:text-stone-350"
                  };
                  const style = urgencyStyle[r.urgency] || urgencyStyle.ok;
                  return (
                    <div key={r.id} className={`p-3 rounded-lg border flex justify-between items-center text-xs font-medium ${style}`}>
                      <div className="min-w-0 flex-1">
                        <p className="font-bold truncate">{r.name}</p>
                        <p className="opacity-85 font-mono font-semibold">₹{r.amount?.toLocaleString("en-IN")} • {r.due_date}</p>
                        <p className="text-[10px] font-bold mt-0.5">
                          {r.is_paid ? "Paid" : r.days_left < 0 ? `Overdue by ${Math.abs(r.days_left)} days` : r.days_left === 0 ? "Due today" : `${r.days_left} days remaining`}
                        </p>
                      </div>
                      <div className="flex gap-1.5 ml-2">
                        {!r.is_paid && (
                          <button onClick={() => handleReminderPay(r.id)} className="bg-white/80 dark:bg-stone-800 hover:bg-white dark:hover:bg-stone-700 px-2 py-1 rounded-md border border-current font-black text-[9px] cursor-pointer">Pay</button>
                        )}
                        <button onClick={() => handleReminderDelete(r.id)} className="hover:text-coral-600 cursor-pointer p-1 text-stone-400 font-bold bg-transparent border-none" title="Delete">✕</button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <EmptyState text="No bill reminders set." sub="Click Add to get started." />
            )}
          </SectionCard>
        </div>
      )}

      {/* Transactions Table Section */}
      <SectionCard
        title="Transaction history"
        desc={`${filteredTransactions.length} of ${transactions.length} total`}
        action={
          userEmail && (
            <div className="flex flex-wrap gap-2 justify-end">
              <button
                onClick={handleAutoCategorize}
                disabled={isAutoCatting}
                className="bg-stone-800 dark:bg-stone-700 hover:bg-stone-900 disabled:bg-stone-400 text-white text-xs font-bold py-2 px-3.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer border-none"
              >
                {isAutoCatting ? (
                  <><span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>Categorizing…</>
                ) : "Auto-categorize"}
              </button>
              <input
                id="receipt-upload"
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  const file = e.target.files?.[0];
                  if (file) scanReceipt(file);
                  e.target.value = "";
                }}
              />
              <button
                onClick={() => document.getElementById("receipt-upload")?.click()}
                disabled={isScanningReceipt}
                className="bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 hover:bg-stone-50 disabled:opacity-60 text-stone-600 dark:text-stone-300 text-xs font-bold py-2 px-3.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer"
              >
                {isScanningReceipt ? (
                  <><span className="w-3.5 h-3.5 border-2 border-stone-400 border-t-transparent rounded-full animate-spin"></span>Scanning…</>
                ) : (
                  <>
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.822 1.316Z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z" />
                    </svg>
                    Scan receipt
                  </>
                )}
              </button>
              <input
                id="csv-upload"
                type="file"
                accept=".csv"
                className="hidden"
                onChange={async (e) => {
                  const file = e.target.files?.[0];
                  if (!file) return;
                  const token = localStorage.getItem("token");
                  const formData = new FormData();
                  formData.append("file", file);
                  try {
                    const res = await fetch(`${API_URL}/import/csv`, {
                      method: "POST",
                      headers: { Authorization: `Bearer ${token}` },
                      body: formData,
                    });
                    const data = await res.json();
                    alert(data.message || "Import complete");
                    window.location.reload();
                  } catch (err) {
                    console.error(err);
                    alert("Failed to upload CSV");
                  }
                }}
              />
              <button
                onClick={() => document.getElementById("csv-upload")?.click()}
                className="bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 hover:bg-stone-50 text-stone-600 dark:text-stone-300 text-xs font-bold py-2 px-3.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
                </svg>
                Import CSV
              </button>
              <button
                onClick={() => {
                  setTxModalMode("add");
                  setTxDescription("");
                  setTxAmount("");
                  setTxCategory("Shopping");
                  setTxType("expense");
                  setTxDate(new Date().toISOString().split("T")[0]);
                  setShowTxModal(true);
                }}
                className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2 px-3.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer border-none"
              >
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                </svg>
                Add transaction
              </button>
            </div>
          )
        }
      >
        {/* Filters Bar */}
        <div className="flex flex-col md:flex-row gap-3 mb-5">
          <input
            type="text"
            placeholder="Search descriptions…"
            value={filterSearch}
            onChange={(e) => setFilterSearch(e.target.value)}
            className="bg-stone-50 dark:bg-stone-950 border border-stone-200 dark:border-stone-800 rounded-lg px-4 py-2 text-xs focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200 w-full sm:w-56"
          />
          <select
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            className="bg-stone-50 dark:bg-stone-950 border border-stone-200 dark:border-stone-800 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200 cursor-pointer"
          >
            <option value="All">All categories</option>
            {categories.map((c: any) => <option key={c.id} value={c.name}>{c.name}</option>)}
          </select>
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="bg-stone-50 dark:bg-stone-950 border border-stone-200 dark:border-stone-800 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200 cursor-pointer"
          >
            <option value="All">All types</option>
            <option value="income">Income</option>
            <option value="expense">Expense</option>
          </select>
        </div>

        {selectedIds.length > 0 && (
          <div className="mb-5 bg-teal-50 dark:bg-teal-950/30 border border-teal-100 dark:border-teal-900 rounded-lg p-3 flex flex-wrap items-center gap-3">
            <span className="text-xs font-bold text-teal-800 dark:text-teal-300">{selectedIds.length} selected</span>
            <div className="flex items-center gap-2">
              <select
                value={bulkCategory}
                onChange={(e) => setBulkCategory(e.target.value)}
                className="bg-white dark:bg-stone-900 border border-teal-200 dark:border-teal-800 rounded-md px-2 py-1.5 text-xs text-stone-700 dark:text-stone-200 cursor-pointer"
              >
                <option value="">Recategorize to…</option>
                {categories.map((c: any) => <option key={c.id} value={c.name}>{c.name}</option>)}
              </select>
              <button
                onClick={() => { if (bulkCategory) { handleBulkRecategorize(selectedIds, bulkCategory); setSelectedIds([]); setBulkCategory(""); } }}
                disabled={!bulkCategory}
                className="bg-teal-700 hover:bg-teal-800 disabled:bg-teal-300 text-white text-xs font-bold py-1.5 px-3 rounded-md transition-all cursor-pointer border-none"
              >
                Apply
              </button>
            </div>
            <button
              onClick={() => { handleBulkDelete(selectedIds); setSelectedIds([]); }}
              className="bg-coral-600 hover:bg-coral-700 text-white text-xs font-bold py-1.5 px-3 rounded-md transition-all cursor-pointer border-none ml-auto"
            >
              Delete selected
            </button>
            <button
              onClick={() => setSelectedIds([])}
              className="text-xs font-bold text-stone-500 hover:text-stone-700 bg-transparent border-none cursor-pointer"
            >
              Clear
            </button>
          </div>
        )}

        {autoCatResult && (
          <div className="mb-5 bg-stone-100 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-lg p-3 flex justify-between items-center text-xs text-stone-700 dark:text-stone-300">
            <span className="font-semibold">{autoCatResult.message}</span>
            <button onClick={() => setAutoCatResult(null)} className="font-bold text-teal-700 dark:text-teal-400 hover:underline cursor-pointer bg-transparent border-none">Dismiss</button>
          </div>
        )}

        <div className="overflow-x-auto -mx-1">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-stone-200 dark:border-stone-800 text-stone-400 dark:text-stone-500 text-[11px] font-bold uppercase tracking-wider">
                {userEmail && (
                  <th className="pb-3 pl-1 w-8">
                    <input
                      type="checkbox"
                      checked={filteredTransactions.length > 0 && selectedIds.length === filteredTransactions.length}
                      onChange={() => toggleSelectAll(filteredTransactions.map((t: any) => t.id))}
                      className="w-3.5 h-3.5 accent-teal-700 cursor-pointer"
                    />
                  </th>
                )}
                <th className="pb-3 pl-1">Date</th>
                <th className="pb-3">Description</th>
                <th className="pb-3">Category</th>
                <th className="pb-3 text-right pr-1">Amount</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100 dark:divide-stone-850 text-sm font-medium text-stone-700 dark:text-stone-300">
              {filteredTransactions.length > 0 ? (
                filteredTransactions.map((t: any) => {
                  const isIncome = t.transaction_type === "income" || t.category === "Income";
                  return (
                    <tr key={t.id} className="hover:bg-stone-50/60 dark:hover:bg-stone-850/30 transition-colors group">
                      {userEmail && (
                        <td className="py-3.5 pl-1">
                          <input
                            type="checkbox"
                            checked={selectedIds.includes(t.id)}
                            onChange={() => toggleSelect(t.id)}
                            className="w-3.5 h-3.5 accent-teal-700 cursor-pointer"
                          />
                        </td>
                      )}
                      <td className="py-3.5 pl-1 text-xs font-mono text-stone-500 dark:text-stone-400">{t.transaction_date}</td>
                      <td className="py-3.5 font-semibold text-stone-800 dark:text-stone-200">{t.description}</td>
                      <td className="py-3.5"><CategoryPill category={t.category} isIncome={isIncome} categories={categories} /></td>
                      <td className={`py-3.5 text-right pr-1 font-mono font-bold ${isIncome ? "text-teal-700 dark:text-teal-450" : "text-stone-800 dark:text-stone-200"}`}>
                        <span className="mr-3">{isIncome ? "+" : "−"}₹{t.amount?.toLocaleString("en-IN") || 0}</span>
                        {userEmail && (
                          <span className="inline-flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                            <button onClick={() => openEditTxModal(t)} className="text-stone-400 hover:text-teal-700 dark:hover:text-teal-400 cursor-pointer bg-transparent border-none" title="Edit">
                              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                                <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.128-1.897L16.863 4.487Zm0 0L19.5 7.125" />
                              </svg>
                            </button>
                            <button onClick={() => handleTxDelete(t.id)} className="text-stone-400 hover:text-coral-600 cursor-pointer bg-transparent border-none" title="Delete">
                              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                                <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.34 9m-4.72 0-.34-9m9.03-3.03a17.902 17.902 0 0 1-1.07 3.5M18.13 6a22.09 22.09 0 0 0-1.85-.3M14.74 9a22.38 22.38 0 0 0-5.48 0M10.5 6.857V5.07c0-.704.57-1.286 1.27-1.286h2.46c.7 0 1.27.582 1.27 1.286v1.787M3.75 6a17.925 17.925 0 0 1 1.07-3.5M6.37 6a22.09 22.09 0 0 1 1.85-.3M6.37 6a22.38 22.38 0 0 1 5.48 0" />
                              </svg>
                            </button>
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={userEmail ? 5 : 4} className="text-center py-12 text-stone-400 dark:text-stone-500 font-medium">No matching transaction records found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </SectionCard>

      {/* Recently Deleted — safety net for undo/soft-delete */}
      {userEmail && trash.length > 0 && (
        <div className="mt-5 bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm overflow-hidden">
          <button
            onClick={() => setShowTrashPanel(v => !v)}
            className="w-full flex items-center justify-between px-5 py-3.5 bg-transparent border-none cursor-pointer text-left"
          >
            <span className="text-sm font-serif font-bold text-stone-700 dark:text-stone-300">
              Recently deleted ({trash.length})
            </span>
            <span className="text-xs text-stone-400">{showTrashPanel ? "Hide" : "Show"}</span>
          </button>
          {showTrashPanel && (
            <div className="border-t border-stone-100 dark:border-stone-850 divide-y divide-stone-50 dark:divide-stone-850">
              {trash.map((t: any) => (
                <div key={t.id} className="flex items-center justify-between px-5 py-3 text-sm">
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold text-stone-700 dark:text-stone-300 truncate">{t.description}</p>
                    <p className="text-[11px] text-stone-450 font-mono">
                      {t.transaction_type === "income" ? "+" : "−"}₹{t.amount?.toLocaleString("en-IN")} • {t.transaction_date} • {t.category}
                    </p>
                  </div>
                  <div className="flex gap-2 ml-3 shrink-0">
                    <button
                      onClick={() => handleRestoreTransaction(t.id)}
                      className="text-xs font-bold text-teal-700 hover:text-teal-800 bg-teal-50 dark:bg-teal-950/30 dark:text-teal-400 px-2.5 py-1.5 rounded-md border-none cursor-pointer"
                    >
                      Restore
                    </button>
                    <button
                      onClick={() => handlePurgeTrash(t.id)}
                      className="text-xs font-bold text-coral-600 hover:text-coral-700 bg-transparent border-none cursor-pointer px-1"
                      title="Permanently delete"
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </>
  );
};

/* ============================================================================
   Shared presentational helpers — keep in sync with Layout.tsx's design system
   ========================================================================= */

function StatCard({ label, value, icon, accent, sub, isCount }: { label: string; value: number; icon: "up" | "down" | "check" | "list"; accent: "teal" | "coral" | "blue" | "gold"; sub: string; isCount?: boolean }) {
  const accentMap: Record<string, { border: string; text: string; bg: string }> = {
    teal: { border: "border-l-teal-600", text: "text-teal-700 dark:text-teal-400", bg: "bg-teal-50 dark:bg-teal-950/30" },
    coral: { border: "border-l-coral-500", text: "text-coral-700 dark:text-coral-400", bg: "bg-coral-50 dark:bg-coral-950/30" },
    blue: { border: "border-l-blue-500", text: "text-blue-700 dark:text-blue-400", bg: "bg-blue-50 dark:bg-blue-950/30" },
    gold: { border: "border-l-amber-500", text: "text-amber-700 dark:text-amber-400", bg: "bg-amber-50 dark:bg-amber-950/30" }
  };
  const c = accentMap[accent];
  const paths: Record<string, React.ReactNode> = {
    up: <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.28m5.94 2.28-2.28 5.941" />,
    down: <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6 9 12.75l4.306-4.307a11.95 11.95 0 0 1 5.814 5.519l2.74 1.22m0 0-5.94 2.281m5.94-2.28-2.28 5.941" />,
    check: <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM9 12.75 11.25 15 15 9.75" />,
    list: <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75Zm.007 8.25H3.75v-.008h.008V15Zm-.008 3h.008v.008H3.75V18Z" />
  };
  return (
    <div className={`bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 border-l-4 ${c.border} shadow-sm p-5`}>
      <div className="flex justify-between items-start mb-3">
        <span className="text-[11px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider">{label}</span>
        <div className={`${c.bg} ${c.text} p-2 rounded-lg`}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.25} stroke="currentColor" className="w-4 h-4">{paths[icon]}</svg>
        </div>
      </div>
      <p className="text-2xl font-mono font-bold text-stone-850 dark:text-stone-100">{isCount ? value : `₹${(value || 0).toLocaleString("en-IN")}`}</p>
      <p className="text-[11px] text-stone-450 dark:text-stone-500 font-medium mt-1.5">{sub}</p>
    </div>
  );
}

function SectionCard({ title, desc, action, children }: { title: string; desc?: string; action?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-5 sm:p-6">
      <div className="flex flex-wrap justify-between items-start gap-3 mb-5">
        <div>
          <h2 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100">{title}</h2>
          {desc && <p className="text-xs text-stone-450 dark:text-stone-550 mt-0.5">{desc}</p>}
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}

function EmptyState({ text, sub }: { text: string; sub: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-10 bg-stone-50/60 dark:bg-stone-900/40 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
      <p className="text-sm text-stone-500 dark:text-stone-400 font-semibold">{text}</p>
      {sub && <p className="text-xs text-stone-400 dark:text-stone-500 mt-1 text-center px-6">{sub}</p>}
    </div>
  );
}

function CategoryPill({ category, isIncome, categories }: { category: string; isIncome: boolean; categories: { id: number; name: string; color: string }[] }) {
  const match = categories.find(c => c.name === category);
  const dotColor = isIncome ? "#0F6E56" : (match?.color || "#8A8F98");
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-300">
      <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ backgroundColor: dotColor }}></span>
      {category}
    </span>
  );
}

export default Overview;
