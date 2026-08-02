import React from "react";
import { useFinance } from "../context/FinanceContext";

const Calendar: React.FC = () => {
  const {
    subscriptions,
    calendarMonth,
    setCalendarMonth,
  } = useFinance();

  const year = calendarMonth.getFullYear();
  const month = calendarMonth.getMonth();
  const getDaysInMonth = (y: number, m: number) => new Date(y, m + 1, 0).getDate();
  const getFirstDayOfMonth = (y: number, m: number) => new Date(y, m, 1).getDay();
  const daysInMonth = getDaysInMonth(year, month);
  const firstDay = getFirstDayOfMonth(year, month);
  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
  const today = new Date();

  const getSubscriptionDueDates = () => {
    const dueDays: Record<number, string[]> = {};
    subscriptions.forEach(s => {
      if (s.next_due_date) {
        const d = new Date(s.next_due_date);
        if (d.getFullYear() === year && d.getMonth() === month) {
          const day = d.getDate();
          if (!dueDays[day]) dueDays[day] = [];
          dueDays[day].push(s.name);
        }
      }
    });
    return dueDays;
  };

  const dueDates = getSubscriptionDueDates();

  return (
    <div className="space-y-6">
      <div className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm">
        <div className="flex flex-wrap justify-between items-center gap-4 mb-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setCalendarMonth(new Date(year, month - 1, 1))}
              className="bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 dark:hover:bg-stone-750 p-2 rounded-lg cursor-pointer transition-all border-none"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4 text-stone-600 dark:text-stone-300">
                <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 19.5 8.25 12l7.5-7.5" />
              </svg>
            </button>
            <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">
              {calendarMonth.toLocaleString("default", { month: "long", year: "numeric" })}
            </h2>
            <button
              onClick={() => setCalendarMonth(new Date(year, month + 1, 1))}
              className="bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 dark:hover:bg-stone-750 p-2 rounded-lg cursor-pointer transition-all border-none"
            >
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4 text-stone-600 dark:text-stone-300">
                <path strokeLinecap="round" strokeLinejoin="round" d="m8.25 4.5 7.5 7.5-7.5 7.5" />
              </svg>
            </button>
          </div>
          <div className="flex items-center gap-2 text-xs text-stone-500 dark:text-stone-400">
            <span className="flex items-center gap-1.5"><span className="w-3 h-3 rounded-full bg-teal-600 inline-block"></span> Bill due</span>
            <span className="flex items-center gap-1.5 ml-4"><span className="w-3 h-3 rounded-full bg-coral-500 inline-block"></span> Today</span>
          </div>
        </div>

        {/* Day Names */}
        <div className="grid grid-cols-7 mb-2">
          {dayNames.map(d => (
            <div key={d} className="text-center text-[10px] font-bold uppercase text-stone-400 dark:text-stone-500 py-2">{d}</div>
          ))}
        </div>

        {/* Calendar Grid */}
        <div className="grid grid-cols-7 gap-1">
          {Array.from({ length: firstDay }).map((_, i) => (
            <div key={`empty-${i}`} className="h-16 rounded-lg"></div>
          ))}
          {Array.from({ length: daysInMonth }).map((_, i) => {
            const day = i + 1;
            const isToday = today.getDate() === day && today.getMonth() === month && today.getFullYear() === year;
            const bills = dueDates[day] || [];
            return (
              <div
                key={day}
                className={`h-16 rounded-lg border p-1.5 flex flex-col transition-all ${
                  isToday
                    ? "border-coral-300 bg-coral-50 dark:bg-coral-950/20"
                    : bills.length > 0
                    ? "border-teal-200 dark:border-teal-900 bg-teal-50 dark:bg-teal-950/20"
                    : "border-stone-100 dark:border-stone-800 bg-white dark:bg-stone-900"
                }`}
              >
                <span className={`text-xs font-mono font-bold ${isToday ? "text-coral-600 dark:text-coral-400" : "text-stone-500 dark:text-stone-400"}`}>{day}</span>
                <div className="flex flex-col gap-0.5 mt-0.5 overflow-hidden">
                  {bills.slice(0, 2).map((b, idx) => (
                    <span key={idx} className="text-[7px] font-bold text-teal-700 dark:text-teal-400 bg-teal-100 dark:bg-teal-950/60 px-1 rounded truncate">{b}</span>
                  ))}
                  {bills.length > 2 && <span className="text-[7px] text-stone-400">+{bills.length - 2} more</span>}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {subscriptions.length === 0 && (
        <div className="text-center py-10 bg-white dark:bg-stone-900 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
          <p className="text-sm text-stone-450 dark:text-stone-550 font-medium">No subscriptions tracked yet. Go to Subscriptions & bills to add them.</p>
        </div>
      )}
    </div>
  );
};

export default Calendar;
