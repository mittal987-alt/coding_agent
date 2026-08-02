import React, { useState, useEffect } from "react";

export const CurrencyConverterWidget: React.FC = () => {
  const [currencies, setCurrencies] = useState<{ code: string; name: string; symbol: string }[]>([]);
  const [fromCurrency, setFromCurrency] = useState("USD");
  const [toCurrency, setToCurrency] = useState("INR");
  const [amount, setAmount] = useState<string>("100");
  const [convertedAmount, setConvertedAmount] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetch("http://localhost:8000/currency/supported")
      .then((res) => res.json())
      .then((data) => setCurrencies(data))
      .catch((err) => console.error("Failed to load currencies", err));
  }, []);

  const handleConvert = async () => {
    if (!amount || isNaN(Number(amount))) return;
    setLoading(true);
    try {
      const res = await fetch(
        `http://localhost:8000/currency/convert?amount=${amount}&from_currency=${fromCurrency}&to_currency=${toCurrency}`
      );
      if (res.ok) {
        const data = await res.json();
        setConvertedAmount(data.converted);
      }
    } catch (error) {
      console.error("Conversion failed", error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-stone-900 rounded-2xl p-6 border border-stone-150 dark:border-stone-800 shadow-sm mt-7 transition-all">
      <div className="flex items-center gap-3 mb-5">
        <div className="bg-teal-50 dark:bg-teal-900/30 p-2.5 rounded-xl text-teal-700 dark:text-teal-400">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818l.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <div>
          <h3 className="font-serif font-bold text-lg text-stone-800 dark:text-stone-100">Currency Converter</h3>
          <p className="text-xs text-stone-500 dark:text-stone-400 font-medium">Live exchange rates</p>
        </div>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 items-end">
        <div className="flex-1 w-full">
          <label className="block text-[10px] font-bold text-stone-400 uppercase tracking-wider mb-1.5 ml-1">Amount</label>
          <div className="relative">
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="w-full bg-stone-50 dark:bg-stone-850/50 border border-stone-200 dark:border-stone-700/80 rounded-xl px-4 py-2.5 text-sm font-medium text-stone-800 dark:text-stone-200 focus:outline-none focus:ring-2 focus:ring-teal-500/50"
              placeholder="0.00"
            />
          </div>
        </div>

        <div className="flex-1 w-full flex items-center gap-3">
          <div className="flex-1">
            <label className="block text-[10px] font-bold text-stone-400 uppercase tracking-wider mb-1.5 ml-1">From</label>
            <select
              value={fromCurrency}
              onChange={(e) => setFromCurrency(e.target.value)}
              className="w-full bg-stone-50 dark:bg-stone-850/50 border border-stone-200 dark:border-stone-700/80 rounded-xl px-3 py-2.5 text-sm font-medium text-stone-800 dark:text-stone-200 focus:outline-none focus:ring-2 focus:ring-teal-500/50 appearance-none cursor-pointer"
            >
              {currencies.map(c => (
                <option key={c.code} value={c.code}>{c.code} - {c.name}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-center justify-center pt-5 text-stone-400">
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
              <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
            </svg>
          </div>

          <div className="flex-1">
            <label className="block text-[10px] font-bold text-stone-400 uppercase tracking-wider mb-1.5 ml-1">To</label>
            <select
              value={toCurrency}
              onChange={(e) => setToCurrency(e.target.value)}
              className="w-full bg-stone-50 dark:bg-stone-850/50 border border-stone-200 dark:border-stone-700/80 rounded-xl px-3 py-2.5 text-sm font-medium text-stone-800 dark:text-stone-200 focus:outline-none focus:ring-2 focus:ring-teal-500/50 appearance-none cursor-pointer"
            >
              {currencies.map(c => (
                <option key={c.code} value={c.code}>{c.code} - {c.name}</option>
              ))}
            </select>
          </div>
        </div>

        <button
          onClick={handleConvert}
          disabled={loading || !amount}
          className="w-full sm:w-auto bg-teal-700 hover:bg-teal-800 text-white px-6 py-2.5 rounded-xl font-bold text-sm transition-all shadow-sm shadow-teal-900/20 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center min-w-[100px]"
        >
          {loading ? "..." : "Convert"}
        </button>
      </div>

      {convertedAmount !== null && (
        <div className="mt-5 p-4 bg-teal-50/50 dark:bg-teal-900/10 border border-teal-100 dark:border-teal-900/30 rounded-xl flex items-center justify-between animate-in fade-in zoom-in-95 duration-200">
          <span className="text-sm font-medium text-stone-600 dark:text-stone-400">Result:</span>
          <div className="text-xl font-mono font-bold text-teal-800 dark:text-teal-400 flex items-center gap-1.5">
            {currencies.find(c => c.code === toCurrency)?.symbol}
            {convertedAmount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
            <span className="text-xs ml-1 font-sans text-teal-600/70 dark:text-teal-500/50">{toCurrency}</span>
          </div>
        </div>
      )}
    </div>
  );
};
