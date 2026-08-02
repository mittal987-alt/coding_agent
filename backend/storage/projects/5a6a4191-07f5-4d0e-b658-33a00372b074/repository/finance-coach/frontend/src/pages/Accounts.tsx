import React from "react";
import { useFinance } from "../context/FinanceContext";

const Accounts: React.FC = () => {
  const {
    accounts,
    setAccountModalMode,
    setAccountName,
    setAccountType,
    setAccountBalance,
    setShowAccountModal,
    openEditAccountModal,
    handleAccountDelete,
  } = useFinance();

  const openAddModal = () => {
    setAccountModalMode("add");
    setAccountName("");
    setAccountType("Bank");
    setAccountBalance("0");
    setShowAccountModal(true);
  };

  // Left-border accent per account type, using the ledger palette
  const typeAccent: Record<string, string> = {
    Bank: "border-l-blue-500",
    "Credit Card": "border-l-coral-500",
    Cash: "border-l-teal-500",
    "UPI Wallet": "border-l-amber-500"
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4 bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm">
        <div>
          <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Wallets & accounts</h2>
          <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">Manage your bank accounts, cards, and wallets.</p>
        </div>
        <button
          onClick={openAddModal}
          className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer border-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Add account
        </button>
      </div>

      {accounts.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {accounts.map((a: any) => {
            const accent = typeAccent[a.account_type] || "border-l-stone-400";
            return (
              <div
                key={a.id}
                className={`bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 border-l-4 ${accent} rounded-xl p-5 shadow-sm hover:shadow-md transition-all group`}
              >
                <div className="flex justify-between items-start mb-7">
                  <div>
                    <p className="text-[10px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-widest">{a.account_type}</p>
                    <h3 className="text-base font-bold text-stone-800 dark:text-stone-100 mt-1">{a.name}</h3>
                  </div>
                  <div className="flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={() => openEditAccountModal(a)}
                      className="text-stone-400 hover:text-teal-700 dark:hover:text-teal-400 cursor-pointer bg-transparent border-none"
                      title="Edit"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.128-1.897L16.863 4.487Z" />
                      </svg>
                    </button>
                    <button
                      onClick={() => handleAccountDelete(a.id)}
                      className="text-stone-400 hover:text-coral-600 cursor-pointer bg-transparent border-none"
                      title="Delete"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.34 9m-4.72 0-.34-9M9.172 6.857V5.07c0-.704.57-1.286 1.27-1.286h2.46c.7 0 1.27.582 1.27 1.286v1.787M3.75 6a17.9 17.9 0 0 1 16.5 0" />
                      </svg>
                    </button>
                  </div>
                </div>
                <div>
                  <p className="text-[10px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider mb-1">Balance</p>
                  <p className="text-2xl font-mono font-bold text-stone-850 dark:text-stone-100">₹{a.balance?.toLocaleString("en-IN") || 0}</p>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
          <h3 className="text-base font-serif font-bold text-stone-700 dark:text-stone-350">No accounts added yet</h3>
          <p className="text-xs text-stone-450 dark:text-stone-500 mt-1 mb-6 text-center max-w-sm">Add bank accounts, credit cards, or wallets to track balances in one place.</p>
          <button
            onClick={openAddModal}
            className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-6 rounded-lg transition-all cursor-pointer border-none"
          >
            Add first account
          </button>
        </div>
      )}
    </div>
  );
};

export default Accounts;
