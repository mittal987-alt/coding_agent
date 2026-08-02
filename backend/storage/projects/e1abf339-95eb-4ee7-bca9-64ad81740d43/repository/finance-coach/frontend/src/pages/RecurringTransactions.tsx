import React, { useState, useEffect } from "react";
import { useFinance } from "../context/FinanceContext";
import { API_URL } from "../config";

const API = API_URL;

const FREQUENCIES = ["daily", "weekly", "monthly", "yearly"];

const freq_label: Record<string, string> = {
  daily: "Daily", weekly: "Weekly", monthly: "Monthly", yearly: "Yearly"
};

const RecurringTransactions: React.FC = () => {
  const { userEmail, setShowAuthModal, setAuthMode, confirmAction, showToast, supportedCurrencies, categories } = useFinance();
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [triggering, setTriggering] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);

  // Form state
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [category, setCategory] = useState("Others");
  const [txType, setTxType] = useState("expense");
  const [frequency, setFrequency] = useState("monthly");
  const [nextDate, setNextDate] = useState(new Date().toISOString().split("T")[0]);
  const [isActive, setIsActive] = useState(true);
  const [currency, setCurrency] = useState("INR");

  const token = () => localStorage.getItem("token");
  const headers = () => ({ Authorization: `Bearer ${token()}`, "Content-Type": "application/json" });

  const load = async () => {
    if (!token()) { setLoading(false); return; }
    setLoading(true);
    try {
      const res = await fetch(`${API}/recurring/`, { headers: { Authorization: `Bearer ${token()}` } });
      if (res.ok) setItems(await res.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { load(); }, [userEmail]);

  const openCreate = () => {
    setEditId(null);
    setDescription(""); setAmount(""); setCategory("Others"); setTxType("expense");
    setFrequency("monthly"); setNextDate(new Date().toISOString().split("T")[0]); setIsActive(true);
    setCurrency("INR");
    setShowModal(true);
  };

  const openEdit = (item: any) => {
    setEditId(item.id);
    setDescription(item.description); setAmount(String(item.original_amount ?? item.amount));
    setCategory(item.category); setTxType(item.transaction_type);
    setFrequency(item.frequency); setNextDate(item.next_date); setIsActive(item.is_active);
    setCurrency(item.currency || "INR");
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = { description, amount: parseFloat(amount), category, transaction_type: txType, frequency, next_date: nextDate, is_active: isActive, currency };
    const url = editId ? `${API}/recurring/${editId}` : `${API}/recurring/`;
    const method = editId ? "PUT" : "POST";
    try {
      const res = await fetch(url, { method, headers: headers(), body: JSON.stringify(payload) });
      if (res.ok) { setShowModal(false); load(); }
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirmAction("Delete this recurring transaction?"))) return;
    try {
      await fetch(`${API}/recurring/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token()}` } });
      load();
    } catch (e) { console.error(e); }
  };

  const handleTrigger = async () => {
    setTriggering(true);
    try {
      const res = await fetch(`${API}/recurring/trigger`, { method: "POST", headers: { Authorization: `Bearer ${token()}` } });
      const data = await res.json();
      showToast(data.message, "success");
      load();
    } catch (e) { console.error(e); }
    setTriggering(false);
  };

  const typeColors: Record<string, string> = {
    income: "bg-teal-50 dark:bg-teal-950/30 text-teal-700 dark:text-teal-400 border-teal-200 dark:border-teal-900",
    expense: "bg-coral-50 dark:bg-coral-950/30 text-coral-700 dark:text-coral-400 border-coral-200 dark:border-coral-900",
  };
  const freqColors: Record<string, string> = {
    daily: "bg-violet-50 dark:bg-violet-950/30 text-violet-700 border-violet-200 dark:border-violet-900",
    weekly: "bg-blue-50 dark:bg-blue-950/30 text-blue-700 border-blue-200 dark:border-blue-900",
    monthly: "bg-teal-50 dark:bg-teal-950/30 text-teal-700 border-teal-200 dark:border-teal-900",
    yearly: "bg-amber-50 dark:bg-amber-950/30 text-amber-700 border-amber-200 dark:border-amber-900",
  };

  if (!userEmail) return (
    <div className="flex flex-col items-center justify-center py-32 bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800">
      <p className="font-serif font-bold text-stone-700 dark:text-stone-300 mb-2">Sign in to manage recurring transactions</p>
      <button onClick={() => { setAuthMode("login"); setShowAuthModal(true); }} className="mt-2 bg-teal-700 hover:bg-teal-800 text-white text-sm font-bold py-2.5 px-6 rounded-lg border-none cursor-pointer">Sign in</button>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm">
        <div>
          <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Recurring transactions</h2>
          <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">Auto-schedule income and expenses on a fixed cadence.</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleTrigger}
            disabled={triggering}
            className="bg-stone-800 dark:bg-stone-700 hover:bg-stone-900 disabled:bg-stone-400 text-white text-xs font-bold py-2.5 px-4 rounded-lg border-none cursor-pointer flex items-center gap-1.5 transition-all"
          >
            {triggering && <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />}
            {triggering ? "Running…" : "Run due now"}
          </button>
          <button
            onClick={openCreate}
            className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-4 rounded-lg border-none cursor-pointer flex items-center gap-1.5 transition-all"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
            Add schedule
          </button>
        </div>
      </div>

      {/* List */}
      {loading ? (
        <div className="text-center py-16 text-stone-400 font-serif">Loading…</div>
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
          <h3 className="font-serif font-bold text-stone-700 dark:text-stone-300">No recurring schedules yet</h3>
          <p className="text-xs text-stone-450 mt-1 mb-6">Set up salary auto-log, rent, subscriptions, and more.</p>
          <button onClick={openCreate} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-6 rounded-lg border-none cursor-pointer">Add first schedule</button>
        </div>
      ) : (
        <div className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-stone-150 dark:border-stone-800 text-stone-450 dark:text-stone-550 text-[11px] font-bold uppercase tracking-wider">
                  <th className="py-4 pl-6">Description</th>
                  <th className="py-4">Frequency</th>
                  <th className="py-4">Category</th>
                  <th className="py-4">Type</th>
                  <th className="py-4">Next date</th>
                  <th className="py-4 text-right pr-6">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-50 dark:divide-stone-850">
                {items.map((item) => (
                  <tr key={item.id} className={`hover:bg-stone-50/60 dark:hover:bg-stone-850/20 transition-colors group ${!item.is_active ? "opacity-50" : ""}`}>
                    <td className="py-4 pl-6">
                      <div className="flex items-center gap-2">
                        <div className={`w-1.5 h-1.5 rounded-full ${item.is_active ? "bg-teal-600" : "bg-stone-300"}`}></div>
                        <span className="font-bold text-stone-800 dark:text-stone-200 text-sm">{item.description}</span>
                      </div>
                    </td>
                    <td className="py-4">
                      <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full border ${freqColors[item.frequency] || ""}`}>{freq_label[item.frequency]}</span>
                    </td>
                    <td className="py-4 text-xs text-stone-600 dark:text-stone-400">{item.category}</td>
                    <td className="py-4">
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full border ${typeColors[item.transaction_type] || ""}`}>{item.transaction_type}</span>
                    </td>
                    <td className="py-4 text-xs font-mono text-stone-600 dark:text-stone-400">{item.next_date}</td>
                    <td className="py-4 pr-6 text-right">
                      <span className={`font-mono font-bold text-sm ${item.transaction_type === "income" ? "text-teal-700 dark:text-teal-400" : "text-coral-600 dark:text-coral-400"}`}>
                        {item.transaction_type === "income" ? "+" : "−"}₹{item.amount?.toLocaleString("en-IN")}
                      </span>
                      {item.currency && item.currency !== "INR" && (
                        <span className="block text-[10px] text-stone-400 font-mono mt-0.5">
                          {item.currency} {item.original_amount?.toLocaleString("en-IN")}
                        </span>
                      )}
                      <span className="inline-flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity ml-4">
                        <button onClick={() => openEdit(item)} className="text-stone-400 hover:text-teal-700 bg-transparent border-none cursor-pointer text-xs">✎</button>
                        <button onClick={() => handleDelete(item.id)} className="text-stone-400 hover:text-coral-600 bg-transparent border-none cursor-pointer text-xs">✕</button>
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/55 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-stone-900 rounded-2xl shadow-xl border border-stone-150 dark:border-stone-800 max-w-md w-full p-7 relative">
            <button onClick={() => setShowModal(false)} className="absolute top-4 right-4 text-stone-400 hover:text-stone-650 bg-transparent border-none cursor-pointer p-1.5 rounded-md hover:bg-stone-100 dark:hover:bg-stone-800">✕</button>
            <div className="mb-6">
              <h3 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">{editId ? "Edit schedule" : "New recurring schedule"}</h3>
              <p className="text-xs text-stone-550 dark:text-stone-450 mt-1">Auto-generate transactions on a fixed cadence</p>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Description</label>
                <input required value={description} onChange={e => setDescription(e.target.value)} placeholder="e.g. Monthly salary" className="modal-input" />
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Currency</label>
                  <select value={currency} onChange={e => setCurrency(e.target.value)} className="modal-input cursor-pointer">
                    {supportedCurrencies.map(c => <option key={c.code} value={c.code}>{c.code} ({c.symbol})</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">
                    Amount ({supportedCurrencies.find(c => c.code === currency)?.symbol || "₹"})
                  </label>
                  <input required type="number" value={amount} onChange={e => setAmount(e.target.value)} className="modal-input" />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Type</label>
                  <select value={txType} onChange={e => setTxType(e.target.value)} className="modal-input cursor-pointer">
                    <option value="expense">Expense</option>
                    <option value="income">Income</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Category</label>
                  <select value={category} onChange={e => setCategory(e.target.value)} className="modal-input cursor-pointer">
                    {categories.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Frequency</label>
                  <select value={frequency} onChange={e => setFrequency(e.target.value)} className="modal-input cursor-pointer">
                    {FREQUENCIES.map(f => <option key={f} value={f}>{freq_label[f]}</option>)}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Next trigger date</label>
                <input required type="date" value={nextDate} onChange={e => setNextDate(e.target.value)} className="modal-input" />
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="is-active" checked={isActive} onChange={e => setIsActive(e.target.checked)} className="w-4 h-4 accent-teal-700 cursor-pointer" />
                <label htmlFor="is-active" className="text-sm text-stone-700 dark:text-stone-300 cursor-pointer">Active (will trigger automatically)</label>
              </div>
              <button type="submit" className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3 rounded-lg text-sm border-none cursor-pointer transition-all mt-2">
                {editId ? "Save changes" : "Create schedule"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default RecurringTransactions;
