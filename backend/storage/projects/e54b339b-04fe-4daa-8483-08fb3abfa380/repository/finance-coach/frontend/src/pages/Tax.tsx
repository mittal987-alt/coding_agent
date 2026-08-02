import React from "react";
import { useFinance } from "../context/FinanceContext";

const Tax: React.FC = () => {
  const { taxData } = useFinance();

  if (!taxData) {
    return (
      <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
        <p className="font-serif font-bold text-stone-700 dark:text-stone-300">No income data found</p>
        <p className="text-sm mt-1 text-stone-450 dark:text-stone-500">Upload statements or add income transactions to estimate your tax.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 mb-8">
      {/* Hero Tax Card */}
      <div className="bg-amber-700 dark:bg-amber-900 rounded-2xl p-6 sm:p-7 text-white">
        <div className="flex flex-col md:flex-row items-center gap-8">
          <div className="text-center flex-shrink-0">
            <p className="text-[11px] font-bold opacity-70 uppercase tracking-widest mb-1">Estimated tax liability</p>
            <p className="text-4xl font-mono font-bold">₹{taxData.total_tax_liability?.toLocaleString("en-IN")}</p>
            <p className="text-sm font-bold mt-1 opacity-80">Effective rate {taxData.effective_tax_rate}%</p>
          </div>
          <div className="flex-1 grid grid-cols-2 gap-3 w-full">
            <div className="bg-white/15 rounded-lg p-4">
              <p className="text-xs opacity-70 font-bold mb-1">Gross income</p>
              <p className="text-lg font-mono font-bold">₹{taxData.gross_income?.toLocaleString("en-IN")}</p>
            </div>
            <div className="bg-white/15 rounded-lg p-4">
              <p className="text-xs opacity-70 font-bold mb-1">Standard deduction</p>
              <p className="text-lg font-mono font-bold">₹{taxData.standard_deduction?.toLocaleString("en-IN")}</p>
            </div>
            <div className="bg-white/15 rounded-lg p-4">
              <p className="text-xs opacity-70 font-bold mb-1">Net taxable income</p>
              <p className="text-lg font-mono font-bold">₹{taxData.net_taxable_income?.toLocaleString("en-IN")}</p>
            </div>
            <div className="bg-white/15 rounded-lg p-4">
              <p className="text-xs opacity-70 font-bold mb-1">Rebate 87A</p>
              <p className="text-lg font-mono font-bold">₹{taxData.rebate_87A?.toLocaleString("en-IN")}</p>
            </div>
          </div>
        </div>
        <p className="text-xs opacity-70 mt-4 font-medium">{taxData.regime}</p>
      </div>

      {/* Slab Breakdown */}
      {taxData.slab_breakdown && taxData.slab_breakdown.length > 0 && (
        <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-6">
          <h2 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100 mb-4">Tax slab breakdown</h2>
          <div className="space-y-2.5">
            {taxData.slab_breakdown.map((slab: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-3 bg-stone-50 dark:bg-stone-800/50 rounded-lg">
                <div>
                  <p className="text-sm font-bold text-stone-700 dark:text-stone-200">{slab.slab}</p>
                  <p className="text-xs text-stone-500 dark:text-stone-400 font-mono">₹{slab.income_in_slab?.toLocaleString("en-IN")} in slab</p>
                </div>
                <div className="text-right">
                  <p className="text-xs font-bold text-amber-700 dark:text-amber-400">{slab.rate}</p>
                  <p className="text-sm font-mono font-bold text-stone-800 dark:text-stone-100">₹{slab.tax?.toLocaleString("en-IN")}</p>
                </div>
              </div>
            ))}
            <div className="flex items-center justify-between p-3 bg-amber-50 dark:bg-amber-950/20 rounded-lg border border-amber-100 dark:border-amber-900">
              <p className="text-sm font-bold text-amber-800 dark:text-amber-300">4% Health & education cess</p>
              <p className="text-sm font-mono font-bold text-amber-800 dark:text-amber-300">₹{taxData.cess_4pct?.toLocaleString("en-IN")}</p>
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-6">
        <h2 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100 mb-4">Tax saving tips</h2>
        <div className="space-y-2.5">
          {taxData.tips?.map((tip: string, i: number) => (
            <div key={i} className="flex gap-3 p-3.5 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-100 dark:border-blue-900">
              <p className="text-sm text-blue-800 dark:text-blue-300 font-medium">{tip}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Tax;
