import React, { useState, useEffect } from "react";
import { useFinance } from "../context/FinanceContext";

const Notifications: React.FC = () => {
  const {
    alertsData,
    reminders,
    handleReminderPay,
    handleReminderDelete,
    handleReminderSnooze,
    setShowReminderModal,
  } = useFinance();

  const [permission, setPermission] = useState<NotificationPermission | "unsupported">(
    typeof window !== "undefined" && "Notification" in window ? Notification.permission : "unsupported"
  );

  const requestPermission = async () => {
    if (!("Notification" in window)) return;
    const result = await Notification.requestPermission();
    setPermission(result);
  };

  // Re-sync permission state if the user changes it via the browser's own UI
  useEffect(() => {
    if ("Notification" in window) setPermission(Notification.permission);
  }, []);

  const unpaid = reminders.filter((r: any) => !r.is_paid);
  const paid = reminders.filter((r: any) => r.is_paid);

  const groups: { key: string; label: string; items: any[]; style: string }[] = [
    { key: "overdue", label: "Overdue", items: unpaid.filter((r: any) => r.urgency === "overdue"), style: "border-coral-200 dark:border-coral-900 bg-coral-50 dark:bg-coral-950/20 text-coral-700 dark:text-coral-450" },
    { key: "urgent", label: "Due very soon", items: unpaid.filter((r: any) => r.urgency === "urgent"), style: "border-amber-200 dark:border-amber-900 bg-amber-50 dark:bg-amber-950/20 text-amber-700 dark:text-amber-400" },
    { key: "soon", label: "Coming up", items: unpaid.filter((r: any) => r.urgency === "soon"), style: "border-teal-200 dark:border-teal-900 bg-teal-50 dark:bg-teal-950/20 text-teal-700 dark:text-teal-400" },
    { key: "ok", label: "Later", items: unpaid.filter((r: any) => r.urgency === "ok"), style: "border-stone-150 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/50 text-stone-600 dark:text-stone-350" },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap justify-between items-center gap-4 bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm">
        <div>
          <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Notifications</h2>
          <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">Smart alerts and bill reminders, all in one place.</p>
        </div>
        <div className="flex items-center gap-3">
          {permission === "unsupported" ? (
            <span className="text-xs text-stone-400">Browser notifications aren't supported here.</span>
          ) : permission === "granted" ? (
            <span className="flex items-center gap-1.5 text-xs font-bold text-teal-700 dark:text-teal-400 bg-teal-50 dark:bg-teal-950/40 px-3 py-2 rounded-lg">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-600"></span>
              Browser alerts on
            </span>
          ) : permission === "denied" ? (
            <span className="text-xs font-bold text-coral-600 dark:text-coral-400 bg-coral-50 dark:bg-coral-950/30 px-3 py-2 rounded-lg">
              Blocked — enable in browser settings
            </span>
          ) : (
            <button
              onClick={requestPermission}
              className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-all cursor-pointer border-none"
            >
              Enable browser alerts
            </button>
          )}
          <button
            onClick={() => setShowReminderModal(true)}
            className="bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 dark:hover:bg-stone-750 text-stone-600 dark:text-stone-300 text-xs font-bold py-2.5 px-4 rounded-lg transition-all cursor-pointer border-none"
          >
            + Add reminder
          </button>
        </div>
      </div>

      {permission === "default" && (
        <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900 rounded-lg p-3.5 text-xs text-amber-800 dark:text-amber-300">
          Turn on browser alerts to get notified the moment a bill is due or overdue, even in another tab.
        </div>
      )}

      {/* Smart Alerts */}
      <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-6">
        <h3 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100 mb-4">Smart alerts</h3>
        {alertsData && alertsData.alerts?.length > 0 ? (
          <div className="space-y-2.5">
            {alertsData.alerts.map((alert: any, i: number) => (
              <div
                key={i}
                className={`p-4 rounded-lg text-sm font-medium border-l-4 ${
                  alert.type === "critical"
                    ? "bg-coral-50 dark:bg-coral-950/30 border-coral-500 text-coral-900 dark:text-coral-300"
                    : alert.type === "warning"
                    ? "bg-amber-50 dark:bg-amber-950/30 border-amber-500 text-amber-900 dark:text-amber-300"
                    : "bg-teal-50 dark:bg-teal-950/20 border-teal-500 text-teal-900 dark:text-teal-300"
                }`}
              >
                <p className="font-bold mb-0.5">{alert.title}</p>
                <p className="opacity-80 text-xs">{alert.message}</p>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-10 bg-stone-50/60 dark:bg-stone-900/40 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
            <p className="text-sm text-stone-500 dark:text-stone-400 font-semibold">No alerts right now.</p>
            <p className="text-xs text-stone-400 dark:text-stone-500 mt-1">You'll see budget, bill, and spending warnings here.</p>
          </div>
        )}
      </div>

      {/* Bill Reminders, grouped by urgency */}
      <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-6">
        <h3 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100 mb-4">Bill reminders</h3>

        {unpaid.length === 0 && paid.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 bg-stone-50/60 dark:bg-stone-900/40 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
            <p className="text-sm text-stone-500 dark:text-stone-400 font-semibold">No bill reminders set.</p>
            <p className="text-xs text-stone-400 dark:text-stone-500 mt-1">Add one to get notified before it's due.</p>
          </div>
        ) : (
          <div className="space-y-6">
            {groups.filter(g => g.items.length > 0).map(group => (
              <div key={group.key}>
                <p className="text-[11px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider mb-2">{group.label} ({group.items.length})</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {group.items.map((r: any) => (
                    <div key={r.id} className={`p-3.5 rounded-lg border flex justify-between items-center text-xs font-medium ${group.style}`}>
                      <div className="min-w-0 flex-1">
                        <p className="font-bold truncate flex items-center gap-1.5">
                          {r.name}
                          {r.is_recurring && (
                            <span className="text-[8px] font-bold uppercase tracking-wider bg-white/60 dark:bg-stone-900/60 px-1.5 py-0.5 rounded-full opacity-80" title={`Repeats ${r.recurrence_frequency}`}>
                              ↻ {r.recurrence_frequency}
                            </span>
                          )}
                        </p>
                        <p className="opacity-85 font-mono font-semibold">₹{r.amount?.toLocaleString("en-IN")} • {r.due_date}</p>
                        <p className="text-[10px] font-bold mt-0.5">
                          {r.days_left < 0 ? `Overdue by ${Math.abs(r.days_left)} days` : r.days_left === 0 ? "Due today" : `${r.days_left} days left`}
                        </p>
                      </div>
                      <div className="flex flex-col gap-1 ml-2 items-end">
                        <div className="flex gap-1.5">
                          <button onClick={() => handleReminderPay(r.id)} className="bg-white/80 dark:bg-stone-800 hover:bg-white dark:hover:bg-stone-700 px-2 py-1 rounded-md border border-current font-black text-[9px] cursor-pointer">Pay</button>
                          <button onClick={() => handleReminderDelete(r.id)} className="hover:text-coral-600 cursor-pointer p-1 text-stone-400 font-bold bg-transparent border-none" title="Delete">✕</button>
                        </div>
                        <button
                          onClick={() => handleReminderSnooze(r.id, 3)}
                          className="text-[9px] font-bold underline decoration-dotted opacity-70 hover:opacity-100 cursor-pointer bg-transparent border-none p-0"
                          title="Push due date back 3 days"
                        >
                          Snooze 3d
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}

            {paid.length > 0 && (
              <div>
                <p className="text-[11px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider mb-2">Paid ({paid.length})</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {paid.map((r: any) => (
                    <div key={r.id} className="p-3.5 rounded-lg border border-stone-150 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/40 flex justify-between items-center text-xs font-medium text-stone-500 dark:text-stone-400 opacity-70">
                      <div className="min-w-0 flex-1">
                        <p className="font-bold truncate">{r.name}</p>
                        <p className="opacity-85 font-mono font-semibold">₹{r.amount?.toLocaleString("en-IN")} • {r.due_date}</p>
                        <p className="text-[10px] font-bold mt-0.5 text-teal-600 dark:text-teal-400">Paid</p>
                      </div>
                      <button onClick={() => handleReminderDelete(r.id)} className="hover:text-coral-600 cursor-pointer p-1 text-stone-400 font-bold bg-transparent border-none" title="Delete">✕</button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default Notifications;
