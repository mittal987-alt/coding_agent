import React, { useEffect, useState } from "react";

const API = "http://127.0.0.1:8000";

interface DailyBriefData {
  brief_date: string | null;
  yesterday_spend: number;
  yesterday_income: number;
  category_breakdown: Record<string, number>;
  bills_due_today: { name: string; amount: number; source: string }[];
  recurring_triggered_count: number;
  alerts_critical_count: number;
  alerts_warning_count: number;
  generated: boolean;
}

const DailyBrief: React.FC = () => {
  const [brief, setBrief] = useState<DailyBriefData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const token = () => localStorage.getItem("token");

  const load = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/daily-brief`, {
        headers: { Authorization: `Bearer ${token()}` },
      });
      if (res.ok) setBrief(await res.json());
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  useEffect(() => {
    load();
  }, []);

  const refreshNow = async () => {
    setRefreshing(true);
    try {
      await fetch(`${API}/daily-brief/generate`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token()}` },
      });
      await load();
    } catch (e) {
      console.error(e);
    }
    setRefreshing(false);
  };

  const categoryEntries: [string, number][] = brief
    ? (Object.entries(brief.category_breakdown) as [string, number][]).sort((a, b) => b[1] - a[1])
    : [];
  const categoryTotal = categoryEntries.reduce((sum: number, [, v]: [string, number]) => sum + v, 0) || 1;
  const chartColors = ["#0F6E56", "#D85A30", "#BA7517", "#378ADD", "#7C6FDB", "#B0522D"];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4 bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm">
        <div>
          <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Daily brief</h2>
          <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">
            {brief?.brief_date
              ? `Generated for ${brief.brief_date}`
              : "Auto-generated every night at 00:05 — nothing yet for today."}
          </p>
        </div>
        <button
          onClick={refreshNow}
          disabled={refreshing}
          className="bg-teal-700 hover:bg-teal-800 disabled:bg-teal-400 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer border-none"
        >
          {refreshing ? (
            <><span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>Refreshing…</>
          ) : "Refresh now"}
        </button>
      </div>

      {loading ? (
        <div className="text-center py-16 text-stone-400 font-serif">Loading…</div>
      ) : !brief || !brief.generated ? (
        <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
          <h3 className="font-serif font-bold text-stone-700 dark:text-stone-300">No brief yet</h3>
          <p className="text-xs text-stone-450 mt-1 mb-6 text-center max-w-sm">
            The scheduler builds this automatically overnight. Click "Refresh now" to generate today's brief immediately.
          </p>
        </div>
      ) : (
        <>
          {/* Yesterday summary */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-5">
            <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 border-l-4 border-l-coral-500 shadow-sm p-5">
              <p className="text-[11px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider mb-2">Yesterday's spend</p>
              <p className="text-2xl font-mono font-bold text-stone-850 dark:text-stone-100">₹{brief.yesterday_spend.toLocaleString("en-IN")}</p>
            </div>
            <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 border-l-4 border-l-teal-600 shadow-sm p-5">
              <p className="text-[11px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider mb-2">Yesterday's income</p>
              <p className="text-2xl font-mono font-bold text-stone-850 dark:text-stone-100">₹{brief.yesterday_income.toLocaleString("en-IN")}</p>
            </div>
            <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 border-l-4 border-l-amber-500 shadow-sm p-5">
              <p className="text-[11px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider mb-2">Auto-pay ran</p>
              <p className="text-2xl font-mono font-bold text-stone-850 dark:text-stone-100">{brief.recurring_triggered_count}</p>
              <p className="text-[11px] text-stone-450 mt-1">transaction{brief.recurring_triggered_count === 1 ? "" : "s"} triggered overnight</p>
            </div>
          </div>

          {/* Alerts summary */}
          <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-6">
            <h3 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100 mb-4">Alert status</h3>
            <div className="flex flex-wrap gap-3">
              <span className={`text-sm font-bold px-4 py-2 rounded-lg ${brief.alerts_critical_count > 0 ? "bg-coral-50 dark:bg-coral-950/30 text-coral-700 dark:text-coral-400" : "bg-stone-50 dark:bg-stone-800 text-stone-400"}`}>
                {brief.alerts_critical_count} critical
              </span>
              <span className={`text-sm font-bold px-4 py-2 rounded-lg ${brief.alerts_warning_count > 0 ? "bg-amber-50 dark:bg-amber-950/30 text-amber-700 dark:text-amber-400" : "bg-stone-50 dark:bg-stone-800 text-stone-400"}`}>
                {brief.alerts_warning_count} warning{brief.alerts_warning_count === 1 ? "" : "s"}
              </span>
              {brief.alerts_critical_count === 0 && brief.alerts_warning_count === 0 && (
                <span className="text-sm font-bold px-4 py-2 rounded-lg bg-teal-50 dark:bg-teal-950/30 text-teal-700 dark:text-teal-400">
                  All clear
                </span>
              )}
            </div>
            <p className="text-xs text-stone-450 mt-3">See the full breakdown on the Notifications page.</p>
          </div>

          {/* Category breakdown + Bills due today */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
            <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-6">
              <h3 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100 mb-4">Where yesterday went</h3>
              {categoryEntries.length > 0 ? (
                <div className="space-y-2.5">
                  {categoryEntries.map(([cat, amt], i) => {
                    const pct = (amt / categoryTotal) * 100;
                    return (
                      <div key={cat} className="flex flex-col gap-1">
                        <div className="flex justify-between items-center text-xs font-bold text-stone-700 dark:text-stone-300">
                          <span className="flex items-center gap-1.5">
                            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: chartColors[i % chartColors.length] }}></span>
                            {cat}
                          </span>
                          <span className="font-mono">₹{amt.toLocaleString("en-IN")} ({pct.toFixed(0)}%)</span>
                        </div>
                        <div className="w-full bg-stone-100 dark:bg-stone-800 rounded-full h-1.5">
                          <div className="h-1.5 rounded-full" style={{ width: `${pct}%`, backgroundColor: chartColors[i % chartColors.length] }}></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p className="text-sm text-stone-450">No spending recorded yesterday.</p>
              )}
            </div>

            <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-6">
              <h3 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100 mb-4">Due today</h3>
              {brief.bills_due_today.length > 0 ? (
                <div className="space-y-2.5">
                  {brief.bills_due_today.map((b, i) => (
                    <div key={i} className="flex justify-between items-center p-3 bg-stone-50 dark:bg-stone-800/50 rounded-lg text-sm">
                      <div>
                        <p className="font-bold text-stone-700 dark:text-stone-300">{b.name}</p>
                        <p className="text-[10px] text-stone-400 uppercase font-bold tracking-wider">{b.source}</p>
                      </div>
                      <span className="font-mono font-bold text-stone-800 dark:text-stone-200">₹{b.amount.toLocaleString("en-IN")}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-stone-450">Nothing due today.</p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DailyBrief;
