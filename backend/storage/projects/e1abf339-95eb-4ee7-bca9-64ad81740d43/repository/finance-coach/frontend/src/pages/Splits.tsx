import React from "react";
import { useFinance } from "../context/FinanceContext";

const Splits: React.FC = () => {
  const {
    splits,
    setSplitDescription,
    setSplitTotal,
    setSplitFriend,
    setSplitOwed,
    setShowSplitModal,
    handleSplitSettle,
    handleSplitDelete,
  } = useFinance();

  const totalOwed = splits
    .filter((s: any) => !s.is_settled)
    .reduce((sum: number, s: any) => sum + s.amount_owed, 0);

  const openAddModal = () => {
    setSplitDescription("");
    setSplitTotal("");
    setSplitFriend("");
    setSplitOwed("");
    setShowSplitModal(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4 bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm">
        <div>
          <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Shared bills</h2>
          <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">
            Total owed to you:{" "}
            <strong className="font-mono text-teal-700 dark:text-teal-400">
              ₹{totalOwed.toLocaleString("en-IN")}
            </strong>
          </p>
        </div>
        <button
          onClick={openAddModal}
          className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer border-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Record split
        </button>
      </div>

      {splits.length > 0 ? (
        <div className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 rounded-xl shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-stone-150 dark:border-stone-800 text-stone-450 dark:text-stone-550 text-[11px] font-bold uppercase tracking-wider">
                  <th className="py-4 pl-6">Description</th>
                  <th className="py-4">Friend</th>
                  <th className="py-4">Total bill</th>
                  <th className="py-4">They owe</th>
                  <th className="py-4 text-center">Status</th>
                  <th className="py-4 pr-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-stone-50 dark:divide-stone-850">
                {splits.map((s: any) => (
                  <tr key={s.id} className="hover:bg-stone-50/60 dark:hover:bg-stone-850/20 transition-colors">
                    <td className="py-4 pl-6 font-semibold text-stone-800 dark:text-stone-200 text-sm">{s.description}</td>
                    <td className="py-4 text-sm font-bold text-stone-600 dark:text-stone-350">{s.friend_name}</td>
                    <td className="py-4 text-sm font-mono text-stone-550 dark:text-stone-400">₹{s.total_amount?.toLocaleString("en-IN")}</td>
                    <td className="py-4 font-mono font-bold text-teal-700 dark:text-teal-400 text-sm">₹{s.amount_owed?.toLocaleString("en-IN")}</td>
                    <td className="py-4 text-center">
                      {s.is_settled ? (
                        <span className="bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-400 text-[10px] font-bold px-2.5 py-1 rounded-full">Settled</span>
                      ) : (
                        <span className="bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400 text-[10px] font-bold px-2.5 py-1 rounded-full">Pending</span>
                      )}
                    </td>
                    <td className="py-4 pr-6 text-right">
                      <div className="flex justify-end gap-2">
                        {!s.is_settled && (
                          <button
                            onClick={() => handleSplitSettle(s.id)}
                            className="bg-teal-50 hover:bg-teal-100 dark:bg-teal-950/30 text-teal-700 dark:text-teal-400 text-[10px] font-bold px-2.5 py-1.5 rounded-md cursor-pointer transition-all border-none"
                          >
                            Settle up
                          </button>
                        )}
                        <button
                          onClick={() => handleSplitDelete(s.id)}
                          className="text-stone-400 hover:text-coral-600 cursor-pointer p-1 bg-transparent border-none"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                            <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.34 9m-4.72 0-.34-9M9.172 6.857V5.07c0-.704.57-1.286 1.27-1.286h2.46c.7 0 1.27.582 1.27 1.286v1.787M3.75 6a17.9 17.9 0 0 1 16.5 0" />
                          </svg>
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
          <h3 className="text-base font-serif font-bold text-stone-700 dark:text-stone-350">No splits recorded</h3>
          <p className="text-xs text-stone-450 dark:text-stone-500 mt-1 mb-6 text-center max-w-sm">Track shared expenses for dinners, rent, trips, and more.</p>
          <button
            onClick={openAddModal}
            className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-6 rounded-lg transition-all cursor-pointer border-none"
          >
            Record first split
          </button>
        </div>
      )}
    </div>
  );
};

export default Splits;
