import React from "react";
import { useFinance } from "../context/FinanceContext";

const Goals: React.FC = () => {
  const {
    goals,
    setGoalModalMode,
    setGoalName,
    setGoalTargetAmount,
    setGoalCurrentAmount,
    setGoalTargetDate,
    setShowGoalModal,
    openEditGoalModal,
    handleGoalDelete,
  } = useFinance();

  const openAddModal = () => {
    setGoalModalMode("add");
    setGoalName("");
    setGoalTargetAmount("");
    setGoalCurrentAmount("0");
    setGoalTargetDate(new Date().toISOString().split("T")[0]);
    setShowGoalModal(true);
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap justify-between items-center gap-4 bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm transition-colors">
        <div>
          <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Savings goals</h2>
          <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">Plan and track your milestones over time.</p>
        </div>
        <button
          onClick={openAddModal}
          className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer border-none"
        >
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
          </svg>
          Create savings goal
        </button>
      </div>

      {goals.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {goals.map((g) => {
            const percentage = Math.min((g.current_amount / g.target_amount) * 100, 100);
            const isCompleted = g.current_amount >= g.target_amount;
            return (
              <div key={g.id} className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 rounded-xl shadow-sm p-5 hover:shadow-md transition-all flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="font-bold text-stone-800 dark:text-stone-100 text-base">{g.name}</h3>
                      <p className="text-[10px] text-stone-400 dark:text-stone-500 font-medium">Target date {g.target_date}</p>
                    </div>
                    {isCompleted ? (
                      <span className="bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-400 text-[10px] font-bold px-2.5 py-1 rounded-full">
                        Completed
                      </span>
                    ) : (
                      <span className="bg-stone-100 dark:bg-stone-800 text-stone-500 dark:text-stone-400 text-[10px] font-bold px-2.5 py-1 rounded-full">
                        In progress
                      </span>
                    )}
                  </div>

                  <div className="mb-5">
                    <div className="flex justify-between text-xs font-mono font-bold text-stone-600 dark:text-stone-400 mb-1.5">
                      <span>{percentage.toFixed(0)}%</span>
                      <span>₹{g.current_amount.toLocaleString("en-IN")} / ₹{g.target_amount.toLocaleString("en-IN")}</span>
                    </div>
                    <div className="w-full bg-stone-100 dark:bg-stone-850 rounded-full h-2.5 overflow-hidden">
                      <div
                        className="h-2.5 rounded-full transition-all duration-500 bg-teal-600"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

                <div className="flex gap-2 border-t border-stone-100 dark:border-stone-850 pt-4">
                  <button
                    onClick={() => openEditGoalModal(g)}
                    className="flex-1 bg-stone-50 hover:bg-stone-100 dark:bg-stone-850 dark:hover:bg-stone-800 border border-stone-200 dark:border-stone-800 text-stone-600 dark:text-stone-300 text-xs font-bold py-2 rounded-lg transition-all cursor-pointer"
                  >
                    Log progress / edit
                  </button>
                  <button
                    onClick={() => handleGoalDelete(g.id)}
                    className="bg-coral-50 hover:bg-coral-100 dark:bg-coral-950/20 text-coral-600 dark:text-coral-450 text-xs font-bold p-2 rounded-lg border border-coral-100 dark:border-coral-900/60 transition-all cursor-pointer"
                    title="Delete goal"
                  >
                    ✕
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800 transition-colors">
          <h3 className="text-base font-serif font-bold text-stone-700 dark:text-stone-350">No savings goals yet</h3>
          <p className="text-xs text-stone-450 dark:text-stone-500 mt-1 mb-6 text-center max-w-sm">
            Add milestones to track purchases, emergency funds, or investment goals with automated progress reporting.
          </p>
          <button
            onClick={openAddModal}
            className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-6 rounded-lg transition-all cursor-pointer border-none"
          >
            Get started
          </button>
        </div>
      )}
    </div>
  );
};

export default Goals;
