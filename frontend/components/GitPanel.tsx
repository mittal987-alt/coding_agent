"use client";

import { useEffect, useState, useCallback } from "react";
import { Loader2, GitBranch, GitCommit, Check, ChevronDown, ChevronRight, RefreshCw, Upload, Plus, Trash2 } from "lucide-react";
import { apiBaseUrl } from "@/lib/api";

type FileStatus = "modified" | "untracked" | "staged" | "deleted";

type ChangedFile = {
  path: string;
  status: FileStatus;
};

type Commit = {
  hash: string;
  author: string;
  email: string;
  date: string;
  message: string;
};

const STATUS_COLOR: Record<FileStatus, string> = {
  modified: "text-yellow-400",
  untracked: "text-green-400",
  staged: "text-blue-400",
  deleted: "text-red-400",
};
const STATUS_LETTER: Record<FileStatus, string> = {
  modified: "M",
  untracked: "U",
  staged: "A",
  deleted: "D",
};

export default function GitPanel({ projectId }: { projectId: string }) {
  const [changes, setChanges] = useState<ChangedFile[]>([]);
  const [commits, setCommits] = useState<Commit[]>([]);
  const [commitMsg, setCommitMsg] = useState("");
  const [isCommitting, setIsCommitting] = useState(false);
  const [commitError, setCommitError] = useState<string | null>(null);
  const [commitSuccess, setCommitSuccess] = useState<string | null>(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(false);
  const [showLog, setShowLog] = useState(false);
  const [isLoadingLog, setIsLoadingLog] = useState(false);

  const [branches, setBranches] = useState<{current: string, branches: string[]}>({ current: "main", branches: [] });
  const [showBranches, setShowBranches] = useState(false);
  const [newBranchName, setNewBranchName] = useState("");
  const [isBranchLoading, setIsBranchLoading] = useState(false);

  const loadBranches = useCallback(async () => {
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/git/branches`);
      const json = await res.json();
      if (json.success && json.data) {
        setBranches(json.data);
      }
    } catch {
      // silently fail
    }
  }, [projectId]);

  const refreshStatus = useCallback(async () => {
    setIsLoadingStatus(true);
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/git/status`);
      const json = await res.json();
      if (json.success && json.data) {
        const data = json.data as Record<string, string>;
        setChanges(
          Object.entries(data).map(([path, status]) => ({
            path,
            status: status as FileStatus,
          }))
        );
      }
    } catch {
      // silently fail
    } finally {
      setIsLoadingStatus(false);
    }
  }, [projectId]);

  const loadLog = useCallback(async () => {
    setIsLoadingLog(true);
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/git/log`);
      const json = await res.json();
      if (json.success) setCommits(json.data || []);
    } catch {
      // silently fail
    } finally {
      setIsLoadingLog(false);
    }
  }, [projectId]);

  useEffect(() => {
    refreshStatus();
    loadBranches();
    const interval = setInterval(refreshStatus, 3000);
    const handleRefreshEvent = () => { refreshStatus(); loadBranches(); };
    window.addEventListener("git-refresh", handleRefreshEvent);
    return () => {
      clearInterval(interval);
      window.removeEventListener("git-refresh", handleRefreshEvent);
    };
  }, [refreshStatus]);

  useEffect(() => {
    if (showLog) loadLog();
  }, [showLog, loadLog]);

  const handleCommit = async () => {
    if (!commitMsg.trim()) return;
    setIsCommitting(true);
    setCommitError(null);
    setCommitSuccess(null);
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/git/commit`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: commitMsg }),
      });
      const json = await res.json();
      if (json.success) {
        setCommitSuccess("Committed successfully!");
        setCommitMsg("");
        await refreshStatus();
        if (showLog) await loadLog();
        setTimeout(() => setCommitSuccess(null), 3000);
      } else {
        setCommitError(json.message || "Commit failed.");
      }
    } catch (e: any) {
      setCommitError(e.message || "Commit failed.");
    } finally {
      setIsCommitting(false);
    }
  };

  const [isPushing, setIsPushing] = useState(false);

  const handlePush = async () => {
    setIsPushing(true);
    setCommitError(null);
    setCommitSuccess(null);
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/git/push`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });
      const json = await res.json();
      if (json.success) {
        setCommitSuccess("Pushed to GitHub successfully!");
        if (showLog) await loadLog();
        setTimeout(() => setCommitSuccess(null), 4000);
      } else {
        setCommitError(json.message || "Push failed.");
      }
    } catch (e: any) {
      setCommitError(e.message || "Push failed.");
    } finally {
      setIsPushing(false);
    }
  };

  const handleCreateBranch = async () => {
    if (!newBranchName.trim()) return;
    setIsBranchLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/git/branches`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newBranchName.trim() }),
      });
      const json = await res.json();
      if (json.success) {
        setNewBranchName("");
        await loadBranches();
        await refreshStatus();
      }
    } finally {
      setIsBranchLoading(false);
    }
  };

  const handleCheckoutBranch = async (branch: string) => {
    if (branch === branches.current) return;
    setIsBranchLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/git/checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ branch }),
      });
      const json = await res.json();
      if (json.success) {
        await loadBranches();
        await refreshStatus();
        if (showLog) await loadLog();
      }
    } finally {
      setIsBranchLoading(false);
    }
  };

  const handleDeleteBranch = async (branch: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (branch === branches.current || !confirm(`Delete branch '${branch}'?`)) return;
    setIsBranchLoading(true);
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/git/branches/${encodeURIComponent(branch)}`, {
        method: "DELETE",
      });
      const json = await res.json();
      if (json.success) {
        await loadBranches();
      }
    } finally {
      setIsBranchLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full text-sm overflow-hidden">
      {/* Branches section */}
      <div className="border-b border-gray-800">
        <button
          onClick={() => setShowBranches(!showBranches)}
          className="flex items-center gap-2 w-full px-4 py-2 text-xs text-gray-400 hover:text-gray-200 hover:bg-gray-800/50 transition-colors"
        >
          {showBranches ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          <span className="font-semibold uppercase tracking-wider flex items-center gap-2">
            Branches <span className="bg-blue-500/20 text-blue-400 px-1.5 py-0.5 rounded normal-case font-mono">{branches.current}</span>
          </span>
          {isBranchLoading && <Loader2 size={10} className="animate-spin ml-auto" />}
        </button>
        {showBranches && (
          <div className="bg-gray-900/30 py-2 border-t border-gray-800/50">
            <div className="px-4 pb-2 flex gap-2">
              <input 
                type="text" 
                value={newBranchName}
                onChange={(e) => setNewBranchName(e.target.value)}
                placeholder="New branch name..."
                className="flex-1 bg-gray-900 border border-gray-700 rounded px-2 py-1 text-xs text-gray-200 focus:outline-none focus:border-blue-500"
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleCreateBranch();
                }}
              />
              <button
                onClick={handleCreateBranch}
                disabled={!newBranchName.trim() || isBranchLoading}
                className="p-1 bg-gray-800 hover:bg-gray-700 rounded disabled:opacity-50 text-gray-300"
                title="Create branch"
              >
                <Plus size={14} />
              </button>
            </div>
            <ul className="max-h-32 overflow-y-auto">
              {branches.branches.map(b => (
                <li 
                  key={b}
                  onClick={() => handleCheckoutBranch(b)}
                  className={`flex items-center gap-2 px-4 py-1.5 text-xs cursor-pointer group ${b === branches.current ? 'bg-blue-500/10 text-blue-400' : 'text-gray-300 hover:bg-gray-800/50'}`}
                >
                  <GitBranch size={12} className={b === branches.current ? 'text-blue-500' : 'text-gray-500'} />
                  <span className="font-mono flex-1">{b}</span>
                  {b !== branches.current && (
                    <button 
                      onClick={(e) => handleDeleteBranch(b, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 text-gray-500 hover:text-red-400 rounded transition-all"
                      title="Delete branch"
                    >
                      <Trash2 size={12} />
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Changes section */}
      <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800">
        <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
          Changes ({changes.length})
        </span>
        <button
          onClick={refreshStatus}
          disabled={isLoadingStatus}
          className="p-1 text-gray-500 hover:text-gray-200 rounded transition-colors"
          title="Refresh status"
        >
          <RefreshCw size={12} className={isLoadingStatus ? "animate-spin" : ""} />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto min-h-0">
        {changes.length === 0 ? (
          <div className="px-4 py-6 text-center text-xs text-gray-600">
            <GitBranch size={20} className="mx-auto mb-2 text-gray-700" />
            No changes detected
          </div>
        ) : (
          <ul className="py-1">
            {changes.map((f) => (
              <li
                key={f.path}
                className="flex items-center gap-2 px-4 py-1 hover:bg-gray-800/50 group"
              >
                <span className={`text-[10px] font-bold w-3 shrink-0 ${STATUS_COLOR[f.status]}`}>
                  {STATUS_LETTER[f.status]}
                </span>
                <span className="truncate text-xs text-gray-300 font-mono flex-1" title={f.path}>
                  {f.path}
                </span>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Commit & Push box */}
      <div className="border-t border-gray-800 p-3 flex flex-col gap-2">
        <textarea
          value={commitMsg}
          onChange={(e) => setCommitMsg(e.target.value)}
          placeholder="Commit message…"
          rows={2}
          className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs resize-none focus:outline-none focus:ring-1 focus:ring-blue-500 text-gray-200 placeholder-gray-600"
          onKeyDown={(e) => {
            if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
              e.preventDefault();
              handleCommit();
            }
          }}
        />
        {commitError && <p className="text-xs text-red-400 leading-snug">{commitError}</p>}
        {commitSuccess && (
          <p className="text-xs text-green-400 flex items-center gap-1">
            <Check size={11} /> {commitSuccess}
          </p>
        )}
        <div className="flex gap-2">
          <button
            onClick={handleCommit}
            disabled={!commitMsg.trim() || isCommitting}
            className="flex-1 flex items-center justify-center gap-1.5 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-medium transition-colors"
          >
            {isCommitting ? (
              <Loader2 size={12} className="animate-spin" />
            ) : (
              <GitCommit size={12} />
            )}
            Commit All
          </button>
          <button
            onClick={handlePush}
            disabled={isPushing}
            title="Push local commits to remote GitHub repository"
            className="flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 disabled:opacity-40 text-gray-200 hover:text-white text-xs font-medium transition-colors border border-gray-700"
          >
            {isPushing ? (
              <Loader2 size={12} className="animate-spin" />
            ) : (
              <Upload size={12} />
            )}
            Push
          </button>
        </div>
      </div>

      {/* Commit log toggle */}
      <div className="border-t border-gray-800">
        <button
          onClick={() => setShowLog(!showLog)}
          className="flex items-center gap-2 w-full px-4 py-2 text-xs text-gray-400 hover:text-gray-200 hover:bg-gray-800/50 transition-colors"
        >
          {showLog ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
          <span className="font-semibold uppercase tracking-wider">Commit History</span>
          {isLoadingLog && <Loader2 size={10} className="animate-spin ml-auto" />}
        </button>
        {showLog && (
          <ul className="max-h-40 overflow-y-auto border-t border-gray-800">
            {commits.length === 0 && !isLoadingLog ? (
              <li className="px-4 py-4 text-xs text-gray-600 text-center">No commits yet</li>
            ) : (
              commits.map((c) => (
                <li key={c.hash} className="flex flex-col gap-0.5 px-4 py-2 border-b border-gray-800/50 hover:bg-gray-800/30">
                  <span className="text-xs text-gray-200 leading-snug">{c.message}</span>
                  <div className="flex gap-2 text-[10px] text-gray-500">
                    <span className="font-mono">{c.hash.slice(0, 7)}</span>
                    <span>{c.author}</span>
                    <span className="ml-auto">{c.date}</span>
                  </div>
                </li>
              ))
            )}
          </ul>
        )}
      </div>
    </div>
  );
}
