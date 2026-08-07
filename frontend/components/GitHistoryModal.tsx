import React, { useEffect, useState } from "react";
import { X, GitCommit, RotateCcw, Loader2 } from "lucide-react";
import { ProjectService, GitCommit as GitCommitType } from "@/services/projects";

interface GitHistoryModalProps {
  isOpen: boolean;
  projectId: string;
  onClose: () => void;
  onRolledBack: () => void; // called after a successful rollback, to refresh file tree/editor
}

export const GitHistoryModal: React.FC<GitHistoryModalProps> = ({
  isOpen,
  projectId,
  onClose,
  onRolledBack,
}) => {
  const [commits, setCommits] = useState<GitCommitType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [rollingBackHash, setRollingBackHash] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen) return;
    setIsLoading(true);
    setError(null);
    ProjectService.getGitLog(projectId, 30)
      .then(setCommits)
      .catch((err) => setError(err.message || "Failed to load history"))
      .finally(() => setIsLoading(false));
  }, [isOpen, projectId]);

  if (!isOpen) return null;

  const handleRollback = async (hash: string) => {
    const confirmed = window.confirm(
      "Revert to this commit? This creates a new commit undoing everything after it. This cannot be un-reverted automatically."
    );
    if (!confirmed) return;

    setRollingBackHash(hash);
    setError(null);
    try {
      await ProjectService.rollbackCommit(projectId, hash);
      const refreshed = await ProjectService.getGitLog(projectId, 30);
      setCommits(refreshed);
      onRolledBack();
    } catch (err: any) {
      setError(err?.message || "Rollback failed.");
    } finally {
      setRollingBackHash(null);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden border border-gray-200 dark:border-gray-800 max-h-[75vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-800">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <GitCommit size={18} />
            History
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        {error && (
          <div className="mx-6 mt-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-sm">
            {error}
          </div>
        )}

        <div className="overflow-y-auto flex-1 p-2">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 size={20} className="animate-spin text-gray-400" />
            </div>
          ) : commits.length === 0 ? (
            <div className="p-8 text-center text-sm text-gray-500">No commits yet.</div>
          ) : (
            commits.map((commit, i) => {
              const isAiCommit = commit.message.startsWith("AI:");
              const isRollingBack = rollingBackHash === commit.hash;
              return (
                <div
                  key={commit.hash}
                  className="flex items-start justify-between gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-lg transition-colors"
                >
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2 mb-0.5">
                      {isAiCommit && (
                        <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-blue-100 dark:bg-blue-900/40 text-blue-600 dark:text-blue-400">
                          AI
                        </span>
                      )}
                      <span className="text-sm text-gray-800 dark:text-gray-200 truncate">
                        {commit.message}
                      </span>
                    </div>
                    <div className="text-xs text-gray-400 font-mono">
                      {commit.hash.slice(0, 7)} · {commit.author} · {commit.date}
                    </div>
                  </div>
                  {i > 0 && (
                    <button
                      onClick={() => handleRollback(commit.hash)}
                      disabled={isRollingBack}
                      title="Revert to this commit"
                      className="shrink-0 p-1.5 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors disabled:opacity-50"
                    >
                      {isRollingBack ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <RotateCcw size={14} />
                      )}
                    </button>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};