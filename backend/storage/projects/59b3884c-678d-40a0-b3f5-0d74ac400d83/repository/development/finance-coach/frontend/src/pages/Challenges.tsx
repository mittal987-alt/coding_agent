import React, { useState, useEffect } from "react";
import { useFinance } from "../context/FinanceContext";

const API = "http://127.0.0.1:8000";

const COLOR_MAP: Record<string, { bg: string; border: string; badge: string; progress: string; text: string }> = {
  teal: {
    bg: "bg-teal-50 dark:bg-teal-950/30",
    border: "border-teal-200 dark:border-teal-800",
    badge: "bg-teal-100 dark:bg-teal-900/60 text-teal-700 dark:text-teal-300",
    progress: "bg-gradient-to-r from-teal-500 to-teal-400",
    text: "text-teal-700 dark:text-teal-300",
  },
  violet: {
    bg: "bg-violet-50 dark:bg-violet-950/30",
    border: "border-violet-200 dark:border-violet-800",
    badge: "bg-violet-100 dark:bg-violet-900/60 text-violet-700 dark:text-violet-300",
    progress: "bg-gradient-to-r from-violet-500 to-violet-400",
    text: "text-violet-700 dark:text-violet-300",
  },
  amber: {
    bg: "bg-amber-50 dark:bg-amber-950/30",
    border: "border-amber-200 dark:border-amber-800",
    badge: "bg-amber-100 dark:bg-amber-900/60 text-amber-700 dark:text-amber-300",
    progress: "bg-gradient-to-r from-amber-500 to-amber-400",
    text: "text-amber-700 dark:text-amber-300",
  },
  coral: {
    bg: "bg-red-50 dark:bg-red-950/30",
    border: "border-red-200 dark:border-red-800",
    badge: "bg-red-100 dark:bg-red-900/60 text-red-700 dark:text-red-300",
    progress: "bg-gradient-to-r from-red-500 to-orange-400",
    text: "text-red-700 dark:text-red-300",
  },
};

const Challenges: React.FC = () => {
  const { userEmail, setShowAuthModal, setAuthMode } = useFinance();
  const [challenges, setChallenges] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [joiningType, setJoiningType] = useState<string | null>(null);
  const [leavingType, setLeavingType] = useState<string | null>(null);

  const token = () => localStorage.getItem("token");

  const load = async () => {
    if (!token()) { setLoading(false); return; }
    setLoading(true);
    try {
      const res = await fetch(`${API}/challenges/`, {
        headers: { Authorization: `Bearer ${token()}` },
      });
      if (res.ok) {
        const data = await res.json();
        setChallenges(data);
      }
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  useEffect(() => { load(); }, [userEmail]);

  const joinChallenge = async (type: string) => {
    if (!token()) { setAuthMode("login"); setShowAuthModal(true); return; }
    setJoiningType(type);
    try {
      const res = await fetch(`${API}/challenges/join`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token()}`, "Content-Type": "application/json" },
        body: JSON.stringify({ challenge_type: type }),
      });
      if (res.ok) await load();
    } catch (e) { console.error(e); }
    setJoiningType(null);
  };

  const leaveChallenge = async (type: string) => {
    if (!token()) return;
    setLeavingType(type);
    try {
      const res = await fetch(`${API}/challenges/${type}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token()}` },
      });
      if (res.ok) await load();
    } catch (e) { console.error(e); }
    setLeavingType(null);
  };

  if (!userEmail) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] gap-4">
        <span className="text-5xl">🏆</span>
        <p className="font-serif font-bold text-xl text-stone-700 dark:text-stone-300">Challenges await you</p>
        <p className="text-sm text-stone-500 dark:text-stone-400 text-center max-w-xs">Sign in to join gamified savings and spending challenges to build better financial habits.</p>
        <button
          onClick={() => { setAuthMode("login"); setShowAuthModal(true); }}
          className="bg-gradient-to-r from-teal-600 to-teal-500 text-white font-bold py-2.5 px-6 rounded-xl shadow-[0_0_15px_rgba(15,110,86,0.3)] hover:shadow-[0_0_20px_rgba(20,184,166,0.5)] transition-all duration-300 hover:-translate-y-0.5 cursor-pointer border-none"
        >
          Sign in
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6 mb-8">
      {/* Header */}
      <div className="mb-7">
        <h2 className="font-serif font-bold text-2xl text-stone-900 dark:text-stone-50">Savings Challenges</h2>
        <p className="text-xs text-stone-450 dark:text-stone-500 font-medium mt-0.5">Join structured challenges to build better financial habits</p>
      </div>

      {/* Stats bar */}
      {challenges.length > 0 && (
        <div className="grid grid-cols-3 gap-4 mb-2">
          <div className="bg-white dark:bg-stone-900/80 border border-stone-150 dark:border-stone-700/50 rounded-xl p-4 text-center shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300">
            <p className="text-2xl font-mono font-bold text-stone-800 dark:text-stone-100">
              {challenges.filter(c => c.joined).length}
            </p>
            <p className="text-[11px] font-bold text-stone-400 uppercase tracking-wider mt-1">Active</p>
          </div>
          <div className="bg-white dark:bg-stone-900/80 border border-stone-150 dark:border-stone-700/50 rounded-xl p-4 text-center shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300">
            <p className="text-2xl font-mono font-bold text-teal-600 dark:text-teal-400">
              {challenges.filter(c => c.is_complete).length}
            </p>
            <p className="text-[11px] font-bold text-stone-400 uppercase tracking-wider mt-1">Completed</p>
          </div>
          <div className="bg-white dark:bg-stone-900/80 border border-stone-150 dark:border-stone-700/50 rounded-xl p-4 text-center shadow-sm hover:shadow-md hover:-translate-y-0.5 transition-all duration-300">
            <p className="text-2xl font-mono font-bold text-amber-600 dark:text-amber-400">
              {challenges.filter(c => !c.joined).length}
            </p>
            <p className="text-[11px] font-bold text-stone-400 uppercase tracking-wider mt-1">Available</p>
          </div>
        </div>
      )}

      {/* Challenge Cards */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-10 h-10 border-2 border-stone-300 dark:border-stone-700 border-t-teal-600 rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {challenges.map((ch) => {
            const colors = COLOR_MAP[ch.color] || COLOR_MAP.teal;
            const isJoining = joiningType === ch.type;
            const isLeaving = leavingType === ch.type;

            return (
              <div
                key={ch.type}
                className={`relative bg-white dark:bg-stone-900/80 backdrop-blur-sm border ${colors.border} rounded-2xl p-6 shadow-sm hover:shadow-lg hover:-translate-y-0.5 transition-all duration-300 overflow-hidden ${ch.is_complete ? "ring-2 ring-teal-400 dark:ring-teal-600" : ""}`}
              >
                {/* Completion ribbon */}
                {ch.is_complete && (
                  <div className="absolute top-3 right-3 bg-teal-500 text-white text-[10px] font-black px-2 py-0.5 rounded-full">
                    ✓ Complete!
                  </div>
                )}

                {/* Icon + Title */}
                <div className="flex items-start gap-4 mb-4">
                  <div className={`w-12 h-12 rounded-xl ${colors.badge} flex items-center justify-center text-2xl shrink-0 shadow-sm`}>
                    {ch.icon}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="font-serif font-bold text-base text-stone-800 dark:text-stone-100 leading-tight">{ch.name}</h3>
                    <p className="text-xs text-stone-500 dark:text-stone-400 mt-1 leading-relaxed">{ch.description}</p>
                  </div>
                </div>

                {/* Progress (only when joined) */}
                {ch.joined && (
                  <div className="mb-4">
                    <div className="flex justify-between items-center mb-1.5">
                      <span className={`text-xs font-bold ${colors.text}`}>{ch.label}</span>
                      <span className="text-xs font-mono font-bold text-stone-500 dark:text-stone-400">{ch.pct}%</span>
                    </div>
                    <div className="bg-stone-100 dark:bg-stone-800 rounded-full h-2.5 overflow-hidden">
                      <div
                        className={`${colors.progress} h-full rounded-full transition-all duration-700`}
                        style={{ width: `${Math.min(ch.pct, 100)}%` }}
                      />
                    </div>
                    {ch.sub && <p className="text-[11px] text-stone-400 dark:text-stone-500 mt-1.5">{ch.sub}</p>}
                    {ch.started_at && (
                      <p className="text-[10px] text-stone-400 mt-1">Started {new Date(ch.started_at).toLocaleDateString("en-IN", { day: "numeric", month: "short", year: "numeric" })}</p>
                    )}
                  </div>
                )}

                {/* Actions */}
                <div className="flex gap-2 mt-2">
                  {!ch.joined ? (
                    <button
                      onClick={() => joinChallenge(ch.type)}
                      disabled={isJoining}
                      className={`flex-1 bg-gradient-to-r from-teal-600 to-teal-500 hover:from-teal-500 hover:to-teal-400 disabled:from-stone-400 disabled:to-stone-400 text-white font-bold text-sm py-2.5 rounded-xl transition-all duration-300 hover:-translate-y-0.5 shadow-[0_0_12px_rgba(15,110,86,0.25)] hover:shadow-[0_0_20px_rgba(20,184,166,0.4)] cursor-pointer border-none`}
                    >
                      {isJoining ? "Joining…" : "Join Challenge"}
                    </button>
                  ) : (
                    <>
                      <div className={`flex-1 text-center py-2.5 rounded-xl text-sm font-bold ${colors.badge}`}>
                        {ch.is_complete ? "🎉 Completed!" : "In Progress"}
                      </div>
                      <button
                        onClick={() => leaveChallenge(ch.type)}
                        disabled={isLeaving}
                        className="px-3 py-2.5 rounded-xl text-xs font-semibold text-stone-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-950/30 transition-all cursor-pointer bg-transparent border border-stone-200 dark:border-stone-700"
                      >
                        {isLeaving ? "…" : "Leave"}
                      </button>
                    </>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Tips */}
      <div className="bg-amber-50 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-800 rounded-xl p-4 mt-2">
        <p className="text-xs font-bold text-amber-800 dark:text-amber-300 mb-1">💡 How challenges work</p>
        <p className="text-xs text-amber-700 dark:text-amber-400 leading-relaxed">
          Progress is calculated in real-time from your actual transaction data. Keep adding transactions regularly to track your progress accurately. You can join multiple challenges at once!
        </p>
      </div>
    </div>
  );
};

export default Challenges;
