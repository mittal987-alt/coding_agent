import React, { createContext, useContext, useState, useEffect, useRef } from "react";
import { API_URL } from "../config";

interface FinanceContextType {
  data: any;
  setData: React.Dispatch<React.SetStateAction<any>>;
  transactions: any[];
  setTransactions: React.Dispatch<React.SetStateAction<any[]>>;
  file: File | null;
  setFile: React.Dispatch<React.SetStateAction<File | null>>;
  insights: any;
  setInsights: React.Dispatch<React.SetStateAction<any>>;
  userEmail: string | null;
  setUserEmail: React.Dispatch<React.SetStateAction<string | null>>;
  userName: string | null;
  setUserName: React.Dispatch<React.SetStateAction<string | null>>;

  // Auth Modals & Loading States
  showAuthModal: boolean;
  setShowAuthModal: React.Dispatch<React.SetStateAction<boolean>>;
  authMode: "login" | "signup";
  setAuthMode: React.Dispatch<React.SetStateAction<"login" | "signup">>;
  authName: string;
  setAuthName: React.Dispatch<React.SetStateAction<string>>;
  authEmail: string;
  setAuthEmail: React.Dispatch<React.SetStateAction<string>>;
  authPassword: string;
  setAuthPassword: React.Dispatch<React.SetStateAction<string>>;
  authError: string;
  setAuthError: React.Dispatch<React.SetStateAction<string>>;
  isUploading: boolean;
  setIsUploading: React.Dispatch<React.SetStateAction<boolean>>;
  isLoadingAuth: boolean;
  setIsLoadingAuth: React.Dispatch<React.SetStateAction<boolean>>;
  pdfPassword: string;
  setPdfPassword: React.Dispatch<React.SetStateAction<string>>;
  pdfPasswordMessage: string;
  setPdfPasswordMessage: React.Dispatch<React.SetStateAction<string>>;
  showPdfPasswordPrompt: boolean;
  setShowPdfPasswordPrompt: React.Dispatch<React.SetStateAction<boolean>>;

  // Budgets
  budgets: any[];
  setBudgets: React.Dispatch<React.SetStateAction<any[]>>;
  budgetCategory: string;
  setBudgetCategory: React.Dispatch<React.SetStateAction<string>>;
  budgetAmount: string;
  setBudgetAmount: React.Dispatch<React.SetStateAction<string>>;

  // AI Chatbot
  chatOpen: boolean;
  setChatOpen: React.Dispatch<React.SetStateAction<boolean>>;
  chatInput: string;
  setChatInput: React.Dispatch<React.SetStateAction<string>>;
  chatLoading: boolean;
  setChatLoading: React.Dispatch<React.SetStateAction<boolean>>;
  chatMessages: any[];
  setChatMessages: React.Dispatch<React.SetStateAction<any[]>>;

  // Transactions CRUD
  showTxModal: boolean;
  setShowTxModal: React.Dispatch<React.SetStateAction<boolean>>;
  showReceiptScanModal: boolean;
  setShowReceiptScanModal: React.Dispatch<React.SetStateAction<boolean>>;
  txModalMode: "add" | "edit";
  setTxModalMode: React.Dispatch<React.SetStateAction<"add" | "edit">>;
  selectedTxId: number | null;
  setSelectedTxId: React.Dispatch<React.SetStateAction<number | null>>;
  txDescription: string;
  setTxDescription: React.Dispatch<React.SetStateAction<string>>;
  txAmount: string;
  setTxAmount: React.Dispatch<React.SetStateAction<string>>;
  txCategory: string;
  setTxCategory: React.Dispatch<React.SetStateAction<string>>;
  txType: string;
  setTxType: React.Dispatch<React.SetStateAction<string>>;
  txDate: string;
  setTxDate: React.Dispatch<React.SetStateAction<string>>;
  txAccountId: string;
  setTxAccountId: React.Dispatch<React.SetStateAction<string>>;
  txCurrency: string;
  setTxCurrency: React.Dispatch<React.SetStateAction<string>>;
  txReceiptUrl: string | null;
  setTxReceiptUrl: React.Dispatch<React.SetStateAction<string | null>>;
  statementCurrency: string;
  setStatementCurrency: React.Dispatch<React.SetStateAction<string>>;
  supportedCurrencies: { code: string; name: string; symbol: string }[];

  // Custom categories
  categories: { id: number; name: string; color: string }[];
  loadCategories: () => Promise<void>;
  handleCategoryCreate: (name: string, color: string) => Promise<boolean>;
  handleCategoryUpdate: (id: number, name: string, color: string) => Promise<void>;
  handleCategoryDelete: (id: number) => Promise<void>;

  // Toasts & confirm dialog (replace browser alert()/confirm())
  toasts: { id: number; message: string; type: "success" | "error" | "info" }[];
  showToast: (message: string, type?: "success" | "error" | "info") => void;
  confirmState: { message: string } | null;
  confirmAction: (message: string) => Promise<boolean>;
  respondConfirm: (result: boolean) => void;

  // Transaction Filters
  filterSearch: string;
  setFilterSearch: React.Dispatch<React.SetStateAction<string>>;
  filterCategory: string;
  setFilterCategory: React.Dispatch<React.SetStateAction<string>>;
  filterType: string;
  setFilterType: React.Dispatch<React.SetStateAction<string>>;

  // Theme
  theme: "light" | "dark";
  setTheme: React.Dispatch<React.SetStateAction<"light" | "dark">>;

  // Data states
  trendsData: any[];
  goals: any[];
  subscriptions: any[];
  detectedSubs: any[];
  accounts: any[];
  splits: any[];
  healthScore: any;
  alertsData: any;
  showAlertsPanel: boolean;
  setShowAlertsPanel: React.Dispatch<React.SetStateAction<boolean>>;
  taxData: any;
  budgetPlan: any;
  applyingPlan: boolean;
  netWorth: any;
  reminders: any[];
  showReminderModal: boolean;
  setShowReminderModal: React.Dispatch<React.SetStateAction<boolean>>;
  reminderName: string;
  setReminderName: React.Dispatch<React.SetStateAction<string>>;
  reminderAmount: string;
  setReminderAmount: React.Dispatch<React.SetStateAction<string>>;
  reminderDueDate: string;
  setReminderDueDate: React.Dispatch<React.SetStateAction<string>>;
  reminderCategory: string;
  setReminderCategory: React.Dispatch<React.SetStateAction<string>>;
  reminderIsRecurring: boolean;
  setReminderIsRecurring: React.Dispatch<React.SetStateAction<boolean>>;
  reminderFrequency: string;
  setReminderFrequency: React.Dispatch<React.SetStateAction<string>>;
  autoCatResult: any;
  setAutoCatResult: React.Dispatch<React.SetStateAction<any>>;
  isAutoCatting: boolean;
  heatmapData: any;
  gamificationData: any;
  calendarMonth: Date;
  setCalendarMonth: React.Dispatch<React.SetStateAction<Date>>;

  // Accounts CRUD
  showAccountModal: boolean;
  setShowAccountModal: React.Dispatch<React.SetStateAction<boolean>>;
  accountModalMode: "add" | "edit";
  setAccountModalMode: React.Dispatch<React.SetStateAction<"add" | "edit">>;
  selectedAccountId: number | null;
  setSelectedAccountId: React.Dispatch<React.SetStateAction<number | null>>;
  accountName: string;
  setAccountName: React.Dispatch<React.SetStateAction<string>>;
  accountType: string;
  setAccountType: React.Dispatch<React.SetStateAction<string>>;
  accountBalance: string;
  setAccountBalance: React.Dispatch<React.SetStateAction<string>>;

  // Splits CRUD
  showSplitModal: boolean;
  setShowSplitModal: React.Dispatch<React.SetStateAction<boolean>>;
  splitDescription: string;
  setSplitDescription: React.Dispatch<React.SetStateAction<string>>;
  splitTotal: string;
  setSplitTotal: React.Dispatch<React.SetStateAction<string>>;
  splitFriend: string;
  setSplitFriend: React.Dispatch<React.SetStateAction<string>>;
  splitOwed: string;
  setSplitOwed: React.Dispatch<React.SetStateAction<string>>;

  // Savings Goals CRUD
  showGoalModal: boolean;
  setShowGoalModal: React.Dispatch<React.SetStateAction<boolean>>;
  goalModalMode: "add" | "edit";
  setGoalModalMode: React.Dispatch<React.SetStateAction<"add" | "edit">>;
  selectedGoalId: number | null;
  setSelectedGoalId: React.Dispatch<React.SetStateAction<number | null>>;
  goalName: string;
  setGoalName: React.Dispatch<React.SetStateAction<string>>;
  goalTargetAmount: string;
  setGoalTargetAmount: React.Dispatch<React.SetStateAction<string>>;
  goalCurrentAmount: string;
  setGoalCurrentAmount: React.Dispatch<React.SetStateAction<string>>;
  goalTargetDate: string;
  setGoalTargetDate: React.Dispatch<React.SetStateAction<string>>;

  // Subscriptions CRUD
  showSubModal: boolean;
  setShowSubModal: React.Dispatch<React.SetStateAction<boolean>>;
  subModalMode: "add" | "edit";
  setSubModalMode: React.Dispatch<React.SetStateAction<"add" | "edit">>;
  selectedSubId: number | null;
  setSelectedSubId: React.Dispatch<React.SetStateAction<number | null>>;
  subName: string;
  setSubName: React.Dispatch<React.SetStateAction<string>>;
  subAmount: string;
  setSubAmount: React.Dispatch<React.SetStateAction<string>>;
  subCategory: string;
  setSubCategory: React.Dispatch<React.SetStateAction<string>>;
  subBillingCycle: string;
  setSubBillingCycle: React.Dispatch<React.SetStateAction<string>>;
  subNextDueDate: string;
  setSubNextDueDate: React.Dispatch<React.SetStateAction<string>>;

  // Common Action Handlers
  loadData: () => Promise<void>;
  checkUserProfile: () => Promise<void>;
  uploadStatement: () => Promise<void>;
  handleAuthSubmit: (e: React.FormEvent) => Promise<void>;
  handleLogout: () => void;
  handleReminderSubmit: (e: React.FormEvent) => Promise<void>;
  handleReminderPay: (id: number) => Promise<void>;
  handleReminderDelete: (id: number) => Promise<void>;
  handleReminderSnooze: (id: number, days: number) => Promise<void>;
  handleAutoCategorize: () => Promise<void>;
  handleApplyBudgetPlan: () => Promise<void>;
  handleGoalSubmit: (e: React.FormEvent) => Promise<void>;
  handleGoalDelete: (goalId: number) => Promise<void>;
  openEditGoalModal: (g: any) => void;
  handleSubSubmit: (e: React.FormEvent) => Promise<void>;
  handleSubDelete: (subId: number) => Promise<void>;
  openEditSubModal: (s: any) => void;
  acceptDetectedSub: (detected: any) => Promise<void>;
  handleAccountSubmit: (e: React.FormEvent) => Promise<void>;
  handleAccountDelete: (id: number) => Promise<void>;
  openEditAccountModal: (a: any) => void;
  handleSplitSubmit: (e: React.FormEvent) => Promise<void>;
  handleSplitSettle: (id: number) => Promise<void>;
  handleSplitDelete: (id: number) => Promise<void>;
  handleCSVExport: () => void;
  handleBudgetSubmit: (e: React.FormEvent) => Promise<void>;
  handleBudgetDelete: (budgetId: number) => Promise<void>;
  sendChatMessage: (e: React.FormEvent) => Promise<void>;
  handleTxSubmit: (e: React.FormEvent) => Promise<void>;
  handleTxDelete: (txId: number) => Promise<void>;
  handleBulkDelete: (ids: number[]) => Promise<void>;
  handleBulkRecategorize: (ids: number[], category: string) => Promise<void>;
  scanReceipt: (file: File) => Promise<void>;
  isScanningReceipt: boolean;
  openEditTxModal: (tx: any) => void;
  filteredTransactions: any[];
}

const FinanceContext = createContext<FinanceContextType | undefined>(undefined);

export const FinanceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [data, setData] = useState<any>(null);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [file, setFile] = useState<File | null>(null);
  const [insights, setInsights] = useState<any>(null);
  const [userEmail, setUserEmail] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);

  // Authentication UI Modal State
  const [showAuthModal, setShowAuthModal] = useState<boolean>(false);
  const [authMode, setAuthMode] = useState<"login" | "signup">("login");
  const [authName, setAuthName] = useState<string>("");
  const [authEmail, setAuthEmail] = useState<string>("");
  const [authPassword, setAuthPassword] = useState<string>("");
  const [authError, setAuthError] = useState<string>("");
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isLoadingAuth, setIsLoadingAuth] = useState<boolean>(false);
  const [pdfPassword, setPdfPassword] = useState<string>("");
  const [pdfPasswordMessage, setPdfPasswordMessage] = useState<string>("");
  const [showPdfPasswordPrompt, setShowPdfPasswordPrompt] = useState<boolean>(false);

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
  const [showReceiptScanModal, setShowReceiptScanModal] = useState(false);
  const [txModalMode, setTxModalMode] = useState<"add" | "edit">("add");
  const [selectedTxId, setSelectedTxId] = useState<number | null>(null);
  const [txDescription, setTxDescription] = useState("");
  const [txAmount, setTxAmount] = useState("");
  const [txCategory, setTxCategory] = useState("Shopping");
  const [txType, setTxType] = useState("expense");
  const [txDate, setTxDate] = useState(new Date().toISOString().split("T")[0]);
  const [txAccountId, setTxAccountId] = useState("");
  const [txCurrency, setTxCurrency] = useState("INR");
  const [txReceiptUrl, setTxReceiptUrl] = useState<string | null>(null);
  const [isScanningReceipt, setIsScanningReceipt] = useState(false);
  const [statementCurrency, setStatementCurrency] = useState("INR");
  const [categories, setCategories] = useState<{ id: number; name: string; color: string }[]>([]);
  const [supportedCurrencies, setSupportedCurrencies] = useState<{ code: string; name: string; symbol: string }[]>([
    { code: "INR", name: "Indian Rupee", symbol: "₹" }
  ]);

  // Toasts & confirm dialog state
  const [toasts, setToasts] = useState<{ id: number; message: string; type: "success" | "error" | "info" }[]>([]);
  const toastIdRef = useRef(0);
  const showToast = (message: string, type: "success" | "error" | "info" = "success") => {
    const id = ++toastIdRef.current;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000);
  };

  const [confirmState, setConfirmState] = useState<{ message: string } | null>(null);
  const confirmResolverRef = useRef<((result: boolean) => void) | null>(null);
  const confirmAction = (message: string): Promise<boolean> => {
    setConfirmState({ message });
    return new Promise<boolean>(resolve => {
      confirmResolverRef.current = resolve;
    });
  };
  const respondConfirm = (result: boolean) => {
    setConfirmState(null);
    if (confirmResolverRef.current) {
      confirmResolverRef.current(result);
      confirmResolverRef.current = null;
    }
  };

  // Transaction Filters state
  const [filterSearch, setFilterSearch] = useState("");
  const [filterCategory, setFilterCategory] = useState("All");
  const [filterType, setFilterType] = useState("All");

  // Theme state
  const [theme, setTheme] = useState<"light" | "dark">("dark");

  // States
  const [trendsData, setTrendsData] = useState<any[]>([]);
  const [goals, setGoals] = useState<any[]>([]);
  const [subscriptions, setSubscriptions] = useState<any[]>([]);
  const [detectedSubs, setDetectedSubs] = useState<any[]>([]);
  const [accounts, setAccounts] = useState<any[]>([]);
  const [splits, setSplits] = useState<any[]>([]);
  const [healthScore, setHealthScore] = useState<any>(null);
  const [alertsData, setAlertsData] = useState<any>(null);
  const [showAlertsPanel, setShowAlertsPanel] = useState(false);
  const [taxData, setTaxData] = useState<any>(null);
  const [budgetPlan, setBudgetPlan] = useState<any>(null);
  const [applyingPlan, setApplyingPlan] = useState(false);
  const [netWorth, setNetWorth] = useState<any>(null);
  const [reminders, setReminders] = useState<any[]>([]);
  const [showReminderModal, setShowReminderModal] = useState(false);
  const [reminderName, setReminderName] = useState("");
  const [reminderAmount, setReminderAmount] = useState("");
  const [reminderDueDate, setReminderDueDate] = useState(new Date().toISOString().split("T")[0]);
  const [reminderCategory, setReminderCategory] = useState("Others");
  const [reminderIsRecurring, setReminderIsRecurring] = useState(false);
  const [reminderFrequency, setReminderFrequency] = useState("monthly"); // "daily" | "weekly" | "monthly" | "yearly"
  const [autoCatResult, setAutoCatResult] = useState<any>(null);
  const [isAutoCatting, setIsAutoCatting] = useState(false);
  const [heatmapData, setHeatmapData] = useState<any>(null);
  const [gamificationData, setGamificationData] = useState<any>(null);
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

  // Subscriptions Modals and Forms
  const [showSubModal, setShowSubModal] = useState(false);
  const [subModalMode, setSubModalMode] = useState<"add" | "edit">("add");
  const [selectedSubId, setSelectedSubId] = useState<number | null>(null);
  const [subName, setSubName] = useState("");
  const [subAmount, setSubAmount] = useState("");
  const [subCategory, setSubCategory] = useState("Others");
  const [subBillingCycle, setSubBillingCycle] = useState("Monthly");
  const [subNextDueDate, setSubNextDueDate] = useState(new Date().toISOString().split("T")[0]);

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
      setAlertsData(null);
      setTaxData(null);
      setBudgetPlan(null);
      setNetWorth(null);
      setReminders([]);
      setHeatmapData(null);
      setGamificationData(null);
      return;
    }

    const headers: HeadersInit = {
      Authorization: `Bearer ${token}`
    };

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
        setAlertsData(null);
        setTaxData(null);
        setBudgetPlan(null);
        setNetWorth(null);
        setReminders([]);
        setHeatmapData(null);
        setGamificationData(null);
        return;
      }

      const txRes = await fetch(`${API_URL}/transactions`, { headers });
      if (txRes.ok) {
        const txData = await txRes.json();
        setTransactions(txData);
      } else {
        setTransactions([]);
      }

      const insightsRes = await fetch(`${API_URL}/insights`, { headers });
      if (insightsRes.ok) {
        const insightsData = await insightsRes.json();
        setInsights(insightsData);
      } else {
        setInsights({ food: 0, travel: 0, shopping: 0, insights: [] });
      }

      const budgetsRes = await fetch(`${API_URL}/budgets`, { headers });
      if (budgetsRes.ok) {
        const budgetsData = await budgetsRes.json();
        setBudgets(budgetsData);
      } else {
        setBudgets([]);
      }

      const trendsRes = await fetch(`${API_URL}/analytics/trends`, { headers });
      if (trendsRes.ok) {
        const trends = await trendsRes.json();
        setTrendsData(trends);
      } else {
        setTrendsData([]);
      }

      const goalsRes = await fetch(`${API_URL}/goals`, { headers });
      if (goalsRes.ok) {
        const goalsData = await goalsRes.json();
        setGoals(goalsData);
      } else {
        setGoals([]);
      }

      const subsRes = await fetch(`${API_URL}/subscriptions`, { headers });
      if (subsRes.ok) {
        const subsData = await subsRes.json();
        setSubscriptions(subsData);
      } else {
        setSubscriptions([]);
      }

      const detectRes = await fetch(`${API_URL}/subscriptions/detect`, { headers });
      if (detectRes.ok) {
        const detectData = await detectRes.json();
        setDetectedSubs(detectData);
      } else {
        setDetectedSubs([]);
      }

      const accountsRes = await fetch(`${API_URL}/accounts/`, { headers });
      if (accountsRes.ok) {
        setAccounts(await accountsRes.json());
      } else {
        setAccounts([]);
      }

      const splitsRes = await fetch(`${API_URL}/splits/`, { headers });
      if (splitsRes.ok) {
        setSplits(await splitsRes.json());
      } else {
        setSplits([]);
      }

      const healthRes = await fetch(`${API_URL}/analytics/health-score`, { headers });
      if (healthRes.ok) {
        setHealthScore(await healthRes.json());
      } else {
        setHealthScore(null);
      }

      const alertsRes = await fetch(`${API_URL}/alerts`, { headers });
      if (alertsRes.ok) setAlertsData(await alertsRes.json());

      const taxRes = await fetch(`${API_URL}/tax/estimate`, { headers });
      if (taxRes.ok) setTaxData(await taxRes.json());

      const planRes = await fetch(`${API_URL}/budget/plan`, { headers });
      if (planRes.ok) setBudgetPlan(await planRes.json());

      const nwRes = await fetch(`${API_URL}/networth`, { headers });
      if (nwRes.ok) setNetWorth(await nwRes.json());

      const remRes = await fetch(`${API_URL}/reminders`, { headers });
      if (remRes.ok) setReminders(await remRes.json());
      else setReminders([]);

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
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      if (response.ok) {
        const result = await response.json();
        setUserEmail(result.email);
        setUserName(result.name || null);
      } else {
        localStorage.removeItem("token");
        setUserEmail(null);
        setUserName(null);
      }
    } catch (error) {
      console.error("Error fetching profile:", error);
    }
  };

  useEffect(() => {
    loadData();
    checkUserProfile();
    const savedTheme = localStorage.getItem("theme") as "light" | "dark" | null;
    if (savedTheme) {
      setTheme(savedTheme);
    }
    fetch(`${API_URL}/currency/supported`)
      .then(res => res.ok ? res.json() : null)
      .then(data => { if (data) setSupportedCurrencies(data); })
      .catch(err => console.error("Failed to load supported currencies:", err));
    loadCategories();
  }, []);

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  const uploadStatement = async (enforcedPassword?: string) => {
    if (!file) {
      showToast("Please select a PDF file", "error");
      return;
    }

    const token = localStorage.getItem("token");
    if (!token) {
      showToast("Please log in first to upload a statement.", "error");
      setAuthMode("login");
      setShowAuthModal(true);
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("currency", statementCurrency);
    const passwordToSubmit = enforcedPassword || pdfPassword;
    if (passwordToSubmit) {
      formData.append("password", passwordToSubmit);
    }
    setIsUploading(true);

    try {
      const response = await fetch(
        `${API_URL}/upload-statement`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`
          },
          body: formData,
        }
      );

      const result = await response.json();
      setIsUploading(false);

      if (result.success) {
        showToast(`Statement uploaded successfully! Saved ${result.transactions_saved} transactions.`, "success");
        setFile(null);
        setPdfPassword("");
        setShowPdfPasswordPrompt(false);
        setPdfPasswordMessage("");
        const fileInput = document.getElementById("file-upload-input") as HTMLInputElement;
        if (fileInput) fileInput.value = "";
        loadData();
      } else {
        const needsPassword =
          result.requires_password === true ||
          result.requires_password === "true" ||
          result.password_required === true ||
          (typeof result.message === "string" && result.message.toLowerCase().includes("password")) ||
          (typeof result.detail === "string" && result.detail.toLowerCase().includes("password"));

        if (needsPassword) {
          setPdfPasswordMessage(result.message || result.detail || "This PDF is password protected. Enter the file password:");
          setShowPdfPasswordPrompt(true);
          return;
        }

        setShowPdfPasswordPrompt(false);
        setPdfPasswordMessage("");
        showToast(result.message || result.detail || "Statement parsing/upload failed.", "error");
      }
    } catch (error) {
      console.error(error);
      setIsUploading(false);
      showToast("Upload failed. Make sure the backend server is running.", "error");
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
          body: JSON.stringify({ name: authName, email: authEmail, password: authPassword }),
        });
        const data = await response.json();

        if (response.ok) {
          setAuthMode("login");
          showToast("Account created successfully! Please log in.", "success");
        } else {
          setAuthError(data.detail || "Signup failed");
        }
      } else {
        const response = await fetch(`${API_URL}/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email: authEmail, password: authPassword }),
        });
        const data = await response.json();

        if (response.ok) {
          localStorage.setItem("token", data.access_token);
          setUserEmail(authEmail);
          setShowAuthModal(false);
          setAuthPassword("");
          setAuthName("");
          showToast("Logged in successfully!", "success");
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
    setUserName(null);
    showToast("Logged out successfully.", "info");
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
        body: JSON.stringify({
          name: reminderName,
          amount: parseFloat(reminderAmount),
          due_date: reminderDueDate,
          category: reminderCategory,
          is_recurring: reminderIsRecurring,
          recurrence_frequency: reminderIsRecurring ? reminderFrequency : null,
        })
      });
      if (res.ok) {
        setShowReminderModal(false);
        setReminderName(""); setReminderAmount(""); setReminderCategory("Others");
        setReminderIsRecurring(false); setReminderFrequency("monthly");
        loadData();
      }
    } catch (err) { console.error(err); }
  };

  const handleReminderPay = async (id: number) => {
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/reminders/${id}/pay`, {
        method: "PUT",
        headers: { Authorization: token ? `Bearer ${token}` : "" }
      });
      loadData();
    } catch (err) { console.error(err); }
  };

  const handleReminderDelete = async (id: number) => {
    if (!(await confirmAction("Delete this reminder?"))) return;
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/reminders/${id}`, {
        method: "DELETE",
        headers: { Authorization: token ? `Bearer ${token}` : "" }
      });
      loadData();
    } catch (err) { console.error(err); }
  };

  const handleReminderSnooze = async (id: number, days: number) => {
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/reminders/${id}/snooze/${days}`, {
        method: "PUT",
        headers: { Authorization: token ? `Bearer ${token}` : "" }
      });
      loadData();
    } catch (err) { console.error(err); }
  };

  const handleAutoCategorize = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    setIsAutoCatting(true);
    try {
      const res = await fetch(`${API_URL}/transactions/auto-categorize`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      const result = await res.json();
      setAutoCatResult(result);
      loadData();
    } catch (err) { console.error(err); }
    finally { setIsAutoCatting(false); }
  };

  const handleApplyBudgetPlan = async () => {
    if (!budgetPlan || !budgetPlan.plan) return;
    const token = localStorage.getItem("token");
    if (!(await confirmAction(`Apply suggested budgets for ${budgetPlan.plan.length} categories? This will create new budget entries.`))) return;
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
      showToast("Budget plan applied successfully!", "success");
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
    const url = goalModalMode === "add"
      ? `${API_URL}/goals`
      : `${API_URL}/goals/${selectedGoalId}`;
    const method = goalModalMode === "add" ? "POST" : "PUT";

    try {
      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : ""
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setShowGoalModal(false);
        setGoalName("");
        setGoalTargetAmount("");
        setGoalCurrentAmount("0");
        setGoalTargetDate(new Date().toISOString().split("T")[0]);
        loadData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleGoalDelete = async (goalId: number) => {
    if (!(await confirmAction("Are you sure you want to delete this savings goal?"))) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/goals/${goalId}`, {
        method: "DELETE",
        headers: {
          Authorization: token ? `Bearer ${token}` : ""
        }
      });
      if (res.ok) {
        loadData();
      }
    } catch (err) {
      console.error(err);
    }
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
    const payload = {
      name: subName,
      amount: parseFloat(subAmount),
      category: subCategory,
      billing_cycle: subBillingCycle,
      next_due_date: subNextDueDate
    };
    const url = subModalMode === "add"
      ? `${API_URL}/subscriptions`
      : `${API_URL}/subscriptions/${selectedSubId}`;
    const method = subModalMode === "add" ? "POST" : "PUT";

    try {
      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : ""
        },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        setShowSubModal(false);
        setSubName("");
        setSubAmount("");
        setSubCategory("Others");
        setSubBillingCycle("Monthly");
        setSubNextDueDate(new Date().toISOString().split("T")[0]);
        loadData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSubDelete = async (subId: number) => {
    if (!(await confirmAction("Are you sure you want to remove this subscription?"))) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/subscriptions/${subId}`, {
        method: "DELETE",
        headers: {
          Authorization: token ? `Bearer ${token}` : ""
        }
      });
      if (res.ok) {
        loadData();
      }
    } catch (err) {
      console.error(err);
    }
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
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : ""
        },
        body: JSON.stringify(detected)
      });
      if (res.ok) {
        showToast(`${detected.name} added to subscriptions successfully!`, "success");
        loadData();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleAccountSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!accountName) return;
    const token = localStorage.getItem("token");
    const payload = { name: accountName, account_type: accountType, balance: parseFloat(accountBalance || "0") };
    const url = accountModalMode === "add"
      ? `${API_URL}/accounts/`
      : `${API_URL}/accounts/${selectedAccountId}`;
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
    if (!(await confirmAction("Delete this account?"))) return;
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/accounts/${id}`, {
        method: "DELETE",
        headers: { Authorization: token ? `Bearer ${token}` : "" }
      });
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
    const payload = {
      description: splitDescription,
      total_amount: parseFloat(splitTotal),
      friend_name: splitFriend,
      amount_owed: parseFloat(splitOwed)
    };
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
      await fetch(`${API_URL}/splits/${id}/settle`, {
        method: "PUT",
        headers: { Authorization: token ? `Bearer ${token}` : "" }
      });
      loadData();
    } catch (err) { console.error(err); }
  };

  const handleSplitDelete = async (id: number) => {
    if (!(await confirmAction("Delete this split record?"))) return;
    const token = localStorage.getItem("token");
    try {
      await fetch(`${API_URL}/splits/${id}`, {
        method: "DELETE",
        headers: { Authorization: token ? `Bearer ${token}` : "" }
      });
      loadData();
    } catch (err) { console.error(err); }
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

  const handleBudgetSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!budgetAmount || parseFloat(budgetAmount) <= 0) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/budgets`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : ""
        },
        body: JSON.stringify({ category: budgetCategory, amount: parseFloat(budgetAmount) })
      });
      if (res.ok) {
        showToast("Budget target saved successfully!", "success");
        setBudgetAmount("");
        loadData();
      }
    } catch (err) {
      console.error("Error setting budget:", err);
    }
  };

  const handleBudgetDelete = async (budgetId: number) => {
    if (!(await confirmAction("Are you sure you want to delete this budget target?"))) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/budgets/${budgetId}`, {
        method: "DELETE",
        headers: {
          Authorization: token ? `Bearer ${token}` : ""
        }
      });
      if (res.ok) {
        loadData();
      }
    } catch (err) {
      console.error("Error deleting budget:", err);
    }
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
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : ""
        },
        body: JSON.stringify({ message: userMsg })
      });
      const data = await res.json();
      setChatMessages(prev => [...prev, { sender: "ai", text: data.response }]);
    } catch (err) {
      console.error(err);
      setChatMessages(prev => [...prev, { sender: "ai", text: "Sorry, I encountered an issue connecting to the AI Coach." }]);
    } finally {
      setChatLoading(false);
    }
  };

  const scanReceipt = async (file: File) => {
    const token = localStorage.getItem("token");
    if (!token) {
      showToast("Please log in first to scan a receipt.", "error");
      setAuthMode("login");
      setShowAuthModal(true);
      return;
    }
    setIsScanningReceipt(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_URL}/receipts/scan`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      const result = await res.json();
      if (result.success) {
        // Also upload the image for storage
        try {
          const storeRes = await fetch(`${API_URL}/receipts/store`, {
            method: "POST",
            headers: { Authorization: `Bearer ${token}` },
            body: formData,
          });
          if (storeRes.ok) {
            const storeResult = await storeRes.json();
            setTxReceiptUrl(storeResult.url);
          }
        } catch (e) {
          console.error("Failed to store receipt image", e);
        }

        setTxModalMode("add");
        setTxDescription(result.description || "");
        setTxAmount(result.amount ? String(result.amount) : "");
        setTxDate(result.transaction_date || new Date().toISOString().split("T")[0]);
        setTxCategory(result.category || "Others");
        setTxType("expense");
        setTxAccountId("");
        setTxCurrency("INR");
        setShowTxModal(true);
        showToast("Receipt scanned — review the details before saving.", "info");
      } else {
        showToast(result.message || "Couldn't read that receipt.", "error");
      }
    } catch (err) {
      console.error(err);
      showToast("Receipt scan failed. Make sure the backend server is running.", "error");
    } finally {
      setIsScanningReceipt(false);
    }
  };

  const handleTxSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!txDescription || !txAmount) return;

    const payload = {
      description: txDescription,
      amount: parseFloat(txAmount),
      category: txCategory,
      transaction_type: txType,
      transaction_date: txDate,
      account_id: txAccountId ? parseInt(txAccountId) : null,
      currency: txCurrency,
      receipt_image_url: txReceiptUrl,
    };

    const token = localStorage.getItem("token");
    const url = txModalMode === "add"
      ? `${API_URL}/transactions`
      : `${API_URL}/transactions/${selectedTxId}`;
    const method = txModalMode === "add" ? "POST" : "PUT";

    try {
      const res = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: token ? `Bearer ${token}` : ""
        },
        body: JSON.stringify(payload)
      });

      if (res.ok) {
        showToast(`Transaction ${txModalMode === "add" ? "added" : "updated"} successfully!`, "success");
        setShowTxModal(false);
        setTxDescription("");
        setTxAmount("");
        setTxCategory("Shopping");
        setTxType("expense");
        setTxDate(new Date().toISOString().split("T")[0]);
        setTxAccountId("");
        setTxCurrency("INR");
        setTxReceiptUrl(null);
        loadData();
      }
    } catch (err) {
      console.error("Error submitting transaction:", err);
    }
  };

  const handleTxDelete = async (txId: number) => {
    if (!(await confirmAction("Are you sure you want to delete this transaction record?"))) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/transactions/${txId}`, {
        method: "DELETE",
        headers: {
          Authorization: token ? `Bearer ${token}` : ""
        }
      });
      if (res.ok) {
        loadData();
      }
    } catch (err) {
      console.error("Error deleting transaction:", err);
    }
  };

  const handleBulkDelete = async (ids: number[]) => {
    if (ids.length === 0) return;
    if (!(await confirmAction(`Delete ${ids.length} selected transaction${ids.length === 1 ? "" : "s"}? This can't be undone.`))) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/transactions/bulk`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify({ ids })
      });
      if (res.ok) {
        const data = await res.json();
        showToast(`Deleted ${data.deleted} transaction${data.deleted === 1 ? "" : "s"}.`, "success");
        loadData();
      } else {
        showToast("Failed to delete selected transactions.", "error");
      }
    } catch (err) {
      console.error("Error bulk-deleting transactions:", err);
    }
  };

  const handleBulkRecategorize = async (ids: number[], category: string) => {
    if (ids.length === 0) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/transactions/bulk/category`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify({ ids, category })
      });
      if (res.ok) {
        const data = await res.json();
        showToast(`Recategorized ${data.updated} transaction${data.updated === 1 ? "" : "s"} to "${category}".`, "success");
        loadData();
      } else {
        showToast("Failed to recategorize selected transactions.", "error");
      }
    } catch (err) {
      console.error("Error bulk-recategorizing transactions:", err);
    }
  };

  const openEditTxModal = (tx: any) => {
    setSelectedTxId(tx.id);
    setTxDescription(tx.description);
    setTxAmount(tx.amount.toString());
    setTxCategory(tx.category);
    setTxType(tx.transaction_type);
    setTxDate(tx.transaction_date);
    setTxAccountId(tx.account_id ? String(tx.account_id) : "");
    setTxCurrency(tx.currency || "INR");
    setTxReceiptUrl(tx.receipt_image_url || null);
    setTxModalMode("edit");
    setShowTxModal(true);
  };

  const loadCategories = async () => {
    const token = localStorage.getItem("token");
    if (!token) return;
    try {
      const res = await fetch(`${API_URL}/categories`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) setCategories(await res.json());
    } catch (err) { console.error(err); }
  };

  const handleCategoryCreate = async (name: string, color: string): Promise<boolean> => {
    if (!name.trim()) return false;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/categories`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify({ name: name.trim(), color })
      });
      if (res.ok) {
        showToast(`Category "${name.trim()}" added.`, "success");
        loadCategories();
        return true;
      } else {
        const data = await res.json().catch(() => ({}));
        showToast(data.detail || "Failed to add category.", "error");
        return false;
      }
    } catch (err) {
      console.error(err);
      return false;
    }
  };

  const handleCategoryUpdate = async (id: number, name: string, color: string) => {
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/categories/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: token ? `Bearer ${token}` : "" },
        body: JSON.stringify({ name, color })
      });
      if (res.ok) {
        showToast("Category updated.", "success");
        loadCategories();
      }
    } catch (err) { console.error(err); }
  };

  const handleCategoryDelete = async (id: number) => {
    if (!(await confirmAction("Delete this category? Existing entries already using it will keep their label."))) return;
    const token = localStorage.getItem("token");
    try {
      const res = await fetch(`${API_URL}/categories/${id}`, {
        method: "DELETE",
        headers: { Authorization: token ? `Bearer ${token}` : "" }
      });
      if (res.ok) {
        showToast("Category deleted.", "info");
        loadCategories();
      }
    } catch (err) { console.error(err); }
  };

  const filteredTransactions = transactions.filter(t => {
    const matchSearch = t.description.toLowerCase().includes(filterSearch.toLowerCase());
    const matchCategory = filterCategory === "All" || t.category === filterCategory;
    const matchType = filterType === "All" || t.transaction_type === filterType;
    return matchSearch && matchCategory && matchType;
  });

  return (
    <FinanceContext.Provider
      value={{
        data,
        setData,
        transactions,
        setTransactions,
        file,
        setFile,
        insights,
        setInsights,
        userEmail,
        setUserEmail,
        userName,
        setUserName,
        showAuthModal,
        setShowAuthModal,
        authMode,
        setAuthMode,
        authName,
        setAuthName,
        authEmail,
        setAuthEmail,
        authPassword,
        setAuthPassword,
        authError,
        setAuthError,
        isUploading,
        setIsUploading,
        isLoadingAuth,
        setIsLoadingAuth,
        budgets,
        setBudgets,
        budgetCategory,
        setBudgetCategory,
        budgetAmount,
        setBudgetAmount,
        chatOpen,
        setChatOpen,
        chatInput,
        setChatInput,
        chatLoading,
        setChatLoading,
        chatMessages,
        setChatMessages,
        showTxModal,
        setShowTxModal,
        txModalMode,
        setTxModalMode,
        selectedTxId,
        setSelectedTxId,
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
        txReceiptUrl,
        setTxReceiptUrl,
        statementCurrency,
        setStatementCurrency,
        supportedCurrencies,
        categories,
        loadCategories,
        handleCategoryCreate,
        handleCategoryUpdate,
        handleCategoryDelete,
        toasts,
        showToast,
        confirmState,
        confirmAction,
        respondConfirm,
        filterSearch,
        setFilterSearch,
        filterCategory,
        setFilterCategory,
        filterType,
        setFilterType,
        theme,
        setTheme,
        trendsData,
        goals,
        subscriptions,
        detectedSubs,
        accounts,
        splits,
        healthScore,
        alertsData,
        showAlertsPanel,
        setShowAlertsPanel,
        taxData,
        budgetPlan,
        applyingPlan,
        netWorth,
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
        autoCatResult,
        setAutoCatResult,
        isAutoCatting,
        heatmapData,
        gamificationData,
        calendarMonth,
        setCalendarMonth,
        showAccountModal,
        setShowAccountModal,
        accountModalMode,
        setAccountModalMode,
        selectedAccountId,
        setSelectedAccountId,
        accountName,
        setAccountName,
        accountType,
        setAccountType,
        accountBalance,
        setAccountBalance,
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
        showGoalModal,
        setShowGoalModal,
        goalModalMode,
        setGoalModalMode,
        selectedGoalId,
        setSelectedGoalId,
        goalName,
        setGoalName,
        goalTargetAmount,
        setGoalTargetAmount,
        goalCurrentAmount,
        setGoalCurrentAmount,
        goalTargetDate,
        setGoalTargetDate,
        showSubModal,
        setShowSubModal,
        subModalMode,
        setSubModalMode,
        selectedSubId,
        setSelectedSubId,
        subName,
        setSubName,
        subAmount,
        setSubAmount,
        pdfPassword,
        setPdfPassword,
        pdfPasswordMessage,
        setPdfPasswordMessage,
        showPdfPasswordPrompt,
        setShowPdfPasswordPrompt,
        subCategory,
        setSubCategory,
        subBillingCycle,
        setSubBillingCycle,
        subNextDueDate,
        setSubNextDueDate,
        loadData,
        checkUserProfile,
        uploadStatement,
        handleAuthSubmit,
        handleLogout,
        handleReminderSubmit,
        handleReminderPay,
        handleReminderDelete,
        handleReminderSnooze,
        handleAutoCategorize,
        handleApplyBudgetPlan,
        handleGoalSubmit,
        handleGoalDelete,
        openEditGoalModal,
        handleSubSubmit,
        handleSubDelete,
        openEditSubModal,
        acceptDetectedSub,
        handleAccountSubmit,
        handleAccountDelete,
        openEditAccountModal,
        handleSplitSubmit,
        handleSplitSettle,
        handleSplitDelete,
        handleCSVExport,
        handleBudgetSubmit,
        handleBudgetDelete,
        sendChatMessage,
        handleTxSubmit,
        handleTxDelete,
        handleBulkDelete,
        handleBulkRecategorize,
        scanReceipt,
        isScanningReceipt,
        openEditTxModal,
        filteredTransactions,
        showReceiptScanModal,
        setShowReceiptScanModal
      }}
    >
      {children}
    </FinanceContext.Provider>
  );
};

export const useFinance = () => {
  const context = useContext(FinanceContext);
  if (!context) {
    throw new Error("useFinance must be used within a FinanceProvider");
  }
  return context;
};
