import React, { useState, useEffect } from "react";
import { useFinance } from "../context/FinanceContext";

const API = "http://127.0.0.1:8000";

const TYPES = ["Stocks", "Mutual Fund", "FD", "PPF", "Gold", "Crypto", "NPS", "Real Estate", "Others"];

const typeEmoji: Record<string, string> = {
  "Stocks": "📈", "Mutual Fund": "🏦", "FD": "🏛️", "PPF": "🏅",
  "Gold": "🥇", "Crypto": "₿", "NPS": "🎯", "Real Estate": "🏠", "Others": "💼"
};
// Left-border accent per type, drawn from the ledger palette
const typeAccent: Record<string, string> = {
  "Stocks": "border-l-blue-500", "Mutual Fund": "border-l-violet-500",
  "FD": "border-l-teal-500", "PPF": "border-l-amber-500",
  "Gold": "border-l-amber-600", "Crypto": "border-l-coral-500",
  "NPS": "border-l-cyan-500", "Real Estate": "border-l-stone-400", "Others": "border-l-pink-500",
};
const typeBarColor: Record<string, string> = {
  "Stocks": "bg-blue-500", "Mutual Fund": "bg-violet-500", "FD": "bg-teal-500",
  "PPF": "bg-amber-500", "Gold": "bg-amber-600", "Crypto": "bg-coral-500",
  "NPS": "bg-cyan-500", "Real Estate": "bg-stone-400", "Others": "bg-pink-500",
};

const Investments: React.FC = () => {
  const { userEmail, setShowAuthModal, setAuthMode, confirmAction } = useFinance();
  const [investments, setInvestments] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState<number | null>(null);

  const [name, setName] = useState("");
  const [investType, setInvestType] = useState("Stocks");
  const [investedAmount, setInvestedAmount] = useState("");
  const [currentValue, setCurrentValue] = useState("");
  const [units, setUnits] = useState("");
  const [purchasePrice, setPurchasePrice] = useState("");
  const [currentPrice, setCurrentPrice] = useState("");
  const [purchaseDate, setPurchaseDate] = useState(new Date().toISOString().split("T")[0]);
  const [notes, setNotes] = useState("");

  const token = () => localStorage.getItem("token");
  const authHeader = () => ({ Authorization: `Bearer ${token()}`, "Content-Type": "application/json" });

  const load = async () => {
    if (!token()) { setLoading(false); return; }
    setLoading(true);
    try {
      const [invRes, sumRes] = await Promise.all([
        fetch(`${API}/investments/`, { headers: { Authorization: `Bearer ${token()}` } }),
        fetch(`${API}/investments/summary`, { headers: { Authorization: `Bearer ${token()}` } }),
      ]);
      if (invRes.ok) setInvestments(await invRes.json());
      if (sumRes.ok) setSummary(await sumRes.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { load(); }, [userEmail]);

  const openCreate = () => {
    setEditId(null); setName(""); setInvestType("Stocks"); setInvestedAmount(""); setCurrentValue("");
    setUnits(""); setPurchasePrice(""); setCurrentPrice(""); setPurchaseDate(new Date().toISOString().split("T")[0]); setNotes("");
    setShowModal(true);
  };

  const openEdit = (inv: any) => {
    setEditId(inv.id); setName(inv.name); setInvestType(inv.investment_type);
    setInvestedAmount(String(inv.invested_amount)); setCurrentValue(String(inv.current_value));
    setUnits(inv.units ? String(inv.units) : ""); setPurchasePrice(inv.purchase_price ? String(inv.purchase_price) : "");
    setCurrentPrice(inv.current_price ? String(inv.current_price) : "");
    setPurchaseDate(inv.purchase_date); setNotes(inv.notes || "");
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const payload = {
      name, investment_type: investType,
      invested_amount: parseFloat(investedAmount),
      current_value: parseFloat(currentValue),
      units: units ? parseFloat(units) : null,
      purchase_price: purchasePrice ? parseFloat(purchasePrice) : null,
      current_price: currentPrice ? parseFloat(currentPrice) : null,
      purchase_date: purchaseDate,
      notes: notes || null,
    };
    const url = editId ? `${API}/investments/${editId}` : `${API}/investments/`;
    const method = editId ? "PUT" : "POST";
    try {
      const res = await fetch(url, { method, headers: authHeader(), body: JSON.stringify(payload) });
      if (res.ok) { setShowModal(false); load(); }
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirmAction("Remove this investment?"))) return;
    await fetch(`${API}/investments/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token()}` } });
    load();
  };

  const returnPct = (inv: any) => {
    if (!inv.invested_amount) return 0;
    return ((inv.current_value - inv.invested_amount) / inv.invested_amount * 100);
  };

  if (!userEmail) return (
    <div className="flex flex-col items-center justify-center py-32 bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800">
      <p className="font-serif font-bold text-stone-700 dark:text-stone-300 mb-2">Sign in to track your portfolio</p>
      <button onClick={() => { setAuthMode("login"); setShowAuthModal(true); }} className="mt-2 bg-teal-700 hover:bg-teal-800 text-white text-sm font-bold py-2.5 px-6 rounded-lg border-none cursor-pointer">Sign in</button>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm">
        <div>
          <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Investment portfolio</h2>
          <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">Track stocks, mutual funds, FDs, PPF, gold, and more.</p>
        </div>
        <button onClick={openCreate} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-4 rounded-lg border-none cursor-pointer flex items-center gap-1.5 transition-all">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
          Add investment
        </button>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Total invested", value: `₹${summary.total_invested?.toLocaleString("en-IN")}`, color: "text-stone-800 dark:text-stone-200" },
            { label: "Current value", value: `₹${summary.total_current_value?.toLocaleString("en-IN")}`, color: "text-teal-700 dark:text-teal-400" },
            { label: "Total P&L", value: `${summary.total_gain_loss >= 0 ? "+" : ""}₹${summary.total_gain_loss?.toLocaleString("en-IN")}`, color: summary.total_gain_loss >= 0 ? "text-teal-700 dark:text-teal-400" : "text-coral-600 dark:text-coral-400" },
            { label: "Overall return", value: `${summary.overall_return_pct >= 0 ? "+" : ""}${summary.overall_return_pct?.toFixed(2)}%`, color: summary.overall_return_pct >= 0 ? "text-teal-700 dark:text-teal-400" : "text-coral-600 dark:text-coral-400" },
          ].map(card => (
            <div key={card.label} className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 rounded-xl p-5 shadow-sm">
              <p className="text-[10px] font-bold text-stone-450 dark:text-stone-500 uppercase tracking-wider mb-1">{card.label}</p>
              <p className={`text-xl font-mono font-bold ${card.color}`}>{card.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Portfolio Grid */}
      {loading ? (
        <div className="text-center py-16 text-stone-400 font-serif">Loading…</div>
      ) : investments.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
          <h3 className="font-serif font-bold text-stone-700 dark:text-stone-300">No investments added yet</h3>
          <p className="text-xs text-stone-450 mt-1 mb-6">Track your full portfolio — stocks, FDs, MFs, gold, crypto, and more.</p>
          <button onClick={openCreate} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-6 rounded-lg border-none cursor-pointer">Add first investment</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {investments.map((inv) => {
            const ret = returnPct(inv);
            const accent = typeAccent[inv.investment_type] || "border-l-stone-400";
            return (
              <div key={inv.id} className={`bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 border-l-4 ${accent} rounded-xl p-5 shadow-sm hover:shadow-md transition-all relative group`}>
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <span className="text-xl">{typeEmoji[inv.investment_type] || "💼"}</span>
                    <p className="text-[9px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-widest mt-1">{inv.investment_type}</p>
                    <h3 className="font-bold text-sm mt-0.5 leading-tight text-stone-800 dark:text-stone-100">{inv.name}</h3>
                  </div>
                  <div className={`text-xs font-mono font-bold px-2 py-1 rounded-md ${ret >= 0 ? "bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-400" : "bg-coral-50 dark:bg-coral-950/40 text-coral-700 dark:text-coral-400"}`}>
                    {ret >= 0 ? "▲" : "▼"} {Math.abs(ret).toFixed(1)}%
                  </div>
                </div>
                <div className="mt-4 space-y-1">
                  <div className="flex justify-between text-[10px] text-stone-400 font-bold uppercase tracking-wider">
                    <span>Invested</span><span>Current</span>
                  </div>
                  <div className="flex justify-between font-mono font-bold text-base text-stone-800 dark:text-stone-100">
                    <span>₹{inv.invested_amount?.toLocaleString("en-IN")}</span>
                    <span>₹{inv.current_value?.toLocaleString("en-IN")}</span>
                  </div>
                </div>
                {inv.units && (
                  <p className="text-[10px] text-stone-400 mt-2 font-mono">{inv.units} units · ₹{inv.current_price || "—"} / unit</p>
                )}
                <div className="absolute top-3 right-3 flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => openEdit(inv)} className="text-stone-400 hover:text-teal-700 bg-transparent border-none cursor-pointer text-xs">✎</button>
                  <button onClick={() => handleDelete(inv.id)} className="text-stone-400 hover:text-coral-600 bg-transparent border-none cursor-pointer text-xs">✕</button>
                </div>
                <p className="text-[9px] text-stone-400 mt-2">Since {inv.purchase_date}</p>
              </div>
            );
          })}
        </div>
      )}

      {/* Allocation Breakdown */}
      {summary?.allocation && Object.keys(summary.allocation).length > 0 && (
        <div className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 rounded-xl shadow-sm p-6">
          <h3 className="font-serif font-bold text-stone-800 dark:text-stone-100 mb-4">Allocation breakdown</h3>
          <div className="space-y-3">
            {Object.entries(summary.allocation).map(([type, value]: [string, any]) => {
              const pct = summary.total_current_value > 0 ? (value / summary.total_current_value * 100) : 0;
              return (
                <div key={type} className="flex items-center gap-4">
                  <span className="text-sm font-bold text-stone-700 dark:text-stone-300 w-32 flex-shrink-0">{typeEmoji[type] || "💼"} {type}</span>
                  <div className="flex-1 bg-stone-100 dark:bg-stone-850 rounded-full h-2.5 overflow-hidden">
                    <div className={`h-2.5 rounded-full ${typeBarColor[type] || "bg-stone-400"}`} style={{ width: `${pct}%` }} />
                  </div>
                  <span className="text-xs font-mono font-bold text-stone-600 dark:text-stone-400 w-16 text-right">{pct.toFixed(1)}%</span>
                  <span className="text-xs font-mono text-stone-500 dark:text-stone-500 w-28 text-right">₹{value?.toLocaleString("en-IN")}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/55 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-stone-900 rounded-2xl shadow-xl border border-stone-150 dark:border-stone-800 max-w-lg w-full p-7 relative overflow-y-auto max-h-[90vh]">
            <button onClick={() => setShowModal(false)} className="absolute top-4 right-4 text-stone-400 hover:text-stone-650 bg-transparent border-none cursor-pointer p-1.5 rounded-md hover:bg-stone-100 dark:hover:bg-stone-800">✕</button>
            <div className="mb-6">
              <h3 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">{editId ? "Edit investment" : "Add investment"}</h3>
              <p className="text-xs text-stone-550 dark:text-stone-450 mt-1">Record a new asset in your portfolio</p>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Name / ticker</label>
                <input required value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Reliance Industries, Nifty 50 Index" className="modal-input" />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Type</label>
                <div className="grid grid-cols-3 gap-2">
                  {TYPES.map(t => (
                    <button key={t} type="button" onClick={() => setInvestType(t)} className={`text-xs font-bold py-2 px-2 rounded-lg border cursor-pointer transition-all ${investType === t ? "bg-teal-700 border-teal-700 text-white" : "bg-stone-50 dark:bg-stone-800 border-stone-200 dark:border-stone-700 text-stone-600 dark:text-stone-400 hover:border-teal-400"}`}>
                      {typeEmoji[t]} {t}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Invested amount (₹)</label>
                  <input required type="number" value={investedAmount} onChange={e => setInvestedAmount(e.target.value)} className="modal-input" />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Current value (₹)</label>
                  <input required type="number" value={currentValue} onChange={e => setCurrentValue(e.target.value)} className="modal-input" />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Units (optional)</label>
                  <input type="number" value={units} onChange={e => setUnits(e.target.value)} className="modal-input" />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Buy price (₹)</label>
                  <input type="number" value={purchasePrice} onChange={e => setPurchasePrice(e.target.value)} className="modal-input" />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">CMP (₹)</label>
                  <input type="number" value={currentPrice} onChange={e => setCurrentPrice(e.target.value)} className="modal-input" />
                </div>
              </div>
              <div>
                <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Purchase date</label>
                <input required type="date" value={purchaseDate} onChange={e => setPurchaseDate(e.target.value)} className="modal-input" />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Notes</label>
                <input value={notes} onChange={e => setNotes(e.target.value)} placeholder="e.g. SIP of ₹5000/month" className="modal-input" />
              </div>
              <button type="submit" className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3 rounded-lg text-sm border-none cursor-pointer transition-all">
                {editId ? "Save changes" : "Add to portfolio"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Investments;
