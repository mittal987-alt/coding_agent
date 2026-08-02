import React from "react";
import { useFinance } from "../context/FinanceContext";

const Achievements: React.FC = () => {
  const { gamificationData } = useFinance();

  if (!gamificationData) {
    return (
      <div className="flex flex-col items-center justify-center py-20 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
        <p className="font-serif font-bold text-stone-700 dark:text-stone-300">Start tracking to earn badges</p>
        <p className="text-xs text-stone-450 dark:text-stone-500 mt-1">Your streaks and milestones will show up here.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 mb-8">
      {/* Level & XP Hero */}
      <div className="bg-amber-700 dark:bg-amber-900 rounded-2xl p-6 sm:p-7 text-white">
        <div className="flex flex-col md:flex-row items-center gap-8">
          <div className="text-center flex-shrink-0">
            <p className="text-xl font-serif font-bold">{gamificationData.level}</p>
            <p className="text-xs opacity-70 font-bold mt-1 font-mono">{gamificationData.total_xp} XP total</p>
          </div>
          <div className="flex-1 w-full">
            <div className="flex justify-between text-xs font-bold mb-2 font-mono">
              <span>Progress to next level</span>
              <span>{gamificationData.xp_progress} / {gamificationData.xp_needed} XP</span>
            </div>
            <div className="bg-white/20 rounded-full h-3 overflow-hidden">
              <div
                className="bg-white h-full rounded-full transition-all duration-700"
                style={{ width: `${gamificationData.progress_pct}%` }}
              ></div>
            </div>
            <div className="grid grid-cols-3 gap-3 mt-4">
              <div className="bg-white/15 rounded-lg p-3 text-center">
                <p className="text-xl font-mono font-bold">{gamificationData.streak_days}</p>
                <p className="text-xs font-bold mt-1">Day streak</p>
              </div>
              <div className="bg-white/15 rounded-lg p-3 text-center">
                <p className="text-xl font-mono font-bold">{gamificationData.earned_badge_count}</p>
                <p className="text-xs font-bold mt-1">Badges earned</p>
              </div>
              <div className="bg-white/15 rounded-lg p-3 text-center">
                <p className="text-xl font-mono font-bold">{gamificationData.stats?.savings_rate_pct}%</p>
                <p className="text-xs font-bold mt-1">Savings rate</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Badges Grid */}
      <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-6">
        <h2 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100 mb-4">Badge collection</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {gamificationData.badges?.map((badge: any) => (
            <div
              key={badge.id}
              className={`flex items-center gap-3 p-3.5 rounded-lg border transition-all ${
                badge.earned
                  ? "bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800"
                  : "bg-stone-50 dark:bg-stone-800/50 border-stone-100 dark:border-stone-700 opacity-50 grayscale"
              }`}
            >
              <span className="text-2xl leading-none">{badge.icon}</span>
              <div className="flex-1 min-w-0">
                <p className={`text-sm font-bold truncate ${badge.earned ? "text-amber-800 dark:text-amber-300" : "text-stone-500"}`}>{badge.name}</p>
                <p className="text-xs text-stone-400 truncate">{badge.description}</p>
                <p className="text-xs font-mono font-bold text-amber-600 mt-0.5">+{badge.xp} XP</p>
              </div>
              {badge.earned && <span className="text-teal-600 flex-shrink-0">✓</span>}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Achievements;
