import React, { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { useFinance } from "../context/FinanceContext";

/* ============================================================================
   LAYOUT — sidebar shell
   Replaces the horizontal tab strip (12 tabs was overflowing the viewport)
   with a left sidebar. Same routes, same context, same modals — only the
   navigation chrome and palette changed. Visual identity: a "ledger" look —
   serif headings, monospace figures, warm paper background, teal / coral /
   gold accents instead of the indigo-violet gradient.
   ========================================================================= */

const NAV_LINKS: { to: string; label: string; badge?: number; end?: boolean }[] = [
  { to: "/", label: "Overview", end: true },
  { to: "/daily-brief", label: "Daily brief" },
  { to: "/notifications", label: "Notifications" },
  { to: "/goals", label: "Savings goals" },
  { to: "/subscriptions", label: "Subscriptions & bills" },
  { to: "/accounts", label: "Wallets & accounts" },
  { to: "/calendar", label: "Bill calendar" },
  { to: "/splits", label: "Shared bills" },
  { to: "/recurring", label: "Auto-pay" },
  { to: "/investments", label: "Portfolio" },
  { to: "/loans", label: "Loans" },
  { to: "/tax", label: "Tax estimator" },
  { to: "/planner", label: "Budget planner" },
  { to: "/achievements", label: "Achievements" },
  { to: "/challenges", label: "Challenges 🏆" },
  { to: "/settings", label: "Settings" }
];

// Fires a native browser notification once per reminder per day, only for
// unpaid bills that are due today, overdue, or due within 2 days. Dedupe key
// is stored in localStorage so refreshing/navigating doesn't re-fire.
function useBillNotifications(reminders: any[]) {
  React.useEffect(() => {
    if (typeof window === "undefined" || !("Notification" in window)) return;
    if (Notification.permission !== "granted") return;
    if (!reminders || reminders.length === 0) return;

    const today = new Date().toISOString().split("T")[0];
    const storageKey = `notified-reminders-${today}`;
    let notifiedToday: number[] = [];
    try {
      notifiedToday = JSON.parse(localStorage.getItem(storageKey) || "[]");
    } catch {
      notifiedToday = [];
    }

    const due = reminders.filter(
      (r: any) => !r.is_paid && typeof r.days_left === "number" && r.days_left <= 2 && !notifiedToday.includes(r.id)
    );

    if (due.length === 0) return;

    due.forEach((r: any) => {
      const body =
        r.days_left < 0
          ? `Overdue by ${Math.abs(r.days_left)} days — ₹${r.amount?.toLocaleString("en-IN")}`
          : r.days_left === 0
          ? `Due today — ₹${r.amount?.toLocaleString("en-IN")}`
          : `Due in ${r.days_left} days — ₹${r.amount?.toLocaleString("en-IN")}`;
      try {
        new Notification(r.name, { body, tag: `reminder-${r.id}` });
      } catch {
        /* Notification constructor can throw in some contexts; fail silently */
      }
    });

    localStorage.setItem(storageKey, JSON.stringify([...notifiedToday, ...due.map((r: any) => r.id)]));
  }, [reminders]);
}

const Layout: React.FC = () => {
  const {
    theme,
    setTheme,
    isUploading,
    uploadStatement,
    setFile,
    file,
    pdfPassword,
    setPdfPassword,
    pdfPasswordMessage,
    showPdfPasswordPrompt,
    userEmail,
    userName,
    showAlertsPanel,
    setShowAlertsPanel,
    alertsData,
    handleLogout,
    setAuthMode,
    setAuthError,
    setShowAuthModal,
    goals,
    subscriptions,
    accounts,
    splits,
    gamificationData,
    chatOpen,
    setChatOpen,
    chatMessages,
    chatLoading,
    chatInput,
    setChatInput,
    sendChatMessage,
    showAccountModal,
    setShowAccountModal,
    accountModalMode,
    accountName,
    setAccountName,
    accountType,
    setAccountType,
    accountBalance,
    setAccountBalance,
    handleAccountSubmit,
    showSplitModal,
    setShowSplitModal,
    splitDescription,
    setSplitDescription,
    splitTotal,
    setSplitTotal,
    splitFriend,
    setSplitFriend,
    splitOwed,
    setSplitOwed,
    handleSplitSubmit,
    showGoalModal,
    setShowGoalModal,
    goalModalMode,
    goalName,
    setGoalName,
    goalTargetAmount,
    setGoalTargetAmount,
    goalCurrentAmount,
    setGoalCurrentAmount,
    goalTargetDate,
    setGoalTargetDate,
    handleGoalSubmit,
    showSubModal,
    setShowSubModal,
    subModalMode,
    subName,
    setSubName,
    subAmount,
    setSubAmount,
    subCategory,
    setSubCategory,
    subBillingCycle,
    setSubBillingCycle,
    subNextDueDate,
    setSubNextDueDate,
    handleSubSubmit,
    showTxModal,
    setShowTxModal,
    txModalMode,
    txDescription,
    setTxDescription,
    txAmount,
    setTxAmount,
    txCategory,
    setTxCategory,
    txType,
    setTxType,
    txDate,
    setTxDate,
    txAccountId,
    setTxAccountId,
    txCurrency,
    setTxCurrency,
    statementCurrency,
    setStatementCurrency,
    supportedCurrencies,
    categories,
    handleTxSubmit,
    toasts,
    confirmState,
    respondConfirm,
    showAuthModal,
    authMode,
    authName,
    setAuthName,
    authEmail,
    setAuthEmail,
    authPassword,
    setAuthPassword,
    authError,
    isLoadingAuth,
    handleAuthSubmit,
    handleCSVExport,
    reminders,
    showReminderModal,
    setShowReminderModal,
    reminderName,
    setReminderName,
    reminderAmount,
    setReminderAmount,
    reminderDueDate,
    setReminderDueDate,
    reminderCategory,
    setReminderCategory,
    reminderIsRecurring,
    setReminderIsRecurring,
    reminderFrequency,
    setReminderFrequency,
    handleReminderSubmit,
    showReceiptScanModal,
    setShowReceiptScanModal,
    isScanningReceipt,
    scanReceipt,
  } = useFinance();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [showUploadPanel, setShowUploadPanel] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  // Local state for receipt scan preview
  const [selectedReceipt, setSelectedReceipt] = useState<File | null>(null);
  const [receiptPreview, setReceiptPreview] = useState<string | null>(null);

  useBillNotifications(reminders);

  const dueOrOverdueCount = (reminders || []).filter(
    (r: any) => !r.is_paid && (r.urgency === "overdue" || r.urgency === "urgent")
  ).length;

  const badgeFor = (to: string): number | undefined => {
    if (to === "/notifications") return dueOrOverdueCount || undefined;
    if (to === "/goals") return goals.length || undefined;
    if (to === "/subscriptions") return subscriptions.length || undefined;
    if (to === "/accounts") return accounts.length || undefined;
    if (to === "/splits") return splits.filter(s => !s.is_settled).length || undefined;
    if (to === "/achievements" && gamificationData) return gamificationData.earned_badge_count || undefined;
    return undefined;
  };

  return (
    <div className="min-h-screen bg-stone-50 dark:bg-stone-950 font-sans antialiased text-stone-900 dark:text-stone-100 transition-colors duration-300">
      <div className="flex">
        {/* ============================== SIDEBAR ============================== */}
        <aside
  className={`fixed lg:sticky top-0 z-30 h-screen w-72 shrink-0 bg-white/80 dark:bg-stone-900/60 backdrop-blur-xl border-r border-stone-200 dark:border-stone-700/50 flex flex-col transition-transform duration-300 ${
    sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
  }`}
>
          <Link to="/" className="flex items-center gap-3 px-6 py-6 border-b border-stone-200 dark:border-stone-800 decoration-transparent">
            <div className="w-9 h-9 rounded-md bg-teal-700 dark:bg-teal-600 text-white flex items-center justify-center font-serif font-bold text-lg shrink-0">₹</div>
            <div className="min-w-0">
              <h1 className="font-serif font-bold text-lg leading-tight text-stone-900 dark:text-stone-50 truncate">Finance Coach</h1>
              <p className="text-[11px] text-stone-400 dark:text-stone-500 font-medium tracking-wide uppercase">Your money, kept</p>
            </div>
            <button onClick={(e) => { e.preventDefault(); setSidebarOpen(false); }} className="ml-auto lg:hidden text-stone-400 cursor-pointer bg-transparent border-none">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </Link>

          <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-0.5">
            {NAV_LINKS.map(link => {
              const badge = badgeFor(link.to);
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  end={link.end}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    `w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-semibold transition-all cursor-pointer relative decoration-transparent ${
                      isActive
                        ? "bg-teal-50 dark:bg-teal-950/40 text-teal-800 dark:text-teal-300"
                        : "text-stone-500 dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800/60 hover:text-stone-700 dark:hover:text-stone-200"
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      {isActive && <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r bg-teal-700 dark:bg-teal-400" />}
                      <span className="flex-1 text-left">{link.label}</span>
                      {!!badge && (
                        <span className="text-[10px] font-bold bg-stone-100 dark:bg-stone-800 text-stone-500 dark:text-stone-400 rounded-full px-1.5 py-0.5 min-w-[18px] text-center">
                          {badge}
                        </span>
                      )}
                    </>
                  )}
                </NavLink>
              );
            })}
          </nav>

          <div className="p-4 border-t border-stone-200 dark:border-stone-800 space-y-3">
            <div className="flex gap-2">
              <button
                onClick={() => {
                  const a = document.createElement("a");
                  a.href = `http://127.0.0.1:8000/report/pdf?email=${userEmail}`;
                  a.click();
                }}
                className="flex-1 flex items-center justify-center gap-1.5 bg-coral-50 hover:bg-coral-100 dark:bg-coral-950/30 dark:hover:bg-coral-950/50 text-coral-700 dark:text-coral-400 border border-coral-100 dark:border-coral-900 text-[11px] font-bold px-2 py-2 rounded-md transition-all cursor-pointer"
                title="Download health report PDF"
              >
                PDF report
              </button>
              <button
                onClick={handleCSVExport}
                className="flex-1 flex items-center justify-center gap-1.5 bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 dark:hover:bg-stone-750 text-stone-600 dark:text-stone-300 text-[11px] font-bold px-2 py-2 rounded-md transition-all cursor-pointer border-none"
                title="Export transactions as CSV"
              >
                Export CSV
              </button>
            </div>

            <button
              onClick={() => setTheme(theme === "light" ? "dark" : "light")}
              className="w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-bold text-stone-500 dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800/60 transition-all cursor-pointer bg-transparent border-none"
            >
              {theme === "light" ? (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m0 13.5V21M9.75 15h4.5m-4.5-6h4.5m-7.364-3.636 1.591 1.591m8.546 8.546 1.591 1.591M3 12h2.25m13.5 0H21M5.757 18.243l1.591-1.591m8.546-8.546 1.591-1.591M12 7.5a4.5 4.5 0 1 1 0 9 4.5 4.5 0 0 1 0-9Z" />
                </svg>
              )}
              {theme === "light" ? "Switch to dark" : "Switch to light"}
            </button>

            {userEmail ? (
              <div className="flex items-center gap-2 px-1">
                <div className="w-8 h-8 rounded-full bg-teal-100 dark:bg-teal-950/60 text-teal-800 dark:text-teal-300 flex items-center justify-center text-xs font-bold shrink-0">
                  {(userName || userEmail).slice(0, 1).toUpperCase()}
                </div>
                <span className="text-xs font-semibold text-stone-600 dark:text-stone-300 truncate flex-1" title={userName || userEmail}>
                  {userName || userEmail}
                </span>
                <button onClick={handleLogout} title="Sign out" className="text-stone-400 hover:text-coral-600 cursor-pointer p-1 bg-transparent border-none">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l-3 3m0 0 3 3m-3-3h12.75" />
                  </svg>
                </button>
              </div>
            ) : (
              <button
                onClick={() => { setAuthMode("login"); setAuthError(""); setShowAuthModal(true); }}
                className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white text-xs font-bold py-2.5 rounded-md transition-all duration-300 transform hover:-translate-y-0.5 shadow-[0_0_15px_rgba(15,110,86,0.3)] hover:shadow-[0_0_20px_rgba(20,184,166,0.5)] cursor-pointer border-none"
              >
                Sign in
              </button>
            )}
          </div>
        </aside>

        {sidebarOpen && <div onClick={() => setSidebarOpen(false)} className="fixed inset-0 bg-stone-900/40 z-20 lg:hidden" />}

        {/* ============================== MAIN ============================== */}
        <main className="flex-1 min-w-0">
          <header className="sticky top-0 z-10 bg-stone-50/80 dark:bg-stone-950/70 backdrop-blur-xl border-b border-stone-200 dark:border-stone-700/50 shadow-sm px-5 sm:px-8 py-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-stone-500 cursor-pointer bg-transparent border-none">
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                </svg>
              </button>

              <div className="flex flex-wrap items-center gap-3 ml-auto">
                {/* Scan receipt — compact button that opens a popover */}
                <div className="relative">
                  <button
                    onClick={() => {
                      setShowReceiptScanModal(!showReceiptScanModal);
                      setShowUploadPanel(false);
                    }}
                    className="relative flex items-center gap-1.5 bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 hover:bg-stone-50 dark:hover:bg-stone-800 text-stone-600 dark:text-stone-300 text-xs font-bold py-2.5 px-3.5 rounded-lg transition-all cursor-pointer"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.25} stroke="currentColor" className="w-4 h-4">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 0 1 5.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 0 0 2.25 2.25h15A2.25 2.25 0 0 0 21.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 0 0-1.134-.175 2.31 2.31 0 0 1-1.64-1.055l-.822-1.316a2.192 2.192 0 0 0-1.736-1.039 48.774 48.774 0 0 0-5.232 0 2.192 2.192 0 0 0-1.736 1.039l-.821 1.316Z" />
                      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 1 1-9 0 4.5 4.5 0 0 1 9 0ZM18.75 10.5h.008v.008h-.008V10.5Z" />
                    </svg>
                    <span className="hidden sm:inline">Scan receipt</span>
                    {selectedReceipt && <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-teal-600"></span>}
                  </button>

                  {showReceiptScanModal && (
                    <div className="absolute right-0 top-12 w-80 bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-xl shadow-xl z-50 p-4">
                      <div className="flex justify-between items-center mb-3">
                        <p className="text-xs font-bold uppercase tracking-wider text-stone-400 dark:text-stone-500">Scan receipt photo</p>
                        <button
                          onClick={() => setShowReceiptScanModal(false)}
                          className="text-stone-400 hover:text-stone-600 cursor-pointer text-lg leading-none bg-transparent border-none"
                        >
                          ×
                        </button>
                      </div>
                      <div className="flex flex-col gap-3">
                        <div className="flex items-center gap-2 bg-stone-50 dark:bg-stone-950 p-1.5 rounded-lg border border-stone-200 dark:border-stone-800">
                          <input
                            id="receipt-upload-input"
                            type="file"
                            accept="image/*"
                            capture="environment"
                            onChange={(e) => {
                              if (e.target.files?.[0]) {
                                const file = e.target.files[0];
                                setSelectedReceipt(file);
                                const reader = new FileReader();
                                reader.onloadend = () => {
                                  setReceiptPreview(reader.result as string);
                                };
                                reader.readAsDataURL(file);
                              }
                            }}
                            className="text-xs text-stone-600 dark:text-stone-300 file:mr-2 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-white dark:file:bg-stone-800 file:text-teal-700 dark:file:text-teal-400 hover:file:bg-teal-50 cursor-pointer flex-1 min-w-0"
                          />
                        </div>

                        {receiptPreview && (
                          <div className="flex flex-col items-center justify-center border border-stone-150 dark:border-stone-800 rounded-lg p-2 bg-stone-50 dark:bg-stone-950">
                            <img
                              src={receiptPreview}
                              alt="Receipt Preview"
                              className="max-h-36 rounded-md object-contain"
                            />
                            <button
                              onClick={() => {
                                setSelectedReceipt(null);
                                setReceiptPreview(null);
                                const fileInput = document.getElementById("receipt-upload-input") as HTMLInputElement;
                                if (fileInput) fileInput.value = "";
                              }}
                              className="text-[10px] text-coral-600 hover:underline mt-2 font-bold cursor-pointer bg-transparent border-none"
                            >
                              Remove photo
                            </button>
                          </div>
                        )}

                          <button
                            onClick={() => {
                              if (selectedReceipt) {
                                scanReceipt(selectedReceipt).then(() => {
                                  setSelectedReceipt(null);
                                  setReceiptPreview(null);
                                });
                              }
                            }}
                            disabled={isScanningReceipt || !selectedReceipt}
                            className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 disabled:from-stone-400 disabled:to-stone-400 dark:disabled:from-stone-800 dark:disabled:to-stone-800 text-white text-xs font-bold py-2.5 rounded-md transition-all duration-300 transform hover:-translate-y-0.5 shadow-[0_0_15px_rgba(15,110,86,0.3)] hover:shadow-[0_0_20px_rgba(20,184,166,0.5)] flex items-center justify-center gap-1.5 cursor-pointer border-none"
                          >
                          {isScanningReceipt ? (
                            <>
                              <span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                              Reading receipt…
                            </>
                          ) : (
                            "Scan receipt"
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>

                {/* Upload statement — compact button that opens a popover */}
                <div className="relative">
                  <button
                    onClick={() => {
                      setShowUploadPanel(v => !v);
                      setShowReceiptScanModal(false);
                    }}
                    className="relative flex items-center gap-1.5 bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 hover:bg-stone-50 dark:hover:bg-stone-800 text-stone-600 dark:text-stone-300 text-xs font-bold py-2.5 px-3.5 rounded-lg transition-all cursor-pointer"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.25} stroke="currentColor" className="w-4 h-4">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
                    </svg>
                    <span className="hidden sm:inline">Upload statement</span>
                    {file && <span className="absolute -top-1 -right-1 w-2.5 h-2.5 rounded-full bg-teal-600"></span>}
                  </button>

                  {showUploadPanel && (
                    <div className="absolute right-0 top-12 w-80 bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-xl shadow-xl z-50 p-4">
                      <div className="flex justify-between items-center mb-3">
                        <p className="text-xs font-bold uppercase tracking-wider text-stone-400 dark:text-stone-500">Upload bank statement</p>
                        <button onClick={() => setShowUploadPanel(false)} className="text-stone-400 hover:text-stone-600 cursor-pointer text-lg leading-none bg-transparent border-none">×</button>
                      </div>
                      <div className="flex items-center gap-2 bg-stone-50 dark:bg-stone-950 p-1.5 rounded-lg border border-stone-200 dark:border-stone-800 mb-1">
                        <input
                          id="file-upload-input"
                          type="file"
                          accept=".pdf"
                          onChange={(e) => { if (e.target.files?.[0]) setFile(e.target.files[0]); }}
                          className="text-xs text-stone-600 dark:text-stone-300 file:mr-2 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-white dark:file:bg-stone-800 file:text-teal-700 dark:file:text-teal-400 hover:file:bg-teal-50 cursor-pointer flex-1 min-w-0"
                        />
                      </div>
                      {file && <p className="text-[11px] text-stone-450 dark:text-stone-500 mb-2 truncate">Selected: {file.name}</p>}
                      <div className="mb-3">
                        <label className="block text-[10px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider mb-1">Statement currency</label>
                        <select
                          value={statementCurrency}
                          onChange={(e) => setStatementCurrency(e.target.value)}
                          className="w-full text-xs bg-stone-50 dark:bg-stone-950 border border-stone-200 dark:border-stone-800 rounded-md px-2 py-1.5 text-stone-700 dark:text-stone-200 cursor-pointer"
                        >
                          {supportedCurrencies.map(c => <option key={c.code} value={c.code}>{c.code} ({c.symbol})</option>)}
                        </select>
                      </div>
                      <button
                        onClick={() => uploadStatement()}
                        disabled={isUploading || !file}
                        className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 disabled:from-stone-400 disabled:to-stone-400 dark:disabled:from-stone-800 dark:disabled:to-stone-800 text-white text-xs font-bold py-2.5 rounded-md transition-all duration-300 transform hover:-translate-y-0.5 shadow-[0_0_15px_rgba(15,110,86,0.3)] hover:shadow-[0_0_20px_rgba(20,184,166,0.5)] flex items-center justify-center gap-1.5 cursor-pointer border-none"
                      >
                        {isUploading ? (
                          <><span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>Parsing…</>
                        ) : "Upload statement"}
                      </button>

                      {(file || showPdfPasswordPrompt) && (
                        <div className="mt-3 rounded-lg border border-amber-300 bg-amber-50 p-2.5 text-xs text-amber-800 dark:border-amber-700 dark:bg-amber-950/30 dark:text-amber-300">
                          <p className="mb-2 font-medium">{pdfPasswordMessage || "If your PDF is encrypted, enter the password here before uploading."}</p>
                          <div className="flex items-center gap-2">
                            <input
                              type="password"
                              value={pdfPassword}
                              onChange={(e) => setPdfPassword(e.target.value)}
                              placeholder="PDF password"
                              className="w-full rounded-md border border-amber-300 bg-white px-2 py-1.5 text-xs text-stone-700 outline-none dark:border-amber-700 dark:bg-stone-900 dark:text-stone-200"
                            />
                            <button
                              onClick={() => uploadStatement()}
                              disabled={isUploading || (!pdfPassword.trim() && !file)}
                              className="rounded-md bg-amber-600 px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-amber-700 disabled:bg-amber-400 border-none whitespace-nowrap"
                            >
                              Apply
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>

                {/* Alerts bell */}
                {userEmail && (
                  <div className="relative">
                    <button
                      onClick={() => setShowAlertsPanel(!showAlertsPanel)}
                      className="relative p-2.5 rounded-lg border border-stone-200 dark:border-stone-800 bg-white dark:bg-stone-900 hover:bg-stone-50 dark:hover:bg-stone-800 transition-all text-stone-500 dark:text-stone-300 cursor-pointer"
                      title="Smart alerts"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                        <path strokeLinecap="round" strokeLinejoin="round" d="M14.857 17.082a23.848 23.848 0 0 0 5.454-1.31A8.967 8.967 0 0 1 18 9.75V9A6 6 0 0 0 6 9v.75a8.967 8.967 0 0 1-2.312 6.022c1.733.64 3.56 1.085 5.455 1.31m5.714 0a24.255 24.255 0 0 1-5.714 0m5.714 0a3 3 0 1 1-5.714 0" />
                      </svg>
                      {alertsData && alertsData.critical_count > 0 && (
                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-coral-600 text-white text-[9px] font-black rounded-full flex items-center justify-center">{alertsData.critical_count}</span>
                      )}
                      {alertsData && alertsData.critical_count === 0 && alertsData.warning_count > 0 && (
                        <span className="absolute -top-1 -right-1 w-4 h-4 bg-amber-400 text-white text-[9px] font-black rounded-full flex items-center justify-center">{alertsData.warning_count}</span>
                      )}
                    </button>
                    {showAlertsPanel && alertsData && (
                      <div className="absolute right-0 top-12 w-96 max-h-[420px] overflow-y-auto bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-xl shadow-xl z-50 p-4">
                        <div className="flex justify-between items-center mb-3">
                          <h3 className="text-sm font-bold font-serif text-stone-800 dark:text-stone-100">Smart alerts</h3>
                          <button onClick={() => setShowAlertsPanel(false)} className="text-stone-400 hover:text-stone-600 cursor-pointer text-lg leading-none bg-transparent border-none">×</button>
                        </div>
                        <div className="space-y-2">
                          {alertsData.alerts.map((alert: any, i: number) => (
                            <div key={i} className={`p-3 rounded-lg text-xs font-medium border-l-4 ${
                              alert.type === "critical" ? "bg-coral-50 dark:bg-coral-950/30 border-coral-500 text-coral-900 dark:text-coral-300" :
                              alert.type === "warning" ? "bg-amber-50 dark:bg-amber-950/30 border-amber-500 text-amber-900 dark:text-amber-300" :
                              "bg-teal-50 dark:bg-teal-950/20 border-teal-500 text-teal-900 dark:text-teal-300"
                            }`}>
                              <p className="font-bold mb-0.5">{alert.title}</p>
                              <p className="opacity-80">{alert.message}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Identity — avatar with dropdown */}
                {userEmail ? (
                  <div className="relative">
                    <button
                      onClick={() => setShowUserMenu(v => !v)}
                      className="flex items-center gap-2 bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 hover:bg-stone-50 dark:hover:bg-stone-800 rounded-lg pl-1.5 pr-2.5 py-1.5 transition-all cursor-pointer"
                    >
                      <div className="w-7 h-7 rounded-full bg-teal-700 dark:bg-teal-600 text-white flex items-center justify-center text-xs font-bold shrink-0">
                        {userEmail.slice(0, 1).toUpperCase()}
                      </div>
                      <span className="text-xs font-semibold text-stone-700 dark:text-stone-200 max-w-[160px] truncate hidden sm:inline">{userEmail}</span>
                      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.25} stroke="currentColor" className="w-3.5 h-3.5 text-stone-400 hidden sm:inline">
                        <path strokeLinecap="round" strokeLinejoin="round" d="m19.5 8.25-7.5 7.5-7.5-7.5" />
                      </svg>
                    </button>
                    {showUserMenu && (
                      <div className="absolute right-0 top-12 w-60 bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-xl shadow-xl z-50 p-2">
                        <div className="px-2.5 py-2 border-b border-stone-100 dark:border-stone-800 mb-1">
                          <p className="text-[10px] font-bold text-stone-400 uppercase tracking-wider">Signed in as</p>
                          <p className="text-xs font-semibold text-stone-700 dark:text-stone-200 truncate mt-0.5">{userEmail}</p>
                        </div>
                        <button
                          onClick={() => { setTheme(theme === "light" ? "dark" : "light"); setShowUserMenu(false); }}
                          className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-semibold text-stone-600 dark:text-stone-300 hover:bg-stone-50 dark:hover:bg-stone-800 transition-all cursor-pointer bg-transparent border-none text-left"
                        >
                          {theme === "light" ? "Switch to dark theme" : "Switch to light theme"}
                        </button>
                        <button
                          onClick={() => { setShowUserMenu(false); handleLogout(); }}
                          className="w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-xs font-semibold text-coral-600 dark:text-coral-400 hover:bg-coral-50 dark:hover:bg-coral-950/30 transition-all cursor-pointer bg-transparent border-none text-left"
                        >
                          Sign out
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  <button
                    onClick={() => { setAuthMode("login"); setAuthError(""); setShowAuthModal(true); }}
                    className="bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-all duration-300 transform hover:-translate-y-0.5 shadow-[0_0_15px_rgba(15,110,86,0.3)] hover:shadow-[0_0_20px_rgba(20,184,166,0.5)] cursor-pointer border-none"
                  >
                    Sign in
                  </button>
                )}
              </div>
            </div>
          </header>

          <div className="px-5 sm:px-8 py-7 pb-28">
            <Outlet />
          </div>
        </main>
      </div>

      {/* ============================== MODALS ============================== */}

      {showAccountModal && (
        <Modal onClose={() => setShowAccountModal(false)} title={accountModalMode === "add" ? "Add account" : "Edit account"} desc="Track balance across your wallets and bank accounts">
          <form onSubmit={handleAccountSubmit} className="space-y-4">
            <Field label="Account name"><input type="text" required value={accountName} onChange={e => setAccountName(e.target.value)} placeholder="e.g. HDFC Savings" className="modal-input" /></Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Account type">
                <select value={accountType} onChange={e => setAccountType(e.target.value)} className="modal-input cursor-pointer">
                  {["Bank","Credit Card","Cash","UPI Wallet"].map(t => <option key={t}>{t}</option>)}
                </select>
              </Field>
              <Field label="Balance (₹)"><input type="number" value={accountBalance} onChange={e => setAccountBalance(e.target.value)} placeholder="0" className="modal-input" /></Field>
            </div>
            <SubmitButton>{accountModalMode === "add" ? "Add account" : "Save changes"}</SubmitButton>
          </form>
        </Modal>
      )}

      {showSplitModal && (
        <Modal onClose={() => setShowSplitModal(false)} title="Record split bill" desc="Track shared expenses with friends or housemates">
          <form onSubmit={handleSplitSubmit} className="space-y-4">
            <Field label="Description"><input type="text" required value={splitDescription} onChange={e => setSplitDescription(e.target.value)} placeholder="e.g. Group dinner" className="modal-input" /></Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Total bill (₹)"><input type="number" required value={splitTotal} onChange={e => setSplitTotal(e.target.value)} placeholder="2500" className="modal-input" /></Field>
              <Field label="Friend's name"><input type="text" required value={splitFriend} onChange={e => setSplitFriend(e.target.value)} placeholder="Rahul" className="modal-input" /></Field>
            </div>
            <Field label="Amount they owe (₹)"><input type="number" required value={splitOwed} onChange={e => setSplitOwed(e.target.value)} placeholder="1250" className="modal-input" /></Field>
            <SubmitButton>Record split</SubmitButton>
          </form>
        </Modal>
      )}

      {showGoalModal && (
        <Modal onClose={() => setShowGoalModal(false)} title={goalModalMode === "add" ? "Create savings goal" : "Edit savings goal"} desc="Define savings targets and track milestone progress">
          <form onSubmit={handleGoalSubmit} className="space-y-4">
            <Field label="Goal name"><input type="text" required value={goalName} onChange={(e) => setGoalName(e.target.value)} placeholder="e.g. New MacBook Pro" className="modal-input" /></Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Target amount (₹)"><input type="number" required value={goalTargetAmount} onChange={(e) => setGoalTargetAmount(e.target.value)} placeholder="150000" className="modal-input" /></Field>
              <Field label="Current saved (₹)"><input type="number" value={goalCurrentAmount} onChange={(e) => setGoalCurrentAmount(e.target.value)} placeholder="15000" className="modal-input" /></Field>
            </div>
            <Field label="Target date"><input type="date" required value={goalTargetDate} onChange={(e) => setGoalTargetDate(e.target.value)} className="modal-input" /></Field>
            <SubmitButton>{goalModalMode === "add" ? "Create goal" : "Save changes"}</SubmitButton>
          </form>
        </Modal>
      )}

      {showSubModal && (
        <Modal onClose={() => setShowSubModal(false)} title={subModalMode === "add" ? "Register subscription" : "Edit subscription"} desc="Track monthly or yearly recurring bills">
          <form onSubmit={handleSubSubmit} className="space-y-4">
            <Field label="Subscription name"><input type="text" required value={subName} onChange={(e) => setSubName(e.target.value)} placeholder="e.g. Netflix Premium" className="modal-input" /></Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Amount (₹)"><input type="number" required value={subAmount} onChange={(e) => setSubAmount(e.target.value)} placeholder="649.00" className="modal-input" /></Field>
              <Field label="Category">
                <select value={subCategory} onChange={(e) => setSubCategory(e.target.value)} className="modal-input cursor-pointer">
                  {categories.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
                </select>
              </Field>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Billing cycle">
                <select value={subBillingCycle} onChange={(e) => setSubBillingCycle(e.target.value)} className="modal-input cursor-pointer">
                  <option value="Monthly">Monthly</option>
                  <option value="Yearly">Yearly</option>
                </select>
              </Field>
              <Field label="Next due date"><input type="date" required value={subNextDueDate} onChange={(e) => setSubNextDueDate(e.target.value)} className="modal-input" /></Field>
            </div>
            <SubmitButton>{subModalMode === "add" ? "Track subscription" : "Save changes"}</SubmitButton>
          </form>
        </Modal>
      )}

      {showTxModal && (
        <Modal onClose={() => setShowTxModal(false)} title={txModalMode === "add" ? "Add transaction" : "Edit transaction"} desc="Keep track of your income and day-to-day spending">
          <form onSubmit={handleTxSubmit} className="space-y-4">
            <Field label="Description"><input type="text" required value={txDescription} onChange={(e) => setTxDescription(e.target.value)} placeholder="e.g. Swiggy order" className="modal-input" /></Field>
            <div className="grid grid-cols-3 gap-4">
              <Field label="Currency">
                <select value={txCurrency} onChange={(e) => setTxCurrency(e.target.value)} className="modal-input cursor-pointer">
                  {supportedCurrencies.map(c => <option key={c.code} value={c.code}>{c.code} ({c.symbol})</option>)}
                </select>
              </Field>
              <Field label={`Amount (${supportedCurrencies.find(c => c.code === txCurrency)?.symbol || "₹"})`}>
                <input type="number" step="0.01" required value={txAmount} onChange={(e) => setTxAmount(e.target.value)} placeholder="250.00" className="modal-input" />
              </Field>
              <Field label="Date"><input type="date" required value={txDate} onChange={(e) => setTxDate(e.target.value)} className="modal-input" /></Field>
            </div>
            {txCurrency !== "INR" && (
              <p className="text-[11px] text-stone-450 dark:text-stone-500 -mt-2">Converted to ₹ automatically when saved.</p>
            )}
            <div className="grid grid-cols-2 gap-4">
              <Field label="Category">
                <select value={txCategory} onChange={(e) => setTxCategory(e.target.value)} className="modal-input cursor-pointer">
                  {categories.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
                </select>
              </Field>
              <Field label="Type">
                <select value={txType} onChange={(e) => setTxType(e.target.value)} className="modal-input cursor-pointer">
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </Field>
            </div>
            <Field label="Account (optional)">
              <select value={txAccountId} onChange={(e) => setTxAccountId(e.target.value)} className="modal-input cursor-pointer">
                <option value="">No account linked</option>
                {accounts.map((a: any) => (
                  <option key={a.id} value={a.id}>{a.name} ({a.account_type})</option>
                ))}
              </select>
            </Field>
            <SubmitButton>{txModalMode === "add" ? "Create record" : "Save changes"}</SubmitButton>
          </form>
        </Modal>
      )}

      {showAuthModal && (
        <Modal onClose={() => setShowAuthModal(false)} title={authMode === "login" ? "Welcome back" : "Create account"} desc={authMode === "login" ? "Sign in to access your financial dashboard" : "Sign up to track and plan your budget"}>
          {authError && (
            <div className="bg-coral-50 dark:bg-coral-950/20 border border-coral-100 dark:border-coral-900 text-coral-700 dark:text-coral-400 text-xs font-semibold p-3 rounded-lg mb-4">{authError}</div>
          )}
          <form onSubmit={handleAuthSubmit} className="space-y-4">
            {authMode === "signup" && (
              <Field label="Full name"><input type="text" required value={authName} onChange={(e) => setAuthName(e.target.value)} placeholder="Enter your name" className="modal-input" /></Field>
            )}
            <Field label="Email address"><input type="email" required value={authEmail} onChange={(e) => setAuthEmail(e.target.value)} placeholder="name@example.com" className="modal-input" /></Field>
            <Field label="Password"><input type="password" required value={authPassword} onChange={(e) => setAuthPassword(e.target.value)} placeholder="••••••••" className="modal-input" /></Field>
            <button type="submit" disabled={isLoadingAuth} className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 disabled:from-teal-400 disabled:to-teal-400 text-white font-bold py-3 rounded-lg transition-all duration-300 transform hover:-translate-y-0.5 shadow-[0_0_15px_rgba(15,110,86,0.3)] hover:shadow-[0_0_20px_rgba(20,184,166,0.5)] text-sm mt-2 flex items-center justify-center cursor-pointer border-none">
              {isLoadingAuth ? <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span> : authMode === "login" ? "Sign in" : "Register account"}
            </button>
          </form>
          <div className="text-center mt-6">
            <button onClick={() => { setAuthMode(authMode === "login" ? "signup" : "login"); setAuthError(""); }} className="text-xs text-teal-700 dark:text-teal-400 hover:text-teal-800 font-bold transition-all cursor-pointer bg-transparent border-none">
              {authMode === "login" ? "Don't have an account? Sign up" : "Already have an account? Log in"}
            </button>
          </div>
        </Modal>
      )}

      {showReminderModal && (
        <Modal onClose={() => setShowReminderModal(false)} title="Add bill reminder" desc="Get notified before your bills are due">
          <form onSubmit={handleReminderSubmit} className="space-y-4">
            <Field label="Bill / reminder name"><input type="text" required value={reminderName} onChange={e => setReminderName(e.target.value)} placeholder="e.g. Broadband bill" className="modal-input" /></Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Amount (₹)"><input type="number" required value={reminderAmount} onChange={e => setReminderAmount(e.target.value)} placeholder="999" className="modal-input" /></Field>
              <Field label="Category">
                <select value={reminderCategory} onChange={e => setReminderCategory(e.target.value)} className="modal-input cursor-pointer">
                  {categories.map(c => <option key={c.id} value={c.name}>{c.name}</option>)}
                </select>
              </Field>
            </div>
            <Field label="Due date"><input type="date" required value={reminderDueDate} onChange={e => setReminderDueDate(e.target.value)} className="modal-input" /></Field>
            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="reminder-recurring"
                checked={reminderIsRecurring}
                onChange={e => setReminderIsRecurring(e.target.checked)}
                className="w-4 h-4 accent-teal-700 cursor-pointer"
              />
              <label htmlFor="reminder-recurring" className="text-sm text-stone-700 dark:text-stone-300 cursor-pointer">
                Repeats — auto-create the next reminder when this one is paid
              </label>
            </div>
            {reminderIsRecurring && (
              <Field label="Repeat frequency">
                <select value={reminderFrequency} onChange={e => setReminderFrequency(e.target.value)} className="modal-input cursor-pointer">
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              </Field>
            )}
            <SubmitButton>Create reminder</SubmitButton>
          </form>
        </Modal>
      )}

      {/* ============================== FLOATING AI COPILOT ============================== */}
      {userEmail && (
        <div className="fixed bottom-6 right-6 z-40">
          {/* Chat Panel */}
          {chatOpen && (
            <div className="absolute bottom-20 right-0 w-80 md:w-[420px] h-[520px] bg-white dark:bg-stone-900/95 backdrop-blur-xl border border-stone-200 dark:border-stone-700/60 rounded-2xl shadow-2xl flex flex-col overflow-hidden" style={{boxShadow:"0 25px 60px rgba(0,0,0,0.25), 0 0 30px rgba(15,110,86,0.15)"}}>
              {/* Header */}
              <div className="bg-gradient-to-r from-teal-700 to-teal-600 p-4 text-white flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center text-sm font-bold shrink-0">🤖</div>
                <div className="flex-1 min-w-0">
                  <p className="font-serif font-bold text-sm leading-tight">Finance AI Copilot</p>
                  <p className="text-[10px] text-white/70">Powered by Gemini · Your financial data is context</p>
                </div>
                <button onClick={() => setChatOpen(false)} className="text-white/70 hover:text-white cursor-pointer bg-transparent border-none shrink-0">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>
                </button>
              </div>

              {/* Quick Ask Chips — shown only when chat is empty */}
              {chatMessages.length === 0 && (
                <div className="p-3 border-b border-stone-100 dark:border-stone-800 bg-stone-50/60 dark:bg-stone-950/30">
                  <p className="text-[10px] font-bold text-stone-400 uppercase tracking-wider mb-2">Quick ask</p>
                  <div className="flex flex-wrap gap-1.5">
                    {[
                      "How's my spending this month?",
                      "Am I on budget?",
                      "What's my biggest expense?",
                      "How's my savings rate?",
                      "Any budget alerts?",
                    ].map(chip => (
                      <button
                        key={chip}
                        onClick={() => { setChatInput(chip); }}
                        className="text-[10px] font-semibold bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-300 border border-teal-200 dark:border-teal-800 rounded-full px-2.5 py-1 hover:bg-teal-100 dark:hover:bg-teal-900/60 transition-all cursor-pointer"
                      >
                        {chip}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Messages */}
              <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-stone-50/40 dark:bg-stone-950/20 text-xs">
                {chatMessages.length === 0 && (
                  <div className="flex flex-col items-center justify-center h-full text-center gap-2 opacity-60">
                    <span className="text-3xl">💬</span>
                    <p className="text-xs text-stone-500 dark:text-stone-400 font-medium">Ask me anything about<br/>your finances!</p>
                  </div>
                )}
                {chatMessages.map((msg, index) => (
                  <div key={index} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                    {msg.sender !== "user" && (
                      <div className="w-6 h-6 rounded-full bg-teal-100 dark:bg-teal-950/60 text-teal-700 dark:text-teal-300 flex items-center justify-center text-[10px] shrink-0 mr-2 mt-0.5">🤖</div>
                    )}
                    <div className={`max-w-[82%] rounded-2xl p-3 ${msg.sender === "user"
                      ? "bg-gradient-to-br from-teal-600 to-teal-700 text-white rounded-tr-none shadow-md"
                      : "bg-white dark:bg-stone-800/80 border border-stone-100 dark:border-stone-700/50 text-stone-800 dark:text-stone-200 rounded-tl-none shadow-sm"
                    }`}>
                      <p className="leading-relaxed whitespace-pre-line" dangerouslySetInnerHTML={{
                        __html: msg.text
                          .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                          .replace(/\n•/g, '<br/>•')
                          .replace(/\n-/g, '<br/>-')
                      }} />
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="w-6 h-6 rounded-full bg-teal-100 dark:bg-teal-950/60 text-teal-700 dark:text-teal-300 flex items-center justify-center text-[10px] shrink-0 mr-2">🤖</div>
                    <div className="bg-white dark:bg-stone-800 border border-stone-100 dark:border-stone-700 rounded-2xl rounded-tl-none p-3 flex items-center gap-1.5">
                      <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-bounce"></span>
                      <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-bounce" style={{animationDelay:"0.15s"}}></span>
                      <span className="w-1.5 h-1.5 bg-teal-500 rounded-full animate-bounce" style={{animationDelay:"0.3s"}}></span>
                    </div>
                  </div>
                )}
              </div>

              {/* Input */}
              <form onSubmit={sendChatMessage} className="p-3 border-t border-stone-150 dark:border-stone-800 bg-white dark:bg-stone-900 flex gap-2">
                <input
                  type="text"
                  required
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask the AI Copilot…"
                  className="flex-1 bg-stone-50 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-xl px-3 py-2.5 text-xs focus:outline-none focus:border-teal-500 text-stone-800 dark:text-stone-100 placeholder:text-stone-400"
                />
                <button
                  type="submit"
                  disabled={chatLoading}
                  className="bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 disabled:from-teal-400 disabled:to-teal-400 text-white px-4 rounded-xl cursor-pointer border-none transition-all duration-200 font-bold text-sm shadow-[0_0_10px_rgba(15,110,86,0.3)]"
                >
                  ↑
                </button>
              </form>
            </div>
          )}

          {/* Toggle Button */}
          <button
            onClick={() => setChatOpen(!chatOpen)}
            title="AI Financial Copilot"
            className={`relative bg-gradient-to-br from-teal-600 to-teal-700 hover:from-teal-500 hover:to-teal-600 text-white p-4 rounded-full shadow-[0_0_20px_rgba(15,110,86,0.5)] hover:shadow-[0_0_30px_rgba(20,184,166,0.6)] transition-all duration-300 ${chatOpen ? "rotate-0 scale-95" : "hover:scale-105"} flex items-center justify-center cursor-pointer border-none`}
          >
            {chatOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>
            ) : (
              <>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
                </svg>
                {/* Pulse ring */}
                <span className="absolute inset-0 rounded-full animate-ping bg-teal-500 opacity-20"></span>
              </>
            )}
          </button>
        </div>
      )}


      {/* ============================== TOASTS ============================== */}
      {toasts.length > 0 && (
        <div className="fixed bottom-6 left-6 z-[60] flex flex-col gap-2 max-w-xs">
          {toasts.map(t => (
            <div
              key={t.id}
              className={`rounded-lg shadow-lg px-4 py-3 text-sm font-semibold text-white flex items-start gap-2 ${
                t.type === "success" ? "bg-teal-700" : t.type === "error" ? "bg-coral-600" : "bg-stone-800"
              }`}
            >
              <span className="flex-1">{t.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* ============================== CONFIRM DIALOG ============================== */}
      {confirmState && (
        <div className="fixed inset-0 z-[70] flex items-center justify-center bg-stone-900/55 backdrop-blur-sm p-4">
          <div className="bg-white dark:bg-stone-900 rounded-2xl shadow-xl border border-stone-150 dark:border-stone-800 max-w-sm w-full p-6">
            <p className="text-sm font-semibold text-stone-800 dark:text-stone-100 mb-6">{confirmState.message}</p>
            <div className="flex gap-3">
              <button
                onClick={() => respondConfirm(false)}
                className="flex-1 bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 dark:hover:bg-stone-750 text-stone-600 dark:text-stone-300 text-sm font-bold py-2.5 rounded-lg transition-all cursor-pointer border-none"
              >
                Cancel
              </button>
              <button
                onClick={() => respondConfirm(true)}
                className="flex-1 bg-coral-600 hover:bg-coral-700 text-white text-sm font-bold py-2.5 rounded-lg transition-all cursor-pointer border-none"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}

      <style>{`
        .modal-input {
          width: 100%;
          background: #FAFAF7;
          border: 1px solid #E7E2D6;
          border-radius: 0.65rem;
          padding: 0.65rem 1rem;
          font-size: 0.875rem;
          color: #1c1917;
        }
        .dark .modal-input { background: #1c1917; border-color: #3f3a32; color: #f5f5f4; }
        .modal-input:focus { outline: none; border-color: #0F6E56; }
      `}</style>
    </div>
  );
};

/* ============================================================================
   Shared modal helpers
   ========================================================================= */

function Modal({ title, desc, onClose, children }: { title: string; desc?: string; onClose: () => void; children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-stone-900/55 backdrop-blur-sm p-4">
      <div className="bg-white dark:bg-stone-900 rounded-2xl shadow-xl border border-stone-150 dark:border-stone-800 max-w-md w-full p-7 relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-stone-400 hover:text-stone-650 dark:hover:text-stone-350 hover:bg-stone-100 dark:hover:bg-stone-850 p-1.5 rounded-md cursor-pointer bg-transparent border-none">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-5 h-5">
            <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
          </svg>
        </button>
        <div className="mb-6">
          <h3 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">{title}</h3>
          {desc && <p className="text-xs text-stone-550 dark:text-stone-450 mt-1">{desc}</p>}
        </div>
        {children}
      </div>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label className="block text-[11px] font-bold text-stone-500 dark:text-stone-400 uppercase tracking-wider mb-1.5">{label}</label>
      {children}
    </div>
  );
}

function SubmitButton({ children }: { children: React.ReactNode }) {
  return (
    <button type="submit" className="w-full bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 text-white font-bold py-3 rounded-lg transition-all duration-300 transform hover:-translate-y-0.5 shadow-[0_0_15px_rgba(15,110,86,0.3)] hover:shadow-[0_0_20px_rgba(20,184,166,0.5)] text-sm mt-2 cursor-pointer border-none">
      {children}
    </button>
  );
}

export default Layout;
