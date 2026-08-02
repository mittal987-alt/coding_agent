import React, { useState, useEffect } from "react";
import { useFinance } from "../context/FinanceContext";
import { API_URL } from "../config";

const API = API_URL;

const LOAN_TYPES = ["Home", "Car", "Personal", "Education", "Business", "Gold", "Others"];

const loanTypeEmoji: Record<string, string> = {
  Home: "🏠", Car: "🚗", Personal: "👤", Education: "🎓",
  Business: "💼", Gold: "🥇", Others: "📋"
};
// Left-border accent per loan type, drawn from the ledger palette
const loanTypeAccent: Record<string, string> = {
  Home: "border-l-blue-500", Car: "border-l-stone-400",
  Personal: "border-l-violet-500", Education: "border-l-teal-500",
  Business: "border-l-amber-500", Gold: "border-l-amber-600",
  Others: "border-l-pink-500",
};

function computeEmi(principal: number, rate: number, months: number): number {
  if (rate === 0) return principal / months;
  const r = rate / 12 / 100;
  return principal * r * Math.pow(1 + r, months) / (Math.pow(1 + r, months) - 1);
}

const Loans: React.FC = () => {
  const { userEmail, setShowAuthModal, setAuthMode, confirmAction } = useFinance();
  const [loans, setLoans] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showSchedule, setShowSchedule] = useState<any>(null);
  const [editId, setEditId] = useState<number | null>(null);

  // Form
  const [name, setName] = useState("");
  const [loanType, setLoanType] = useState("Personal");
  const [principal, setPrincipal] = useState("");
  const [rate, setRate] = useState("");
  const [tenure, setTenure] = useState("");
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0]);
  const [outstanding, setOutstanding] = useState("");
  const [lender, setLender] = useState("");
  const [isActive, setIsActive] = useState(true);

  const token = () => localStorage.getItem("token");
  const authHeader = () => ({ Authorization: `Bearer ${token()}`, "Content-Type": "application/json" });

  const load = async () => {
    if (!token()) { setLoading(false); return; }
    setLoading(true);
    try {
      const [lRes, sRes] = await Promise.all([
        fetch(`${API}/loans/`, { headers: { Authorization: `Bearer ${token()}` } }),
        fetch(`${API}/loans/summary`, { headers: { Authorization: `Bearer ${token()}` } }),
      ]);
      if (lRes.ok) setLoans(await lRes.json());
      if (sRes.ok) setSummary(await sRes.json());
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { load(); }, [userEmail]);

  const computedEmi = () => {
    if (!principal || !rate || !tenure) return 0;
    return computeEmi(parseFloat(principal), parseFloat(rate), parseInt(tenure));
  };

  const openCreate = () => {
    setEditId(null); setName(""); setLoanType("Personal"); setPrincipal(""); setRate(""); setTenure("");
    setStartDate(new Date().toISOString().split("T")[0]); setOutstanding(""); setLender(""); setIsActive(true);
    setShowModal(true);
  };

  const openEdit = (l: any) => {
    setEditId(l.id); setName(l.name); setLoanType(l.loan_type); setPrincipal(String(l.principal_amount));
    setRate(String(l.interest_rate)); setTenure(String(l.tenure_months)); setStartDate(l.start_date);
    setOutstanding(String(l.outstanding_amount)); setLender(l.lender_name || ""); setIsActive(l.is_active);
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const emi = computedEmi();
    const payload = {
      name, loan_type: loanType,
      principal_amount: parseFloat(principal),
      interest_rate: parseFloat(rate),
      tenure_months: parseInt(tenure),
      start_date: startDate,
      emi_amount: parseFloat(emi.toFixed(2)),
      outstanding_amount: parseFloat(outstanding || principal),
      lender_name: lender || null,
      is_active: isActive,
    };
    const url = editId ? `${API}/loans/${editId}` : `${API}/loans/`;
    const method = editId ? "PUT" : "POST";
    try {
      const res = await fetch(url, { method, headers: authHeader(), body: JSON.stringify(payload) });
      if (res.ok) { setShowModal(false); load(); }
    } catch (e) { console.error(e); }
  };

  const handleDelete = async (id: number) => {
    if (!(await confirmAction("Remove this loan?"))) return;
    await fetch(`${API}/loans/${id}`, { method: "DELETE", headers: { Authorization: `Bearer ${token()}` } });
    load();
  };

  const loadSchedule = async (id: number) => {
    const res = await fetch(`${API}/loans/${id}/schedule`, { headers: { Authorization: `Bearer ${token()}` } });
    if (res.ok) setShowSchedule(await res.json());
  };

  if (!userEmail) return (
    <div className="flex flex-col items-center justify-center py-32 bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800">
      <p className="font-serif font-bold text-stone-700 dark:text-stone-300 mb-2">Sign in to track your loans</p>
      <button onClick={() => { setAuthMode("login"); setShowAuthModal(true); }} className="mt-2 bg-teal-700 hover:bg-teal-800 text-white text-sm font-bold py-2.5 px-6 rounded-lg border-none cursor-pointer">Sign in</button>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm">
        <div>
          <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Loan & EMI tracker</h2>
          <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">Track all your loans, EMIs, and amortization schedules.</p>
        </div>
        <button onClick={openCreate} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-4 rounded-lg border-none cursor-pointer flex items-center gap-1.5 transition-all">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4"><path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" /></svg>
          Add loan
        </button>
      </div>

      {/* Summary */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {[
            { label: "Active loans", value: String(summary.active_loans), color: "text-stone-800 dark:text-stone-200" },
            { label: "Total outstanding", value: `₹${summary.total_outstanding?.toLocaleString("en-IN")}`, color: "text-coral-600 dark:text-coral-400" },
            { label: "Monthly EMI burden", value: `₹${summary.monthly_emi_burden?.toLocaleString("en-IN")}`, color: "text-amber-600 dark:text-amber-400" },
            { label: "Paid so far", value: `₹${summary.total_paid_so_far?.toLocaleString("en-IN")}`, color: "text-teal-700 dark:text-teal-400" },
          ].map(c => (
            <div key={c.label} className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 rounded-xl p-5 shadow-sm">
              <p className="text-[10px] font-bold text-stone-450 dark:text-stone-500 uppercase tracking-wider mb-1">{c.label}</p>
              <p className={`text-xl font-mono font-bold ${c.color}`}>{c.value}</p>
            </div>
          ))}
        </div>
      )}

      {/* Loan Cards */}
      {loading ? (
        <div className="text-center py-16 text-stone-400 font-serif">Loading…</div>
      ) : loans.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
          <h3 className="font-serif font-bold text-stone-700 dark:text-stone-300">No loans tracked yet</h3>
          <p className="text-xs text-stone-450 mt-1 mb-6">Add home, car, personal loans, or credit card debt to monitor repayment progress.</p>
          <button onClick={openCreate} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-6 rounded-lg border-none cursor-pointer">Add first loan</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {loans.map((loan) => {
            const progress = loan.principal_amount > 0 ? Math.min(((loan.principal_amount - loan.outstanding_amount) / loan.principal_amount) * 100, 100) : 0;
            const accent = loanTypeAccent[loan.loan_type] || "border-l-stone-400";
            return (
              <div key={loan.id} className={`bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 border-l-4 ${accent} rounded-xl p-5 shadow-sm hover:shadow-md transition-all relative group`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="text-xl">{loanTypeEmoji[loan.loan_type] || "📋"}</span>
                    <p className="text-[9px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-widest mt-1">{loan.loan_type} loan {!loan.is_active && "· Closed"}</p>
                    <h3 className="font-bold text-sm mt-0.5 text-stone-800 dark:text-stone-100">{loan.name}</h3>
                    {loan.lender_name && <p className="text-[10px] text-stone-400 mt-0.5">{loan.lender_name}</p>}
                  </div>
                  <div className="text-right flex-shrink-0">
                    <p className="text-[9px] text-stone-400 font-bold">RATE</p>
                    <p className="font-mono font-bold text-lg text-stone-800 dark:text-stone-100">{loan.interest_rate}%</p>
                  </div>
                </div>

                {/* Progress Bar */}
                <div className="mb-3 mt-4">
                  <div className="flex justify-between text-[10px] text-stone-400 mb-1 font-bold">
                    <span>Repaid</span><span className="font-mono">{progress.toFixed(0)}%</span>
                  </div>
                  <div className="bg-stone-100 dark:bg-stone-800 rounded-full h-2">
                    <div className="bg-teal-600 rounded-full h-2 transition-all" style={{ width: `${progress}%` }} />
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2">
                  <div className="bg-stone-50 dark:bg-stone-800/60 rounded-lg p-2.5">
                    <p className="text-[9px] text-stone-400 font-bold">EMI/MONTH</p>
                    <p className="font-mono font-bold text-sm text-stone-800 dark:text-stone-100">₹{loan.emi_amount?.toLocaleString("en-IN")}</p>
                  </div>
                  <div className="bg-stone-50 dark:bg-stone-800/60 rounded-lg p-2.5">
                    <p className="text-[9px] text-stone-400 font-bold">OUTSTANDING</p>
                    <p className="font-mono font-bold text-sm text-stone-800 dark:text-stone-100">₹{loan.outstanding_amount?.toLocaleString("en-IN")}</p>
                  </div>
                </div>

                <div className="flex gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button onClick={() => loadSchedule(loan.id)} className="flex-1 bg-stone-100 dark:bg-stone-800 hover:bg-stone-200 dark:hover:bg-stone-750 text-stone-600 dark:text-stone-300 text-[10px] font-bold py-1.5 rounded-md border-none cursor-pointer transition-all">Schedule</button>
                  <button onClick={() => openEdit(loan)} className="bg-stone-100 dark:bg-stone-800 hover:bg-stone-200 dark:hover:bg-stone-750 text-stone-600 dark:text-stone-300 text-[10px] font-bold py-1.5 px-3 rounded-md border-none cursor-pointer transition-all">✎</button>
                  <button onClick={() => handleDelete(loan.id)} className="bg-coral-50 dark:bg-coral-950/30 hover:bg-coral-100 text-coral-600 dark:text-coral-400 text-[10px] font-bold py-1.5 px-3 rounded-md border-none cursor-pointer transition-all">✕</button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Amortization Schedule Modal */}
      {showSchedule && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/55 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-stone-900 rounded-2xl shadow-xl border border-stone-150 dark:border-stone-800 w-full max-w-2xl max-h-[85vh] flex flex-col">
            <div className="p-6 border-b border-stone-150 dark:border-stone-800 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-serif font-bold text-stone-800 dark:text-stone-100">{showSchedule.loan_name} — amortization</h3>
                <p className="text-xs text-stone-500 mt-0.5 font-mono">EMI ₹{showSchedule.emi?.toLocaleString("en-IN")} · Interest ₹{showSchedule.total_interest_outflow?.toLocaleString("en-IN")} · Total ₹{showSchedule.total_repayment?.toLocaleString("en-IN")}</p>
              </div>
              <button onClick={() => setShowSchedule(null)} className="text-stone-400 hover:text-stone-650 bg-transparent border-none cursor-pointer p-1.5 rounded-md hover:bg-stone-100 dark:hover:bg-stone-800">✕</button>
            </div>
            <div className="overflow-auto flex-1 p-4">
              <table className="w-full text-xs border-collapse">
                <thead>
                  <tr className="text-stone-450 font-bold uppercase tracking-wider border-b border-stone-150 dark:border-stone-800">
                    <th className="py-2 px-3 text-left">Month</th>
                    <th className="py-2 px-3 text-right">EMI (₹)</th>
                    <th className="py-2 px-3 text-right">Principal (₹)</th>
                    <th className="py-2 px-3 text-right">Interest (₹)</th>
                    <th className="py-2 px-3 text-right">Balance (₹)</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-50 dark:divide-stone-850 font-mono">
                  {showSchedule.schedule?.map((row: any) => (
                    <tr key={row.month} className="hover:bg-stone-50 dark:hover:bg-stone-850/30">
                      <td className="py-2 px-3 font-bold text-stone-700 dark:text-stone-300">{row.month}</td>
                      <td className="py-2 px-3 text-right text-stone-600 dark:text-stone-400">{row.emi?.toLocaleFixed ? row.emi.toLocaleString("en-IN") : row.emi}</td>
                      <td className="py-2 px-3 text-right text-teal-700 dark:text-teal-400 font-bold">{row.principal_paid?.toLocaleString("en-IN")}</td>
                      <td className="py-2 px-3 text-right text-coral-600 dark:text-coral-400">{row.interest_paid?.toLocaleString("en-IN")}</td>
                      <td className="py-2 px-3 text-right font-bold text-stone-700 dark:text-stone-300">{row.balance?.toLocaleString("en-IN")}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {/* Add/Edit Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/55 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-stone-900 rounded-2xl shadow-xl border border-stone-150 dark:border-stone-800 max-w-lg w-full p-7 relative overflow-y-auto max-h-[90vh]">
            <button onClick={() => setShowModal(false)} className="absolute top-4 right-4 text-stone-400 hover:text-stone-650 bg-transparent border-none cursor-pointer p-1.5 rounded-md hover:bg-stone-100 dark:hover:bg-stone-800">✕</button>
            <div className="mb-6">
              <h3 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">{editId ? "Edit loan" : "Add new loan"}</h3>
              <p className="text-xs text-stone-550 dark:text-stone-450 mt-1">EMI is auto-calculated from your inputs</p>
            </div>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Loan name</label>
                <input required value={name} onChange={e => setName(e.target.value)} placeholder="e.g. HDFC Home Loan" className="modal-input" />
              </div>
              <div>
                <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Loan type</label>
                <div className="grid grid-cols-4 gap-2">
                  {LOAN_TYPES.map(t => (
                    <button key={t} type="button" onClick={() => setLoanType(t)} className={`text-xs font-bold py-2 px-2 rounded-lg border cursor-pointer transition-all ${loanType === t ? "bg-teal-700 border-teal-700 text-white" : "bg-stone-50 dark:bg-stone-800 border-stone-200 dark:border-stone-700 text-stone-600 dark:text-stone-400 hover:border-teal-400"}`}>
                      {loanTypeEmoji[t]} {t}
                    </button>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Principal (₹)</label>
                  <input required type="number" value={principal} onChange={e => setPrincipal(e.target.value)} className="modal-input" />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Rate (% p.a.)</label>
                  <input required type="number" step="0.01" value={rate} onChange={e => setRate(e.target.value)} className="modal-input" />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Tenure (months)</label>
                  <input required type="number" value={tenure} onChange={e => setTenure(e.target.value)} className="modal-input" />
                </div>
              </div>
              {principal && rate && tenure && (
                <div className="bg-teal-50 dark:bg-teal-950/30 border border-teal-100 dark:border-teal-900 rounded-lg p-4 text-center">
                  <p className="text-xs text-teal-700 dark:text-teal-400 font-bold uppercase tracking-wider mb-1">Calculated monthly EMI</p>
                  <p className="text-2xl font-mono font-bold text-teal-800 dark:text-teal-300">₹{computedEmi().toLocaleString("en-IN", { maximumFractionDigits: 0 })}</p>
                </div>
              )}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Start date</label>
                  <input required type="date" value={startDate} onChange={e => setStartDate(e.target.value)} className="modal-input" />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Outstanding (₹)</label>
                  <input type="number" value={outstanding} onChange={e => setOutstanding(e.target.value)} placeholder="Leave blank = full principal" className="modal-input" />
                </div>
              </div>
              <div>
                <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">Lender name</label>
                <input value={lender} onChange={e => setLender(e.target.value)} placeholder="e.g. HDFC Bank, SBI, ICICI" className="modal-input" />
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="active-loan" checked={isActive} onChange={e => setIsActive(e.target.checked)} className="w-4 h-4 accent-teal-700 cursor-pointer" />
                <label htmlFor="active-loan" className="text-sm text-stone-700 dark:text-stone-300 cursor-pointer">Active (ongoing EMI)</label>
              </div>
              <button type="submit" className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3 rounded-lg text-sm border-none cursor-pointer transition-all">
                {editId ? "Save changes" : "Add loan"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Loans;
