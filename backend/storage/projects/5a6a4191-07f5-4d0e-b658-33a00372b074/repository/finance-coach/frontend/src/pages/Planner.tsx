import React, { useState, useEffect } from "react";
import { useFinance } from "../context/FinanceContext";

const Planner: React.FC = () => {
  const { budgetPlan, handleApplyBudgetPlan, applyingPlan, netWorth } = useFinance();
  const [activeTab, setActiveTab] = useState<"budget" | "wealth">("budget");

  // Wealth & FIRE Simulator Inputs
  const [currentAge, setCurrentAge] = useState<number>(25);
  const [retirementAge, setRetirementAge] = useState<number>(55);
  const [lifeExpectancy, setLifeExpectancy] = useState<number>(85);
  const [startWealth, setStartWealth] = useState<string>("0");
  const [monthlySip, setMonthlySip] = useState<string>("15000");
  const [returnRate, setReturnRate] = useState<string>("12");
  const [inflation, setInflation] = useState<string>("6");
  const [retirementExpenseToday, setRetirementExpenseToday] = useState<string>("40000");

  // Prefill initial wealth from actual Net Worth once loaded
  useEffect(() => {
    if (netWorth && netWorth.net_worth !== undefined) {
      setStartWealth(String(Math.max(0, Math.round(netWorth.net_worth))));
    }
  }, [netWorth]);

  // Run Simulation Calculations
  const ageVal = Math.max(1, currentAge);
  const retireVal = Math.max(ageVal + 1, retirementAge);
  const lifeVal = Math.max(retireVal + 1, lifeExpectancy);
  const wealthVal = Math.max(0, parseFloat(startWealth) || 0);
  const sipVal = Math.max(0, parseFloat(monthlySip) || 0);
  const returnVal = Math.max(0, parseFloat(returnRate) || 0) / 100;
  const inflationVal = Math.max(0, parseFloat(inflation) || 0) / 100;
  const expenseVal = Math.max(0, parseFloat(retirementExpenseToday) || 0);

  const monthlyReturn = Math.pow(1 + returnVal, 1 / 12) - 1;

  let simulatedWealth = wealthVal;
  const yearByYear: any[] = [];
  let ageOfDepletion: number | null = null;
  let targetCorpusNeeded = 0;
  let corpusAtRetirement = 0;

  // Calculate target corpus needed at retirement: 
  // We calculate this as the present value of all retirement expenses from retirementAge to lifeExpectancy, discounted at return rate vs inflation.
  for (let age = ageVal; age <= lifeVal; age++) {
    const isAccumulating = age < retireVal;
    let interestEarned = 0;
    let annualInvestment = 0;
    let annualWithdrawal = 0;

    const startingWealth = simulatedWealth;

    if (isAccumulating) {
      for (let m = 0; m < 12; m++) {
        simulatedWealth += sipVal;
        const monthlyInterest = simulatedWealth * monthlyReturn;
        simulatedWealth += monthlyInterest;
        interestEarned += monthlyInterest;
        annualInvestment += sipVal;
      }
    } else {
      // Inflated monthly expense for this specific age
      const inflatedMonthlyExpense = expenseVal * Math.pow(1 + inflationVal, age - ageVal);
      for (let m = 0; m < 12; m++) {
        if (simulatedWealth > 0) {
          simulatedWealth -= inflatedMonthlyExpense;
          annualWithdrawal += inflatedMonthlyExpense;
          if (simulatedWealth < 0) {
            annualWithdrawal += simulatedWealth;
            simulatedWealth = 0;
          }
          const monthlyInterest = simulatedWealth * monthlyReturn;
          simulatedWealth += monthlyInterest;
          interestEarned += monthlyInterest;
        }
      }

      if (startingWealth > 0 && simulatedWealth === 0 && ageOfDepletion === null) {
        ageOfDepletion = age;
      }
    }

    if (age === retireVal) {
      corpusAtRetirement = startingWealth;
    }

    yearByYear.push({
      age,
      phase: isAccumulating ? "Accumulation" : "Retirement",
      annualSip: annualInvestment,
      annualWithdrawal: annualWithdrawal,
      interest: interestEarned,
      endingWealth: simulatedWealth,
    });
  }

  // Calculate approximate corpus needed at retirement age to survive until life expectancy
  let tempNeeded = 0;
  for (let age = retireVal; age <= lifeVal; age++) {
    const inflatedMonthlyExpense = expenseVal * Math.pow(1 + inflationVal, age - ageVal);
    // discounted back to retirement age
    const discountFactor = Math.pow(1 + returnVal, age - retireVal);
    tempNeeded += (inflatedMonthlyExpense * 12) / discountFactor;
  }
  targetCorpusNeeded = Math.round(tempNeeded);

  // Binary search required SIP to not deplete before life expectancy
  const findRequiredSip = () => {
    let low = 0;
    let high = 10000000; // 1 Cr monthly max
    let bestSip = 0;

    for (let iter = 0; iter < 40; iter++) {
      const mid = (low + high) / 2;
      let tempWealth = wealthVal;
      let failed = false;

      for (let age = ageVal; age <= lifeVal; age++) {
        const isAccumulating = age < retireVal;
        if (isAccumulating) {
          for (let m = 0; m < 12; m++) {
            tempWealth += mid;
            tempWealth += tempWealth * monthlyReturn;
          }
        } else {
          const inflatedMonthlyExpense = expenseVal * Math.pow(1 + inflationVal, age - ageVal);
          for (let m = 0; m < 12; m++) {
            tempWealth -= inflatedMonthlyExpense;
            if (tempWealth < 0) {
              tempWealth = 0;
              failed = true;
              break;
            }
            tempWealth += tempWealth * monthlyReturn;
          }
        }
      }

      if (tempWealth > 0 && !failed) {
        bestSip = mid;
        high = mid;
      } else {
        low = mid;
      }
    }
    return Math.ceil(bestSip);
  };

  const requiredSip = findRequiredSip();
  const hasShortfall = corpusAtRetirement < targetCorpusNeeded;

  return (
    <div className="space-y-6 mb-8">
      {/* Tab Navigation */}
      <div className="flex border-b border-stone-200 dark:border-stone-800">
        <button
          onClick={() => setActiveTab("budget")}
          className={`py-3 px-6 text-sm font-serif font-bold transition-all cursor-pointer border-none bg-transparent ${
            activeTab === "budget"
              ? "border-b-2 border-solid border-teal-700 text-teal-700 dark:text-teal-400"
              : "text-stone-450 hover:text-stone-700 dark:hover:text-stone-200"
          }`}
        >
          Smart budget planner
        </button>
        <button
          onClick={() => setActiveTab("wealth")}
          className={`py-3 px-6 text-sm font-serif font-bold transition-all cursor-pointer border-none bg-transparent ${
            activeTab === "wealth"
              ? "border-b-2 border-solid border-teal-700 text-teal-700 dark:text-teal-400"
              : "text-stone-450 hover:text-stone-700 dark:hover:text-stone-200"
          }`}
        >
          Wealth & FIRE Simulator
        </button>
      </div>

      {activeTab === "budget" ? (
        // --- BUDGET PLANNER TAB ---
        !budgetPlan ? (
          <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
            <p className="font-serif font-bold text-stone-700 dark:text-stone-300">No plan data yet</p>
            <p className="text-sm text-stone-450 mt-1">Add transactions and budgets to generate your personalized monthly plan.</p>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <h2 className="text-2xl font-serif font-bold text-stone-850 dark:text-stone-100">Smart budget planner</h2>
                <p className="text-sm text-stone-500 dark:text-stone-400">
                  Based on {budgetPlan.last_month} actuals • Projected savings:{" "}
                  <span className={`font-mono font-bold ${budgetPlan.projected_savings >= 0 ? "text-teal-700 dark:text-teal-400" : "text-coral-600 dark:text-coral-400"}`}>
                    ₹{budgetPlan.projected_savings?.toLocaleString("en-IN")}
                  </span>
                </p>
              </div>
              <button
                onClick={handleApplyBudgetPlan}
                disabled={applyingPlan}
                className="bg-teal-700 hover:bg-teal-800 disabled:bg-teal-400 text-white font-bold py-2.5 px-5 rounded-lg transition-all cursor-pointer flex items-center gap-2 text-sm border-none"
              >
                {applyingPlan && <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>}
                {applyingPlan ? "Applying…" : "Apply plan"}
              </button>
            </div>

            <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="bg-stone-50 dark:bg-stone-800 border-b border-stone-150 dark:border-stone-700">
                      <th className="text-left px-5 py-4 text-[11px] font-bold text-stone-500 uppercase tracking-wider">Category</th>
                      <th className="text-right px-5 py-4 text-[11px] font-bold text-stone-500 uppercase tracking-wider">Last month actual</th>
                      <th className="text-right px-5 py-4 text-[11px] font-bold text-stone-500 uppercase tracking-wider">Current budget</th>
                      <th className="text-right px-5 py-4 text-[11px] font-bold text-stone-500 uppercase tracking-wider">Suggested budget</th>
                      <th className="text-left px-5 py-4 text-[11px] font-bold text-stone-500 uppercase tracking-wider">Advice</th>
                    </tr>
                  </thead>
                  <tbody>
                    {budgetPlan.plan?.map((item: any, i: number) => (
                      <tr key={i} className="border-b border-stone-50 dark:border-stone-800/60 hover:bg-stone-50/60 dark:hover:bg-stone-800/30 transition-colors">
                        <td className="px-5 py-4 font-bold text-stone-800 dark:text-stone-200">{item.category}</td>
                        <td className="px-5 py-4 text-right font-mono text-stone-600 dark:text-stone-400">₹{item.last_month_actual?.toLocaleString("en-IN")}</td>
                        <td className="px-5 py-4 text-right font-mono text-stone-600 dark:text-stone-400">
                          {item.current_budget > 0 ? `₹${item.current_budget?.toLocaleString("en-IN")}` : "—"}
                        </td>
                        <td className="px-5 py-4 text-right font-mono font-bold text-teal-700 dark:text-teal-400">₹{item.suggested_budget?.toLocaleString("en-IN")}</td>
                        <td className="px-5 py-4">
                          <span
                            className={`text-xs font-bold px-2.5 py-1 rounded-full ${
                              item.status === "overspent"
                                ? "bg-coral-100 text-coral-700 dark:bg-coral-950/30 dark:text-coral-400"
                                : item.status === "unbudgeted"
                                ? "bg-amber-100 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400"
                                : "bg-teal-100 text-teal-700 dark:bg-teal-950/30 dark:text-teal-400"
                            }`}
                          >
                            {item.advice}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )
      ) : (
        // --- WEALTH & FIRE SIMULATOR TAB ---
        <div className="space-y-6">
          <div>
            <h2 className="text-2xl font-serif font-bold text-stone-850 dark:text-stone-100">Wealth & FIRE Simulator</h2>
            <p className="text-sm text-stone-500 dark:text-stone-400">Calculate financial independence and retirement projections based on compound interest.</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Form Column */}
            <div className="lg:col-span-1 bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 p-6 space-y-4">
              <h3 className="font-serif font-bold text-stone-800 dark:text-stone-200 border-b border-stone-100 dark:border-stone-800 pb-2 mb-3">Simulation Inputs</h3>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1">Current Age</label>
                  <input
                    type="number"
                    value={currentAge}
                    onChange={(e) => setCurrentAge(parseInt(e.target.value) || 0)}
                    className="w-full bg-stone-50 dark:bg-stone-850 border border-stone-200 dark:border-stone-700 rounded-lg p-2 font-mono text-sm focus:outline-none focus:border-teal-700 text-stone-850 dark:text-stone-100"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1">Retire Age</label>
                  <input
                    type="number"
                    value={retirementAge}
                    onChange={(e) => setRetirementAge(parseInt(e.target.value) || 0)}
                    className="w-full bg-stone-50 dark:bg-stone-850 border border-stone-200 dark:border-stone-700 rounded-lg p-2 font-mono text-sm focus:outline-none focus:border-teal-700 text-stone-850 dark:text-stone-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1">Life Expectancy (Age)</label>
                <input
                  type="number"
                  value={lifeExpectancy}
                  onChange={(e) => setLifeExpectancy(parseInt(e.target.value) || 0)}
                  className="w-full bg-stone-50 dark:bg-stone-850 border border-stone-200 dark:border-stone-700 rounded-lg p-2 font-mono text-sm focus:outline-none focus:border-teal-700 text-stone-850 dark:text-stone-100"
                />
              </div>

              <div>
                <label className="block text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1">Current Savings (₹)</label>
                <input
                  type="number"
                  value={startWealth}
                  onChange={(e) => setStartWealth(e.target.value)}
                  className="w-full bg-stone-50 dark:bg-stone-850 border border-stone-200 dark:border-stone-700 rounded-lg p-2 font-mono text-sm focus:outline-none focus:border-teal-700 text-stone-850 dark:text-stone-100"
                />
                <p className="text-[10px] text-stone-400 mt-0.5">Pre-filled with your actual Net Worth.</p>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1">Monthly SIP (₹)</label>
                <input
                  type="number"
                  value={monthlySip}
                  onChange={(e) => setMonthlySip(e.target.value)}
                  className="w-full bg-stone-50 dark:bg-stone-850 border border-stone-200 dark:border-stone-700 rounded-lg p-2 font-mono text-sm focus:outline-none focus:border-teal-700 text-stone-850 dark:text-stone-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1">Return Rate (%)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={returnRate}
                    onChange={(e) => setReturnRate(e.target.value)}
                    className="w-full bg-stone-50 dark:bg-stone-850 border border-stone-200 dark:border-stone-700 rounded-lg p-2 font-mono text-sm focus:outline-none focus:border-teal-700 text-stone-850 dark:text-stone-100"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1">Inflation (%)</label>
                  <input
                    type="number"
                    step="0.5"
                    value={inflation}
                    onChange={(e) => setInflation(e.target.value)}
                    className="w-full bg-stone-50 dark:bg-stone-850 border border-stone-200 dark:border-stone-700 rounded-lg p-2 font-mono text-sm focus:outline-none focus:border-teal-700 text-stone-850 dark:text-stone-100"
                  />
                </div>
              </div>

              <div>
                <label className="block text-[11px] font-bold text-stone-500 uppercase tracking-wider mb-1">Retirement Expenses/Month (₹)</label>
                <input
                  type="number"
                  value={retirementExpenseToday}
                  onChange={(e) => setRetirementExpenseToday(e.target.value)}
                  className="w-full bg-stone-50 dark:bg-stone-850 border border-stone-200 dark:border-stone-700 rounded-lg p-2 font-mono text-sm focus:outline-none focus:border-teal-700 text-stone-850 dark:text-stone-100"
                />
                <p className="text-[10px] text-stone-400 mt-0.5">Expressed in today's currency value.</p>
              </div>
            </div>

            {/* Results Column */}
            <div className="lg:col-span-2 space-y-6">
              {/* Summary Cards */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 rounded-xl p-5 shadow-sm">
                  <span className="text-[11px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider">Required Corpus</span>
                  <div className="text-2xl font-serif font-bold text-stone-800 dark:text-stone-100 mt-1 font-mono">
                    ₹{targetCorpusNeeded.toLocaleString("en-IN")}
                  </div>
                  <span className="text-xs text-stone-450 block mt-1">Needed by age {retireVal}</span>
                </div>

                <div className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 rounded-xl p-5 shadow-sm">
                  <span className="text-[11px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider">Projected Corpus</span>
                  <div className={`text-2xl font-serif font-bold mt-1 font-mono ${hasShortfall ? "text-coral-600 dark:text-coral-400" : "text-teal-700 dark:text-teal-400"}`}>
                    ₹{Math.round(corpusAtRetirement).toLocaleString("en-IN")}
                  </div>
                  <span className="text-xs text-stone-450 block mt-1">Accumulated by age {retireVal}</span>
                </div>
              </div>

              {/* Status Alert Box */}
              <div className={`rounded-xl border p-5 flex items-start gap-3.5 ${
                hasShortfall 
                  ? "bg-coral-50/50 dark:bg-coral-950/20 border-coral-200/50 dark:border-coral-900/30" 
                  : "bg-teal-50/50 dark:bg-teal-950/20 border-teal-200/50 dark:border-teal-900/30"
              }`}>
                <span className="text-xl leading-none">{hasShortfall ? "⚠️" : "🎉"}</span>
                <div className="space-y-1">
                  <h4 className={`font-serif font-bold text-sm ${hasShortfall ? "text-coral-800 dark:text-coral-400" : "text-teal-800 dark:text-teal-400"}`}>
                    {hasShortfall ? "Retirement Shortfall Detected" : "On Track for Financial Independence!"}
                  </h4>
                  <p className="text-xs text-stone-600 dark:text-stone-450 leading-relaxed">
                    {hasShortfall ? (
                      <>
                        Your projected savings at retirement will fall short by{" "}
                        <span className="font-mono font-bold">₹{Math.round(targetCorpusNeeded - corpusAtRetirement).toLocaleString("en-IN")}</span>. 
                        Your wealth will deplete at age <span className="font-bold">{ageOfDepletion || lifeVal}</span>.
                      </>
                    ) : (
                      <>
                        Excellent! Your wealth plan supports your retirement expenses. You will maintain a surplus balance of{" "}
                        <span className="font-mono font-bold">₹{Math.round(yearByYear[yearByYear.length - 1].endingWealth).toLocaleString("en-IN")}</span> at age {lifeVal}.
                      </>
                    )}
                  </p>

                  <div className="pt-2 text-xs border-t border-dashed border-stone-200 dark:border-stone-850 mt-2">
                    <span className="font-semibold text-stone-700 dark:text-stone-300">Coach Recommendation:</span>{" "}
                    {hasShortfall ? (
                      <>
                        Start investing <span className="font-mono font-bold text-teal-700 dark:text-teal-400">₹{requiredSip.toLocaleString("en-IN")}/month</span> (increase of ₹{(requiredSip - sipVal).toLocaleString("en-IN")}) to retire safely at age {retireVal}.
                      </>
                    ) : (
                      "Your investments are highly optimized. Keep maintaining this rate of saving!"
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Year by Year Table */}
          <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm overflow-hidden mt-6">
            <h3 className="font-serif font-bold text-stone-800 dark:text-stone-200 border-b border-stone-100 dark:border-stone-800 px-5 py-4">Yearly Projection Log</h3>
            <div className="overflow-x-auto max-h-96">
              <table className="w-full text-sm">
                <thead className="sticky top-0 bg-stone-50 dark:bg-stone-800 border-b border-stone-150 dark:border-stone-700 z-10">
                  <tr>
                    <th className="text-left px-5 py-3 text-[10px] font-bold text-stone-500 uppercase tracking-wider">Age</th>
                    <th className="text-left px-5 py-3 text-[10px] font-bold text-stone-500 uppercase tracking-wider">Phase</th>
                    <th className="text-right px-5 py-3 text-[10px] font-bold text-stone-500 uppercase tracking-wider">Annual SIP</th>
                    <th className="text-right px-5 py-3 text-[10px] font-bold text-stone-500 uppercase tracking-wider">Annual Spend</th>
                    <th className="text-right px-5 py-3 text-[10px] font-bold text-stone-500 uppercase tracking-wider">Interest Earned</th>
                    <th className="text-right px-5 py-3 text-[10px] font-bold text-stone-500 uppercase tracking-wider">Ending Wealth</th>
                  </tr>
                </thead>
                <tbody>
                  {yearByYear.map((row, i) => (
                    <tr key={i} className="border-b border-stone-50 dark:border-stone-850 hover:bg-stone-50/60 dark:hover:bg-stone-800/30 transition-colors">
                      <td className="px-5 py-3 font-bold text-stone-800 dark:text-stone-200 font-mono">{row.age}</td>
                      <td className="px-5 py-3">
                        <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                          row.phase === "Accumulation" 
                            ? "bg-teal-50 text-teal-700 dark:bg-teal-950/20 dark:text-teal-400" 
                            : "bg-amber-50 text-amber-700 dark:bg-amber-950/20 dark:text-amber-400"
                        }`}>
                          {row.phase}
                        </span>
                      </td>
                      <td className="px-5 py-3 text-right font-mono text-stone-600 dark:text-stone-400">
                        {row.annualSip > 0 ? `₹${Math.round(row.annualSip).toLocaleString("en-IN")}` : "—"}
                      </td>
                      <td className="px-5 py-3 text-right font-mono text-stone-600 dark:text-stone-400">
                        {row.annualWithdrawal > 0 ? `₹${Math.round(row.annualWithdrawal).toLocaleString("en-IN")}` : "—"}
                      </td>
                      <td className="px-5 py-3 text-right font-mono text-teal-600 dark:text-teal-500">
                        ₹{Math.round(row.interest).toLocaleString("en-IN")}
                      </td>
                      <td className={`px-5 py-3 text-right font-mono font-bold ${row.endingWealth === 0 ? "text-coral-600 dark:text-coral-450" : "text-stone-800 dark:text-stone-200"}`}>
                        ₹{Math.round(row.endingWealth).toLocaleString("en-IN")}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Planner;
