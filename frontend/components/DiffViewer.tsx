"use client";

import { useState, useEffect, useCallback } from "react";
import { DiffEditor } from "@monaco-editor/react";
import { X, Loader2, CheckCircle2, XCircle, LayoutTemplate, AlignLeft, AlertTriangle } from "lucide-react";

type DiffMode = "split" | "inline";

const LANG_MAP: Record<string, string> = {
  ts: "typescript", tsx: "typescript", js: "javascript", jsx: "javascript",
  py: "python", json: "json", md: "markdown", css: "css", html: "html",
  sh: "shell", yaml: "yaml", yml: "yaml", toml: "toml", rs: "rust",
  go: "go", java: "java", cpp: "cpp", c: "c", rb: "ruby",
};

function getLanguage(filePath: string): string {
  const ext = filePath.split(".").pop()?.toLowerCase() || "";
  return LANG_MAP[ext] || "plaintext";
}

type ToastState = {
  type: "success" | "error";
  message: string;
} | null;

export default function DiffViewer({
  projectId,
  filePath,
  onClose,
  onAccept,
}: {
  projectId: string;
  filePath: string;
  onClose: () => void;
  /** Called with the accepted (kept) content so the editor can update */
  onAccept?: (filePath: string, content: string) => void;
}) {
  const [original, setOriginal] = useState<string | null>(null);
  const [modified, setModified] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [diffMode, setDiffMode] = useState<DiffMode>("split");
  const [isActioning, setIsActioning] = useState(false);
  const [toast, setToast] = useState<ToastState>(null);
  const [isNewFile, setIsNewFile] = useState(false);

  const showToast = (type: "success" | "error", message: string) => {
    setToast({ type, message });
    setTimeout(() => setToast(null), 3000);
  };

  useEffect(() => {
    async function loadDiff() {
      setError(null);
      setOriginal(null);
      setModified(null);
      try {
        // Fetch current (working copy) content
        const modRes = await fetch(
          `http://localhost:8000/api/v1/projects/${projectId}/files/content?path=${encodeURIComponent(filePath)}`
        );
        const modJson = await modRes.json();
        if (modJson.success && modJson.data?.content !== undefined) {
          setModified(modJson.data.content);
        } else {
          setModified("");
        }

        // Fetch original (git HEAD)
        const origRes = await fetch(
          `http://localhost:8000/api/v1/projects/${projectId}/git/file?path=${encodeURIComponent(filePath)}`
        );
        const origJson = await origRes.json();
        if (origJson.success) {
          setOriginal(origJson.data);
          setIsNewFile(false);
        } else {
          // New file — no HEAD version
          setOriginal("");
          setIsNewFile(true);
        }
      } catch (e: any) {
        setError(e.message || "Failed to load diff");
      }
    }
    loadDiff();
  }, [projectId, filePath]);

  /** Accept: keep the modified version (already on disk, just notify parent) */
  const handleAccept = useCallback(async () => {
    if (modified === null) return;
    setIsActioning(true);
    try {
      // File is already on disk, just signal the parent to update its editor model
      if (onAccept) onAccept(filePath, modified);
      showToast("success", "Changes accepted ✓");
      setTimeout(() => onClose(), 1200);
    } catch {
      showToast("error", "Failed to accept changes");
    } finally {
      setIsActioning(false);
    }
  }, [modified, filePath, onAccept, onClose]);

  /** Reject: restore file to git HEAD by calling the revert-file endpoint */
  const handleReject = useCallback(async () => {
    if (isNewFile) {
      showToast("error", "Cannot revert — file has no committed version");
      return;
    }
    setIsActioning(true);
    try {
      const res = await fetch(
        `http://localhost:8000/api/v1/projects/${projectId}/git/revert-file`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ path: filePath }),
        }
      );
      const json = await res.json();
      if (json.success) {
        if (onAccept) onAccept(filePath, json.data?.content ?? original ?? "");
        showToast("success", "Changes rejected — reverted to HEAD");
        setTimeout(() => onClose(), 1200);
      } else {
        showToast("error", json.message || "Revert failed");
      }
    } catch {
      showToast("error", "Network error during revert");
    } finally {
      setIsActioning(false);
    }
  }, [isNewFile, projectId, filePath, original, onAccept, onClose]);

  // Keyboard shortcut: Escape to close
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [onClose]);

  /* ─── Error state ─── */
  if (error) {
    return (
      <div className="flex flex-col h-full bg-[#1e1e1e] items-center justify-center gap-3">
        <AlertTriangle size={28} className="text-red-400" />
        <p className="text-sm text-red-400">{error}</p>
        <button
          onClick={onClose}
          className="px-4 py-1.5 bg-gray-800 rounded-lg hover:bg-gray-700 text-white text-xs transition-colors"
        >
          Close
        </button>
      </div>
    );
  }

  /* ─── Loading state ─── */
  if (original === null || modified === null) {
    return (
      <div className="flex flex-col h-full items-center justify-center bg-[#1e1e1e] text-gray-400 gap-2">
        <Loader2 className="animate-spin" size={20} />
        <span className="text-sm">Loading diff for <span className="font-mono text-gray-300">{filePath}</span>…</span>
      </div>
    );
  }

  const hasChanges = original !== modified;
  const lang = getLanguage(filePath);

  /* ─── Diff-stats (rough line counts) ─── */
  const originalLines = original.split("\n");
  const modifiedLines = modified.split("\n");
  const addedLines = modifiedLines.filter(
    (l, i) => l !== (originalLines[i] ?? "")
  ).length;

  return (
    <div className="flex flex-col h-full bg-[#1e1e1e] relative">
      {/* ── Toast notification ── */}
      {toast && (
        <div
          className={`absolute top-3 left-1/2 -translate-x-1/2 z-50 flex items-center gap-2 px-4 py-2 rounded-xl shadow-2xl text-sm font-medium transition-all duration-300 ${
            toast.type === "success"
              ? "bg-green-900/90 border border-green-500/50 text-green-300"
              : "bg-red-900/90 border border-red-500/50 text-red-300"
          }`}
        >
          {toast.type === "success" ? (
            <CheckCircle2 size={15} className="text-green-400" />
          ) : (
            <XCircle size={15} className="text-red-400" />
          )}
          {toast.message}
        </div>
      )}

      {/* ── Header ── */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#141414] border-b border-gray-800/80 shrink-0">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex flex-col min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 shrink-0">Changes in</span>
              <span className="text-sm text-gray-200 font-mono font-medium truncate">{filePath}</span>
            </div>
            <div className="flex items-center gap-2 mt-0.5">
              {isNewFile ? (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-green-900/50 text-green-400 border border-green-700/40 font-medium">
                  NEW FILE
                </span>
              ) : hasChanges ? (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-yellow-900/50 text-yellow-400 border border-yellow-700/40 font-medium">
                  MODIFIED
                </span>
              ) : (
                <span className="text-[10px] px-1.5 py-0.5 rounded bg-gray-800 text-gray-500 border border-gray-700 font-medium">
                  UNCHANGED
                </span>
              )}
              {hasChanges && (
                <span className="text-[10px] text-gray-600 font-mono">
                  ~{addedLines} line{addedLines !== 1 ? "s" : ""} changed
                </span>
              )}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-2 shrink-0">
          {/* Inline / Split toggle */}
          <div className="flex items-center bg-gray-800 rounded-lg p-0.5">
            <button
              onClick={() => setDiffMode("split")}
              title="Side-by-side diff"
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs transition-colors ${
                diffMode === "split"
                  ? "bg-gray-700 text-white"
                  : "text-gray-500 hover:text-gray-300"
              }`}
            >
              <LayoutTemplate size={12} />
              Split
            </button>
            <button
              onClick={() => setDiffMode("inline")}
              title="Inline diff"
              className={`flex items-center gap-1 px-2.5 py-1 rounded-md text-xs transition-colors ${
                diffMode === "inline"
                  ? "bg-gray-700 text-white"
                  : "text-gray-500 hover:text-gray-300"
              }`}
            >
              <AlignLeft size={12} />
              Inline
            </button>
          </div>

          {/* Accept / Reject */}
          {hasChanges && (
            <div className="flex items-center gap-1.5">
              <button
                onClick={handleReject}
                disabled={isActioning || isNewFile}
                title={isNewFile ? "Cannot revert — new file has no committed version" : "Reject changes (restore to git HEAD)"}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-red-950/50 hover:bg-red-900/60 border border-red-800/50 text-red-400 hover:text-red-300 disabled:opacity-40 disabled:cursor-not-allowed transition-all"
              >
                {isActioning ? (
                  <Loader2 size={11} className="animate-spin" />
                ) : (
                  <XCircle size={11} />
                )}
                Reject
              </button>
              <button
                onClick={handleAccept}
                disabled={isActioning}
                title="Accept changes (keep current version)"
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-green-950/50 hover:bg-green-900/60 border border-green-800/50 text-green-400 hover:text-green-300 disabled:opacity-40 transition-all"
              >
                {isActioning ? (
                  <Loader2 size={11} className="animate-spin" />
                ) : (
                  <CheckCircle2 size={11} />
                )}
                Accept
              </button>
            </div>
          )}

          <button
            onClick={onClose}
            className="p-1.5 hover:bg-gray-800 text-gray-500 hover:text-white rounded-lg transition-colors"
            title="Close (Esc)"
          >
            <X size={15} />
          </button>
        </div>
      </div>

      {/* ── No changes notice ── */}
      {!hasChanges && (
        <div className="flex-1 flex flex-col items-center justify-center text-gray-500 gap-2">
          <CheckCircle2 size={32} className="text-green-500/40" />
          <p className="text-sm">No changes — file is identical to git HEAD</p>
          <button
            onClick={onClose}
            className="mt-2 text-xs text-gray-600 hover:text-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      )}

      {/* ── Monaco Diff Editor ── */}
      {hasChanges && (
        <div className="flex-1 relative">
          <DiffEditor
            original={original}
            modified={modified}
            language={lang}
            theme="vs-dark"
            options={{
              renderSideBySide: diffMode === "split",
              readOnly: true,
              minimap: { enabled: false },
              scrollBeyondLastLine: false,
              fontSize: 13,
              fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",
              lineNumbers: "on",
              diffWordWrap: "on",
              renderOverviewRuler: true,
              scrollbar: { verticalScrollbarSize: 6, horizontalScrollbarSize: 6 },
            }}
          />
        </div>
      )}
    </div>
  );
}
