import React, { useState, useEffect } from "react";

const API = "http://127.0.0.1:8000";

const TOP_CURRENCIES = [
  { code: "USD", flag: "🇺🇸", name: "US Dollar" },
  { code: "EUR", flag: "🇪🇺", name: "Euro" },
  { code: "GBP", flag: "🇬🇧", name: "British Pound" },
  { code: "JPY", flag: "🇯🇵", name: "Japanese Yen" },
  { code: "SGD", flag: "🇸🇬", name: "Singapore Dollar" },
  { code: "AED", flag: "🇦🇪", name: "UAE Dirham" },
  { code: "CAD", flag: "🇨🇦", name: "Canadian Dollar" },
  { code: "AUD", flag: "🇦🇺", name: "Australian Dollar" },
];

const CurrencyWidget: React.FC = () => {
  const [rates, setRates] = useState<Record<string, number>>({});
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [converterAmount, setConverterAmount] = useState("100");
  const [converterCurrency, setConverterCurrency] = useState("USD");
  const [converterResult, setConverterResult] = useState<number | null>(null);
  const [converting, setConverting] = useState(false);

  const loadRates = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API}/currency/rates`);
      if (res.ok) {
        const data = await res.json();
        // API returns { rates: [{ code, name, rate_inr, ... }], base: "INR" }
        const map: Record<string, number> = {};
        const ratesArray = Array.isArray(data) ? data : (data.rates ?? []);
        ratesArray.forEach((c: any) => {
          map[c.code] = c.rate_inr ?? c.rate_to_inr ?? c.rate ?? 1;
        });
        setRates(map);
        setLastUpdated(new Date());
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { loadRates(); }, []);

  const handleConvert = async () => {
    const amount = parseFloat(converterAmount);
    if (!amount || isNaN(amount)) return;
    setConverting(true);
    try {
      const res = await fetch(
        `${API}/currency/convert?amount=${amount}&from_currency=${converterCurrency}&to_currency=INR`
      );
      if (res.ok) {
        const data = await res.json();
        setConverterResult(data.converted ?? data.result ?? null);
      }
    } catch (e) { console.error(e); }
    setConverting(false);
  };

  const getRate = (code: string) => rates[code] ?? null;

  return (
    <div className="bg-white dark:bg-stone-900/80 backdrop-blur-sm border border-stone-150 dark:border-stone-700/50 rounded-2xl shadow-sm hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 overflow-hidden">
      {/* Header */}
      <div className="px-5 py-4 border-b border-stone-100 dark:border-stone-800 flex items-center justify-between">
        <div>
          <h3 className="font-serif font-bold text-base text-stone-800 dark:text-stone-100">Live Exchange Rates</h3>
          <p className="text-[11px] text-stone-400 dark:text-stone-500 mt-0.5">vs Indian Rupee (INR)</p>
        </div>
        <div className="flex items-center gap-2">
          {!loading && (
            <div className="flex items-center gap-1.5 text-[10px] font-bold text-teal-600 dark:text-teal-400">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-500 animate-pulse"></span>
              Live
            </div>
          )}
          <button
            onClick={loadRates}
            disabled={loading}
            className="p-1.5 rounded-lg text-stone-400 hover:text-stone-600 hover:bg-stone-100 dark:hover:bg-stone-800 transition-all cursor-pointer bg-transparent border-none"
            title="Refresh rates"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className={`w-4 h-4 ${loading ? "animate-spin" : ""}`}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" />
            </svg>
          </button>
        </div>
      </div>

      {/* Rates Grid */}
      <div className="p-4">
        {loading ? (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {TOP_CURRENCIES.map(c => (
              <div key={c.code} className="animate-pulse bg-stone-100 dark:bg-stone-800 rounded-xl h-16"></div>
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {TOP_CURRENCIES.map(({ code, flag, name }) => {
              const rate = getRate(code);
              return (
                <div
                  key={code}
                  className="bg-stone-50 dark:bg-stone-800/60 border border-stone-100 dark:border-stone-700/50 rounded-xl p-3 hover:bg-stone-100 dark:hover:bg-stone-800 transition-all cursor-default"
                >
                  <div className="flex items-center gap-1.5 mb-1">
                    <span className="text-base leading-none">{flag}</span>
                    <span className="text-[11px] font-black text-stone-500 dark:text-stone-400">{code}</span>
                  </div>
                  <p className="text-sm font-mono font-bold text-stone-800 dark:text-stone-100">
                    {rate ? `₹${rate.toFixed(2)}` : "—"}
                  </p>
                  <p className="text-[10px] text-stone-400 truncate">{name}</p>
                </div>
              );
            })}
          </div>
        )}

        {lastUpdated && (
          <p className="text-[10px] text-stone-400 dark:text-stone-600 mt-3 text-right">
            Updated {lastUpdated.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" })}
          </p>
        )}
      </div>

      {/* Mini Converter */}
      <div className="px-4 pb-4 border-t border-stone-100 dark:border-stone-800 pt-4">
        <p className="text-[10px] font-bold text-stone-400 uppercase tracking-wider mb-2">Quick Converter</p>
        <div className="flex gap-2 items-center">
          <input
            type="number"
            value={converterAmount}
            onChange={e => setConverterAmount(e.target.value)}
            className="w-24 bg-stone-50 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-lg px-2.5 py-2 text-sm font-mono font-bold text-stone-800 dark:text-stone-100 focus:outline-none focus:border-teal-500"
            placeholder="100"
          />
          <select
            value={converterCurrency}
            onChange={e => { setConverterCurrency(e.target.value); setConverterResult(null); }}
            className="bg-stone-50 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-lg px-2 py-2 text-sm font-bold text-stone-700 dark:text-stone-200 focus:outline-none focus:border-teal-500 cursor-pointer"
          >
            {TOP_CURRENCIES.map(c => (
              <option key={c.code} value={c.code}>{c.flag} {c.code}</option>
            ))}
          </select>
          <span className="text-xs text-stone-400 font-bold">→ INR</span>
          <button
            onClick={handleConvert}
            disabled={converting}
            className="bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white text-xs font-bold px-3 py-2 rounded-lg transition-all duration-200 cursor-pointer border-none shadow-[0_0_8px_rgba(15,110,86,0.2)]"
          >
            {converting ? "…" : "Go"}
          </button>
          {converterResult !== null && (
            <span className="text-sm font-mono font-bold text-teal-600 dark:text-teal-400">
              ₹{converterResult.toLocaleString("en-IN", { maximumFractionDigits: 2 })}
            </span>
          )}
        </div>
      </div>
    </div>
  );
};

export default CurrencyWidget;
