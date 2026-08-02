import React, { useState, useEffect } from "react";
import { useFinance } from "../context/FinanceContext";
import { API_URL } from "../config";

const API = API_URL;

// ─── Icons ────────────────────────────────────────────────────────────────────
const Icon = {
  user: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 6a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0ZM4.501 20.118a7.5 7.5 0 0 1 14.998 0A17.933 17.933 0 0 1 12 21.75c-2.676 0-5.216-.584-7.499-1.632Z" />
    </svg>
  ),
  palette: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M4.098 19.902a3.75 3.75 0 0 0 5.304 0l6.401-6.402M6.75 21A3.75 3.75 0 0 1 3 17.25V4.125C3 3.504 3.504 3 4.125 3h5.25c.621 0 1.125.504 1.125 1.125v4.072M6.75 21a3.75 3.75 0 0 0 3.75-3.75V8.197M6.75 21h13.125c.621 0 1.125-.504 1.125-1.125v-5.25c0-.621-.504-1.125-1.125-1.125h-4.072M10.5 8.197l2.88-2.88c.438-.439 1.15-.439 1.59 0l3.712 3.713c.44.44.44 1.152 0 1.59l-2.879 2.88M6.75 17.25h.008v.008H6.75v-.008Z" />
    </svg>
  ),
  tag: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.568 3H5.25A2.25 2.25 0 0 0 3 5.25v4.318c0 .597.237 1.17.659 1.591l9.581 9.581c.699.699 1.78.872 2.607.33a18.095 18.095 0 0 0 5.223-5.223c.542-.827.369-1.908-.33-2.607L11.16 3.66A2.25 2.25 0 0 0 9.568 3Z" />
    </svg>
  ),
  lock: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
    </svg>
  ),
  cloud: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 16.5V9.75m0 0 3 3m-3-3-3 3M6.75 19.5a4.5 4.5 0 0 1-1.41-8.775 5.25 5.25 0 0 1 10.233-2.33 3 3 0 0 1 3.758 3.848A3.752 3.752 0 0 1 18 19.5H6.75Z" />
    </svg>
  ),
  danger: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z" />
    </svg>
  ),
  logout: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 9V5.25A2.25 2.25 0 0 1 10.5 3h6a2.25 2.25 0 0 1 2.25 2.25v13.5A2.25 2.25 0 0 1 16.5 21h-6a2.25 2.25 0 0 1-2.25-2.25V15m-3 0-3-3m0 0 3-3m-3 3H15" />
    </svg>
  ),
  check: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-3.5 h-3.5">
      <path strokeLinecap="round" strokeLinejoin="round" d="m4.5 12.75 6 6 9-13.5" />
    </svg>
  ),
  edit: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-3.5 h-3.5">
      <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.128-1.897L16.863 4.487Zm0 0L19.5 7.125" />
    </svg>
  ),
  trash: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-3.5 h-3.5">
      <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.34 9m-4.72 0-.34-9m9.03-3.03a17.902 17.902 0 0 1-1.07 3.5M18.13 6a22.09 22.09 0 0 0-1.85-.3M14.74 9a22.38 22.38 0 0 0-5.48 0M10.5 6.857V5.07c0-.704.57-1.286 1.27-1.286h2.46c.7 0 1.27.582 1.27 1.286v1.787M3.75 6a17.925 17.925 0 0 1 1.07-3.5M6.37 6a22.09 22.09 0 0 1 1.85-.3M6.37 6a22.38 22.38 0 0 1 5.48 0" />
    </svg>
  ),
  spinner: <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin inline-block" />,
  moon: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.72 9.72 0 0 1 18 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 0 0 3 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 0 0 9.002-5.998Z" />
    </svg>
  ),
  sun: (
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
      <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386-1.591 1.591M21 12h-2.25m-.386 6.364-1.591-1.591M12 18.75V21m-4.773-4.227-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 1 1-7.5 0 3.75 3.75 0 0 1 7.5 0Z" />
    </svg>
  ),
};

// ─── Section Card ─────────────────────────────────────────────────────────────
const SectionCard: React.FC<{
  title: string;
  icon?: React.ReactNode;
  children: React.ReactNode;
  danger?: boolean;
}> = ({ title, icon, children, danger }) => (
  <div className={`bg-white dark:bg-stone-900 border rounded-xl shadow-sm p-6 ${danger ? "border-red-200 dark:border-red-900/50" : "border-stone-150 dark:border-stone-800"}`}>
    <div className="flex items-center gap-2 mb-5">
      {icon && (
        <span className={`${danger ? "text-red-500 dark:text-red-400" : "text-teal-700 dark:text-teal-400"}`}>
          {icon}
        </span>
      )}
      <h3 className={`text-base font-serif font-bold ${danger ? "text-red-600 dark:text-red-400" : "text-stone-850 dark:text-stone-100"}`}>
        {title}
      </h3>
    </div>
    {children}
  </div>
);

// ─── Row ──────────────────────────────────────────────────────────────────────
const Row: React.FC<{ label: string; sub?: string; children: React.ReactNode }> = ({ label, sub, children }) => (
  <div className="flex items-center justify-between gap-4 py-3 border-b border-stone-100 dark:border-stone-800/60 last:border-0">
    <div>
      <p className="text-sm font-semibold text-stone-700 dark:text-stone-300">{label}</p>
      {sub && <p className="text-xs text-stone-450 dark:text-stone-500 mt-0.5">{sub}</p>}
    </div>
    <div className="shrink-0">{children}</div>
  </div>
);

// ─── Pill Button ──────────────────────────────────────────────────────────────
const PillBtn: React.FC<React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "primary" | "secondary" | "danger" }> = ({
  variant = "secondary", className = "", children, ...rest
}) => {
  const base = "text-xs font-bold py-1.5 px-3.5 rounded-lg transition-all cursor-pointer border-none whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed";
  const styles = {
    primary:   "bg-teal-700 hover:bg-teal-800 text-white",
    secondary: "bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 dark:hover:bg-stone-750 text-stone-600 dark:text-stone-300",
    danger:    "bg-red-600 hover:bg-red-700 text-white",
  };
  return <button className={`${base} ${styles[variant]} ${className}`} {...rest}>{children}</button>;
};

// ─── Settings Page ────────────────────────────────────────────────────────────
const Settings: React.FC = () => {
  const {
    userEmail, theme, setTheme, handleLogout, showToast, confirmAction,
    categories, handleCategoryCreate, handleCategoryUpdate, handleCategoryDelete,
    accounts, transactions,
  } = useFinance();

  const token = () => localStorage.getItem("token");

  // ── Profile ──
  const [displayName, setDisplayName] = useState("");
  const [editingName, setEditingName] = useState(false);
  const [savingName, setSavingName] = useState(false);

  // ── Password ──
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [savingPassword, setSavingPassword] = useState(false);
  const [showPasswords, setShowPasswords] = useState(false);

  // ── Categories ──
  const [newCategoryName, setNewCategoryName] = useState("");
  const [newCategoryColor, setNewCategoryColor] = useState("#0F6E56");
  const [addingCategory, setAddingCategory] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editName, setEditName] = useState("");
  const [editColor, setEditColor] = useState("#0F6E56");

  // ── Backup ──
  const [exportingBackup, setExportingBackup] = useState(false);
  const [importingBackup, setImportingBackup] = useState(false);

  // ── Account deletion ──
  const [deleting, setDeleting] = useState(false);

  // ── Preferences ──
  const [defaultCurrency, setDefaultCurrency] = useState(() => localStorage.getItem("defaultCurrency") || "INR");

  const CURRENCIES = [
    { code: "INR", label: "₹ Indian Rupee" },
    { code: "USD", label: "$ US Dollar" },
    { code: "EUR", label: "€ Euro" },
    { code: "GBP", label: "£ British Pound" },
    { code: "JPY", label: "¥ Japanese Yen" },
    { code: "AED", label: "د.إ UAE Dirham" },
    { code: "SGD", label: "S$ Singapore Dollar" },
    { code: "CAD", label: "C$ Canadian Dollar" },
    { code: "AUD", label: "A$ Australian Dollar" },
  ];

  // Load profile name on mount
  useEffect(() => {
    const t = token();
    if (!t) return;
    fetch(`${API}/profile`, { headers: { Authorization: `Bearer ${t}` } })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d?.name) setDisplayName(d.name); });
  }, [userEmail]);

  // ── Handlers ──
  const handleSaveName = async () => {
    if (!displayName.trim()) return;
    setSavingName(true);
    try {
      const res = await fetch(`${API}/profile/name`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token()}` },
        body: JSON.stringify({ name: displayName.trim() }),
      });
      if (res.ok) {
        showToast("Display name updated.", "success");
        setEditingName(false);
      } else {
        showToast("Failed to update name.", "error");
      }
    } catch {
      showToast("Couldn't reach the backend.", "error");
    } finally {
      setSavingName(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!currentPassword || !newPassword) return;
    if (newPassword !== confirmPassword) { showToast("Passwords don't match.", "error"); return; }
    if (newPassword.length < 6) { showToast("New password must be at least 6 characters.", "error"); return; }
    setSavingPassword(true);
    try {
      const res = await fetch(`${API}/profile/password`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token()}` },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
      });
      if (res.ok) {
        showToast("Password updated successfully.", "success");
        setCurrentPassword(""); setNewPassword(""); setConfirmPassword("");
      } else {
        const d = await res.json().catch(() => ({}));
        showToast(d.detail || "Failed to update password.", "error");
      }
    } catch { showToast("Couldn't reach the backend.", "error"); }
    finally { setSavingPassword(false); }
  };

  const handleAddCategory = async () => {
    if (!newCategoryName.trim()) return;
    setAddingCategory(true);
    const ok = await handleCategoryCreate(newCategoryName.trim(), newCategoryColor);
    if (ok) { setNewCategoryName(""); setNewCategoryColor("#0F6E56"); }
    setAddingCategory(false);
  };

  const saveEdit = async () => {
    if (editingId === null) return;
    await handleCategoryUpdate(editingId, editName, editColor);
    setEditingId(null);
  };

  const handleExportBackup = async () => {
    setExportingBackup(true);
    try {
      const res = await fetch(`${API}/backup/export`, { headers: { Authorization: `Bearer ${token()}` } });
      if (!res.ok) { showToast("Failed to export backup.", "error"); return; }
      const data = await res.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `finance-backup-${new Date().toISOString().split("T")[0]}.json`;
      document.body.appendChild(a); a.click(); a.remove();
      window.URL.revokeObjectURL(url);
      showToast("Backup downloaded.", "success");
    } catch { showToast("Couldn't reach the backend.", "error"); }
    finally { setExportingBackup(false); }
  };

  const handleImportBackup = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const ok = await confirmAction("Restore from backup? ALL current data will be permanently replaced.");
    if (!ok) { e.target.value = ""; return; }
    setImportingBackup(true);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${API}/backup/import`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token()}` },
        body: formData,
      });
      if (res.ok) {
        showToast("Backup restored! Reloading…", "success");
        setTimeout(() => window.location.reload(), 1500);
      } else {
        const d = await res.json().catch(() => ({}));
        showToast(d.detail || "Failed to restore backup.", "error");
      }
    } catch { showToast("Couldn't reach the backend.", "error"); }
    finally { setImportingBackup(false); e.target.value = ""; }
  };

  const handleDefaultCurrencyChange = (code: string) => {
    setDefaultCurrency(code);
    localStorage.setItem("defaultCurrency", code);
    showToast(`Default currency set to ${code}.`, "success");
  };

  const handleDeleteAccount = async () => {
    const ok = await confirmAction("Delete your account permanently? This action cannot be undone.");
    if (!ok) return;
    setDeleting(true);
    try {
      const res = await fetch(`${API}/profile`, { method: "DELETE", headers: { Authorization: `Bearer ${token()}` } });
      if (res.ok) { showToast("Account deleted.", "info"); handleLogout(); }
      else showToast("Failed to delete account.", "error");
    } catch { showToast("Couldn't reach the backend.", "error"); }
    finally { setDeleting(false); }
  };

  // ── Stats ──
  const expenseCount = transactions.filter(t => t.transaction_type === "expense").length;
  const incomeCount  = transactions.filter(t => t.transaction_type === "income").length;

  return (
    <div className="space-y-5 max-w-2xl">
      {/* Page header */}
      <div className="bg-white dark:bg-stone-900 border border-stone-150 dark:border-stone-800 p-6 rounded-xl shadow-sm">
        <h2 className="text-xl font-serif font-bold text-stone-850 dark:text-stone-100">Settings</h2>
        <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-1">Manage your account, preferences, and data.</p>
      </div>

      {/* ── Profile ── */}
      <SectionCard title="Profile" icon={Icon.user}>
        <Row label="Email" sub="Your login email cannot be changed.">
          <span className="text-sm font-mono text-stone-500 dark:text-stone-400">{userEmail}</span>
        </Row>

        <Row label="Display name" sub="Shown on reports and the AI coach.">
          {editingName ? (
            <div className="flex items-center gap-2">
              <input
                type="text"
                value={displayName}
                onChange={e => setDisplayName(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") handleSaveName(); if (e.key === "Escape") setEditingName(false); }}
                autoFocus
                className="modal-input py-1 text-sm w-40"
              />
              <PillBtn variant="primary" onClick={handleSaveName} disabled={savingName}>
                {savingName ? Icon.spinner : "Save"}
              </PillBtn>
              <PillBtn onClick={() => setEditingName(false)}>Cancel</PillBtn>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <span className="text-sm font-semibold text-stone-700 dark:text-stone-300">{displayName || "—"}</span>
              <button
                onClick={() => setEditingName(true)}
                className="text-stone-400 hover:text-teal-700 dark:hover:text-teal-400 bg-transparent border-none cursor-pointer p-1"
                title="Edit name"
              >
                {Icon.edit}
              </button>
            </div>
          )}
        </Row>

        <Row label="Account stats" sub="Your usage at a glance.">
          <div className="flex gap-3 text-xs font-bold text-stone-500 dark:text-stone-400">
            <span className="text-teal-700 dark:text-teal-400">{incomeCount} income</span>
            <span>·</span>
            <span>{expenseCount} expense</span>
            <span>·</span>
            <span>{accounts.length} account{accounts.length !== 1 ? "s" : ""}</span>
          </div>
        </Row>

        <div className="pt-2 flex justify-end">
          <button
            onClick={handleLogout}
            className="flex items-center gap-1.5 text-xs font-bold text-stone-400 hover:text-red-500 dark:hover:text-red-400 transition-colors bg-transparent border-none cursor-pointer"
          >
            {Icon.logout}
            Sign out
          </button>
        </div>
      </SectionCard>

      {/* ── Preferences ── */}
      <SectionCard title="Preferences" icon={Icon.palette}>
        <Row label="Appearance" sub={`Currently using ${theme} mode.`}>
          <button
            onClick={() => setTheme(theme === "light" ? "dark" : "light")}
            className="flex items-center gap-2 bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 dark:hover:bg-stone-750 text-stone-600 dark:text-stone-300 text-xs font-bold py-1.5 px-3.5 rounded-lg transition-all cursor-pointer border-none"
          >
            {theme === "light" ? Icon.moon : Icon.sun}
            {theme === "light" ? "Dark mode" : "Light mode"}
          </button>
        </Row>

        <Row label="Default currency" sub="Used when adding new transactions.">
          <select
            id="default-currency-select"
            value={defaultCurrency}
            onChange={e => handleDefaultCurrencyChange(e.target.value)}
            className="modal-input py-1.5 text-sm w-44"
          >
            {CURRENCIES.map(c => (
              <option key={c.code} value={c.code}>{c.label}</option>
            ))}
          </select>
        </Row>
      </SectionCard>

      {/* ── Categories ── */}
      <SectionCard title="Categories" icon={Icon.tag}>
        <p className="text-xs text-stone-450 dark:text-stone-500 -mt-2 mb-4">
          Used across transactions, budgets, subscriptions, and reminders. Deleting a category won't affect existing records.
        </p>

        <div className="space-y-2 mb-4">
          {categories.map(cat => (
            <div key={cat.id} className="flex items-center gap-3 p-2.5 rounded-lg border border-stone-100 dark:border-stone-800 group">
              {editingId === cat.id ? (
                <>
                  <input type="color" value={editColor} onChange={e => setEditColor(e.target.value)}
                    className="w-7 h-7 rounded cursor-pointer border border-stone-200 dark:border-stone-700 bg-transparent p-0 shrink-0" />
                  <input type="text" value={editName} onChange={e => setEditName(e.target.value)}
                    onKeyDown={e => { if (e.key === "Enter") saveEdit(); if (e.key === "Escape") setEditingId(null); }}
                    autoFocus className="modal-input flex-1 py-1 text-sm" />
                  <PillBtn variant="primary" onClick={saveEdit}>Save</PillBtn>
                  <PillBtn onClick={() => setEditingId(null)}>Cancel</PillBtn>
                </>
              ) : (
                <>
                  <span className="w-3 h-3 rounded-full shrink-0" style={{ backgroundColor: cat.color }} />
                  <span className="flex-1 text-sm font-semibold text-stone-700 dark:text-stone-300">{cat.name}</span>
                  <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button onClick={() => { setEditingId(cat.id); setEditName(cat.name); setEditColor(cat.color); }}
                      className="text-stone-400 hover:text-teal-700 bg-transparent border-none cursor-pointer p-1">{Icon.edit}</button>
                    <button onClick={() => handleCategoryDelete(cat.id)}
                      className="text-stone-400 hover:text-red-500 bg-transparent border-none cursor-pointer p-1">{Icon.trash}</button>
                  </div>
                </>
              )}
            </div>
          ))}
          {categories.length === 0 && (
            <p className="text-xs text-stone-400 dark:text-stone-500 text-center py-4">No categories yet. Add one below.</p>
          )}
        </div>

        <div className="flex items-center gap-2 pt-4 border-t border-stone-100 dark:border-stone-800">
          <input type="color" value={newCategoryColor} onChange={e => setNewCategoryColor(e.target.value)}
            className="w-8 h-8 rounded cursor-pointer border border-stone-200 dark:border-stone-700 bg-transparent p-0 shrink-0" />
          <input
            type="text"
            placeholder="New category name…"
            value={newCategoryName}
            onChange={e => setNewCategoryName(e.target.value)}
            onKeyDown={e => { if (e.key === "Enter") handleAddCategory(); }}
            className="modal-input flex-1 py-1.5 text-sm"
          />
          <PillBtn variant="primary" onClick={handleAddCategory} disabled={addingCategory || !newCategoryName.trim()}>
            {addingCategory ? Icon.spinner : "Add"}
          </PillBtn>
        </div>
      </SectionCard>

      {/* ── Security ── */}
      <SectionCard title="Security" icon={Icon.lock}>
        <p className="text-xs text-stone-450 dark:text-stone-500 -mt-2 mb-4">
          Change your password. You'll need to re-enter your current password to confirm.
        </p>

        <form onSubmit={handleChangePassword} className="space-y-3">
          {(["Current password", "New password", "Confirm new password"] as const).map((label, i) => {
            const values = [currentPassword, newPassword, confirmPassword];
            const setters = [setCurrentPassword, setNewPassword, setConfirmPassword];
            return (
              <div key={label} className="relative">
                <input
                  id={`password-field-${i}`}
                  type={showPasswords ? "text" : "password"}
                  required
                  placeholder={label}
                  value={values[i]}
                  onChange={e => setters[i](e.target.value)}
                  className="modal-input pr-10"
                />
              </div>
            );
          })}

          <div className="flex items-center gap-2 pt-1">
            <input type="checkbox" id="show-passwords" checked={showPasswords} onChange={e => setShowPasswords(e.target.checked)}
              className="w-3.5 h-3.5 accent-teal-700 cursor-pointer" />
            <label htmlFor="show-passwords" className="text-xs text-stone-500 dark:text-stone-400 cursor-pointer select-none">Show passwords</label>
          </div>

          <PillBtn
            variant="primary"
            type="submit"
            disabled={savingPassword || !currentPassword || !newPassword || !confirmPassword}
            className="text-sm py-2.5 px-5"
          >
            {savingPassword ? <>{Icon.spinner} Saving…</> : "Update password"}
          </PillBtn>
        </form>
      </SectionCard>

      {/* ── Data & Backup ── */}
      <SectionCard title="Data & backup" icon={Icon.cloud}>
        <p className="text-xs text-stone-450 dark:text-stone-500 -mt-2 mb-5">
          Download your entire financial history — transactions, accounts, budgets, goals, and more — as a single JSON file. You can restore from any previous backup at any time.
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
          <div className="p-3 rounded-lg bg-stone-50 dark:bg-stone-850 border border-stone-100 dark:border-stone-800 text-center">
            <p className="text-lg font-bold font-mono text-teal-700 dark:text-teal-400">{transactions.length}</p>
            <p className="text-xs text-stone-450 dark:text-stone-500 mt-0.5">Transactions</p>
          </div>
          <div className="p-3 rounded-lg bg-stone-50 dark:bg-stone-850 border border-stone-100 dark:border-stone-800 text-center">
            <p className="text-lg font-bold font-mono text-teal-700 dark:text-teal-400">{accounts.length}</p>
            <p className="text-xs text-stone-450 dark:text-stone-500 mt-0.5">Accounts</p>
          </div>
          <div className="p-3 rounded-lg bg-stone-50 dark:bg-stone-850 border border-stone-100 dark:border-stone-800 text-center">
            <p className="text-lg font-bold font-mono text-teal-700 dark:text-teal-400">{categories.length}</p>
            <p className="text-xs text-stone-450 dark:text-stone-500 mt-0.5">Categories</p>
          </div>
        </div>

        <div className="flex flex-wrap gap-3">
          <button
            id="export-backup-btn"
            onClick={handleExportBackup}
            disabled={exportingBackup}
            className="bg-teal-700 hover:bg-teal-800 disabled:opacity-60 text-white text-sm font-bold py-2.5 px-5 rounded-lg transition-all cursor-pointer border-none flex items-center gap-2"
          >
            {exportingBackup ? <>{Icon.spinner} Preparing…</> : "Download full backup"}
          </button>

          <input type="file" accept=".json" id="backup-file-input" onChange={handleImportBackup} className="hidden" />
          <button
            id="import-backup-btn"
            onClick={() => document.getElementById("backup-file-input")?.click()}
            disabled={importingBackup}
            className="bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 dark:hover:bg-stone-750 text-stone-700 dark:text-stone-300 text-sm font-bold py-2.5 px-5 rounded-lg transition-all cursor-pointer border-none flex items-center gap-2"
          >
            {importingBackup ? <>{Icon.spinner} Restoring…</> : "Restore from backup"}
          </button>
        </div>
      </SectionCard>

      {/* ── Danger zone ── */}
      <SectionCard title="Danger zone" icon={Icon.danger} danger>
        <p className="text-xs text-stone-500 dark:text-stone-400 -mt-2 mb-5">
          Permanently deletes your account and all associated data including transactions, budgets, and goals. This action <strong>cannot be undone</strong>. We recommend exporting a backup first.
        </p>
        <button
          id="delete-account-btn"
          onClick={handleDeleteAccount}
          disabled={deleting}
          className="bg-red-600 hover:bg-red-700 disabled:opacity-60 text-white text-sm font-bold py-2.5 px-5 rounded-lg transition-all cursor-pointer border-none flex items-center gap-2"
        >
          {deleting ? <>{Icon.spinner} Deleting…</> : "Delete my account"}
        </button>
      </SectionCard>

      {/* ── About ── */}
      <div className="text-center py-2">
        <p className="text-xs text-stone-400 dark:text-stone-600 font-medium">Finance AI Coach · v1.0</p>
        <p className="text-xs text-stone-350 dark:text-stone-700 mt-0.5">Your data stays on your own server. Always.</p>
      </div>
    </div>
  );
};

export default Settings;
