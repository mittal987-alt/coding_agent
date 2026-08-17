"use client";

import React, { useEffect, useState, useCallback } from "react";
import {
  Activity, GitCommit, FileCode, CheckCircle, X,
  BarChart3, Clock, Users, RefreshCw, AlertCircle, TrendingUp,
} from "lucide-react";
import { ProjectService } from "@/services/projects";

export default function ProjectDashboardModal({
  isOpen,
  onClose,
  projectId,
}: {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
}) {
  const [stats, setStats] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchStats = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const data = await ProjectService.getProjectStats(projectId);
      setStats(data);
    } catch (err: any) {
      console.error("Failed to fetch project stats:", err);
      setError(
        err?.response?.data?.detail || err?.message || "Failed to load stats"
      );
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    if (isOpen) {
      fetchStats();
    } else {
      // Reset so next open re-fetches fresh data
      setStats(null);
      setError(null);
    }
  }, [isOpen, fetchStats]);

  // Close on Escape
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  type StatCard = {
    label: string;
    value: string;
    icon: React.ElementType;
    color: string;
  };

  const statCards: StatCard[] = stats
    ? [
        { label: "Lines Changed",  value: stats.linesChanged?.toLocaleString()  ?? "—", icon: FileCode,     color: "green"  },
        { label: "Files Tracked",  value: stats.filesModified?.toLocaleString() ?? "—", icon: Activity,     color: "purple" },
        { label: "Total Commits",  value: stats.totalCommits?.toLocaleString()  ?? "—", icon: GitCommit,    color: "yellow" },
        { label: "Tests Passed",   value: stats.testsPassed?.toLocaleString()   ?? "—", icon: CheckCircle,  color: "blue"   },
        { label: "Active Agents",  value: stats.activeAgents?.toLocaleString()  ?? "—", icon: Users,        color: "orange" },
        { label: "Time Saved",     value: stats.timeSaved                        ?? "—", icon: Clock,        color: "teal"   },
      ]
    : [];

  const colorMap: Record<string, { bg: string; text: string }> = {
    green:  { bg: "bg-green-500/10",  text: "text-green-400"  },
    purple: { bg: "bg-purple-500/10", text: "text-purple-400" },
    yellow: { bg: "bg-yellow-500/10", text: "text-yellow-400" },
    blue:   { bg: "bg-blue-500/10",   text: "text-blue-400"   },
    orange: { bg: "bg-orange-500/10", text: "text-orange-400" },
    teal:   { bg: "bg-teal-500/10",   text: "text-teal-400"   },
  };

  return (
    <div
      className="fixed inset-0 z-[150] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-[#1e1e1e] border border-gray-700/80 rounded-xl p-6 w-full max-w-2xl shadow-2xl relative"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400 border border-blue-500/30">
              <BarChart3 size={20} />
            </div>
            <div>
              <h2 className="text-lg font-semibold text-white">Project Dashboard</h2>
              <p className="text-xs text-gray-400">
                Activity and agent metrics for this workspace.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchStats}
              disabled={isLoading}
              title="Refresh stats"
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors disabled:opacity-40"
            >
              <RefreshCw size={14} className={isLoading ? "animate-spin" : ""} />
            </button>
            <button
              onClick={onClose}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
            >
              <X size={16} />
            </button>
          </div>
        </div>

        {/* Body */}
        {isLoading ? (
          <div className="grid grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div
                key={i}
                className="bg-[#252526] border border-gray-700/50 p-4 rounded-xl animate-pulse"
              >
                <div className="h-3 bg-gray-700 rounded w-2/3 mb-3" />
                <div className="h-7 bg-gray-600 rounded w-1/2" />
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="h-48 flex flex-col items-center justify-center gap-3">
            <AlertCircle size={32} className="text-red-400" />
            <p className="text-red-400 text-sm font-medium">Failed to load stats</p>
            <p className="text-gray-500 text-xs text-center max-w-xs">{error}</p>
            <button
              onClick={fetchStats}
              className="mt-2 px-4 py-1.5 bg-gray-800 hover:bg-gray-700 text-white text-xs rounded-lg transition-colors"
            >
              Retry
            </button>
          </div>
        ) : stats ? (
          <>
            <div className="grid grid-cols-3 gap-4">
              {statCards.map(({ label, value, icon: Icon, color }) => {
                const { bg, text } = colorMap[color];
                return (
                  <div
                    key={label}
                    className="bg-[#252526] border border-gray-700/50 p-4 rounded-xl flex items-center gap-4 hover:border-gray-600 transition-colors"
                  >
                    <div className={`p-2 ${bg} ${text} rounded-lg shrink-0`}>
                      <Icon size={20} />
                    </div>
                    <div className="min-w-0">
                      <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold truncate">
                        {label}
                      </p>
                      <p className="text-2xl font-bold text-white truncate">{value}</p>
                    </div>
                  </div>
                );
              })}
            </div>
            <p className="text-xs text-gray-600 mt-4 text-center flex items-center justify-center gap-1">
              <TrendingUp size={11} />
              Stats are derived from git history in real-time
            </p>
          </>
        ) : null}
      </div>
    </div>
  );
}
