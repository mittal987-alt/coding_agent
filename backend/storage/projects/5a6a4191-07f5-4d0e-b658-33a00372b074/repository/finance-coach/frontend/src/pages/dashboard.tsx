import { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { API_URL } from "../config";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Legend
} from "recharts";

/* ============================================================================
   FINANCE AI COACH — redesigned UI
   Visual identity: a "ledger" aesthetic. Serif headings, monospace tabular
   figures for money, warm paper backgrounds, and a teal / coral / gold palette
   in place of the generic indigo-violet gradient. Navigation moves from a
   horizontal tab strip (which overflowed with 9 items) to a left sidebar with
   7 sections, each grouping related features:
     Overview        — the daily-glance numbers
     Transactions    — the ledger itself (pulled out of Overview, it was
                        crowding the glanceable stuff)
     Budgets & Plan  — budgets + the AI planner, same domain
     Goals & Bills   — savings goals, subscriptions, bill calendar, reminders
                        — all "money committed to the future" in one place
     Accounts        — wallets/cards + shared/split bills — "who holds what"
     Insights & Tax  — alerts, spending heatmap, tax estimate — analysis
     Achievements    — gamification, a distinct mode of engagement
   ========================================================================= */

function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [insights, setInsights] = useState<any>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);

  // Authentication UI Modal State
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [authName, setAuthName] = useState<string>("");
  const [authEmail, setAuthEmail] = useState<string>("");
  const [authPassword, setAuthPassword] = useState<string>("");
  const [authError, setAuthError] = useState<string>("");
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isLoadingAuth, setIsLoadingAuth] = useState<boolean>(false);

  // Budgets state
  const [budgets, setBudgets] = useState<any[]>([]);
  const [budgetCategory, setBudgetCategory] = useState("Food");
  const [budgetAmount, setBudgetAmount] = useState("");

  // AI Chatbot state
  const [chatOpen, setChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState<any[]>([
    {
      sender: "ai",
      text: "Hello! I am your AI Financial Coach. Ask me anything about your budgets, transactions, or saving habits!"
    }
  ]);

  // Transaction CRUD state
  const [showTxModal, setShowTxModal] = useState(false);
  const [txModalMode, setTxModalMode] = useState<"add" | "edit">("add");
  const [selectedTxId, setSelectedTxId] = useState<number | null>(null);
  const [txDescription, setTxDescription] = useState("");
  const [txAmount, setTxAmount] = useState("");
  const [txCategory, setTxCategory] = useState("Shopping");
  const [txType, setTxType] = useState("expense");
  const [txDate, setTxDate] = useState(new Date().toISOString().split("T")[0]);

  // Transaction Filters state
  const [filterSearch, setFilterSearch] = useState("");
  const [filterCategory, setFilterCategory] = useState("All");
  const [filterType, setFilterType] = useState("All");

  // Theme state
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  // Section + sub-section navigation
  const [activeTab, setActiveTab] = useState<
    "overview" | "transactions" | "budgets" | "goals" | "accounts" | "insights" | "achievements"
  >("overview");
  const [goalsSubTab, setGoalsSubTab] = useState<"goals" | "subscriptions" | "calendar" | "reminders">("goals");
  const [insightsSubTab, setInsightsSubTab] = useState<"alerts" | "heatmap" | "tax">("alerts");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [trendsData, setTrendsData] = useState<any[]>([]);
  const [goals, setGoals] = useState<any[]>([]);
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [detectedSubs, setDetectedSubs] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [splits, setSplits] = useState<any[]>([]);
  const [healthScore, setHealthScore] = useState<any>(null);
  // Alerts
  const [alertsData, setAlertsData] = useState<any>(null);
  const [showAlertsPanel, setShowAlertsPanel] = useState(false);
  // Tax Estimator
  const [taxData, setTaxData] = useState<any>(null);
  // Budget Planner
  const [budgetPlan, setBudgetPlan] = useState<any>(null);
  const [applyingPlan, setApplyingPlan] = useState(false);
  // Net Worth
  const [netWorth, setNetWorth] = useState<any>(null);
  // Payment Reminders
  const [reminders, setReminders] = useState<any[]>([]);
  const [showReminderModal, setShowReminderModal] = useState(false);
  const [reminderName, setReminderName] = useState("");
  const [reminderAmount, setReminderAmount] = useState("");
  const [reminderDueDate, setReminderDueDate] = useState(new Date().toISOString().split("T")[0]);
  const [reminderCategory, setReminderCategory] = useState("Others");
  // Auto-Categorize
  const [autoCatResult, setAutoCatResult] = useState<any>(null);
  const [isAutoCatting, setIsAutoCatting] = useState(false);
  // Heatmap
  const [heatmapData, setHeatmapData] = useState<any>(null);
  // Gamification
  const [gamificationData, setGamificationData] = useState<any>(null);

  // Bill Calendar State
  const [calendarMonth, setCalendarMonth] = useState(new Date());

  // Accounts Modal and Form
  const [showAccountModal, setShowAccountModal] = useState(false);
  const [accountModalMode, setAccountModalMode] = useState<"add" | "edit">("add");
  const [selectedAccountId, setSelectedAccountId] = useState<number | null>(null);
  const [accountName, setAccountName] = useState("");
  const [accountType, setAccountType] = useState("Bank");
  const [accountBalance, setAccountBalance] = useState("0");

  // Splits Modal and Form
  const [showSplitModal, setShowSplitModal] = useState(false);
  const [splitDescription, setSplitDescription] = useState("");
  const [splitTotal, setSplitTotal] = useState("");
  const [splitFriend, setSplitFriend] = useState("");
  const [splitOwed, setSplitOwed] = useState("");

  // Savings Goals Modals and Forms
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [goalModalMode, setGoalModalMode] = useState<"add" | "edit">("add");
  const [selectedGoalId, setSelectedGoalId] = useState<number | null>(null);
  const [goalName, setGoalName] = useState("");
  const [goalTargetAmount, setGoalTargetAmount] = useState("");
  const [goalCurrentAmount, setGoalCurrentAmount] = useState("0");
  const [goalTargetDate, setGoalTargetDate] = useState(new Date().toISOString().split("T")[0]);
  const [pdfPassword, setPdfPassword] = useState<string>("");
  const [showPdfPasswordPrompt, setShowPdfPasswordPrompt] = useState(false);
  const [pdfPasswordMessage, setPdfPasswordMessage] = useState("");
  // Subscriptions Modals and Forms
  const [showSubModal, setShowSubModal] = useState(false);
  const [subModalMode, setSubModalMode] = useState<"add" | "edit">("add");
  const [selectedSubId, setSelectedSubId] = useState<number | null>(null);
  const [subName, setSubName] = useState("");
  const [subAmount, setSubAmount] = useState("");
  const [subCategory, setSubCategory] = useState("Others");
  const [subBillingCycle, setSubBillingCycle] = useState("Monthly");
  const [subNextDueDate, setSubNextDueDate] = useState(new Date().toISOString().split("T")[0]);

  // Ledger palette for the expense-share chart (teal / coral / gold family)
  const chartColors = ["#0F6E56", "#D85A30", "#BA7517", "#378ADD"];

  const chartData = [
    { name: "Food", value: insights?.food || 0 },
    { name: "Travel", value: insights?.travel || 0 },
    { name: "Shopping", value: insights?.shopping || 0 }
  ].filter(item => item.value > 0);

  const loadData = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setData({ income: 0, expense: 0, savings: 0, total_transactions: 0 });
      setTransactions([]);
      setInsights({ food: 0, travel: 0, shopping: 0, insights: [] });
      setBudgets([]);
      setTrendsData([]);
      setGoals([]);
      setSubscriptions([]);
      setDetectedSubs([]);
      setAccounts([]);
      setSplits([]);
      setHealthScore(null);
      return;
    }

    const headers: HeadersInit = { Authorization: `Bearer ${token}` };

    try {
      const dashboardRes = await fetch(`${API_URL}/dashboard`, { headers });
      if (dashboardRes.ok) {
        const dashboardData = await dashboardRes.json();
        setData(dashboardData);
      } else if (dashboardRes.status === 401) {
        localStorage.removeItem("token");
        setUserEmail(null);
        setData({ income: 0, expense: 0, savings: 0, total_transactions: 0 });
        setTransactions([]);
        setInsights({ food: 0, travel: 0, shopping: 0, insights: [] });
        setBudgets([]);
        setTrendsData([]);
        setGoals([]);
        setSubscriptions([]);
        setDetectedSubs([]);
        setAccounts([]);
        setSplits([]);
        setHealthScore(null);
        return;
      }

      const txRes = await fetch(`${API_URL}/transactions`, { headers });
      setTransactions(txRes.ok ? await txRes.json() : []);

      const insightsRes = await fetch(`${API_URL}/insights`, { headers });
      setInsights(insightsRes.ok ? await insightsRes.json() : { food: 0, travel: 0, shopping: 0, insights: [] });

      const budgetsRes = await fetch(`${API_URL}/budgets`, { headers });
      setBudgets(budgetsRes.ok ? await budgetsRes.json() : []);

      const trendsRes = await fetch(`${API_URL}/analytics/trends`, { headers });
      setTrendsData(trendsRes.ok ? await trendsRes.json() : []);

      const goalsRes = await fetch(`${API_URL}/goals`, { headers });
      setGoals(goalsRes.ok ? await goalsRes.json() : []);

      const subsRes = await fetch(`${API_URL}/subscriptions`, { headers });
      setSubscriptions(subsRes.ok ? await subsRes.json() : []);

      const detectRes = await fetch(`${API_URL}/subscriptions/detect`, { headers });
      setDetectedSubs(detectRes.ok ? await detectRes.json() : []);

      const accountsRes = await fetch(`${API_URL}/accounts/`, { headers });
      setAccounts(accountsRes.ok ? await accountsRes.json() : []);

      const splitsRes = await fetch(`${API_URL}/splits/`, { headers });
      setSplits(splitsRes.ok ? await splitsRes.json() : []);

      const healthRes = await fetch(`${API_URL}/analytics/health-score`, { headers });
      setHealthScore(healthRes.ok ? await healthRes.json() : null);

      const alertsRes = await fetch(`${API_URL}/alerts`, { headers });
      if (alertsRes.ok) setAlertsData(await alertsRes.json());

      const taxRes = await fetch(`${API_URL}/tax/estimate`, { headers });
      if (taxRes.ok) setTaxData(await taxRes.json());

      const planRes = await fetch(`${API_URL}/budget/plan`, { headers });
      if (planRes.ok) setBudgetPlan(await planRes.json());

      const nwRes = await fetch(`${API_URL}/networth`, { headers });
      if (nwRes.ok) setNetWorth(await nwRes.json());

      const remRes = await fetch(`${API_URL}/reminders`, { headers });
      setReminders(remRes.ok ? await remRes.json() : []);

      const hmRes = await fetch(`${API_URL}/analytics/daily-spend`, { headers });
      if (hmRes.ok) setHeatmapData(await hmRes.json());

      const gameRes = await fetch(`${API_URL}/gamification/stats`, { headers });
      if (gameRes.ok) setGamificationData(await gameRes.json());
    } catch (err) {
      console.error("Error fetching financial data:", err);
      setData({ income: 0, expense: 0, savings: 0, total_transactions: 0 });
      setTransactions([]);
      setInsights({ food: 0, travel: 0, shopping: 0, insights: [] });
      setBudgets([]);
      setTrendsData([]);
      setGoals([]);
      setSubscriptions([]);
      setDetectedSubs([]);
      setAccounts([]);
      setSplits([]);
      setHealthScore(null);
      setAlertsData(null);
      setTaxData(null);
      setBudgetPlan(null);
      setNetWorth(null);
      setReminders([]);
      setHeatmapData(null);
      setGamificationData(null);
    }
  };

  const checkUserProfile = async () => {
    const token = localStorage.getItem("token");
    if (!token) {
      setUserEmail(null);
      return;
    }
    try {
      const response = await fetch(`${API_URL}/profile`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (response.ok) {
        const result = await response.json();
        setUserEmail(result.email);
      } else {
        localStorage.removeItem("token");
        setUserEmail(null);
      }
    } catch (error) {
      console.error("Error fetching profile:", error);
    }
  };

  useEffect(() => {
    loadData();
    checkUserProfile();
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
    if (savedTheme) setTheme(savedTheme);
  }, []);

  useEffect(() => {
    if (theme === "dark") document.documentElement.classList.add("dark");
    else document.documentElement.classList.remove("dark");
    localStorage.setItem("theme", theme);
  }, [theme]);

  const uploadStatement = async (enforcedPassword?: string) => {
    if (!file) {
      alert("Please select a PDF file");
      return;
    }
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Please log in first to upload a statement.");
      setAuthMode("login");
      setShowAuthModal(true);
      return;
    }
    const formData = new FormData();
    formData.append("file", file);
    const passwordToSubmit = enforcedPassword || pdfPassword;
    if (passwordToSubmit) formData.append("password", passwordToSubmit);
    setIsUploading(true);
    try {
      const response = await fetch(`${API_URL}/upload-statement`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      const result = await response.json();
      setIsUploading(false);
      console.log("upload-statement response:", result);

      if (result.success) {
        alert(`Statement uploaded successfully! Saved ${result.transactions_saved} transactions.`);
        setFile(null);
        setPdfPassword("");
        setShowPdfPasswordPrompt(false);
        setPdfPasswordMessage("");
        const fileInput = document.getElementById("file-upload-input") as HTMLInputElement;
        if (fileInput) fileInput.value = "";
        loadData();
        return;
      }

      const needsPassword =
        result.requires_password === true ||
        result.requires_password === "true" ||
        result.password_required === true ||
        (typeof result.message === "string" && result.message.toLowerCase().includes("password")) ||
        (typeof result.detail === "string" && result.detail.toLowerCase().includes("password"));

      if (needsPassword) {
        const promptMessage = result.message || result.detail || "This PDF is password protected. Enter the file password:";
        setPdfPasswordMessage(promptMessage);
        setShowPdfPasswordPrompt(true);
        setPdfPassword("");
        return;
      }

      setShowPdfPasswordPrompt(false);
      setPdfPasswordMessage("");
      alert(result.message || result.detail || "Statement parsing/upload failed.");
    } catch (error) {
      console.error(error);
      setIsUploading(false);
      alert("Upload failed. Make sure the backend server is running.");
    }
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setAuthError("");
    setIsLoadingAuth(true);
    try {
      if (authMode === "signup") {
        const response = await fetch(`${API_URL}/signup`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ name: authName, email: authEmail, password: authPassword })
        });
        const data = await response.json();
        if (response.ok) {
          setAuthMode("login");
          alert("Account created successfully! Please log in.");
        } else {
          setAuthError(data.detail || "Signup failed");
        }
      } else {
        const response = await fetch(`${API_URL}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: authEmail, password: authPassword })
        });
        const data = await response.json();
        if (response.ok) {
          localStorage.setItem("token", data.access_token);
          setUserEmail(authEmail);
          setShowAuthModal(false);
          setAuthPassword("");
          setAuthName("");
          alert("Logged in successfully!");
          loadData();
        } else {
          setAuthError(data.detail || "Invalid credentials");
        }
      }
    } catch (error) {
      console.error(error);
      setAuthError("Failed to connect to the authentication server");
    } finally {
      setIsLoadingAuth(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setUserEmail(null);
    alert("Logged out successfully.");
    setTrendsData([]);
    setGoals([]);
    setSubscriptions([]);
    setDetectedSubs([]);
    setAccounts([]);
    setSplits([]);
    setHealthScore(null);
    setAlertsData(null);
    setTaxData(null);
    setBudgetPlan(null);
    setNetWorth(null);
    setReminders([]);
    setHeatmapData(null);
    setGamificationData(null);
    loadData();
  };

  const handleReminderSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!reminderName || !reminderAmount || !reminderDueDate) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/reminders`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify({ name: reminderName, amount: parseFloat(reminderAmount), due_date: reminderDueDate, category: reminderCategory })
      });
      if (res.ok) {
        setShowReminderModal(false);
        setReminderName(""); setReminderAmount(""); setReminderCategory("Others");
        loadData();
      }
    } catch (err) { console.error(err); }
  };

  const handleReminderPay = async (id: number) => {
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/reminders/${id}/pay`, { method: "PUT", headers: { Authorization: token ? `Bearer ${token}` : "" } });
      loadData();
    } catch (err) { console.error(err); }
  };

  const handleReminderDelete = async (id: number) => {
    if (!confirm("Delete this reminder?")) return;
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/reminders/${id}`, { method: "DELETE", headers: { Authorization: token ? `Bearer ${token}` : "" } });
      loadData();
    } catch (err) { console.error(err); }
  };

  const handleAutoCategorize = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    setIsAutoCatting(true);
    try {
      const res = await fetch(`${API_URL}/transactions/auto-categorize`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
      const result = await res.json();
      setAutoCatResult(result);
      loadData();
    } catch (err) { console.error(err); }
    finally { setIsAutoCatting(false); }
  };

  const handleApplyBudgetPlan = async () => {
    if (!budgetPlan || !budgetPlan.plan) return;
    const token = localStorage.getItem("token");
    if (!confirm(`Apply suggested budgets for ${budgetPlan.plan.length} categories? This will create new budget entries.`)) return;
    setApplyingPlan(true);
    try {
      for (const item of budgetPlan.plan) {
        if (item.suggested_budget > 0) {
          await fetch(`${API_URL}/budgets`, {
            method: "POST",
            headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
            body: JSON.stringify({ category: item.category, amount: item.suggested_budget })
          });
        }
      }
      alert("Budget plan applied successfully!");
      loadData();
    } catch (err) { console.error(err); }
    finally { setApplyingPlan(false); }
  };

  const handleGoalSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!goalName || !goalTargetAmount) return;
    const token = localStorage.getItem("token");
    const payload = {
      name: goalName,
      target_amount: parseFloat(goalTargetAmount),
      current_amount: parseFloat(goalCurrentAmount || "0"),
      target_date: goalTargetDate
    };
    const url = goalModalMode === "add" ? `${API_URL}/goals` : `${API_URL}/goals/${selectedGoalId}`;
    const method = goalModalMode === "add" ? "POST" : "PUT";
    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setShowGoalModal(false);
        setGoalName(""); setGoalTargetAmount(""); setGoalCurrentAmount("0");
        setGoalTargetDate(new Date().toISOString().split("T")[0]);
        loadData();
      }
    } catch (err) { console.error(err); }
  };

  const handleGoalDelete = async (goalId: number) => {
    if (!confirm("Are you sure you want to delete this savings goal?")) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/goals/${goalId}`, { method: "DELETE", headers: { Authorization: token ? `Bearer ${token}` : "" } });
      if (res.ok) loadData();
    } catch (err) { console.error(err); }
  };

  const openEditGoalModal = (g: any) => {
    setSelectedGoalId(g.id);
    setGoalName(g.name);
    setGoalTargetAmount(g.target_amount.toString());
    setGoalCurrentAmount(g.current_amount.toString());
    setGoalTargetDate(g.target_date);
    setGoalModalMode("edit");
    setShowGoalModal(true);
  };

  const handleSubSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subName || !subAmount || !subNextDueDate) return;
    const token = localStorage.getItem("token");
    const payload = { name: subName, amount: parseFloat(subAmount), category: subCategory, billing_cycle: subBillingCycle, next_due_date: subNextDueDate };
    const url = subModalMode === "add" ? `${API_URL}/subscriptions` : `${API_URL}/subscriptions/${selectedSubId}`;
    const method = subModalMode === "add" ? "POST" : "PUT";
    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setShowSubModal(false);
        setSubName(""); setSubAmount(""); setSubCategory("Others"); setSubBillingCycle("Monthly");
        setSubNextDueDate(new Date().toISOString().split("T")[0]);
        loadData();
      }
    } catch (err) { console.error(err); }
  };

  const handleSubDelete = async (subId: number) => {
    if (!confirm("Are you sure you want to remove this subscription?")) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/subscriptions/${subId}`, { method: "DELETE", headers: { Authorization: token ? `Bearer ${token}` : "" } });
      if (res.ok) loadData();
    } catch (err) { console.error(err); }
  };

  const openEditSubModal = (s: any) => {
    setSelectedSubId(s.id);
    setSubName(s.name);
    setSubAmount(s.amount.toString());
    setSubCategory(s.category);
    setSubBillingCycle(s.billing_cycle);
    setSubNextDueDate(s.next_due_date);
    setSubModalMode("edit");
    setShowSubModal(true);
  };

  const acceptDetectedSub = async (detected: any) => {
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/subscriptions`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify(detected)
      });
      if (res.ok) {
        alert(`${detected.name} added to subscriptions successfully!`);
        loadData();
      }
    } catch (err) { console.error(err); }
  };

  const handleAccountSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountName) return;
    const token = localStorage.getItem("token");
    const payload = { name: accountName, account_type: accountType, balance: parseFloat(accountBalance || "0") };
    const url = accountModalMode === "add" ? `${API_URL}/accounts/` : `${API_URL}/accounts/${selectedAccountId}`;
    const method = accountModalMode === "add" ? "POST" : "PUT";
    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setShowAccountModal(false);
        setAccountName(""); setAccountType("Bank"); setAccountBalance("0");
        loadData();
      }
    } catch (err) { console.error(err); }
  };

  const handleAccountDelete = async (id: number) => {
    if (!confirm("Delete this account?")) return;
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/accounts/${id}`, { method: "DELETE", headers: { Authorization: token ? `Bearer ${token}` : "" } });
      loadData();
    } catch (err) { console.error(err); }
  };

  const openEditAccountModal = (a: any) => {
    setSelectedAccountId(a.id);
    setAccountName(a.name);
    setAccountType(a.account_type);
    setAccountBalance(a.balance.toString());
    setAccountModalMode("edit");
    setShowAccountModal(true);
  };

  const handleSplitSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!splitDescription || !splitTotal || !splitFriend || !splitOwed) return;
    const token = localStorage.getItem("token");
    const payload = { description: splitDescription, total_amount: parseFloat(splitTotal), friend_name: splitFriend, amount_owed: parseFloat(splitOwed) };
    try {
      const res = await fetch(`${API_URL}/splits/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setShowSplitModal(false);
        setSplitDescription(""); setSplitTotal(""); setSplitFriend(""); setSplitOwed("");
        loadData();
      }
    } catch (err) { console.error(err); }
  };

  const handleSplitSettle = async (id: number) => {
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/splits/${id}/settle`, { method: "PUT", headers: { Authorization: token ? `Bearer ${token}` : "" } });
      loadData();
    } catch (err) { console.error(err); }
  };

  const handleSplitDelete = async (id: number) => {
    if (!confirm("Delete this split record?")) return;
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/splits/${id}`, { method: "DELETE", headers: { Authorization: token ? `Bearer ${token}` : "" } });
      loadData();
    } catch (err) { console.error(err); }
  };
  const handlePDFExport = async () => {
    const token = localStorage.getItem("token");

    if (!token) {
      alert("Please login first.");
      return;
    }

    try {
      const response = await fetch(`${API_URL}/report/pdf`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const error = await response.text();
        console.error(error);
        alert("Failed to generate PDF");
        return;
      }

      const blob = await response.blob();

      const url = window.URL.createObjectURL(blob);

      const a = document.createElement("a");
      a.href = url;
      a.download = "finance_report.pdf";

      document.body.appendChild(a);
      a.click();

      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error(err);
      alert("PDF download failed");
    }
  };

  const handleCSVExport = () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    const url = `${API_URL}/reports/csv`;
    const a = document.createElement("a");
    a.href = url;
    a.setAttribute("download", "finance_report.csv");
    fetch(url, { headers: { Authorization: `Bearer ${token}` } })
      .then(res => res.blob())
      .then(blob => {
        const blobUrl = window.URL.createObjectURL(blob);
        a.href = blobUrl;
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(blobUrl);
      })
      .catch(err => console.error("CSV export error:", err));
  };

  const getDaysInMonth = (year: number, month: number) => new Date(year, month + 1, 0).getDate();
  const getFirstDayOfMonth = (year: number, month: number) => new Date(year, month, 1).getDay();
  const getSubscriptionDueDates = () => {
    const dueDays: Record<number, string[]> = {};
    subscriptions.forEach(s => {
      if (s.next_due_date) {
        const d = new Date(s.next_due_date);
        if (d.getFullYear() === calendarMonth.getFullYear() && d.getMonth() === calendarMonth.getMonth()) {
          const day = d.getDate();
          if (!dueDays[day]) dueDays[day] = [];
          dueDays[day].push(s.name);
        }
      }
    });
    return dueDays;
  };

  const handleBudgetSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!budgetAmount || parseFloat(budgetAmount) <= 0) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/budgets`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify({ category: budgetCategory, amount: parseFloat(budgetAmount) })
      });
      if (res.ok) {
        alert("Budget target saved successfully!");
        setBudgetAmount("");
        loadData();
      }
    } catch (err) { console.error("Error setting budget:", err); }
  };

  const handleBudgetDelete = async (budgetId: number) => {
    if (!confirm("Are you sure you want to delete this budget target?")) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/budgets/${budgetId}`, { method: "DELETE", headers: { Authorization: token ? `Bearer ${token}` : "" } });
      if (res.ok) loadData();
    } catch (err) { console.error("Error deleting budget:", err); }
  };

  const sendChatMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatInput("");
    setChatMessages(prev => [...prev, { sender: "user", text: userMsg }]);
    setChatLoading(true);
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();
      setChatMessages(prev => [...prev, { sender: "ai", text: data.response }]);
    } catch (err) {
      console.error(err);
      setChatMessages(prev => [...prev, { sender: "ai", text: "Sorry, I encountered an issue connecting to the AI Coach." }]);
    } finally { setChatLoading(false); }
  };

  const handleTxSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!txDescription || !txAmount) return;
    const payload = { description: txDescription, amount: parseFloat(txAmount), category: txCategory, transaction_type: txType, transaction_date: txDate };
    const token = localStorage.getItem("token");
    const url = txModalMode === "add" ? `${API_URL}/transactions` : `${API_URL}/transactions/${selectedTxId}`;
    const method = txModalMode === "add" ? "POST" : "PUT";
    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        alert(`Transaction ${txModalMode === "add" ? "added" : "updated"} successfully!`);
        setShowTxModal(false);
        setTxDescription(""); setTxAmount(""); setTxCategory("Shopping"); setTxType("expense");
        setTxDate(new Date().toISOString().split("T")[0]);
        loadData();
      }
    } catch (err) { console.error("Error submitting transaction:", err); }
  };

  const handleTxDelete = async (txId: number) => {
    if (!confirm("Are you sure you want to delete this transaction record?")) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/transactions/${txId}`, { method: "DELETE", headers: { Authorization: token ? `Bearer ${token}` : "" } });
      if (res.ok) loadData();
    } catch (err) { console.error("Error deleting transaction:", err); }
  };

  const openEditTxModal = (tx: any) => {
    setSelectedTxId(tx.id);
    setTxDescription(tx.description);
    setTxAmount(tx.amount.toString());
    setTxCategory(tx.category);
    setTxType(tx.transaction_type);
    setTxDate(tx.transaction_date);
    setTxModalMode("edit");
    setShowTxModal(true);
  };

  const filteredTransactions = transactions.filter(t => {
    const matchSearch = t.description.toLowerCase().includes(filterSearch.toLowerCase());
    const matchCategory = filterCategory === "All" || t.category === filterCategory;
    const matchType = filterType === "All" || t.transaction_type === filterType;
    return matchSearch && matchCategory && matchType;
  });

  /* ----------------------------- shared bits ----------------------------- */

  const NAV_ITEMS: { key: typeof activeTab; label: string; icon: ReactNode; badge?: number }[] = [
    {
      key: "overview", label: "Overview", icon: (
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6A2.25 2.25 0 0 1 6 3.75h2.25A2.25 2.25 0 0 1 10.5 6v2.25a2.25 2.25 0 0 1-2.25 2.25H6a2.25 2.25 0 0 1-2.25-2.25V6ZM3.75 15.75A2.25 2.25 0 0 1 6 13.5h2.25a2.25 2.25 0 0 1 2.25 2.25V18a2.25 2.25 0 0 1-2.25 2.25H6A2.25 2.25 0 0 1 3.75 18v-2.25ZM13.5 6a2.25 2.25 0 0 1 2.25-2.25H18A2.25 2.25 0 0 1 20.25 6v2.25A2.25 2.25 0 0 1 18 10.5h-2.25a2.25 2.25 0 0 1-2.25-2.25V6ZM13.5 15.75a2.25 2.25 0 0 1 2.25-2.25H18a2.25 2.25 0 0 1 2.25 2.25V18A2.25 2.25 0 0 1 18 20.25h-2.25A2.25 2.25 0 0 1 13.5 18v-2.25Z" />
      )
    },
    {
      key: "transactions", label: "Transactions", icon: (
        <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 6.75h12M8.25 12h12m-12 5.25h12M3.75 6.75h.007v.008H3.75V6.75Zm.007 8.25H3.75v-.008h.008V15Zm-.008 3h.008v.008H3.75V18Z" />
      )
    },
    {
      key: "budgets", label: "Budgets & plan", icon: (
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v12m-3-2.818.879.659c1.171.879 3.07.879 4.242 0 1.172-.879 1.172-2.303 0-3.182C13.536 12.219 12.768 12 12 12c-.725 0-1.45-.22-2.003-.659-1.106-.879-1.106-2.303 0-3.182s2.9-.879 4.006 0l.415.33M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
      )
    },
    {
      key: "goals", label: "Goals & bills", icon: (
        <path strokeLinecap="round" strokeLinejoin="round" d="M12 6v6h4.5m4.5 0a9 9 0 1 1-18 0 9 9 0 0 1 18 0Z" />
      ), badge: goals.length + subscriptions.length
    },
    {
      key: "accounts", label: "Accounts & splits", icon: (
        <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 8.25h19.5M2.25 9h19.5m-16.5 5.25h6m-6 2.25h3m-4.5-9V19.5A2.25 2.25 0 0 0 6 21.75h12a2.25 2.25 0 0 0 2.25-2.25V6.75a2.25 2.25 0 0 0-2.25-2.25H6A2.25 2.25 0 0 0 3.75 6.75Z" />
      ), badge: splits.filter(s => !s.is_settled).length
    },
    {
      key: "insights", label: "Insights & tax", icon: (
        <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 21l8.982-11.861H13.62l.818-5.096L5.5 15.904h4.313Z" />
      ), badge: alertsData?.critical_count || undefined
    },
    {
      key: "achievements", label: "Achievements", icon: (
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 18.75h-9m9 0a3 3 0 0 1 3 3h-15a3 3 0 0 1 3-3m9 0v-3.375c0-.621-.503-1.125-1.125-1.125h-.871M7.5 18.75v-3.375c0-.621.504-1.125 1.125-1.125h.872m5.007 0H9.497m5.007 0a7.454 7.454 0 0 1-.982-3.172M9.497 14.25a7.454 7.454 0 0 0 .981-3.172M5.25 4.236c-.982.143-1.954.317-2.916.52A6.003 6.003 0 0 0 7.73 9.728M5.25 4.236V4.5c0 2.108.966 3.99 2.48 5.228M5.25 4.236V2.721C7.456 2.41 9.71 2.25 12 2.25c2.291 0 4.545.16 6.75.47v1.516M7.73 9.728a6.726 6.726 0 0 0 2.748 1.35m8.272-6.842V4.5c0 2.108-.966 3.99-2.48 5.228m2.48-5.492a46.32 46.32 0 0 1 2.916.52 6.003 6.003 0 0 1-5.395 4.972m0 0a6.726 6.726 0 0 1-2.749 1.35" />
      )
    }
  ];

  const pageTitles: Record<string, { title: string; sub: string }> = {
    overview: { title: "Overview", sub: "Where your money stands today" },
    transactions: { title: "Transactions", sub: "Every entry in your ledger" },
    budgets: { title: "Budgets & plan", sub: "Targets you've set, and what the AI suggests" },
    goals: { title: "Goals & bills", sub: "What you're saving for, and what's coming due" },
    accounts: { title: "Accounts & splits", sub: "Wallets, cards, and money shared with others" },
    insights: { title: "Insights & tax", sub: "Alerts, patterns, and your estimated tax" },
    achievements: { title: "Achievements", sub: "Your financial-habit streaks and badges" }
  };

  if (!data) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-stone-50 dark:bg-stone-950 transition-colors">
        <div className="w-10 h-10 border-2 border-stone-300 dark:border-stone-700 border-t-teal-700 dark:border-t-teal-400 rounded-full animate-spin mb-4"></div>
        <p className="text-stone-500 dark:text-stone-400 font-serif text-lg">Opening the ledger…</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-stone-50 dark:bg-stone-950 font-sans antialiased text-stone-900 dark:text-stone-100 transition-colors duration-300">
      <div className="flex">
        {/* ============================== SIDEBAR ============================== */}
        <aside
          className={`fixed lg:sticky top-0 z-30 h-screen w-72 shrink-0 bg-white dark:bg-stone-900 border-r border-stone-200 dark:border-stone-800 flex flex-col transition-transform duration-200 ${sidebarOpen ? "translate-x-0" : "-translate-x-full lg:translate-x-0"
            }`}
        >
          <div className="flex items-center gap-3 px-6 py-6 border-b border-stone-200 dark:border-stone-800">
            <div className="w-9 h-9 rounded-md bg-teal-700 dark:bg-teal-600 text-white flex items-center justify-center font-serif font-bold text-lg">
              ₹
            </div>
            <div>
              <h1 className="font-serif font-bold text-lg leading-tight text-stone-900 dark:text-stone-50">Finance Coach</h1>
              <p className="text-[11px] text-stone-400 dark:text-stone-500 font-medium tracking-wide uppercase">Your money, kept</p>
            </div>
            <button onClick={() => setSidebarOpen(false)} className="ml-auto lg:hidden text-stone-400 cursor-pointer">
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-5 h-5">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <nav className="flex-1 overflow-y-auto py-4 px-3 space-y-0.5">
            {NAV_ITEMS.map(item => {
              const isActive = activeTab === item.key;
              return (
                <button
                  key={item.key}
                  onClick={() => { setActiveTab(item.key); setSidebarOpen(false); }}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-md text-sm font-semibold transition-all cursor-pointer relative ${isActive
                    ? "bg-teal-50 dark:bg-teal-950/40 text-teal-800 dark:text-teal-300"
                    : "text-stone-500 dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800/60 hover:text-stone-700 dark:hover:text-stone-200"
                    }`}
                >
                  {isActive && <span className="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r bg-teal-700 dark:bg-teal-400" />}
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.75} stroke="currentColor" className="w-[18px] h-[18px] shrink-0">
                    {item.icon}
                  </svg>
                  <span className="flex-1 text-left">{item.label}</span>
                  {!!item.badge && (
                    <span className="text-[10px] font-bold bg-stone-100 dark:bg-stone-800 text-stone-500 dark:text-stone-400 rounded-full px-1.5 py-0.5 min-w-[18px] text-center">
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>

          <div className="p-4 border-t border-stone-200 dark:border-stone-800">
            <button
              onClick={() => setTheme(theme === "light" ? "dark" : "light")}
              className="w-full flex items-center gap-2.5 px-3 py-2 rounded-md text-xs font-bold text-stone-500 dark:text-stone-400 hover:bg-stone-100 dark:hover:bg-stone-800/60 transition-all cursor-pointer mb-2"
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
                  {userEmail.slice(0, 1).toUpperCase()}
                </div>
                <span className="text-xs font-semibold text-stone-600 dark:text-stone-300 truncate flex-1" title={userEmail}>{userEmail}</span>
                <button onClick={handleLogout} title="Sign out" className="text-stone-400 hover:text-coral-600 cursor-pointer p-1">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 9V5.25A2.25 2.25 0 0 0 13.5 3h-6a2.25 2.25 0 0 0-2.25 2.25v13.5A2.25 2.25 0 0 0 7.5 21h6a2.25 2.25 0 0 0 2.25-2.25V15M12 9l-3 3m0 0 3 3m-3-3h12.75" />
                  </svg>
                </button>
              </div>
            ) : (
              <button
                onClick={() => { setAuthMode("login"); setAuthError(""); setShowAuthModal(true); }}
                className="w-full bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 rounded-md transition-all cursor-pointer"
              >
                Sign in
              </button>
            )}
          </div>
        </aside>

        {sidebarOpen && <div onClick={() => setSidebarOpen(false)} className="fixed inset-0 bg-stone-900/40 z-20 lg:hidden" />}

        {/* ============================== MAIN ============================== */}
        <main className="flex-1 min-w-0">
          {/* Top bar */}
          <header className="sticky top-0 z-10 bg-stone-50/90 dark:bg-stone-950/90 backdrop-blur-sm border-b border-stone-200 dark:border-stone-800 px-5 sm:px-8 py-4">
            <div className="flex flex-wrap items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <button onClick={() => setSidebarOpen(true)} className="lg:hidden text-stone-500 cursor-pointer">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
                  </svg>
                </button>
                <div>
                  <h2 className="font-serif font-bold text-2xl text-stone-900 dark:text-stone-50">{pageTitles[activeTab].title}</h2>
                  <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-0.5">{pageTitles[activeTab].sub}</p>
                </div>
              </div>

              <div className="flex flex-wrap items-center gap-3">
                {/* Upload statement */}
                <div className="flex flex-col gap-2">
                  <div className="flex items-center gap-2 bg-white dark:bg-stone-900 p-1.5 rounded-lg border border-stone-200 dark:border-stone-800">
                    <input
                      id="file-upload-input"
                      type="file"
                      accept=".pdf"
                      onChange={(e) => { if (e.target.files?.[0]) setFile(e.target.files[0]); }}
                      className="text-xs text-stone-600 dark:text-stone-300 file:mr-2 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-semibold file:bg-stone-100 dark:file:bg-stone-800 file:text-teal-700 dark:file:text-teal-400 hover:file:bg-teal-50 cursor-pointer max-w-[160px]"
                    />
                    <button
                      onClick={() => uploadStatement(pdfPassword)}
                      disabled={isUploading}
                      className="bg-teal-700 hover:bg-teal-800 disabled:bg-teal-400 text-white text-xs font-bold py-1.5 px-3.5 rounded-md transition-all flex items-center gap-1.5 cursor-pointer whitespace-nowrap"
                    >
                      {isUploading ? (
                        <><span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>Parsing…</>
                      ) : (
                        <>
                          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-3.5 h-3.5">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
                          </svg>
                          Upload statement
                        </>
                      )}
                    </button>
                  </div>
                  {(file || showPdfPasswordPrompt) && (
                    <div className="rounded-lg border border-gold-300 bg-gold-50 p-2.5 text-xs text-gold-800 dark:border-amber-700 dark:bg-amber-950/30 dark:text-amber-300">
                      <p className="mb-2 font-medium">{pdfPasswordMessage || "If your PDF is encrypted, enter the password here before uploading."}</p>
                      <div className="flex flex-col sm:flex-row sm:items-center gap-2">
                        <input
                          type="password"
                          value={pdfPassword}
                          onChange={(e) => setPdfPassword(e.target.value)}
                          placeholder="PDF password"
                          className="w-full max-w-xs rounded-md border border-amber-300 bg-white px-2 py-1.5 text-xs text-stone-700 outline-none dark:border-amber-700 dark:bg-stone-900 dark:text-stone-200"
                        />
                        <button
                          onClick={() => uploadStatement(pdfPassword)}
                          disabled={isUploading || (!pdfPassword.trim() && !file)}
                          className="rounded-md bg-amber-600 px-3 py-1.5 text-[11px] font-semibold text-white hover:bg-amber-700 disabled:bg-amber-400"
                        >
                          Apply password
                        </button>
                      </div>
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
                    </button>
                    {showAlertsPanel && alertsData && (
                      <div className="absolute right-0 top-12 w-96 max-h-[420px] overflow-y-auto bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-xl shadow-xl z-50 p-4">
                        <div className="flex justify-between items-center mb-3">
                          <h3 className="text-sm font-bold font-serif text-stone-800 dark:text-stone-100">Smart alerts</h3>
                          <button onClick={() => setShowAlertsPanel(false)} className="text-stone-400 hover:text-stone-600 cursor-pointer text-lg leading-none">×</button>
                        </div>
                        <div className="space-y-2">
                          {alertsData.alerts.map((alert: any, i: number) => (
                            <div key={i} className={`p-3 rounded-lg text-xs font-medium border-l-4 ${alert.type === "critical" ? "bg-coral-50 dark:bg-coral-950/30 border-coral-500 text-coral-900 dark:text-coral-300" :
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

                {!userEmail && (
                  <button
                    onClick={() => { setAuthMode("login"); setAuthError(""); setShowAuthModal(true); }}
                    className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2.5 px-4 rounded-lg transition-all cursor-pointer"
                  >
                    Sign in
                  </button>
                )}
              </div>
            </div>
          </header>

          <div className="px-5 sm:px-8 py-7 pb-28">

            {/* ============================== OVERVIEW ============================== */}
            {activeTab === "overview" && (
              <div className="space-y-7">
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
                  <StatCard label="Income" value={data.income} icon="up" accent="teal" />
                  <StatCard label="Expenses" value={data.expense} icon="down" accent="coral" />
                  <StatCard label="Net savings" value={data.savings} icon="check" accent="blue" />
                  <StatCard label="Net worth" value={netWorth?.net_worth || 0} icon="home" accent="gold" sub={`Assets ₹${(netWorth?.total_assets || 0).toLocaleString("en-IN")}`} />
                </div>

                {userEmail && healthScore && (
                  <div className="bg-teal-800 dark:bg-teal-950 rounded-2xl p-6 sm:p-7 text-white">
                    <div className="flex flex-col md:flex-row items-center gap-8">
                      <div className="flex-shrink-0 flex flex-col items-center">
                        <div className="relative w-28 h-28">
                          <svg viewBox="0 0 36 36" className="w-28 h-28 -rotate-90">
                            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="rgba(255,255,255,0.18)" strokeWidth="3" />
                            <path d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" fill="none" stroke="#F5C95A" strokeWidth="3" strokeDasharray={`${healthScore.score}, 100`} strokeLinecap="round" />
                          </svg>
                          <div className="absolute inset-0 flex flex-col items-center justify-center">
                            <span className="text-3xl font-mono font-bold">{healthScore.score}</span>
                            <span className="text-[10px] opacity-70">/ 100</span>
                          </div>
                        </div>
                        <p className="text-[11px] font-bold mt-2 opacity-80 uppercase tracking-widest">
                          {healthScore.score >= 80 ? "Excellent" : healthScore.score >= 60 ? "Good" : healthScore.score >= 40 ? "Fair" : "Needs work"}
                        </p>
                      </div>
                      <div className="flex-1 space-y-3 w-full">
                        <div>
                          <h2 className="text-xl font-serif font-bold mb-1">Financial health score</h2>
                          <p className="text-xs text-white/70 font-medium">{healthScore.advice}</p>
                        </div>
                        <div className="grid grid-cols-3 gap-3 mt-4">
                          <div className="bg-white/10 rounded-lg p-3 text-center">
                            <p className="text-2xl font-mono font-bold">{healthScore.savings_score}</p>
                            <p className="text-[10px] font-bold opacity-70 mt-0.5">Savings / 40</p>
                          </div>
                          <div className="bg-white/10 rounded-lg p-3 text-center">
                            <p className="text-2xl font-mono font-bold">{healthScore.budget_score}</p>
                            <p className="text-[10px] font-bold opacity-70 mt-0.5">Budget / 40</p>
                          </div>
                          <div className="bg-white/10 rounded-lg p-3 text-center">
                            <p className="text-2xl font-mono font-bold">{healthScore.goals_score}</p>
                            <p className="text-[10px] font-bold opacity-70 mt-0.5">Goals / 20</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {userEmail && trendsData && trendsData.length > 0 && (
                  <SectionCard title="Cash flow, month by month" desc="Income against expenses over time">
                    <div style={{ width: "100%", height: 300 }}>
                      <ResponsiveContainer>
                        <AreaChart data={trendsData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                          <defs>
                            <linearGradient id="colorIncome" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#0F6E56" stopOpacity={0.25} />
                              <stop offset="95%" stopColor="#0F6E56" stopOpacity={0} />
                            </linearGradient>
                            <linearGradient id="colorExpense" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#D85A30" stopOpacity={0.25} />
                              <stop offset="95%" stopColor="#D85A30" stopOpacity={0} />
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#E7E2D6" className="dark:hidden" />
                          <CartesianGrid strokeDasharray="3 3" stroke="#2A2A26" className="hidden dark:block" />
                          <XAxis dataKey="month" stroke="#A8A296" fontSize={11} tickLine={false} />
                          <YAxis stroke="#A8A296" fontSize={11} tickLine={false} axisLine={false} tickFormatter={(val) => `₹${val}`} />
                          <Tooltip formatter={(value) => [`₹${value}`, ""]} />
                          <Legend verticalAlign="top" height={32} />
                          <Area name="Income" type="monotone" dataKey="income" stroke="#0F6E56" strokeWidth={2} fillOpacity={1} fill="url(#colorIncome)" />
                          <Area name="Expense" type="monotone" dataKey="expense" stroke="#D85A30" strokeWidth={2} fillOpacity={1} fill="url(#colorExpense)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  </SectionCard>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
                  <SectionCard title="AI coach insights" desc="What your data is telling you">
                    {insights && insights.insights && insights.insights.length > 0 ? (
                      <div className="space-y-3">
                        {insights.insights.map((item: string, index: number) => {
                          const isWarning = item.includes("⚠") || item.toLowerCase().includes("high") || item.toLowerCase().includes("limit");
                          return (
                            <div key={index} className={`flex gap-3 p-3.5 rounded-lg border-l-4 ${isWarning ? "bg-amber-50 dark:bg-amber-950/20 border-amber-500 text-amber-900 dark:text-amber-300" : "bg-teal-50 dark:bg-teal-950/10 border-teal-500 text-teal-900 dark:text-teal-300"}`}>
                              <p className="text-sm font-semibold leading-relaxed">{item.replace("⚠ ", "").replace("✅ ", "")}</p>
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      <EmptyState text="No insights yet." sub="Upload a statement or add transactions to trigger analysis." />
                    )}
                  </SectionCard>

                  <SectionCard title="Expense share" desc="Where this period's spending went">
                    {chartData.length > 0 ? (
                      <>
                        <div style={{ width: "100%", height: 170 }} className="flex justify-center items-center mb-3">
                          <ResponsiveContainer>
                            <PieChart>
                              <Pie data={chartData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} innerRadius={46} paddingAngle={3}>
                                {chartData.map((_entry, index) => <Cell key={`cell-${index}`} fill={chartColors[index % chartColors.length]} />)}
                              </Pie>
                              <Tooltip formatter={(value) => [`₹${value}`, "Spent"]} />
                            </PieChart>
                          </ResponsiveContainer>
                        </div>
                        <div className="space-y-2.5">
                          {chartData.map((category, index) => {
                            const percentage = (category.value / (insights?.food + insights?.travel + insights?.shopping || 1)) * 100;
                            return (
                              <div key={category.name} className="flex flex-col gap-1">
                                <div className="flex justify-between items-center text-xs font-bold text-stone-700 dark:text-stone-300">
                                  <span className="flex items-center gap-1.5">
                                    <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: chartColors[index % chartColors.length] }}></span>
                                    {category.name}
                                  </span>
                                  <span className="font-mono">₹{category.value?.toLocaleString("en-IN")} ({percentage.toFixed(0)}%)</span>
                                </div>
                                <div className="w-full bg-stone-100 dark:bg-stone-800 rounded-full h-1.5">
                                  <div className="h-1.5 rounded-full" style={{ width: `${percentage}%`, backgroundColor: chartColors[index % chartColors.length] }}></div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </>
                    ) : (
                      <EmptyState text="No expenditure records." sub="Check back once a statement is processed." />
                    )}
                  </SectionCard>
                </div>
              </div>
            )}

            {/* ============================== TRANSACTIONS ============================== */}
            {activeTab === "transactions" && (
              <SectionCard
                title="Transaction history"
                desc={`${filteredTransactions.length} of ${transactions.length} entries`}
                action={
                  userEmail && (
                    <div className="flex flex-wrap gap-2">
                      <button onClick={handleCSVExport} className="flex items-center gap-1.5 bg-white dark:bg-stone-800 border border-stone-200 dark:border-stone-700 hover:bg-stone-50 dark:hover:bg-stone-750 text-stone-600 dark:text-stone-300 text-xs font-bold px-3 py-2 rounded-lg transition-all cursor-pointer">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5M16.5 12 12 16.5m0 0L7.5 12m4.5 4.5V3" />
                        </svg>
                        Export CSV
                      </button>
                      <button onClick={handlePDFExport}>
                        PDF report
                      </button>
                      <button
                        onClick={handleAutoCategorize}
                        disabled={isAutoCatting}
                        className="bg-stone-800 dark:bg-stone-700 hover:bg-stone-900 disabled:bg-stone-400 text-white text-xs font-bold py-2 px-3.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer"
                      >
                        {isAutoCatting ? <><span className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin"></span>Categorizing…</> : "Auto-categorize"}
                      </button>
                      <button
                        onClick={() => { setTxModalMode("add"); setTxDescription(""); setTxAmount(""); setTxCategory("Shopping"); setTxType("expense"); setTxDate(new Date().toISOString().split("T")[0]); setShowTxModal(true); }}
                        className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2 px-3.5 rounded-lg transition-all flex items-center gap-1.5 cursor-pointer"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.5} stroke="currentColor" className="w-4 h-4">
                          <path strokeLinecap="round" strokeLinejoin="round" d="M12 4.5v15m7.5-7.5h-15" />
                        </svg>
                        Add transaction
                      </button>
                    </div>
                  )
                }
              >
                <div className="flex flex-col md:flex-row gap-3 mb-5">
                  <input
                    type="text" placeholder="Search descriptions…" value={filterSearch} onChange={(e) => setFilterSearch(e.target.value)}
                    className="bg-stone-50 dark:bg-stone-950 border border-stone-200 dark:border-stone-800 rounded-lg px-4 py-2 text-xs focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200 w-full sm:w-56"
                  />
                  <select value={filterCategory} onChange={(e) => setFilterCategory(e.target.value)} className="bg-stone-50 dark:bg-stone-950 border border-stone-200 dark:border-stone-800 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200 cursor-pointer">
                    <option value="All">All categories</option>
                    {["Income", "Food", "Travel", "Shopping", "Fuel", "UPI", "Cash", "Others"].map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                  <select value={filterType} onChange={(e) => setFilterType(e.target.value)} className="bg-stone-50 dark:bg-stone-950 border border-stone-200 dark:border-stone-800 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200 cursor-pointer">
                    <option value="All">All types</option>
                    <option value="income">Income</option>
                    <option value="expense">Expense</option>
                  </select>
                </div>

                {autoCatResult && (
                  <div className="mb-5 bg-stone-100 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-lg p-3 flex justify-between items-center text-xs text-stone-700 dark:text-stone-300">
                    <span className="font-semibold">{autoCatResult.message}</span>
                    <button onClick={() => setAutoCatResult(null)} className="font-bold text-teal-700 dark:text-teal-400 hover:underline cursor-pointer">Dismiss</button>
                  </div>
                )}

                <div className="overflow-x-auto -mx-1">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="border-b border-stone-200 dark:border-stone-800 text-stone-400 dark:text-stone-500 text-[11px] font-bold uppercase tracking-wider">
                        <th className="pb-3 pl-1">Date</th>
                        <th className="pb-3">Description</th>
                        <th className="pb-3">Category</th>
                        <th className="pb-3 text-right pr-1">Amount</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-100 dark:divide-stone-850 text-sm font-medium text-stone-700 dark:text-stone-300">
                      {filteredTransactions.length > 0 ? filteredTransactions.map((t) => {
                        const isIncome = t.transaction_type === "income" || t.category === "Income";
                        return (
                          <tr key={t.id} className="hover:bg-stone-50/60 dark:hover:bg-stone-850/30 transition-colors group">
                            <td className="py-3.5 pl-1 text-xs font-mono text-stone-500 dark:text-stone-400">{t.transaction_date}</td>
                            <td className="py-3.5 font-semibold text-stone-800 dark:text-stone-200">{t.description}</td>
                            <td className="py-3.5"><CategoryPill category={t.category} isIncome={isIncome} /></td>
                            <td className={`py-3.5 text-right pr-1 font-mono font-bold ${isIncome ? "text-teal-700 dark:text-teal-450" : "text-stone-800 dark:text-stone-200"}`}>
                              <span className="mr-3">{isIncome ? "+" : "−"}₹{t.amount?.toLocaleString("en-IN") || 0}</span>
                              {userEmail && (
                                <span className="inline-flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button onClick={() => openEditTxModal(t)} className="text-stone-400 hover:text-teal-700 dark:hover:text-teal-400 cursor-pointer" title="Edit">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                                      <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L6.832 19.82a4.5 4.5 0 0 1-1.897 1.13l-2.685.8.8-2.685a4.5 4.5 0 0 1 1.128-1.897L16.863 4.487Zm0 0L19.5 7.125" />
                                    </svg>
                                  </button>
                                  <button onClick={() => handleTxDelete(t.id)} className="text-stone-400 hover:text-coral-600 cursor-pointer" title="Delete">
                                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-4 h-4">
                                      <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.34 9m-4.72 0-.34-9m9.03-3.03a17.902 17.902 0 0 1-1.07 3.5M18.13 6a22.09 22.09 0 0 0-1.85-.3M14.74 9a22.38 22.38 0 0 0-5.48 0M10.5 6.857V5.07c0-.704.57-1.286 1.27-1.286h2.46c.7 0 1.27.582 1.27 1.286v1.787M3.75 6a17.925 17.925 0 0 1 1.07-3.5M6.37 6a22.09 22.09 0 0 1 1.85-.3M6.37 6a22.38 22.38 0 0 1 5.48 0" />
                                    </svg>
                                  </button>
                                </span>
                              )}
                            </td>
                          </tr>
                        );
                      }) : (
                        <tr><td colSpan={4} className="text-center py-12 text-stone-400 dark:text-stone-500 font-medium">No matching transaction records found.</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </SectionCard>
            )}

            {/* ============================== BUDGETS & PLAN ============================== */}
            {activeTab === "budgets" && (
              <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
                <div className="lg:col-span-2 space-y-5">
                  <SectionCard title="Category budgets" desc="Targets you've set">
                    {budgets.length > 0 ? (
                      <div className="space-y-4 mb-5">
                        {budgets.map((b) => {
                          const categorySpent = transactions.filter(t => t.category === b.category && t.transaction_type === "expense").reduce((sum, t) => sum + t.amount, 0);
                          const percentage = Math.min((categorySpent / b.amount) * 100, 100);
                          const isExceeded = categorySpent > b.amount;
                          const isClose = categorySpent > b.amount * 0.8 && !isExceeded;
                          return (
                            <div key={b.id} className="group flex flex-col gap-1">
                              <div className="flex justify-between items-center text-xs font-bold text-stone-700 dark:text-stone-350">
                                <span className="flex items-center gap-1.5">
                                  {b.category}
                                  <button onClick={() => handleBudgetDelete(b.id)} className="opacity-0 group-hover:opacity-100 text-coral-500 hover:text-coral-600 transition-all font-bold ml-1 cursor-pointer">✕</button>
                                </span>
                                <span className="font-mono">₹{categorySpent.toLocaleString("en-IN")} / ₹{b.amount.toLocaleString("en-IN")}</span>
                              </div>
                              <div className="w-full bg-stone-100 dark:bg-stone-850 rounded-full h-2 overflow-hidden">
                                <div className={`h-2 rounded-full transition-all duration-500 ${isExceeded ? "bg-coral-500" : isClose ? "bg-amber-500" : "bg-teal-600"}`} style={{ width: `${percentage}%` }}></div>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : <EmptyState text="No budgets defined." sub="Use the form below to set target limits." />}

                    {userEmail && (
                      <form onSubmit={handleBudgetSubmit} className="bg-stone-50 dark:bg-stone-950/40 border border-stone-100 dark:border-stone-850 rounded-lg p-3 mt-4">
                        <p className="text-[11px] font-extrabold text-stone-500 dark:text-stone-400 mb-2 uppercase tracking-wide">Set category budget</p>
                        <div className="flex gap-2">
                          <select value={budgetCategory} onChange={(e) => setBudgetCategory(e.target.value)} className="text-xs w-full bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-md p-1.5 focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200 cursor-pointer">
                            {["Food", "Travel", "Shopping", "Fuel", "UPI", "Cash", "Income", "Others"].map(c => <option key={c} value={c}>{c}</option>)}
                          </select>
                          <input type="number" required value={budgetAmount} onChange={(e) => setBudgetAmount(e.target.value)} placeholder="Amount" className="text-xs w-full bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-md p-1.5 focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-200" />
                          <button type="submit" className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold px-3 py-1.5 rounded-md cursor-pointer transition-all">Save</button>
                        </div>
                      </form>
                    )}
                  </SectionCard>
                </div>

                <div className="lg:col-span-3">
                  <SectionCard
                    title="Smart budget planner"
                    desc={budgetPlan ? `Based on ${budgetPlan.last_month} actuals` : "AI-suggested limits per category"}
                    action={budgetPlan && (
                      <button onClick={handleApplyBudgetPlan} disabled={applyingPlan} className="bg-stone-800 dark:bg-stone-700 hover:bg-stone-900 disabled:bg-stone-400 text-white font-bold py-2 px-4 rounded-lg transition-all cursor-pointer text-xs">
                        {applyingPlan ? "Applying…" : "Apply plan"}
                      </button>
                    )}
                  >
                    {budgetPlan ? (
                      <>
                        <p className="text-xs text-stone-500 dark:text-stone-400 mb-4">
                          Projected savings: <span className={`font-mono font-bold ${budgetPlan.projected_savings >= 0 ? "text-teal-700 dark:text-teal-400" : "text-coral-600"}`}>₹{budgetPlan.projected_savings?.toLocaleString("en-IN")}</span>
                        </p>
                        <div className="overflow-x-auto">
                          <table className="w-full text-xs">
                            <thead>
                              <tr className="border-b border-stone-200 dark:border-stone-800 text-stone-400 uppercase tracking-wider">
                                <th className="text-left py-2.5">Category</th>
                                <th className="text-right py-2.5">Last month</th>
                                <th className="text-right py-2.5">Suggested</th>
                                <th className="text-left py-2.5 pl-3">Status</th>
                              </tr>
                            </thead>
                            <tbody>
                              {budgetPlan.plan?.map((item: any, i: number) => (
                                <tr key={i} className="border-b border-stone-100 dark:border-stone-850">
                                  <td className="py-2.5 font-bold text-stone-700 dark:text-stone-300">{item.category}</td>
                                  <td className="py-2.5 text-right font-mono text-stone-500">₹{item.last_month_actual?.toLocaleString("en-IN")}</td>
                                  <td className="py-2.5 text-right font-mono font-bold text-teal-700 dark:text-teal-400">₹{item.suggested_budget?.toLocaleString("en-IN")}</td>
                                  <td className="py-2.5 pl-3">
                                    <span className={`text-[10px] font-bold px-2 py-1 rounded-full ${item.status === "overspent" ? "bg-coral-100 text-coral-700 dark:bg-coral-950/30 dark:text-coral-400" : item.status === "unbudgeted" ? "bg-amber-100 text-amber-700 dark:bg-amber-950/30 dark:text-amber-400" : "bg-teal-100 text-teal-700 dark:bg-teal-950/30 dark:text-teal-400"}`}>{item.advice}</span>
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      </>
                    ) : <EmptyState text="No plan data yet." sub="Add transactions and budgets to generate your monthly plan." />}
                  </SectionCard>
                </div>
              </div>
            )}

            {/* ============================== GOALS & BILLS ============================== */}
            {activeTab === "goals" && (
              <div className="space-y-5">
                <SubPills
                  options={[
                    { key: "goals", label: `Savings goals (${goals.length})` },
                    { key: "subscriptions", label: `Subscriptions (${subscriptions.length})` },
                    { key: "calendar", label: "Bill calendar" },
                    { key: "reminders", label: `Reminders (${reminders.length})` }
                  ]}
                  active={goalsSubTab}
                  onChange={(k) => setGoalsSubTab(k as any)}
                />

                {goalsSubTab === "goals" && (
                  <SectionCard
                    title="Savings goals"
                    desc="Milestones you're working toward"
                    action={userEmail && (
                      <button onClick={() => { setGoalModalMode("add"); setGoalName(""); setGoalTargetAmount(""); setGoalCurrentAmount("0"); setGoalTargetDate(new Date().toISOString().split("T")[0]); setShowGoalModal(true); }} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2 px-3.5 rounded-lg cursor-pointer">+ New goal</button>
                    )}
                  >
                    {goals.length > 0 ? (
                      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                        {goals.map((g) => {
                          const percentage = Math.min((g.current_amount / g.target_amount) * 100, 100);
                          const isCompleted = g.current_amount >= g.target_amount;
                          return (
                            <div key={g.id} className="border border-stone-150 dark:border-stone-800 rounded-xl p-4 flex flex-col justify-between">
                              <div>
                                <div className="flex justify-between items-start mb-3">
                                  <div>
                                    <h3 className="font-bold text-stone-800 dark:text-stone-100 text-sm">{g.name}</h3>
                                    <p className="text-[10px] text-stone-400">Target {g.target_date}</p>
                                  </div>
                                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${isCompleted ? "bg-teal-100 text-teal-700 dark:bg-teal-950/40 dark:text-teal-400" : "bg-stone-100 text-stone-500 dark:bg-stone-800 dark:text-stone-400"}`}>{isCompleted ? "Done" : "In progress"}</span>
                                </div>
                                <div className="mb-4">
                                  <div className="flex justify-between text-xs font-mono font-bold text-stone-600 dark:text-stone-400 mb-1.5">
                                    <span>{percentage.toFixed(0)}%</span>
                                    <span>₹{g.current_amount.toLocaleString("en-IN")} / ₹{g.target_amount.toLocaleString("en-IN")}</span>
                                  </div>
                                  <div className="w-full bg-stone-100 dark:bg-stone-850 rounded-full h-2 overflow-hidden">
                                    <div className="h-2 rounded-full bg-teal-600" style={{ width: `${percentage}%` }}></div>
                                  </div>
                                </div>
                              </div>
                              <div className="flex gap-2 border-t border-stone-100 dark:border-stone-850 pt-3">
                                <button onClick={() => openEditGoalModal(g)} className="flex-1 bg-stone-50 hover:bg-stone-100 dark:bg-stone-850 dark:hover:bg-stone-800 border border-stone-200 dark:border-stone-800 text-stone-600 dark:text-stone-300 text-xs font-bold py-2 rounded-lg cursor-pointer">Edit progress</button>
                                <button onClick={() => handleGoalDelete(g.id)} className="bg-coral-50 hover:bg-coral-100 dark:bg-coral-950/20 text-coral-600 text-xs font-bold p-2 rounded-lg cursor-pointer">✕</button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : <EmptyState text="No savings goals yet." sub="Add milestones to track purchases, emergency funds, or investments." />}
                  </SectionCard>
                )}

                {goalsSubTab === "subscriptions" && (
                  <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
                    <div className="lg:col-span-2">
                      <SectionCard
                        title="Registered subscriptions"
                        desc="Recurring expenses and due dates"
                        action={userEmail && (
                          <button onClick={() => { setSubModalMode("add"); setSubName(""); setSubAmount(""); setSubCategory("Others"); setSubBillingCycle("Monthly"); setSubNextDueDate(new Date().toISOString().split("T")[0]); setShowSubModal(true); }} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2 px-3.5 rounded-lg cursor-pointer">+ Add subscription</button>
                        )}
                      >
                        {subscriptions.length > 0 ? (
                          <div className="overflow-x-auto -mx-1">
                            <table className="w-full text-left text-sm">
                              <thead>
                                <tr className="border-b border-stone-200 dark:border-stone-800 text-stone-400 text-[11px] font-bold uppercase tracking-wider">
                                  <th className="py-2.5 pl-1">Subscription</th>
                                  <th className="py-2.5">Cycle</th>
                                  <th className="py-2.5">Due</th>
                                  <th className="py-2.5 text-right pr-1">Amount</th>
                                </tr>
                              </thead>
                              <tbody className="divide-y divide-stone-100 dark:divide-stone-850">
                                {subscriptions.map((s) => (
                                  <tr key={s.id} className="hover:bg-stone-50/60 dark:hover:bg-stone-850/30 group">
                                    <td className="py-3 pl-1">
                                      <p className="font-bold text-stone-800 dark:text-stone-150">{s.name}</p>
                                      <p className="text-[10px] text-stone-400 uppercase font-bold tracking-wider">{s.category}</p>
                                    </td>
                                    <td className="py-3 text-xs font-bold text-stone-500"><span className="bg-stone-100 dark:bg-stone-800 px-2 py-0.5 rounded-full">{s.billing_cycle}</span></td>
                                    <td className="py-3 text-xs font-mono text-stone-600 dark:text-stone-350">{s.next_due_date}</td>
                                    <td className="py-3 text-right pr-1 font-mono font-bold text-stone-800 dark:text-stone-200">
                                      <span className="mr-4">₹{s.amount?.toLocaleString("en-IN") || 0}</span>
                                      <span className="inline-flex gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button onClick={() => openEditSubModal(s)} className="text-stone-400 hover:text-teal-700 cursor-pointer">✎</button>
                                        <button onClick={() => handleSubDelete(s.id)} className="text-stone-400 hover:text-coral-600 cursor-pointer">✕</button>
                                      </span>
                                    </td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        ) : <EmptyState text="No recurring subscriptions registered yet." sub="" />}
                      </SectionCard>
                    </div>
                    <SectionCard title="Recurring suggestions" desc="Auto-detected from history">
                      {detectedSubs && detectedSubs.length > 0 ? (
                        <div className="space-y-3">
                          {detectedSubs.map((d, idx) => (
                            <div key={idx} className="bg-stone-50 dark:bg-stone-950/50 p-3.5 border border-stone-100 dark:border-stone-850 rounded-lg flex justify-between items-center">
                              <div>
                                <p className="font-bold text-xs text-stone-750 dark:text-stone-200">{d.name}</p>
                                <p className="text-[10px] text-teal-700 dark:text-teal-450 font-mono font-bold mt-0.5">₹{d.amount}/mo</p>
                              </div>
                              <button onClick={() => acceptDetectedSub(d)} className="bg-teal-50 hover:bg-teal-100 dark:bg-teal-950/50 border border-teal-100 dark:border-teal-900 text-teal-700 dark:text-teal-400 text-[10px] font-bold px-2.5 py-1.5 rounded-md cursor-pointer">+ Track</button>
                            </div>
                          ))}
                        </div>
                      ) : <EmptyState text="No recurring patterns detected yet." sub="Upload more statements to activate detection." />}
                    </SectionCard>
                  </div>
                )}

                {goalsSubTab === "calendar" && (() => {
                  const year = calendarMonth.getFullYear();
                  const month = calendarMonth.getMonth();
                  const daysInMonth = getDaysInMonth(year, month);
                  const firstDay = getFirstDayOfMonth(year, month);
                  const dueDates = getSubscriptionDueDates();
                  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
                  const today = new Date();
                  return (
                    <SectionCard
                      title={calendarMonth.toLocaleString("default", { month: "long", year: "numeric" })}
                      desc="Subscription due dates"
                      action={
                        <div className="flex gap-2">
                          <button onClick={() => setCalendarMonth(new Date(year, month - 1, 1))} className="bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 p-1.5 rounded-md cursor-pointer">‹</button>
                          <button onClick={() => setCalendarMonth(new Date(year, month + 1, 1))} className="bg-stone-100 hover:bg-stone-200 dark:bg-stone-800 p-1.5 rounded-md cursor-pointer">›</button>
                        </div>
                      }
                    >
                      <div className="grid grid-cols-7 mb-2">
                        {dayNames.map(d => <div key={d} className="text-center text-[10px] font-bold uppercase text-stone-400 py-2">{d}</div>)}
                      </div>
                      <div className="grid grid-cols-7 gap-1">
                        {Array.from({ length: firstDay }).map((_, i) => <div key={`empty-${i}`} className="h-16 rounded-lg"></div>)}
                        {Array.from({ length: daysInMonth }).map((_, i) => {
                          const day = i + 1;
                          const isToday = today.getDate() === day && today.getMonth() === month && today.getFullYear() === year;
                          const bills = dueDates[day] || [];
                          return (
                            <div key={day} className={`h-16 rounded-lg border p-1.5 flex flex-col ${isToday ? "border-coral-300 bg-coral-50 dark:bg-coral-950/20" : bills.length > 0 ? "border-teal-200 dark:border-teal-900 bg-teal-50 dark:bg-teal-950/20" : "border-stone-100 dark:border-stone-800 bg-white dark:bg-stone-900"}`}>
                              <span className={`text-xs font-mono font-bold ${isToday ? "text-coral-600" : "text-stone-500 dark:text-stone-400"}`}>{day}</span>
                              <div className="flex flex-col gap-0.5 mt-0.5 overflow-hidden">
                                {bills.slice(0, 2).map((b, idx) => <span key={idx} className="text-[7px] font-bold text-teal-700 dark:text-teal-400 bg-teal-100 dark:bg-teal-950/60 px-1 rounded truncate">{b}</span>)}
                                {bills.length > 2 && <span className="text-[7px] text-stone-400">+{bills.length - 2}</span>}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                      {subscriptions.length === 0 && <p className="text-center text-xs text-stone-450 mt-5">No subscriptions tracked yet — add some from the Subscriptions tab.</p>}
                    </SectionCard>
                  );
                })()}

                {goalsSubTab === "reminders" && (
                  <SectionCard
                    title="Bill reminders"
                    desc="Upcoming and overdue payments"
                    action={<button onClick={() => { setReminderName(""); setReminderAmount(""); setReminderDueDate(new Date().toISOString().split("T")[0]); setReminderCategory("Others"); setShowReminderModal(true); }} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2 px-3.5 rounded-lg cursor-pointer">+ Add reminder</button>}
                  >
                    {reminders && reminders.length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        {reminders.map((r: any) => {
                          const urgencyStyle: Record<string, string> = {
                            overdue: "border-coral-200 dark:border-coral-900 bg-coral-50 dark:bg-coral-950/20 text-coral-700 dark:text-coral-450",
                            urgent: "border-amber-200 dark:border-amber-900 bg-amber-50 dark:bg-amber-950/20 text-amber-700 dark:text-amber-400",
                            soon: "border-teal-200 dark:border-teal-900 bg-teal-50 dark:bg-teal-950/20 text-teal-700 dark:text-teal-400",
                            ok: "border-stone-150 dark:border-stone-800 bg-stone-50 dark:bg-stone-800/50 text-stone-600 dark:text-stone-350"
                          };
                          const style = urgencyStyle[r.urgency] || urgencyStyle.ok;
                          return (
                            <div key={r.id} className={`p-3.5 rounded-lg border flex justify-between items-center text-xs font-medium ${style}`}>
                              <div className="min-w-0 flex-1">
                                <p className="font-bold truncate">{r.name}</p>
                                <p className="opacity-85 font-mono font-semibold">₹{r.amount?.toLocaleString("en-IN")} • {r.due_date}</p>
                                <p className="text-[10px] font-bold mt-0.5">
                                  {r.is_paid ? "Paid" : r.days_left < 0 ? `Overdue by ${Math.abs(r.days_left)} days` : r.days_left === 0 ? "Due today" : `${r.days_left} days left`}
                                </p>
                              </div>
                              <div className="flex gap-1.5 ml-2">
                                {!r.is_paid && <button onClick={() => handleReminderPay(r.id)} className="bg-white/80 dark:bg-stone-800 hover:bg-white px-2 py-1 rounded-md border border-current font-black text-[9px] cursor-pointer">Pay</button>}
                                <button onClick={() => handleReminderDelete(r.id)} className="hover:text-coral-600 cursor-pointer p-1 text-stone-400 font-bold">✕</button>
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    ) : <EmptyState text="No bill reminders set." sub="Click Add reminder to get started." />}
                  </SectionCard>
                )}
              </div>
            )}

            {/* ============================== ACCOUNTS & SPLITS ============================== */}
            {activeTab === "accounts" && (
              <div className="space-y-7">
                <SectionCard
                  title="Wallets & accounts"
                  desc="Bank accounts, cards, and wallets"
                  action={userEmail && <button onClick={() => { setAccountModalMode("add"); setAccountName(""); setAccountType("Bank"); setAccountBalance("0"); setShowAccountModal(true); }} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2 px-3.5 rounded-lg cursor-pointer">+ Add account</button>}
                >
                  {accounts.length > 0 ? (
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {accounts.map((a: any) => {
                        const typeAccent: Record<string, string> = { Bank: "border-l-blue-500", "Credit Card": "border-l-coral-500", Cash: "border-l-teal-500", "UPI Wallet": "border-l-amber-500" };
                        const accent = typeAccent[a.account_type] || "border-l-stone-400";
                        return (
                          <div key={a.id} className={`border border-stone-150 dark:border-stone-800 border-l-4 ${accent} rounded-xl p-4`}>
                            <div className="flex justify-between items-start mb-6">
                              <div>
                                <p className="text-[10px] font-bold text-stone-400 uppercase tracking-widest">{a.account_type}</p>
                                <h3 className="text-base font-bold text-stone-800 dark:text-stone-100 mt-0.5">{a.name}</h3>
                              </div>
                              <div className="flex gap-2">
                                <button onClick={() => openEditAccountModal(a)} className="text-stone-400 hover:text-teal-700 cursor-pointer text-xs">✎</button>
                                <button onClick={() => handleAccountDelete(a.id)} className="text-stone-400 hover:text-coral-600 cursor-pointer text-xs">✕</button>
                              </div>
                            </div>
                            <p className="text-[10px] font-bold text-stone-400 uppercase tracking-wider mb-1">Balance</p>
                            <p className="text-2xl font-mono font-bold text-stone-850 dark:text-stone-100">₹{a.balance?.toLocaleString("en-IN") || 0}</p>
                          </div>
                        );
                      })}
                    </div>
                  ) : <EmptyState text="No accounts added yet." sub="Add bank accounts, cards, or wallets to track balances in one place." />}
                </SectionCard>

                <SectionCard
                  title="Shared bills"
                  desc={`Total owed to you: ₹${splits.filter(s => !s.is_settled).reduce((sum: number, s: any) => sum + s.amount_owed, 0).toLocaleString("en-IN")}`}
                  action={userEmail && <button onClick={() => { setSplitDescription(""); setSplitTotal(""); setSplitFriend(""); setSplitOwed(""); setShowSplitModal(true); }} className="bg-teal-700 hover:bg-teal-800 text-white text-xs font-bold py-2 px-3.5 rounded-lg cursor-pointer">+ Record split</button>}
                >
                  {splits.length > 0 ? (
                    <div className="overflow-x-auto -mx-1">
                      <table className="w-full text-left text-sm">
                        <thead>
                          <tr className="border-b border-stone-200 dark:border-stone-800 text-stone-400 text-[11px] font-bold uppercase tracking-wider">
                            <th className="py-2.5 pl-1">Description</th>
                            <th className="py-2.5">Friend</th>
                            <th className="py-2.5">Total</th>
                            <th className="py-2.5">They owe</th>
                            <th className="py-2.5 text-center">Status</th>
                            <th className="py-2.5 pr-1 text-right">Actions</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-stone-100 dark:divide-stone-850">
                          {splits.map((s: any) => (
                            <tr key={s.id} className="hover:bg-stone-50/60 dark:hover:bg-stone-850/30">
                              <td className="py-3 pl-1 font-semibold text-stone-800 dark:text-stone-200">{s.description}</td>
                              <td className="py-3 font-bold text-stone-600 dark:text-stone-350">{s.friend_name}</td>
                              <td className="py-3 font-mono text-stone-500">₹{s.total_amount?.toLocaleString("en-IN")}</td>
                              <td className="py-3 font-mono font-bold text-teal-700 dark:text-teal-400">₹{s.amount_owed?.toLocaleString("en-IN")}</td>
                              <td className="py-3 text-center">
                                {s.is_settled ? <span className="bg-teal-100 text-teal-700 dark:bg-teal-950/40 dark:text-teal-400 text-[10px] font-bold px-2 py-0.5 rounded-full">Settled</span> : <span className="bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 text-[10px] font-bold px-2 py-0.5 rounded-full">Pending</span>}
                              </td>
                              <td className="py-3 pr-1 text-right">
                                <div className="flex justify-end gap-2">
                                  {!s.is_settled && <button onClick={() => handleSplitSettle(s.id)} className="bg-teal-50 hover:bg-teal-100 dark:bg-teal-950/30 text-teal-700 dark:text-teal-400 text-[10px] font-bold px-2.5 py-1.5 rounded-md cursor-pointer">Settle up</button>}
                                  <button onClick={() => handleSplitDelete(s.id)} className="text-stone-400 hover:text-coral-600 cursor-pointer p-1">✕</button>
                                </div>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  ) : <EmptyState text="No splits recorded." sub="Track shared expenses for dinners, rent, trips, and more." />}
                </SectionCard>
              </div>
            )}

            {/* ============================== INSIGHTS & TAX ============================== */}
            {activeTab === "insights" && (
              <div className="space-y-5">
                <SubPills
                  options={[
                    { key: "alerts", label: `Alerts ${alertsData ? `(${alertsData.alerts?.length || 0})` : ""}` },
                    { key: "heatmap", label: "Spending heatmap" },
                    { key: "tax", label: "Tax estimator" }
                  ]}
                  active={insightsSubTab}
                  onChange={(k) => setInsightsSubTab(k as any)}
                />

                {insightsSubTab === "alerts" && (
                  <SectionCard title="Smart alerts" desc="Everything worth your attention right now">
                    {alertsData && alertsData.alerts?.length > 0 ? (
                      <div className="space-y-2.5">
                        {alertsData.alerts.map((alert: any, i: number) => (
                          <div key={i} className={`p-4 rounded-lg text-sm font-medium border-l-4 ${alert.type === "critical" ? "bg-coral-50 dark:bg-coral-950/30 border-coral-500 text-coral-900 dark:text-coral-300" : alert.type === "warning" ? "bg-amber-50 dark:bg-amber-950/30 border-amber-500 text-amber-900 dark:text-amber-300" : "bg-teal-50 dark:bg-teal-950/20 border-teal-500 text-teal-900 dark:text-teal-300"}`}>
                            <p className="font-bold mb-0.5">{alert.title}</p>
                            <p className="opacity-80 text-xs">{alert.message}</p>
                          </div>
                        ))}
                      </div>
                    ) : <EmptyState text="No alerts right now." sub="You'll see budget, bill, and spending warnings here." />}
                  </SectionCard>
                )}

                {insightsSubTab === "heatmap" && (
                  <SectionCard
                    title="90-day spending heatmap"
                    desc={heatmapData ? `Avg daily ₹${heatmapData.avg_daily_spend?.toLocaleString("en-IN")} • Total ₹${heatmapData.total_spend_90d?.toLocaleString("en-IN")}` : "Daily spending intensity"}
                  >
                    {heatmapData && heatmapData.days ? (
                      <div className="flex flex-col items-start overflow-x-auto pb-2">
                        <div className="flex gap-1">
                          {Array.from({ length: 13 }).map((_, weekIdx) => {
                            const weekDays = heatmapData.days.filter((d: any) => d.week === weekIdx);
                            return (
                              <div key={weekIdx} className="flex flex-col gap-1">
                                {weekIdx === 0 && weekDays.length > 0 && Array.from({ length: weekDays[0].day_of_week }).map((_, padIdx) => <div key={`pad-${padIdx}`} className="w-3.5 h-3.5 rounded bg-transparent"></div>)}
                                {weekDays.map((day: any) => {
                                  const levelColors = ["bg-stone-100 dark:bg-stone-800", "bg-teal-100 dark:bg-teal-950/60", "bg-teal-300 dark:bg-teal-900/80", "bg-teal-500 dark:bg-teal-700", "bg-teal-700 dark:bg-teal-500"];
                                  return <div key={day.date} className={`w-3.5 h-3.5 rounded ${levelColors[day.level]}`} title={`${day.date}: ₹${day.amount?.toLocaleString("en-IN")} spent`}></div>;
                                })}
                              </div>
                            );
                          })}
                        </div>
                        <div className="flex justify-between w-full mt-4 text-[10px] text-stone-450 font-bold px-1">
                          <span>90 days ago</span>
                          <div className="flex items-center gap-1">
                            <span>Less</span>
                            <div className="w-2.5 h-2.5 rounded bg-stone-100 dark:bg-stone-800"></div>
                            <div className="w-2.5 h-2.5 rounded bg-teal-100 dark:bg-teal-950/60"></div>
                            <div className="w-2.5 h-2.5 rounded bg-teal-300 dark:bg-teal-900/80"></div>
                            <div className="w-2.5 h-2.5 rounded bg-teal-500"></div>
                            <div className="w-2.5 h-2.5 rounded bg-teal-700 dark:bg-teal-500"></div>
                            <span>More</span>
                          </div>
                          <span>Today</span>
                        </div>
                      </div>
                    ) : <EmptyState text="Loading heatmap…" sub="" />}
                  </SectionCard>
                )}

                {insightsSubTab === "tax" && (
                  <div className="space-y-5">
                    {taxData ? (
                      <>
                        <div className="bg-amber-700 dark:bg-amber-900 rounded-2xl p-6 text-white">
                          <div className="flex flex-col md:flex-row items-center gap-8">
                            <div className="text-center flex-shrink-0">
                              <p className="text-[11px] font-bold opacity-70 uppercase tracking-widest mb-1">Estimated tax liability</p>
                              <p className="text-4xl font-mono font-bold">₹{taxData.total_tax_liability?.toLocaleString("en-IN")}</p>
                              <p className="text-sm font-bold mt-1 opacity-80">Effective rate {taxData.effective_tax_rate}%</p>
                            </div>
                            <div className="flex-1 grid grid-cols-2 gap-3 w-full">
                              <div className="bg-white/15 rounded-lg p-3"><p className="text-xs opacity-70 font-bold mb-1">Gross income</p><p className="text-lg font-mono font-bold">₹{taxData.gross_income?.toLocaleString("en-IN")}</p></div>
                              <div className="bg-white/15 rounded-lg p-3"><p className="text-xs opacity-70 font-bold mb-1">Standard deduction</p><p className="text-lg font-mono font-bold">₹{taxData.standard_deduction?.toLocaleString("en-IN")}</p></div>
                              <div className="bg-white/15 rounded-lg p-3"><p className="text-xs opacity-70 font-bold mb-1">Net taxable income</p><p className="text-lg font-mono font-bold">₹{taxData.net_taxable_income?.toLocaleString("en-IN")}</p></div>
                              <div className="bg-white/15 rounded-lg p-3"><p className="text-xs opacity-70 font-bold mb-1">Rebate 87A</p><p className="text-lg font-mono font-bold">₹{taxData.rebate_87A?.toLocaleString("en-IN")}</p></div>
                            </div>
                          </div>
                          <p className="text-xs opacity-70 mt-4 font-medium">{taxData.regime}</p>
                        </div>

                        {taxData.slab_breakdown && taxData.slab_breakdown.length > 0 && (
                          <SectionCard title="Tax slab breakdown" desc="">
                            <div className="space-y-2.5">
                              {taxData.slab_breakdown.map((slab: any, i: number) => (
                                <div key={i} className="flex items-center justify-between p-3 bg-stone-50 dark:bg-stone-800/50 rounded-lg">
                                  <div>
                                    <p className="text-sm font-bold text-stone-700 dark:text-stone-200">{slab.slab}</p>
                                    <p className="text-xs text-stone-500 font-mono">₹{slab.income_in_slab?.toLocaleString("en-IN")} in slab</p>
                                  </div>
                                  <div className="text-right">
                                    <p className="text-xs font-bold text-amber-700 dark:text-amber-400">{slab.rate}</p>
                                    <p className="text-sm font-mono font-bold text-stone-800 dark:text-stone-100">₹{slab.tax?.toLocaleString("en-IN")}</p>
                                  </div>
                                </div>
                              ))}
                              <div className="flex items-center justify-between p-3 bg-amber-50 dark:bg-amber-950/20 rounded-lg border border-amber-100 dark:border-amber-900">
                                <p className="text-sm font-bold text-amber-800 dark:text-amber-300">4% Health & education cess</p>
                                <p className="text-sm font-mono font-bold text-amber-800 dark:text-amber-300">₹{taxData.cess_4pct?.toLocaleString("en-IN")}</p>
                              </div>
                            </div>
                          </SectionCard>
                        )}

                        <SectionCard title="Tax saving tips" desc="">
                          <div className="space-y-2.5">
                            {taxData.tips?.map((tip: string, i: number) => (
                              <div key={i} className="flex gap-3 p-3.5 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-100 dark:border-blue-900">
                                <p className="text-sm text-blue-800 dark:text-blue-300 font-medium">{tip}</p>
                              </div>
                            ))}
                          </div>
                        </SectionCard>
                      </>
                    ) : <EmptyState text="No income data found." sub="Upload statements or add income transactions to estimate your tax." />}
                  </div>
                )}
              </div>
            )}

            {/* ============================== ACHIEVEMENTS ============================== */}
            {activeTab === "achievements" && (
              <div className="space-y-5">
                {gamificationData ? (
                  <>
                    <div className="bg-gold-700 dark:bg-amber-900 rounded-2xl p-6 text-white" style={{ backgroundColor: "#a3720f" }}>
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
                            <div className="bg-white h-full rounded-full transition-all duration-700" style={{ width: `${gamificationData.progress_pct}%` }}></div>
                          </div>
                          <div className="grid grid-cols-3 gap-3 mt-4">
                            <div className="bg-white/15 rounded-lg p-3 text-center"><p className="text-xl font-mono font-bold">{gamificationData.streak_days}</p><p className="text-xs font-bold mt-1">Day streak</p></div>
                            <div className="bg-white/15 rounded-lg p-3 text-center"><p className="text-xl font-mono font-bold">{gamificationData.earned_badge_count}</p><p className="text-xs font-bold mt-1">Badges earned</p></div>
                            <div className="bg-white/15 rounded-lg p-3 text-center"><p className="text-xl font-mono font-bold">{gamificationData.stats?.savings_rate_pct}%</p><p className="text-xs font-bold mt-1">Savings rate</p></div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <SectionCard title="Badge collection" desc="">
                      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                        {gamificationData.badges?.map((badge: any) => (
                          <div key={badge.id} className={`flex items-center gap-3 p-3.5 rounded-lg border ${badge.earned ? "bg-amber-50 dark:bg-amber-950/20 border-amber-200 dark:border-amber-800" : "bg-stone-50 dark:bg-stone-800/50 border-stone-100 dark:border-stone-700 opacity-50 grayscale"}`}>
                            <div className="flex-1 min-w-0">
                              <p className={`text-sm font-bold truncate ${badge.earned ? "text-amber-800 dark:text-amber-300" : "text-stone-500"}`}>{badge.name}</p>
                              <p className="text-xs text-stone-400 truncate">{badge.description}</p>
                              <p className="text-xs font-mono font-bold text-amber-600 mt-0.5">+{badge.xp} XP</p>
                            </div>
                            {badge.earned && <span className="text-teal-600 flex-shrink-0">✓</span>}
                          </div>
                        ))}
                      </div>
                    </SectionCard>
                  </>
                ) : <EmptyState text="Start tracking to earn badges." sub="" />}
              </div>
            )}
          </div>
        </main>
      </div>

      {/* ============================== FLOATING CHATBOT ============================== */}
      {userEmail && (
        <div className="fixed bottom-6 right-6 z-40">
          <button onClick={() => setChatOpen(!chatOpen)} className="bg-teal-700 hover:bg-teal-800 text-white p-4 rounded-full shadow-lg transition-all hover:scale-105 duration-200 flex items-center justify-center cursor-pointer">
            {chatOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6"><path strokeLinecap="round" strokeLinejoin="round" d="M6 18 18 6M6 6l12 12" /></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2} stroke="currentColor" className="w-6 h-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.625 9.75a.625.625 0 1 1-1.25 0 .625.625 0 0 1 1.25 0Zm4.5 0a.625.625 0 1 1-1.25 0 .625.625 0 0 1 1.25 0Zm4.5 0a.625.625 0 1 1-1.25 0 .625.625 0 0 1 1.25 0Z" />
                <path strokeLinecap="round" strokeLinejoin="round" d="M2.036 12.322a1.012 1.012 0 0 1 0-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178Z" />
              </svg>
            )}
          </button>

          {chatOpen && (
            <div className="absolute bottom-16 right-0 w-80 md:w-96 h-[440px] bg-white dark:bg-stone-900 border border-stone-200 dark:border-stone-800 rounded-2xl shadow-2xl flex flex-col overflow-hidden">
              <div className="bg-teal-800 p-4 text-white flex justify-between items-center">
                <span className="font-serif font-bold text-sm">Finance AI coach</span>
                <button onClick={() => setChatOpen(false)} className="text-white/80 hover:text-white cursor-pointer">✕</button>
              </div>
              <div className="flex-1 p-4 overflow-y-auto space-y-3 bg-stone-50/60 dark:bg-stone-950/30 text-xs">
                {chatMessages.map((msg, index) => (
                  <div key={index} className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}>
                    <div className={`max-w-[85%] rounded-xl p-3 ${msg.sender === "user" ? "bg-teal-700 text-white rounded-tr-none" : "bg-white dark:bg-stone-800 border border-stone-100 dark:border-stone-800 text-stone-800 dark:text-stone-200 rounded-tl-none"}`}>
                      <p className="leading-relaxed whitespace-pre-line">{msg.text}</p>
                    </div>
                  </div>
                ))}
                {chatLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white dark:bg-stone-800 border border-stone-100 dark:border-stone-800 rounded-xl rounded-tl-none p-3 flex items-center gap-1">
                      <span className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce"></span>
                      <span className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce delay-75"></span>
                      <span className="w-1.5 h-1.5 bg-stone-400 rounded-full animate-bounce delay-150"></span>
                    </div>
                  </div>
                )}
              </div>
              <form onSubmit={sendChatMessage} className="p-3 border-t border-stone-150 dark:border-stone-800 bg-white dark:bg-stone-900 flex gap-2">
                <input type="text" required value={chatInput} onChange={(e) => setChatInput(e.target.value)} placeholder="Ask the coach…" className="w-full bg-stone-50 dark:bg-stone-800 border border-stone-200 dark:border-stone-700 rounded-lg px-3 py-2 text-xs focus:outline-none focus:border-teal-600 text-stone-800 dark:text-stone-100" />
                <button type="submit" disabled={chatLoading} className="bg-teal-700 hover:bg-teal-800 disabled:bg-teal-400 text-white px-3.5 rounded-lg cursor-pointer">→</button>
              </form>
            </div>
          )}
        </div>
      )}

      {/* ============================== MODALS ============================== */}

      {showAccountModal && (
        <Modal onClose={() => setShowAccountModal(false)} title={accountModalMode === "add" ? "Add account" : "Edit account"} desc="Track balance across your wallets and bank accounts">
          <form onSubmit={handleAccountSubmit} className="space-y-4">
            <Field label="Account name"><input type="text" required value={accountName} onChange={e => setAccountName(e.target.value)} placeholder="e.g. HDFC Savings" className="modal-input" /></Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Account type">
                <select value={accountType} onChange={e => setAccountType(e.target.value)} className="modal-input cursor-pointer">
                  {["Bank", "Credit Card", "Cash", "UPI Wallet"].map(t => <option key={t}>{t}</option>)}
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
            <Field label="Goal name"><input type="text" required value={goalName} onChange={(e) => setGoalName(e.target.value)} placeholder="e.g. New laptop" className="modal-input" /></Field>
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
            <Field label="Subscription name"><input type="text" required value={subName} onChange={(e) => setSubName(e.target.value)} placeholder="e.g. Netflix" className="modal-input" /></Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Amount (₹)"><input type="number" required value={subAmount} onChange={(e) => setSubAmount(e.target.value)} placeholder="649" className="modal-input" /></Field>
              <Field label="Category">
                <select value={subCategory} onChange={(e) => setSubCategory(e.target.value)} className="modal-input cursor-pointer">
                  {["Entertainment", "Utilities", "Rent", "Shopping", "Others"].map(c => <option key={c}>{c}</option>)}
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

      {showReminderModal && (
        <Modal onClose={() => setShowReminderModal(false)} title="Add payment reminder" desc="">
          <form onSubmit={handleReminderSubmit} className="space-y-4">
            <Field label="Name"><input type="text" required value={reminderName} onChange={(e) => setReminderName(e.target.value)} placeholder="e.g. Credit card bill" className="modal-input" /></Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Amount (₹)"><input type="number" step="0.01" required value={reminderAmount} onChange={(e) => setReminderAmount(e.target.value)} className="modal-input" /></Field>
              <Field label="Due date"><input type="date" required value={reminderDueDate} onChange={(e) => setReminderDueDate(e.target.value)} className="modal-input" /></Field>
            </div>
            <Field label="Category">
              <select value={reminderCategory} onChange={(e) => setReminderCategory(e.target.value)} className="modal-input">
                {["EMI", "Credit Card", "Rent", "Utilities", "Subscription", "Insurance", "Others"].map(c => <option key={c}>{c}</option>)}
              </select>
            </Field>
            <SubmitButton>Add reminder</SubmitButton>
          </form>
        </Modal>
      )}

      {showTxModal && (
        <Modal onClose={() => setShowTxModal(false)} title={txModalMode === "add" ? "Add transaction" : "Edit transaction"} desc={txModalMode === "add" ? "Record a new entry manually" : "Modify existing transaction details"}>
          <form onSubmit={handleTxSubmit} className="space-y-4">
            <Field label="Description"><input type="text" required value={txDescription} onChange={(e) => setTxDescription(e.target.value)} placeholder="e.g. Grocery store" className="modal-input" /></Field>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Amount (₹)"><input type="number" step="0.01" required value={txAmount} onChange={(e) => setTxAmount(e.target.value)} placeholder="250.00" className="modal-input" /></Field>
              <Field label="Date"><input type="date" required value={txDate} onChange={(e) => setTxDate(e.target.value)} className="modal-input" /></Field>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <Field label="Category">
                <select value={txCategory} onChange={(e) => setTxCategory(e.target.value)} className="modal-input cursor-pointer">
                  {["Shopping", "Food", "Travel", "Fuel", "UPI", "Cash", "Income", "Others"].map(c => <option key={c}>{c}</option>)}
                </select>
              </Field>
              <Field label="Type">
                <select value={txType} onChange={(e) => setTxType(e.target.value)} className="modal-input cursor-pointer">
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
              </Field>
            </div>
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
            <button type="submit" disabled={isLoadingAuth} className="w-full bg-teal-700 hover:bg-teal-800 disabled:bg-teal-400 text-white font-bold py-3 rounded-lg transition-all text-sm mt-2 flex items-center justify-center cursor-pointer">
              {isLoadingAuth ? <span className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></span> : authMode === "login" ? "Sign in" : "Register account"}
            </button>
          </form>
          <div className="text-center mt-6">
            <button onClick={() => { setAuthMode(authMode === "login" ? "signup" : "login"); setAuthError(""); }} className="text-xs text-teal-700 dark:text-teal-400 hover:text-teal-800 font-bold transition-all cursor-pointer">
              {authMode === "login" ? "Don't have an account? Sign up" : "Already have an account? Log in"}
            </button>
          </div>
        </Modal>
      )}

      <style>{`
        .modal-input {
          width: 100%;
          background: var(--tw-bg-opacity, 1) #FAFAF7;
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
}

/* ============================================================================
   Shared presentational helpers
   ========================================================================= */

function StatCard({ label, value, icon, accent, sub }: { label: string; value: number; icon: "up" | "down" | "check" | "home"; accent: "teal" | "coral" | "blue" | "gold"; sub?: string }) {
  const accentMap: Record<string, { border: string; text: string; bg: string }> = {
    teal: { border: "border-l-teal-600", text: "text-teal-700 dark:text-teal-400", bg: "bg-teal-50 dark:bg-teal-950/30" },
    coral: { border: "border-l-coral-500", text: "text-coral-700 dark:text-coral-400", bg: "bg-coral-50 dark:bg-coral-950/30" },
    blue: { border: "border-l-blue-500", text: "text-blue-700 dark:text-blue-400", bg: "bg-blue-50 dark:bg-blue-950/30" },
    gold: { border: "border-l-amber-500", text: "text-amber-700 dark:text-amber-400", bg: "bg-amber-50 dark:bg-amber-950/30" }
  };
  const c = accentMap[accent];
  const paths: Record<string, ReactNode> = {
    up: <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.28m5.94 2.28-2.28 5.941" />,
    down: <path strokeLinecap="round" strokeLinejoin="round" d="M2.25 6 9 12.75l4.306-4.307a11.95 11.95 0 0 1 5.814 5.519l2.74 1.22m0 0-5.94 2.281m5.94-2.28-2.28 5.941" />,
    check: <path strokeLinecap="round" strokeLinejoin="round" d="M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM9 12.75 11.25 15 15 9.75" />,
    home: <path strokeLinecap="round" strokeLinejoin="round" d="M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.33l-7.5-5-7.5 5V21" />
  };
  return (
    <div className={`bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 border-l-4 ${c.border} shadow-sm p-5`}>
      <div className="flex justify-between items-start mb-3">
        <span className="text-[11px] font-bold text-stone-400 dark:text-stone-500 uppercase tracking-wider">{label}</span>
        <div className={`${c.bg} ${c.text} p-2 rounded-lg`}>
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={2.25} stroke="currentColor" className="w-4 h-4">{paths[icon]}</svg>
        </div>
      </div>
      <p className="text-2xl font-mono font-bold text-stone-850 dark:text-stone-100">₹{(value || 0).toLocaleString("en-IN")}</p>
      {sub && <p className="text-[11px] text-stone-450 dark:text-stone-500 font-medium mt-1.5">{sub}</p>}
    </div>
  );
}

function SectionCard({ title, desc, action, children }: { title: string; desc?: string; action?: React.ReactNode; children: React.ReactNode }) {
  return (
    <div className="bg-white dark:bg-stone-900 rounded-xl border border-stone-150 dark:border-stone-800 shadow-sm p-5 sm:p-6">
      <div className="flex flex-wrap justify-between items-start gap-3 mb-5">
        <div>
          <h2 className="text-base font-serif font-bold text-stone-850 dark:text-stone-100">{title}</h2>
          {desc && <p className="text-xs text-stone-450 dark:text-stone-550 mt-0.5">{desc}</p>}
        </div>
        {action}
      </div>
      {children}
    </div>
  );
}

function EmptyState({ text, sub }: { text: string; sub: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 bg-stone-50/60 dark:bg-stone-900/40 rounded-xl border border-dashed border-stone-200 dark:border-stone-800">
      <p className="text-sm text-stone-500 dark:text-stone-400 font-semibold">{text}</p>
      {sub && <p className="text-xs text-stone-400 dark:text-stone-500 mt-1 text-center px-6">{sub}</p>}
    </div>
  );
}

function CategoryPill({ category, isIncome }: { category: string; isIncome: boolean }) {
  const styles: Record<string, string> = {
    Food: "bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-400",
    Travel: "bg-amber-50 dark:bg-amber-950/40 text-amber-700 dark:text-amber-400",
    Shopping: "bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-400"
  };
  const style = isIncome ? "bg-teal-50 dark:bg-teal-950/40 text-teal-700 dark:text-teal-400" : (styles[category] || "bg-stone-100 dark:bg-stone-800 text-stone-700 dark:text-stone-350");
  return <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${style}`}>{category}</span>;
}

function SubPills({ options, active, onChange }: { options: { key: string; label: string }[]; active: string; onChange: (k: string) => void }) {
  return (
    <div className="flex flex-wrap gap-2">
      {options.map(o => (
        <button
          key={o.key}
          onClick={() => onChange(o.key)}
          className={`text-xs font-bold px-3.5 py-2 rounded-full border transition-all cursor-pointer ${active === o.key
            ? "bg-teal-700 border-teal-700 text-white"
            : "bg-white dark:bg-stone-900 border-stone-200 dark:border-stone-800 text-stone-500 dark:text-stone-400 hover:bg-stone-50 dark:hover:bg-stone-800"
            }`}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}

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
    <button type="submit" className="w-full bg-teal-700 hover:bg-teal-800 text-white font-bold py-3 rounded-lg transition-all text-sm mt-2 cursor-pointer">
      {children}
    </button>
  );
}

export default Dashboard;
