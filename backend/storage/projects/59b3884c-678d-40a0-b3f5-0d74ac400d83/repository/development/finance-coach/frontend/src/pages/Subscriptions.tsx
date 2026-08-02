import React from "react";
import { useFinance } from "../context/FinanceContext";

const Subscriptions: React.FC = () => {
  const {
    subscriptions,
    detectedSubs,
    setSubModalMode,
    setSubName,
    setSubAmount,
    setSubCategory,
    setSubBillingCycle,
    setSubNextDueDate,
    setShowSubModal,
    openEditSubModal,
    handleSubDelete,
    acceptDetectedSub,
  } = useFinance();

  const openAddModal = () => {
    setSubModalMode("add");
    setSubName("");
    setSubAmount("");
    setSubCategory("Others");
    setSubBillingCycle("Monthly");
    setSubNextDueDate(new Date().toISOString().split("T")[0]);
    setShowSubModal(true);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Subscriptions List */}
      <div className="lg:col-span-2 space-y-6">
        <div className="flex flex-wrap justify-between items-center gap-4 bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm transition-colors">
          <div>
            <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Registered subscriptions</h2>
            <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">Track recurring expenses and monthly due dates.</p>
          </div>
          <button
            onClick={openAddModal}
            className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer border-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
            </svg>
            Add subscription
          </button>
        </div>

        {subscriptions.length > 0 ? (
          <div className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 rounded-xl shadow-sm overflow-hidden transition-colors">
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="border-b border-stone-150 dark:border-stone-800 text-stone-450 dark:text-stone-550 text-[11px] font-bold uppercase tracking-wider">
                    <th className="py-4 pl-6">Subscription</th>
                    <th className="py-4">Billing cycle</th>
                    <th className="py-4">Next due date</th>
                    <th className="py-4 text-right pr-6">Amount</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-stone-50 dark:divide-stone-850 text-sm font-medium text-stone-700 dark:text-stone-300">
                  {subscriptions.map((s) => (
                    <tr key={s.id} className="hover:bg-stone-50/60 dark:hover:bg-stone-850/20 transition-colors group">
                      <td className="py-4 pl-6">
                        <div>
                          <p className="font-bold text-stone-800 dark:text-stone-150">{s.name}</p>
                          <p className="text-[10px] text-stone-450 dark:text-stone-500 uppercase font-bold tracking-wider">{s.category}</p>
                        </div>
                      </td>
                      <td className="py-4 text-xs font-bold text-stone-550 dark:text-stone-400">
                        <span className="bg-stone-100 dark:bg-stone-800 px-2.5 py-0.5 rounded-full">{s.billing_cycle}</span>
                      </td>
                      <td className="py-4 text-xs font-mono text-stone-655 dark:text-stone-350">{s.next_due_date}</td>
                      <td className="py-4 text-right pr-6 font-mono font-bold text-stone-800 dark:text-stone-200">
                        <span className="mr-6">₹{s.amount?.toLocaleString("en-IN") || 0}</span>
                        <span className="inline-flex gap-2.5 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={() => openEditSubModal(s)}
                            className="text-stone-400 hover:text-teal-700 dark:hover:text-teal-400 cursor-pointer bg-transparent border-none"
                            title="Edit subscription"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                              <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.128-1.897L16.863 4.487Zm0 0L19.5 7.125" />
                            </svg>
                          </button>
                          <button
                            onClick={() => handleSubDelete(s.id)}
                            className="text-stone-400 hover:text-coral-600 cursor-pointer bg-transparent border-none"
                            title="Remove subscription"
                          >
                            <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                              <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.34 9m-4.72 0-.34-9m9.03-3.03a17.902 17.902 0 0 1-1.07 3.5M18.13 6a22.09 22.09 0 0 0-1.85-.3M14.74 9a22.38 22.38 0 0 0-5.48 0M10.5 6.857V5.07c0-.704.57-1.286 1.27-1.286h2.46c.7 0 1.27.582 1.27 1.286v1.787M3.75 6a17.925 17.925 0 0 1 1.07-3.5M6.37 6a22.09 22.09 0 0 1 1.85-.3M6.37 6a22.38 22.38 0 0 1 5.48 0" />
                            </svg>
                          </button>
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 transition-colors">
            <p className="text-sm text-stone-450 dark:text-stone-550 font-medium">No recurring subscriptions registered yet.</p>
          </div>
        )}
      </div>

      {/* AI Auto-Detection Panel */}
      <div className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm flex flex-col justify-between h-fit transition-colors">
        <div>
          <div className="mb-6">
            <h3 className="font-serif font-bold text-stone-800 dark:text-stone-100 text-base">Recurring suggestions</h3>
            <p className="text-[11px] text-stone-400 dark:text-stone-500 font-medium mt-0.5">Auto-detected from transaction history</p>
          </div>

          {detectedSubs && detectedSubs.length > 0 ? (
            <div className="space-y-3">
              {detectedSubs.map((d, idx) => (
                <div key={idx} className="bg-stone-50 dark:bg-stone-950/50 p-3.5 border border-stone-100 dark:border-stone-850 rounded-lg flex justify-between items-center transition-all">
                  <div>
                    <p className="font-bold text-xs text-stone-750 dark:text-stone-200">{d.name}</p>
                    <p className="text-[10px] text-teal-700 dark:text-teal-450 font-mono font-bold mt-0.5">₹{d.amount}/month</p>
                    <p className="text-[9px] text-stone-400 dark:text-stone-500 font-semibold mt-1 font-mono">Est. due {d.next_due_date}</p>
                  </div>
                  <button
                    onClick={() => acceptDetectedSub(d)}
                    className="bg-teal-50 hover:bg-teal-100 dark:bg-teal-950/50 dark:hover:bg-teal-900 border border-teal-100 dark:border-teal-900 text-teal-700 dark:text-teal-400 text-[10px] font-bold px-2.5 py-1.5 rounded-md transition-all cursor-pointer"
                  >
                    + Track
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 bg-stone-50/60 dark:bg-stone-950/30 border border-dashed border-stone-200 dark:border-stone-800 rounded-lg">
              <p className="text-xs text-stone-500 dark:text-stone-400 font-medium">No patterns detected yet.</p>
              <p className="text-[10px] text-stone-400 dark:text-stone-500 mt-1 text-center px-4">Add more transactions to enable auto-detection.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Subscriptions;
