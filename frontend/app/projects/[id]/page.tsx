"use client";

import React, { useEffect, useRef, useState, useCallback, useLayoutEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2, MessageSquare, Terminal, FileCode, Play, Folder, Settings, Send, PanelLeft, PanelRight, PanelBottom, Save, GitBranch, Search, FilePlus, FolderPlus, Trash2, Edit3, Brain, Zap, Circle, X, Sun, Moon, BarChart3, Database, Command, History as HistoryIcon, RotateCcw, Sparkles, AlertCircle, CheckCircle2, SplitSquareHorizontal, Mic, FlaskConical, ShieldCheck, ShieldAlert, ShieldX } from "lucide-react";
import { ProjectService, Project } from "@/services/projects";
import { apiBaseUrl } from "@/lib/api";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import remarkGfm from "remark-gfm";
import Editor, { useMonaco } from "@monaco-editor/react";
import type * as Monaco from "monaco-editor";
import { useDropzone } from "react-dropzone";
import dynamic from "next/dynamic";
import { useToast } from "@/components/ToastProvider";
import OnboardingWizard from "@/components/OnboardingWizard";
import ProjectDashboardModal from "@/components/ProjectDashboardModal";
import CommandPalette from "@/components/CommandPalette";
import {
  Panel,
  PanelGroup,
  PanelResizeHandle,
  ImperativePanelHandle,
} from "react-resizable-panels";
import { ProjectSettingsModal } from "@/components/ProjectSettingsModal";
import { SearchModal } from "@/components/SearchModal";
import { KeyboardShortcutsModal } from "@/components/KeyboardShortcutsModal";
import GitPanel from "@/components/GitPanel";
import SearchPanel from "@/components/SearchPanel";
import AgentActivityLog from "@/components/AgentActivityLog";
import DiffViewer from "@/components/DiffViewer";
import PreviewPanel from "@/components/PreviewPanel";
import {GitHistoryModal }from "@/components/GitHistoryModal";
const IDETerminal = dynamic(
  () => import("@/components/terminal"),
  {
    ssr: false,
  }
);

import { CodeBlock } from "./components/CodeBlock";
import { FileNodeItem } from "./components/FileNodeItem";
import { 
  Message, 
  FileStatus, 
  FileNode, 
  TerminalSession, 
  ContextMenuState 
} from "./components/types";
import { 
  fileIconColor, 
  normalizePath, 
  applyGitStatus, 
  getLanguageFromPath, 
  getFileNameFromPath, 
  getTabLabel, 
  statusColor, 
  statusLetter, 
  flattenPaths 
} from "./components/utils";

const SUGGESTED_PROMPTS = [
  "Set up the project structure",
  "Add a login page",
  "Explain this repo",
  "Fix the last error",
];

// ---------------------------------------------------------------------------
// Flat list of all file paths for the fuzzy file finder
// ---------------------------------------------------------------------------
// ---------------------------------------------------------------------------

const SKIP_DIR_SEGMENTS = new Set([
  ".git",
  "node_modules",
  "__pycache__",
  ".venv",
  "venv",
  ".next",
]);

function shouldSkipFile(relativePath: string): boolean {
  const segments = relativePath.replace(/\\/g, "/").split("/");
  return segments.some((seg) => SKIP_DIR_SEGMENTS.has(seg));
}



export default function WorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;
  const { success, error, info } = useToast();

  const [theme, setTheme] = useState<"dark" | "light">("dark");

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [theme]);

  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [isDashboardOpen, setIsDashboardOpen] = useState(false);
  const [isCommandPaletteOpen, setIsCommandPaletteOpen] = useState(false);

  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [chatInput, setChatInput] = useState("");
  const [chatImages, setChatImages] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const abortControllerRef = useRef<AbortController | null>(null);
  // Current agent name shown in the navbar pill (parsed from latest activity)
  const [currentAgentLabel, setCurrentAgentLabel] = useState<string | null>(null);

  // Run Tests & Auto-Fix
  const [isRunningTests, setIsRunningTests] = useState(false);
  const [testRunResult, setTestRunResult] = useState<{ passed: boolean; summary: string } | null>(null);

  // HITL (Human-in-the-Loop) approval banner
  const [hitlPending, setHitlPending] = useState<{ workflowId: string; nodeName: string } | null>(null);
  const [isHitlActioning, setIsHitlActioning] = useState(false);

  const [editorLanguage, setEditorLanguage] = useState("markdown");
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  
  // Split Editor State
  const [isSplitMode, setIsSplitMode] = useState(false);
  const [secondarySelectedFile, setSecondarySelectedFile] = useState<string | null>(null);
  const [activeEditorPane, setActiveEditorPane] = useState<"primary" | "secondary">("primary");
  
  const [diffFile, setDiffFile] = useState<string | null>(null);

  const [openTabs, setOpenTabs] = useState<string[]>([]);
  // Track which tabs have unsaved edits (dirty state)
  const [dirtyTabs, setDirtyTabs] = useState<Set<string>>(new Set());

  const [fileContents, setFileContents] = useState<Record<string, string>>({});
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);

  const [terminals, setTerminals] = useState<TerminalSession[]>([]);
  const [activeTerminalId, setActiveTerminalId] = useState<string | null>(null);
  const [focusedSessionId, setFocusedSessionId] = useState<string | null>(null);
  const [isTerminalMaximized, setIsTerminalMaximized] = useState(false);
  // Map from pane id → terminal actions exposed by IDETerminal
  const terminalActions = useRef<Map<string, { clear: () => void; getContent: () => string; write?: (data: string) => void }>>(new Map());

  // Tab Renaming
  const [editingTabId, setEditingTabId] = useState<string | null>(null);
  const [editingTabLabel, setEditingTabLabel] = useState("");

  // Command History and presets
  const [commandHistory, setCommandHistory] = useState<string[]>(["npm run dev", "npm install", "git status", "git diff"]);
  const [customCommandInput, setCustomCommandInput] = useState("");
  const [showHistoryDropdown, setShowHistoryDropdown] = useState(false);

  // Monaco editor instance and per-file model registry
  const monacoRef = useRef<typeof Monaco | null>(null);
  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const secondaryEditorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
  const monacoModels = useRef<Map<string, Monaco.editor.ITextModel>>(new Map());

  // Right-click context menu
  const [contextMenu, setContextMenu] = useState<ContextMenuState>(null);

  const chatPanelRef = useRef<ImperativePanelHandle>(null);
  const repoPanelRef = useRef<ImperativePanelHandle>(null);
  const terminalPanelRef = useRef<ImperativePanelHandle>(null);

  const [isChatCollapsed, setIsChatCollapsed] = useState(false);
  const [isRepoCollapsed, setIsRepoCollapsed] = useState(false);
  const [isTerminalCollapsed, setIsTerminalCollapsed] = useState(false);
  const [isSavingFile, setIsSavingFile] = useState(false);
  const [fileSaveMsg, setFileSaveMsg] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Right panel tab: "files" | "git" | "search"
  const [rightTab, setRightTab] = useState<"files" | "git" | "search">("files");

  // Inline AI Edit State
  const [isInlineEditOpen, setIsInlineEditOpen] = useState(false);
  const [inlineEditPosition, setInlineEditPosition] = useState({ top: 0, left: 0 });
  const [inlineEditPrompt, setInlineEditPrompt] = useState("");
  const [inlineEditSelection, setInlineEditSelection] = useState<Monaco.Selection | null>(null);
  const [isInlineEditing, setIsInlineEditing] = useState(false);

  // Problems Panel State
  const [problems, setProblems] = useState<Monaco.editor.IMarker[]>([]);
  const [bottomTab, setBottomTab] = useState<"terminal" | "problems">("terminal");

  // Status bar cursor position
  const [cursorPosition, setCursorPosition] = useState({ line: 1, column: 1 });
  // Current git branch name
  const [gitBranch, setGitBranch] = useState<string | null>(null);

  // File action modal state (New File / New Folder / Rename / Delete)
  const [fileActionModal, setFileActionModal] = useState<{
    type: "create_file" | "create_folder" | "rename" | "delete" | null;
    path: string;
    name?: string;
  }>({ type: null, path: "" });
  const [fileInputName, setFileInputName] = useState("");

  const [isUploading, setIsUploading] = useState(false);

  const refreshFileTree = useCallback(async () => {
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/files`);
      const json = await res.json();
      if (json.success) {
        setFileTree(json.data || []);
      }
    } catch (err) {
      console.error("Failed to refresh file tree", err);
    }
  }, [projectId]);

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    setIsUploading(true);
    
    // Create FormData with multiple files and their relative paths
    const formData = new FormData();
    const relativePaths: string[] = [];
    let uploadCount = 0;
    
    acceptedFiles.forEach((file: any) => {
      // use path from react-dropzone if available, fallback to filename
      let relPath = file.path ? file.path.replace(/^\//, "") : file.name;
      // Normalize backslashes to forward slashes and remove leading slash
      relPath = relPath.replace(/\\/g, "/").replace(/^\//, "");
      
      // Filter out files that belong to skipped directories (e.g. node_modules, .git)
      if (shouldSkipFile(relPath)) {
        return;
      }
      
      const parts = relPath.split("/");
      if (parts.length > 1) {
        relPath = parts.slice(1).join("/");
      }
      
      formData.append("files", file);
      relativePaths.push(relPath);
      uploadCount++;
    });

    if (uploadCount === 0) {
      error("No files to upload after filtering out node_modules/.git/etc.");
      setIsUploading(false);
      return;
    }

    formData.append("paths", JSON.stringify(relativePaths));

    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/upload-folder`, {
        method: "POST",
        body: formData,
      });
      const json = await res.json();
      if (json.success) {
        success(`Successfully uploaded ${uploadCount} file(s)`);
        refreshFileTree();
      } else {
        error(json.message || "Failed to upload files");
      }
    } catch (err) {
      console.error("Upload error", err);
      error("Failed to upload files. Server error.");
    } finally {
      setIsUploading(false);
    }
  }, [projectId, refreshFileTree]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    noClick: true,
    noKeyboard: true,
  });

  // Keyboard shortcuts overlay
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);
  // Project settings modal overlay
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);

  // Feature 6/7/8 UI state
  const [isHistoryOpen, setIsHistoryOpen] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  // Phase 5: AI Code Review
  const [isReviewing, setIsReviewing] = useState(false);
  // Zen mode (distraction-free)
  const [isZenMode, setIsZenMode] = useState(false);
  // Editor font size
  const [editorFontSize, setEditorFontSize] = useState(14);

  /* ── Close context menu on any outside click ── */
  useEffect(() => {
    if (!contextMenu) return;
    const handler = () => setContextMenu(null);
    window.addEventListener("click", handler);
    window.addEventListener("contextmenu", handler);
    return () => {
      window.removeEventListener("click", handler);
      window.removeEventListener("contextmenu", handler);
    };
  }, [contextMenu]);

  const handleContextMenu = useCallback(
    (e: React.MouseEvent, node: FileNode) => {
      e.preventDefault();
      e.stopPropagation();
      setContextMenu({ x: e.clientX, y: e.clientY, node });
    },
    []
  );

  const handleFileActionSubmit = async () => {
    if (!fileActionModal.type) return;

    if (fileActionModal.type === "delete") {
      try {
        await fetch(
          `${apiBaseUrl}/projects/${projectId}/files/delete?path=${encodeURIComponent(fileActionModal.path)}`,
          { method: "DELETE" }
        );
        setOpenTabs((prev) => prev.filter((p) => p !== fileActionModal.path));
        if (selectedFile === fileActionModal.path) setSelectedFile(null);
        refreshFileTree();
      } catch (err) {
        console.error("Delete failed", err);
      } finally {
        setFileActionModal({ type: null, path: "" });
      }
      return;
    }

    if (!fileInputName.trim()) return;

    if (fileActionModal.type === "rename") {
      const parts = fileActionModal.path.split("/");
      parts.pop();
      const parentDir = parts.join("/");
      const newPath = parentDir ? `${parentDir}/${fileInputName.trim()}` : fileInputName.trim();
      try {
        await fetch(`${apiBaseUrl}/projects/${projectId}/files/rename`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ old_path: fileActionModal.path, new_path: newPath }),
        });
        if (selectedFile === fileActionModal.path) setSelectedFile(newPath);
        setOpenTabs((prev) => prev.map((t) => (t === fileActionModal.path ? newPath : t)));
        refreshFileTree();
      } catch (err) {
        console.error("Rename failed", err);
      } finally {
        setFileActionModal({ type: null, path: "" });
      }
      return;
    }

    // create_file or create_folder
    const isDir = fileActionModal.type === "create_folder";
    const targetRel = fileActionModal.path
      ? `${fileActionModal.path}/${fileInputName.trim()}`
      : fileInputName.trim();

    try {
      await fetch(`${apiBaseUrl}/projects/${projectId}/files/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: targetRel, is_directory: isDir }),
      });
      refreshFileTree();
      if (!isDir) handleFileClick(targetRel);
    } catch (err) {
      console.error("Create failed", err);
    } finally {
      setFileActionModal({ type: null, path: "" });
    }
  };

  const toggleChatPanel = useCallback(() => {
    const panel = chatPanelRef.current;
    if (!panel) return;
    if (panel.getSize() === 0 || panel.isCollapsed()) panel.expand();
    else panel.collapse();
  }, []);

  const toggleRepoPanel = useCallback(() => {
    const panel = repoPanelRef.current;
    if (!panel) return;
    if (panel.getSize() === 0 || panel.isCollapsed()) panel.expand();
    else panel.collapse();
  }, []);

  const toggleTerminalPanel = useCallback(() => {
    const panel = terminalPanelRef.current;
    if (!panel) return;
    if (panel.getSize() === 0 || panel.isCollapsed()) panel.expand();
    else panel.collapse();
  }, []);

  const [messages, setMessages] = useState<Message[]>([]);
  const [hasLoadedMessages, setHasLoadedMessages] = useState(false);

  // Load chat history
  useEffect(() => {
    if (!projectId) return;
    try {
      const saved = localStorage.getItem(`chat-history-${projectId}`);
      if (saved) {
        setMessages(JSON.parse(saved));
      } else {
        setMessages([{
          id: "1",
          role: "assistant",
          content: "Hello! I am your autonomous AI agent. How can I help you today?",
        }]);
      }
    } catch {
      setMessages([{
        id: "1",
        role: "assistant",
        content: "Hello! I am your autonomous AI agent. How can I help you today?",
      }]);
    }
    setHasLoadedMessages(true);
  }, [projectId]);

  // Save chat history
  useEffect(() => {
    if (!hasLoadedMessages || !projectId) return;
    try {
      localStorage.setItem(`chat-history-${projectId}`, JSON.stringify(messages));
    } catch {
      //
    }
  }, [messages, hasLoadedMessages, projectId]);

  // Dedupe-safe tab opener
  const openTab = (path: string) => {
    setOpenTabs((prev) => (prev.includes(path) ? prev : [...prev, path]));
  };

  // Auto-scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  // Save current file to backend
  const saveCurrentFile = useCallback(async () => {
    if (!selectedFile) return;
    // Get latest content from Monaco model if available, else fall back to state
    const model = monacoModels.current.get(selectedFile);
    const content = model ? model.getValue() : fileContents[selectedFile];
    if (content === undefined) return;
    setIsSavingFile(true);
    try {
      await fetch(
        `${apiBaseUrl}/projects/${projectId}/files/content?path=${encodeURIComponent(selectedFile)}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content }),
        }
      );
      success(`Saved ${selectedFile.split("/").pop()}`);
      // Clear dirty state for this file
      setDirtyTabs((prev) => { const next = new Set(prev); next.delete(selectedFile!); return next; });
      window.dispatchEvent(new Event("git-refresh"));
    } catch {
      error(`Failed to save ${selectedFile.split("/").pop()}`);
    } finally {
      setIsSavingFile(false);
    }
  }, [selectedFile, fileContents, projectId]);

  // Feature 7: Run the project's detected dev/build/test command.
  // The backend spawns a PTY session with the command already injected,
  // then we open a new terminal tab pointing at that session so the user
  // sees live streaming output — no separate WebSocket wiring required.
  const handleRunProject = async () => {
    setIsRunning(true);
    try {
      const result = await ProjectService.runProject(projectId);

      // Open/expand the terminal panel so output is immediately visible
      const panel = terminalPanelRef.current;
      if (panel?.isCollapsed()) panel.expand();

      // Register the new session as a named terminal tab
      const storageKey = `terminal-sessions-${projectId}`;
      try {
        const existing: string[] = JSON.parse(sessionStorage.getItem(storageKey) || "[]");
        sessionStorage.setItem(storageKey, JSON.stringify([...existing, result.run_id]));
      } catch { /* ignore */ }

      setTerminals((prev) => {
        const newTerminal: TerminalSession = {
          id: `run-${Date.now()}`,
          label: `▶ ${result.label}`,
          panes: [{ id: `p-${Date.now()}`, sessionId: result.run_id }],
        };
        setActiveTerminalId(newTerminal.id);
        setFocusedSessionId(result.run_id);
        return [...prev, newTerminal];
      });

      success(`Running: ${result.command}`);
    } catch (err: any) {
      console.error("Run failed:", err);
      error(err?.response?.data?.detail || "Failed to start run.");
    } finally {
      setIsRunning(false);
    }
  };

  // Feature 8: (Re)build the project's RAG vector index
  const handleIndexProject = async () => {
    setIsIndexing(true);
    try {
      const result = await ProjectService.indexProject(projectId);
      success(`Indexed ${result.chunks_indexed} chunks for AI search.`);
    } catch (err: any) {
      console.error("Indexing failed:", err);
      error(err?.response?.data?.detail || "Failed to index project.");
    } finally {
      setIsIndexing(false);
    }
  };

  // Keyboard shortcuts: Ctrl+S save | Ctrl+P file finder | Ctrl+Shift+F search | ? help
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName?.toLowerCase();
      const isEditing = tag === "input" || tag === "textarea" || (e.target as HTMLElement)?.isContentEditable;

      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "s") {
        e.preventDefault();
        saveCurrentFile();
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "p") {
        e.preventDefault();
        setIsCommandPaletteOpen((prev) => !prev);
      }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "f") {
        e.preventDefault();
        setRightTab("search");
        // Ensure the right panel is expanded
        const panel = repoPanelRef.current;
        if (panel?.isCollapsed()) panel.expand();
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "b") {
        e.preventDefault();
        toggleChatPanel();
      }
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "e") {
        e.preventDefault();
        toggleRepoPanel();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "`") {
        e.preventDefault();
        toggleTerminalPanel();
      }
      // Ctrl+Shift+` → new terminal
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === "`") {
        e.preventDefault();
        const panel = terminalPanelRef.current;
        if (panel?.isCollapsed()) panel.expand();
        createTerminal();
      }
      if (e.key === "?" && !isEditing) {
        setIsShortcutsOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setIsCommandPaletteOpen(false);
        setIsShortcutsOpen(false);
        setIsZenMode(false);
      }
      // Ctrl+K Z → Zen Mode
      if ((e.ctrlKey || e.metaKey) && e.key === "z" && !e.shiftKey && !isEditing) {
        e.preventDefault();
        setIsZenMode((v) => !v);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [saveCurrentFile, toggleChatPanel, toggleRepoPanel, toggleTerminalPanel]);

  const createTerminal = async () => {
    try {
      const res = await fetch(
        `${apiBaseUrl}/terminal/projects/${projectId}`,
        { method: "POST" }
      );

      if (!res.ok) throw new Error(`HTTP ${res.status}`);

      const json = await res.json();
      const sessionId: string = json.session_id;

      // Auto-expand the terminal panel when the first terminal is opened
      const panel = terminalPanelRef.current;
      if (panel?.isCollapsed()) panel.expand();

      // Persist session ids in sessionStorage so they survive hot-reloads
      const storageKey = `terminal-sessions-${projectId}`;
      try {
        const existing: string[] = JSON.parse(sessionStorage.getItem(storageKey) || "[]");
        sessionStorage.setItem(storageKey, JSON.stringify([...existing, sessionId]));
      } catch { /* ignore storage errors */ }

      setTerminals((prev) => {
        const newTerminal: TerminalSession = {
          id: `t-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
          label: `Terminal ${prev.length + 1}`,
          panes: [{ id: `p-${Date.now()}`, sessionId }],
        };
        setActiveTerminalId(newTerminal.id);
        setFocusedSessionId(sessionId);
        return [...prev, newTerminal];
      });
    } catch (err) {
      console.error("Failed to create terminal", err);
      error("Failed to start terminal. Is the backend running?");
    }
  };

  const replaceTerminalSession = async (tabId: string, paneId: string) => {
    try {
      const res = await fetch(
        `${apiBaseUrl}/terminal/projects/${projectId}`,
        { method: "POST" }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const newSessionId: string = json.session_id;

      // Remove the clear fn for the old tab since its xterm instance will remount
      terminalActions.current.delete(paneId);

      setTerminals((prev) =>
        prev.map((t) =>
          t.id === tabId
            ? {
                ...t,
                panes: t.panes.map((p) =>
                  p.id === paneId ? { ...p, sessionId: newSessionId } : p
                ),
              }
            : t
        )
      );

      const storageKey = `terminal-sessions-${projectId}`;
      try {
        setTerminals((updatedTerminals) => {
          const allSessionIds = updatedTerminals.flatMap((ut) => ut.panes.map((p) => p.sessionId));
          sessionStorage.setItem(storageKey, JSON.stringify(allSessionIds));
          return updatedTerminals;
        });
      } catch { /* ignore */ }
    } catch (err) {
      console.error("Failed to replace expired terminal session", err);
      error("Failed to start a new terminal. Is the backend running?");
    }
  };

  const closeTerminal = (tabId: string) => {
    setTerminals((prev) => {
      const tab = prev.find((t) => t.id === tabId);
      if (tab) {
        tab.panes.forEach((pane) => {
          terminalActions.current.delete(pane.id);
        });
      }
      const remaining = prev.filter((t) => t.id !== tabId);
      if (activeTerminalId === tabId) {
        setActiveTerminalId(remaining.length > 0 ? remaining[remaining.length - 1].id : null);
      }
      
      const storageKey = `terminal-sessions-${projectId}`;
      try {
        const allSessionIds = remaining.flatMap((ut) => ut.panes.map((p) => p.sessionId));
        sessionStorage.setItem(storageKey, JSON.stringify(allSessionIds));
      } catch { /* ignore */ }

      return remaining;
    });
  };

  const closeTerminalPane = (tabId: string, paneId: string) => {
    terminalActions.current.delete(paneId);
    setTerminals((prev) => {
      const updated = prev.map((t) => {
        if (t.id === tabId) {
          return {
            ...t,
            panes: t.panes.filter((p) => p.id !== paneId),
          };
        }
        return t;
      }).filter((t) => t.panes.length > 0);

      const exists = updated.some((t) => t.id === activeTerminalId);
      if (!exists) {
        setActiveTerminalId(updated.length > 0 ? updated[updated.length - 1].id : null);
      }

      const storageKey = `terminal-sessions-${projectId}`;
      try {
        const allSessionIds = updated.flatMap((ut) => ut.panes.map((p) => p.sessionId));
        sessionStorage.setItem(storageKey, JSON.stringify(allSessionIds));
      } catch { /* ignore */ }

      return updated;
    });
  };

  const splitTerminal = async (tabId: string) => {
    try {
      const activeTab = terminals.find((t) => t.id === tabId);
      if (activeTab && activeTab.panes.length >= 2) {
        error("Maximum 2 split panes side-by-side supported.");
        return;
      }

      const res = await fetch(
        `${apiBaseUrl}/terminal/projects/${projectId}`,
        { method: "POST" }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const sessionId: string = json.session_id;

      setTerminals((prev) =>
        prev.map((t) => {
          if (t.id === tabId) {
            const newPaneId = `p-${Date.now()}`;
            return {
              ...t,
              panes: [...t.panes, { id: newPaneId, sessionId }],
            };
          }
          return t;
        })
      );

      setFocusedSessionId(sessionId);

      const storageKey = `terminal-sessions-${projectId}`;
      try {
        setTerminals((updated) => {
          const allSessionIds = updated.flatMap((ut) => ut.panes.map((p) => p.sessionId));
          sessionStorage.setItem(storageKey, JSON.stringify(allSessionIds));
          return updated;
        });
      } catch { /* ignore */ }
    } catch (err) {
      console.error("Failed to split terminal", err);
      error("Failed to split terminal. Is the backend running?");
    }
  };

  const sendCommandToTerminal = (command: string) => {
    if (!activeTerminalId) return;
    const activeTab = terminals.find((t) => t.id === activeTerminalId);
    if (!activeTab) return;
    
    const targetPane = activeTab.panes.find((p) => p.sessionId === focusedSessionId) || activeTab.panes[0];
    if (!targetPane) return;
    
    const actions = terminalActions.current.get(targetPane.id);
    if (actions && actions.write) {
      actions.write(`${command}\r\n`);
    } else {
      error("Terminal pane not ready or not writable.");
    }
  };

  const clearActiveTerminal = () => {
    if (!activeTerminalId) return;
    const activeTab = terminals.find((t) => t.id === activeTerminalId);
    if (!activeTab) return;
    activeTab.panes.forEach((pane) => {
      const actions = terminalActions.current.get(pane.id);
      if (actions) actions.clear();
    });
  };

  const handleDebugTerminal = () => {
    if (!activeTerminalId) return;
    const activeTab = terminals.find((t) => t.id === activeTerminalId);
    if (!activeTab) return;
    
    const targetPane = activeTab.panes.find((p) => p.sessionId === focusedSessionId) || activeTab.panes[0];
    if (!targetPane) return;
    
    const actions = terminalActions.current.get(targetPane.id);
    if (!actions) return;
    
    const rawContent = actions.getContent();
    const contentToAnalyze = rawContent.slice(-2000);
    
    if (!contentToAnalyze.trim()) {
      error("Terminal is empty.");
      return;
    }
    
    const panel = chatPanelRef.current;
    if (panel && panel.isCollapsed()) panel.expand();
    setIsChatCollapsed(false);
    
    sendPrompt(`I encountered an error in my terminal. Can you analyze this output and provide a fix?\n\n\`\`\`\n${contentToAnalyze}\n\`\`\``);
  };

  const sendPrompt = async (text: string) => {
    if (!text.trim()) return;

    const userContent = text;
    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: userContent,
      images: chatImages.length > 0 ? [...chatImages] : undefined,
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setChatInput("");
    setChatImages([]);
    setIsTyping(true);

    const aiMsgId = (Date.now() + 1).toString();
    setMessages((prev) => [
      ...prev,
      { id: aiMsgId, role: "assistant", content: "", activities: [] },
    ]);

    try {
      const historyToSend = messages
        .filter((msg) => !(msg.role === "assistant" && !msg.content.trim()))
        .map((msg) => ({ role: msg.role, content: msg.content, images: msg.images }));
        
      let contextStr = "";
      if (selectedFile && selectedFile !== "__preview__" && fileContents[selectedFile]) {
        contextStr += `\n\n[Context: Currently active file - ${selectedFile}]\n\`\`\`\n${fileContents[selectedFile]}\n\`\`\``;
      }
      if (isSplitMode && secondarySelectedFile && fileContents[secondarySelectedFile]) {
        contextStr += `\n\n[Context: Secondary active file - ${secondarySelectedFile}]\n\`\`\`\n${fileContents[secondarySelectedFile]}\n\`\`\``;
      }
      
      historyToSend.push({ role: "user", content: userContent + contextStr, images: chatImages.length > 0 ? chatImages : undefined });

      abortControllerRef.current = new AbortController();

      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        signal: abortControllerRef.current.signal,
        body: JSON.stringify({
          messages: historyToSend,
          model: project?.llm_model || "qwen2.5-coder:1.5b",
          temperature: 0.2,
          project_id: projectId,
        }),
      });

      if (!res.body) throw new Error("No body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6);
            if (!dataStr.trim()) continue;
            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.type === "token") {
                setMessages((prev) => prev.map((m) => {
                  if (m.id === aiMsgId) return { ...m, content: m.content + parsed.content };
                  return m;
                }));
              } else if (parsed.type === "activity") {
                setCurrentAgentLabel(parsed.step);
                setMessages((prev) => prev.map((m) => {
                  if (m.id === aiMsgId) return { ...m, activities: [...(m.activities || []), parsed.step] };
                  return m;
                }));
              } else if (parsed.type === "done") {
                setCurrentAgentLabel(null);
                setMessages((prev) => prev.map((m) => {
                  if (m.id === aiMsgId) return { ...m, modifiedFiles: parsed.modified_files, activities: [] };
                  return m;
                }));
                if (parsed.modified_files && parsed.modified_files.length > 0) {
                  // Invalidate cached models so they reload fresh from disk
                  for (const f of parsed.modified_files) {
                    const norm = normalizePath(f);
                    const model = monacoModels.current.get(norm);
                    if (model) { model.dispose(); monacoModels.current.delete(norm); }
                    setFileContents((prev) => { const next = { ...prev }; delete next[norm]; return next; });
                  }
                  refreshFileTree();
                  handleFileClick(parsed.modified_files[0]);
                }
              } else if (parsed.type === "error") {
                setMessages((prev) => prev.map((m) => {
                  if (m.id === aiMsgId) return { ...m, content: m.content + `\n\n**Error:** ${parsed.message}` };
                  return m;
                }));
              }
            } catch (e) {
              console.error("Parse error", e);
            }
          }
        }
      }
    } catch (error: any) {
      if (error.name === "AbortError") {
        console.log("Chat generation stopped by user");
        return;
      }
      console.error("Failed to fetch from LLM API:", error);
      const errorMsg: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: `**Error:** Failed to connect to backend LLM API. Please ensure your backend is running at \`http://localhost:8000\` and you have valid API keys configured.`,
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsTyping(false);
      setCurrentAgentLabel(null);
    }
  };

  const toggleRecording = useCallback(() => {
    if (isRecording) {
      setIsRecording(false);
      return;
    }
    
    // @ts-ignore
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      error("Speech recognition is not supported in your browser.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsRecording(true);
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setChatInput((prev) => prev ? `${prev} ${transcript}` : transcript);
      setIsRecording(false);
    };
    recognition.onerror = (event: any) => {
      console.error("Speech recognition error", event.error);
      setIsRecording(false);
      error("Speech recognition failed: " + event.error);
    };
    recognition.onend = () => setIsRecording(false);

    try {
      recognition.start();
    } catch (err) {
      console.error(err);
      setIsRecording(false);
    }
  }, [isRecording, error]);

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;
    await sendPrompt(chatInput);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileClick = async (filePath: string) => {
    const path = normalizePath(filePath);

    if (activeEditorPane === "primary") {
      setSelectedFile(path);
      setEditorLanguage(getLanguageFromPath(path));
    } else {
      setSecondarySelectedFile(path);
    }

    // Already have content in state -> just switch model
    if (fileContents[path] !== undefined) {
      openTab(path);
      // Switch Monaco model immediately if editor is mounted
      const model = monacoModels.current.get(path);
      if (model) {
        if (activeEditorPane === "primary" && editorRef.current) {
          editorRef.current.setModel(model);
        } else if (activeEditorPane === "secondary" && secondaryEditorRef.current) {
          secondaryEditorRef.current.setModel(model);
        }
      }
      return;
    }

    try {
      const res = await fetch(
        `${apiBaseUrl}/projects/${projectId}/files/content?path=${encodeURIComponent(path)}`
      );
      const json = await res.json();
      const content =
        json.success && json.data?.content !== undefined
          ? json.data.content
          : `// Could not load file: ${path}`;

      setFileContents((prev) => ({ ...prev, [path]: content }));

      // Create a Monaco model for this file
      if (monacoRef.current) {
        const lang = getLanguageFromPath(path);
        const uri = monacoRef.current.Uri.file(path);
        let model = monacoRef.current.editor.getModel(uri);
        if (!model) {
          model = monacoRef.current.editor.createModel(content, lang, uri);
        } else {
          model.setValue(content);
        }
        monacoModels.current.set(path, model);
        if (activeEditorPane === "primary" && editorRef.current) {
          editorRef.current.setModel(model);
        } else if (activeEditorPane === "secondary" && secondaryEditorRef.current) {
          secondaryEditorRef.current.setModel(model);
        }
      }

      openTab(path);
    } catch {
      const content = `// Error loading file: ${path}`;
      setFileContents((prev) => ({ ...prev, [path]: content }));
      openTab(path);
    }
  };

  const handleInlineEditSubmit = async () => {
    if (!inlineEditPrompt.trim() || !inlineEditSelection || !editorRef.current || !selectedFile) return;
    setIsInlineEditing(true);
    
    const editor = editorRef.current;
    const model = editor.getModel();
    if (!model) return;
    
    const selectedText = model.getValueInRange(inlineEditSelection);
    
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: [
            { role: "system", content: "You are an inline AI code editor. Return ONLY the raw modified code to replace the user's selection based on their prompt. Do not use markdown blocks, backticks, or conversational text. Just the code." },
            { role: "user", content: `Code:\n${selectedText}\n\nPrompt: ${inlineEditPrompt}` }
          ],
          model: project?.llm_model || "qwen2.5-coder:1.5b",
          temperature: 0.2,
          project_id: projectId,
        }),
      });

      if (!res.body) throw new Error("No body");
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      
      let buffer = "";
      let newText = "";
      let editRange: import("monaco-editor").IRange = inlineEditSelection;
    

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || "";
        for (const line of lines) {
          if (line.startsWith("data: ")) {
            const dataStr = line.slice(6);
            if (!dataStr.trim() || dataStr.trim() === "[DONE]") continue;
            try {
              const parsed = JSON.parse(dataStr);
              if (parsed.type === "token") {
                const token = parsed.content;
                newText += token;
                
                if (monacoRef.current) {
                  editor.executeEdits("ai-inline", [{
                    range: editRange,
                    text: newText,
                    forceMoveMarkers: true
                  }]);
                  
                  const startOffset = model.getOffsetAt(inlineEditSelection.getStartPosition());
                  const endPos = model.getPositionAt(startOffset + newText.length);
                  editRange = new monacoRef.current.Range(
                    inlineEditSelection.startLineNumber,
                    inlineEditSelection.startColumn,
                    endPos.lineNumber,
                    endPos.column
                  );
                }
              }
            } catch (e) {
              // Ignore parse errors for partial chunks
            }
          }
        }
      }
      
      setFileContents((prev) => ({ ...prev, [selectedFile]: model.getValue() }));
      setDirtyTabs((prev) => new Set([...prev, selectedFile]));

    } catch (error) {
      console.error("Inline edit failed:", error);
    } finally {
      setIsInlineEditing(false);
      setIsInlineEditOpen(false);
      setInlineEditPrompt("");
    }
  };

  const handleCodeReview = async () => {
    if (isReviewing) return;
    if (Object.keys(fileContents).length === 0) {
      error("Open some files first before running a code review.");
      return;
    }
    setIsReviewing(true);
    // Ensure chat panel is open
    const panel = chatPanelRef.current;
    if (panel && panel.isCollapsed()) panel.expand();
    setIsChatCollapsed(false);

    // Build a summary of the open files
    const fileSummaries = Object.entries(fileContents)
      .slice(0, 5) // limit to first 5 open files to avoid token overflow
      .map(([path, content]) => {
        const preview = content.slice(0, 1500);
        return `### ${path}\n\`\`\`\n${preview}${content.length > 1500 ? "\n... (truncated)" : ""}\n\`\`\``;
      })
      .join("\n\n");

    const prompt = `Please perform a **proactive code review** on my open files. For each file, identify:
1. 🐛 **Bugs** or potential runtime errors
2. ⚡ **Performance** improvements
3. 🔒 **Security** concerns
4. 🧹 **Code quality** issues (dead code, complexity, naming)
5. ✅ **Quick wins** — improvements I can make in under 5 minutes

Here are my open files:

${fileSummaries}

Provide actionable, specific suggestions for each issue you find.`;

    try {
      await sendPrompt(prompt);
    } finally {
      setIsReviewing(false);
    }
  };

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const data = await ProjectService.getProject(projectId);
        setProject(data);
      } catch (error) {
        console.error("Failed to fetch project:", error);
      } finally {
        setIsLoading(false);
      }
    };

    const fetchFileTree = async () => {
      setIsLoadingFiles(true);
      try {
        const res = await fetch(`${apiBaseUrl}/projects/${projectId}/files`);
        const json = await res.json();
        if (json.success) {
          setFileTree(json.data || []);
        }
      } catch {
        // Silently fail - empty state shows message
      } finally {
        setIsLoadingFiles(false);
      }
    };

    if (projectId) {
      fetchProject();
      fetchFileTree();

      // Restore persisted terminal sessions (feature: session persistence)
      const storageKey = `terminal-sessions-${projectId}`;
      let restored = false;
      try {
        const saved: string[] = JSON.parse(sessionStorage.getItem(storageKey) || "[]");
        if (saved.length > 0) {
          const restored_sessions: TerminalSession[] = saved.map((sid, i) => ({
            id: `t-restored-${i}-${sid.slice(0, 6)}`,
            label: `Terminal ${i + 1}`,
            panes: [{ id: `p-restored-${i}`, sessionId: sid }],
          }));
          setTerminals(restored_sessions);
          setActiveTerminalId(restored_sessions[restored_sessions.length - 1].id);
          setFocusedSessionId(restored_sessions[restored_sessions.length - 1].panes[0].sessionId);
          restored = true;
        }
      } catch { /* ignore */ }

      if (!restored) createTerminal();

      // Poll git status every 8 s to keep file badge indicators fresh
      const gitPoll = setInterval(() => {
        fetch(`${apiBaseUrl}/projects/${projectId}/git/status`)
          .then((r) => r.json())
          .then((json) => {
            if (json.success && json.data) {
              setFileTree((prev) =>
                applyGitStatus(prev, json.data as Record<string, string>)
              );
            }
          })
          .catch(() => {});
      }, 8000);
      return () => clearInterval(gitPoll);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId]);

  // Poll for Monaco markers (diagnostics) and fetch git branch
  useEffect(() => {
    const interval = setInterval(() => {
      if (monacoRef.current && editorRef.current) {
        const markers = monacoRef.current.editor.getModelMarkers({});
        setProblems(markers);
      }
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Fetch current git branch on mount and every 15s
  useEffect(() => {
    if (!projectId) return;
    const fetchBranch = () => {
      fetch(`${apiBaseUrl}/projects/${projectId}/git/branch`)
        .then((r) => r.json())
        .then((json) => { if (json.success && json.data?.branch) setGitBranch(json.data.branch); })
        .catch(() => {});
    };
    fetchBranch();
    const branchPoll = setInterval(fetchBranch, 15000);
    return () => clearInterval(branchPoll);
  }, [projectId]);

  if (isLoading) {
    return (
      <div className="h-screen bg-background flex flex-col items-center justify-center gap-4">
        <div className="w-10 h-10 rounded-xl bg-surface-2 border border-border-subtle flex items-center justify-center">
          <Loader2 className="w-5 h-5 animate-spin text-accent" />
        </div>
        <p className="text-xs text-text-muted">Loading workspace…</p>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="h-screen bg-background flex flex-col items-center justify-center p-8 text-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-surface-2 border border-border-subtle flex items-center justify-center">
          <FileCode size={22} className="text-text-muted" />
        </div>
        <div>
          <h1 className="text-base font-semibold text-text-primary mb-1">Project not found</h1>
          <p className="text-xs text-text-muted">The project you are looking for does not exist or has been deleted.</p>
        </div>
        <Link href="/projects" className="text-xs text-accent hover:text-accent-hover transition-colors flex items-center gap-1.5">
          <ArrowLeft size={12} /> Back to Projects
        </Link>
      </div>
    );
  }

  const hasNode = fileTree.some((f) => f.name === "package.json") || 
                  fileTree.some((f) => f.name === "app" && f.children?.some((c) => c.name === "package.json"));
                  
  const hasPython = fileTree.some((f) => f.name === "requirements.txt" || f.name === "pyproject.toml" || f.name === "setup.py") ||
                    fileTree.some((f) => f.name === "app" && f.children?.some((c) => c.name === "requirements.txt" || c.name === "pyproject.toml"));

  return (
    <div {...getRootProps()} className={`h-screen flex flex-col bg-background text-foreground overflow-hidden font-sans relative${isZenMode ? " zen-mode" : ""}`}>
      <input {...getInputProps()} />
      {/* Drag & Drop Overlay */}
      {isDragActive && (
        <div className="absolute inset-0 z-50 drop-overlay m-2 rounded-xl flex items-center justify-center transition-all animate-fade-scale-in">
          <div className="glass-panel rounded-2xl px-8 py-6 flex flex-col items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-accent/15 border border-accent/30 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#a5b4fc" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
            </div>
            <div className="text-center">
              <h3 className="font-semibold text-sm text-text-primary">Drop files to upload</h3>
              <p className="text-xs text-text-muted mt-1">Files and folders will be added to the project workspace</p>
            </div>
          </div>
        </div>
      )}
      
      {isUploading && (
        <div className="absolute top-16 right-4 z-50 glass-panel rounded-xl px-4 py-2.5 flex items-center gap-3 animate-slide-in">
          <Loader2 size={14} className="animate-spin text-accent" />
          <span className="text-xs font-medium text-text-primary">Uploading files…</span>
        </div>
      )}

      <style jsx global>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
      `}</style>

      {/* Top Navbar */}
      <header className="h-12 navbar-glass flex items-center px-4 shrink-0 justify-between z-10 sticky top-0">
        <div className="flex items-center gap-3">
          <Link
            href="/projects"
            className="icon-btn"
            title="Back to projects"
          >
            <ArrowLeft size={15} />
          </Link>
          <div className="w-px h-4 bg-border-subtle" />
          <div className="flex flex-col leading-tight">
            <h1 className="text-[13px] font-semibold text-text-primary tracking-tight">
              {project.name}
            </h1>
            <span className="text-[10px] text-text-muted font-mono tracking-tight">
              {project.repository_url || "Local Workspace"}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Agent status pill */}
          <div className={`agent-pill ${isTyping ? "active" : ""}`}>
            <span
              className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                isTyping ? "bg-accent animate-pulse-dot" : "bg-emerald-500"
              }`}
            />
            {isTyping ? (
              <span className="flex items-center gap-1.5">
                <Brain size={10} className="text-indigo-300" />
                {currentAgentLabel
                  ? currentAgentLabel.length > 28
                    ? currentAgentLabel.slice(0, 26) + "…"
                    : currentAgentLabel
                  : "Agent Working…"}
              </span>
            ) : (
              <span>Agent Idle</span>
            )}
            <span className="w-px h-3 bg-border-subtle" />
            <select
              value={project.llm_model || "qwen2.5-coder:1.5b"}
              onChange={async (e) => {
                const newModel = e.target.value;
                setProject((prev) => (prev ? { ...prev, llm_model: newModel } : null));
                try {
                  await ProjectService.updateProject(projectId, { llm_model: newModel });
                  console.log(`AI Model switched to ${newModel}`);
                } catch {
                  console.error("Failed to update AI Model");
                }
              }}
              className="bg-surface-2 hover:bg-surface-3 border border-border-subtle text-accent font-medium text-[11px] rounded px-1.5 py-0.5 outline-none cursor-pointer transition-colors"
              title="Change active AI Model for this workspace"
            >
              <optgroup label="🦙 Ollama (Local Free CPU Models)">
                <option value="qwen2.5-coder:1.5b">Qwen 2.5 Coder 1.5B (Ollama - Default Fast CPU)</option>
                <option value="qwen2.5-coder:7b">Qwen 2.5 Coder 7B (Ollama - High Quality)</option>
                <option value="llama3.1:8b">Llama 3.1 8B (Ollama)</option>
                <option value="deepseek-r1:1.5b">DeepSeek R1 1.5B (Ollama Reasoning)</option>
              </optgroup>
              <optgroup label="☁️ Cloud Models">
                <option value="mistral-small-latest">Mistral Small (Cloud Free API)</option>
                <option value="mistral-large-latest">Mistral Large (Cloud Paid API)</option>
                <option value="gpt-4o">OpenAI GPT-4o</option>
                <option value="gpt-4o-mini">OpenAI GPT-4o Mini</option>
                <option value="gemini-2.0-flash">Google Gemini 2.0 Flash</option>
                <option value="claude-3-5-sonnet-20241022">Claude 3.5 Sonnet</option>
              </optgroup>
            </select>
          </div>

          {/* Layout toggles */}
          <div className="flex items-center gap-0.5 bg-surface-2 rounded-lg p-0.5 border border-border-subtle">
            <button
              onClick={toggleChatPanel}
              title="Toggle AI Assistant panel (Ctrl+B)"
              className={`icon-btn ${!isChatCollapsed ? "active" : ""}`}
            >
              <PanelLeft size={14} />
            </button>
            <button
              onClick={toggleTerminalPanel}
              title="Toggle Terminal panel (Ctrl+`)"
              className={`icon-btn ${!isTerminalCollapsed ? "active" : ""}`}
            >
              <PanelBottom size={14} />
            </button>
            <button
              onClick={toggleRepoPanel}
              title="Toggle Repository panel (Ctrl+E)"
              className={`icon-btn ${!isRepoCollapsed ? "active" : ""}`}
            >
              <PanelRight size={14} />
            </button>
          </div>

          <div className="w-px h-5 bg-border-subtle" />

          {/* Code Review */}
          <button
            onClick={handleCodeReview}
            disabled={isReviewing}
            title="AI Code Review — scan open files for bugs & improvements"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[11px] font-medium transition-all border border-border-subtle text-text-secondary hover:text-text-primary hover:bg-surface-hover disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isReviewing ? (
              <Loader2 size={12} className="animate-spin text-accent" />
            ) : (
              <Brain size={12} className="text-violet-400" />
            )}
            {isReviewing ? "Reviewing…" : "Code Review"}
          </button>

          {/* Run button — most prominent */}
          <button
            onClick={handleRunProject}
            disabled={isRunning}
            title="Run project"
            className="run-btn flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[11px]"
          >
            {isRunning ? <Loader2 size={12} className="animate-spin" /> : <Play size={12} />}
            Run
          </button>

          {/* Run Tests & Auto-Fix button */}
          <button
            id="run-tests-btn"
            onClick={async () => {
              if (!projectId || isRunningTests) return;
              setIsRunningTests(true);
              setTestRunResult(null);
              try {
                const res = await fetch(`${apiBaseUrl}/projects/${projectId}/run-tests`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ auto_fix: true }),
                });
                const data = await res.json();
                setTestRunResult({ passed: data.passed ?? false, summary: data.summary ?? "Tests complete." });
                if (data.hitl_workflow_id) {
                  setHitlPending({ workflowId: data.hitl_workflow_id, nodeName: data.hitl_node ?? "terminal" });
                }
              } catch {
                setTestRunResult({ passed: false, summary: "Failed to reach test runner." });
              } finally {
                setIsRunningTests(false);
              }
            }}
            disabled={isRunningTests}
            title="Run test suite and auto-fix failures with the AI agent"
            className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-[11px] font-medium transition-all border border-emerald-700/50 bg-emerald-900/20 text-emerald-400 hover:bg-emerald-800/30 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            {isRunningTests ? <Loader2 size={12} className="animate-spin" /> : <FlaskConical size={12} />}
            {isRunningTests ? "Testing…" : "Run Tests"}
          </button>

          <div className="w-px h-5 bg-border-subtle" />

          {/* Secondary actions */}
          <button onClick={handleIndexProject} disabled={isIndexing} title="Rebuild AI search index" className="icon-btn disabled:opacity-40">
            {isIndexing ? <Loader2 size={15} className="animate-spin" /> : <Database size={15} />}
          </button>
          <button onClick={() => setIsHistoryOpen(true)} title="Commit history & rollback" className="icon-btn">
            <HistoryIcon size={15} />
          </button>
          <button onClick={() => setTheme(theme === "dark" ? "light" : "dark")} title="Toggle Theme" className="icon-btn">
            {theme === "dark" ? <Sun size={15} /> : <Moon size={15} />}
          </button>
          <button onClick={() => setIsDashboardOpen(true)} title="Project Dashboard" className="icon-btn">
            <BarChart3 size={15} />
          </button>
          <button onClick={() => setIsShortcutsOpen(true)} title="Keyboard shortcuts (?)" className="icon-btn text-[13px] font-semibold">
            ?
          </button>
          <button onClick={() => setIsSettingsOpen(true)} title="Settings" className="icon-btn">
            <Settings size={15} />
          </button>
        </div>
      </header>

      {/* ── HITL Approval Banner ── */}
      {hitlPending && (
        <div className="flex items-center gap-3 px-4 py-2.5 bg-amber-900/20 border-b border-amber-700/40 shrink-0 z-20">
          <ShieldAlert size={15} className="text-amber-400 shrink-0" />
          <div className="flex-1">
            <span className="text-xs font-semibold text-amber-300">Agent paused — awaiting approval</span>
            <span className="ml-2 text-[11px] text-amber-500/80">High-risk action on node: <code className="font-mono">{hitlPending.nodeName}</code></span>
          </div>
          <button
            id="hitl-approve-btn"
            onClick={async () => {
              setIsHitlActioning(true);
              try {
                await fetch(`${apiBaseUrl}/hitl/${hitlPending.workflowId}/approve`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ comment: "Approved via UI" }) });
                setHitlPending(null);
              } finally { setIsHitlActioning(false); }
            }}
            disabled={isHitlActioning}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[11px] font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-colors disabled:opacity-50"
          >
            {isHitlActioning ? <Loader2 size={11} className="animate-spin" /> : <ShieldCheck size={11} />}
            Approve
          </button>
          <button
            id="hitl-reject-btn"
            onClick={async () => {
              setIsHitlActioning(true);
              try {
                await fetch(`${apiBaseUrl}/hitl/${hitlPending.workflowId}/reject`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ reason: "Rejected via UI" }) });
                setHitlPending(null);
              } finally { setIsHitlActioning(false); }
            }}
            disabled={isHitlActioning}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-md text-[11px] font-semibold bg-red-700/80 hover:bg-red-600 text-white transition-colors disabled:opacity-50"
          >
            <ShieldX size={11} />
            Reject
          </button>
        </div>
      )}

      {/* Test Run Result Toast */}
      {testRunResult && (
        <div className={`flex items-center gap-2 px-4 py-2 border-b shrink-0 text-[11px] ${
          testRunResult.passed
            ? "bg-emerald-900/15 border-emerald-700/30 text-emerald-300"
            : "bg-red-900/15 border-red-700/30 text-red-300"
        }`}>
          {testRunResult.passed
            ? <CheckCircle2 size={13} className="text-emerald-400 shrink-0" />
            : <AlertCircle size={13} className="text-red-400 shrink-0" />}
          <span className="flex-1">{testRunResult.summary}</span>
          <button onClick={() => setTestRunResult(null)} className="text-text-muted hover:text-text-primary p-0.5"><X size={12} /></button>
        </div>
      )}

      {/* Main Workspace Layout */}
      <PanelGroup direction="vertical" className="flex-1 min-h-0">
        <Panel defaultSize={75} minSize={30}>
          <PanelGroup direction="horizontal" className="h-full">
            <Panel
              ref={chatPanelRef}
              defaultSize={20}
              minSize={15}
              maxSize={40}
              collapsible
              collapsedSize={0}
              onCollapse={() => setIsChatCollapsed(true)}
              onExpand={() => setIsChatCollapsed(false)}
            >
              {/* Left Panel: Chat Interface */}
              <aside className="h-full border-r border-border-subtle bg-surface-1 flex flex-col">
                {/* Panel header */}
                <div className="h-10 border-b border-border-subtle flex items-center px-4 gap-3 shrink-0">
                  <div className="w-6 h-6 rounded-lg bg-accent/15 border border-accent/20 flex items-center justify-center">
                    <MessageSquare size={12} className="text-accent" />
                  </div>
                  <h2 className="text-[11px] font-semibold text-text-primary uppercase tracking-widest">AI Assistant</h2>
                  {isReviewing && (
                    <span className="ml-auto flex items-center gap-1 text-[10px] text-violet-400 animate-pulse">
                      <Brain size={10} />
                      Reviewing…
                    </span>
                  )}
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
                  {messages.map((msg) => (
                    <div key={msg.id} className={`flex gap-2.5 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                      {/* Avatar */}
                      {msg.role === "assistant" ? (
                        <div className="agent-avatar-ring w-7 h-7 shrink-0">
                          <div className="agent-avatar-inner w-full h-full">
                            <span className="text-[9px] font-bold text-accent">AI</span>
                          </div>
                        </div>
                      ) : (
                        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-violet-600 to-purple-700 flex items-center justify-center shrink-0 text-white text-[9px] font-bold">
                          U
                        </div>
                      )}
                      <div className={`max-w-[86%] ${
                        msg.role === "user"
                          ? "chat-bubble-user text-sm"
                          : "chat-bubble-agent text-sm"
                        }`}
                      >
                        {msg.images && msg.images.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-2">
                            {msg.images.map((img, idx) => (
                              <img key={idx} src={img} alt="attached" className="max-w-full h-auto rounded-lg max-h-48 object-contain border border-white/10" />
                            ))}
                          </div>
                        )}
                        <div className={`prose prose-sm max-w-none space-y-2 break-words prose-chat ${
                          msg.role === "user" ? "prose-invert" : "dark:prose-invert"
                        }`}>
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              code({ node, className, children, ...props }: any) {
                                return <CodeBlock className={className} {...props}>{children}</CodeBlock>;
                              },
                            }}
                          >
                            {msg.content}
                          </ReactMarkdown>
                        </div>
                        {msg.activities && msg.activities.length > 0 && (
                          <AgentActivityLog activities={msg.activities} />
                        )}
                        {msg.modifiedFiles && msg.modifiedFiles.length > 0 && (
                          <div className="mt-2 pt-2 border-t border-border-subtle">
                            <p className="text-[10px] text-emerald-400 font-semibold mb-1.5 flex items-center gap-1">
                              <svg xmlns="http://www.w3.org/2000/svg" width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12" /></svg>
                              {msg.modifiedFiles.length} file{msg.modifiedFiles.length > 1 ? "s" : ""} written
                            </p>
                            <div className="flex flex-col gap-0.5">
                              {msg.modifiedFiles.map((f) => (
                                <div key={f} className="flex items-center justify-between text-[10px] font-mono group/file">
                                  <button
                                    onClick={() => handleFileClick(f)}
                                    className="text-accent hover:text-accent-hover hover:underline truncate"
                                  >
                                    📄 {f}
                                  </button>
                                  <button
                                    onClick={() => setDiffFile(f)}
                                    className="opacity-0 group-hover/file:opacity-100 text-text-muted hover:text-text-secondary transition-opacity ml-2 px-1 py-0.5 rounded hover:bg-surface-hover"
                                    title="View Diff"
                                  >
                                    Diff
                                  </button>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}

                  {/* Suggested prompts shown only before the conversation has started */}
                  {messages.length === 1 && !isTyping && (
                    <div className="flex flex-wrap gap-2 pl-10 animate-fade-in-up">
                      {SUGGESTED_PROMPTS.map((s) => (
                        <button
                          key={s}
                          onClick={() => sendPrompt(s)}
                          className="suggestion-chip"
                        >
                          <Sparkles size={9} className="text-accent opacity-70" />
                          {s}
                        </button>
                      ))}
                    </div>
                  )}

                  {isTyping && (
                    <div className="flex gap-2.5">
                      <div className="agent-avatar-ring w-7 h-7 shrink-0">
                        <div className="agent-avatar-inner w-full h-full">
                          <span className="text-[9px] font-bold text-accent">AI</span>
                        </div>
                      </div>
                      <div className="chat-bubble-agent flex items-center gap-1.5">
                        <span className="w-1.5 h-1.5 bg-accent/60 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                        <span className="w-1.5 h-1.5 bg-accent/60 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                        <span className="w-1.5 h-1.5 bg-accent/60 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
                <div className="px-3 pb-3 border-t border-border-subtle">
                  {chatImages.length > 0 && (
                    <div className="flex gap-2 mb-2 overflow-x-auto pb-1 pt-2">
                      {chatImages.map((img, idx) => (
                        <div key={idx} className="relative shrink-0">
                          <img src={img} alt="upload preview" className="h-14 w-14 object-cover rounded-lg border border-border-subtle" />
                          <button
                            onClick={() => setChatImages(prev => prev.filter((_, i) => i !== idx))}
                            className="absolute -top-1.5 -right-1.5 bg-surface-3 hover:bg-error/20 text-text-muted hover:text-error rounded-full p-0.5 border border-border-subtle transition-colors"
                          >
                            <X size={10} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="cmd-bar mt-2">
                    <textarea
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      onPaste={(e) => {
                        const items = e.clipboardData.items;
                        for (let i = 0; i < items.length; i++) {
                          if (items[i].type.indexOf("image") !== -1) {
                            const blob = items[i].getAsFile();
                            if (blob) {
                              const reader = new FileReader();
                              reader.onload = (ev) => {
                                if (ev.target?.result) {
                                  setChatImages(prev => [...prev, ev.target!.result as string]);
                                }
                              };
                              reader.readAsDataURL(blob);
                            }
                          }
                        }
                      }}
                      placeholder="Ask the agent to do something…"
                      className="w-full bg-transparent pl-10 pr-20 py-3 text-sm resize-none h-20 focus:outline-none text-text-primary placeholder:text-text-muted font-sans"
                    />
                    {/* Image upload */}
                    <label className="absolute left-3 bottom-3 p-1.5 text-text-muted hover:text-text-primary cursor-pointer transition-colors rounded-md hover:bg-surface-hover">
                      <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
                      <input
                        type="file"
                        accept="image/*"
                        className="hidden"
                        multiple
                        onChange={(e) => {
                          const files = e.target.files;
                          if (!files) return;
                          Array.from(files).forEach(file => {
                            const reader = new FileReader();
                            reader.onload = (ev) => {
                              if (ev.target?.result) setChatImages(prev => [...prev, ev.target!.result as string]);
                            };
                            reader.readAsDataURL(file);
                          });
                          e.target.value = "";
                        }}
                      />
                    </label>
                    {/* Mic */}
                    <button
                      onClick={toggleRecording}
                      title="Dictate message"
                      className={`absolute right-12 bottom-3 p-1.5 rounded-md transition-all ${
                        isRecording
                          ? "bg-red-500/20 text-red-400 animate-pulse"
                          : "text-text-muted hover:text-text-primary hover:bg-surface-hover"
                      }`}
                    >
                      <Mic size={14} />
                    </button>
                    {/* Send / Stop */}
                    {isTyping ? (
                      <button
                        onClick={() => abortControllerRef.current?.abort()}
                        title="Stop generation"
                        className="absolute right-3 bottom-3 p-1.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-md transition-colors flex items-center justify-center"
                        style={{ width: "30px", height: "30px" }}
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="6" y="6" width="12" height="12" rx="2" ry="2"/></svg>
                      </button>
                    ) : (
                      <button
                        onClick={handleSendMessage}
                        disabled={!chatInput.trim() && chatImages.length === 0}
                        className="absolute right-3 bottom-3 p-1.5 bg-accent hover:bg-accent-hover disabled:opacity-30 disabled:cursor-not-allowed text-white rounded-md transition-all flex items-center justify-center hover:shadow-lg hover:shadow-accent/20"
                        style={{ width: "30px", height: "30px" }}
                      >
                        <Send size={13} />
                      </button>
                    )}
                  </div>
                </div>

                {/* Quick Action Chips */}
                <div className="px-3 pb-3 flex flex-wrap gap-1.5">
                  {[
                    { label: "Explain", icon: "✨", prompt: selectedFile ? `Explain what the file \`${selectedFile}\` does, its purpose, and key concepts.` : "Explain what this project does." },
                    { label: "Add tests", icon: "🧪", prompt: selectedFile ? `Write comprehensive unit tests for \`${selectedFile}\`. Include edge cases.` : "Write unit tests for the main functionality of this project." },
                    { label: "Add types", icon: "📝", prompt: selectedFile ? `Add TypeScript types and interfaces to \`${selectedFile}\` wherever they are missing.` : "Add TypeScript types to all files that are missing them." },
                    { label: "Optimize", icon: "⚡", prompt: selectedFile ? `Review \`${selectedFile}\` and suggest performance optimizations.` : "Suggest performance optimizations for this project." },
                    { label: "Add docs", icon: "📚", prompt: selectedFile ? `Add JSDoc/docstring comments to all functions and classes in \`${selectedFile}\`.` : "Add documentation comments to the main functions in this project." },
                  ].map(({ label, icon, prompt }) => (
                    <button
                      key={label}
                      onClick={() => sendPrompt(prompt)}
                      disabled={isTyping}
                      className="action-chip"
                    >
                      <span>{icon}</span>
                      {label}
                    </button>
                  ))}
                </div>
              </aside>
            </Panel>

            <PanelResizeHandle className="w-1 bg-gray-200 dark:bg-gray-800 hover:bg-blue-500 cursor-col-resize transition-colors" />

            <Panel defaultSize={60} minSize={30}>
              {/* Center Panel: Editor */}
              <section className="h-full flex flex-col min-w-0 bg-background">
                <div className="flex-1 relative overflow-hidden flex">
                  {/* Primary editor pane */}
                  <div
                    className={`relative overflow-hidden flex flex-col flex-1 ${isSplitMode ? "border-r border-border-subtle" : ""}`}
                    onClick={() => setActiveEditorPane("primary")}
                  >
                    {isSplitMode && (
                      <div className={`absolute top-0 left-0 right-0 h-0.5 z-10 transition-all ${activeEditorPane === "primary" ? "bg-accent" : "bg-transparent"}`} />
                    )}
                <div
                  className="h-10 border-b border-gray-800 flex items-center overflow-x-auto overflow-y-hidden no-scrollbar shrink-0"
                  style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
                >
                  {/* Save button — only when a file is open */}
                  {selectedFile && (
                    <button
                      onClick={saveCurrentFile}
                      disabled={isSavingFile}
                      title="Save file (Ctrl+S)"
                      className="shrink-0 flex items-center gap-1.5 px-3 h-full text-xs border-r border-border-subtle text-text-muted hover:text-text-primary transition-colors disabled:opacity-50"
                    >
                      {isSavingFile ? (
                        <Loader2 size={13} className="animate-spin" />
                      ) : (
                        <Save size={13} />
                      )}
                      {fileSaveMsg ?? "Save"}
                    </button>
                  )}
                  {openTabs.length === 0 && (
                    <div className="px-4 text-sm text-gray-500 shrink-0">
                      No file selected
                    </div>
                  )}

                  {openTabs.map((path) => {
                    const isDirty = dirtyTabs.has(path);
                    return (
                    <div
                      key={path}
                      onClick={() => {
                        setSelectedFile(path);
                        setEditorLanguage(getLanguageFromPath(path));
                        // Switch Monaco model
                        const model = monacoModels.current.get(path);
                        if (editorRef.current && model) editorRef.current.setModel(model);
                      }}
                      title={path}
                      className={`flex items-center gap-2 px-3 h-full cursor-pointer border-r border-border-subtle shrink-0 whitespace-nowrap group/tab transition-colors ${
                        selectedFile === path
                          ? "bg-surface-2 text-text-primary border-t-2 border-t-accent"
                          : "bg-surface-1 text-text-secondary hover:bg-surface-hover"
                      }`}
                    >
                      <FileCode size={13} className={`shrink-0 ${fileIconColor(path.split("/").pop() || "")}`} />
                      <span className="text-xs">{getTabLabel(path, openTabs)}</span>
                      {isDirty && (
                        <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 shrink-0" title="Unsaved changes" />
                      )}
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          const tabs = openTabs.filter((t) => t !== path);
                          setOpenTabs(tabs);
                          // Dispose the Monaco model for closed tab
                          const model = monacoModels.current.get(path);
                          if (model) { model.dispose(); monacoModels.current.delete(path); }
                          setDirtyTabs((prev) => { const next = new Set(prev); next.delete(path); return next; });
                          if (selectedFile === path) {
                            if (tabs.length > 0) {
                              const nextPath = tabs[tabs.length - 1];
                              setSelectedFile(nextPath);
                              setEditorLanguage(getLanguageFromPath(nextPath));
                              const nextModel = monacoModels.current.get(nextPath);
                              if (editorRef.current && nextModel) editorRef.current.setModel(nextModel);
                            } else {
                              setSelectedFile(null);
                            }
                          }
                        }}
                        className="shrink-0 opacity-50 group-hover/tab:opacity-100 hover:text-white transition-opacity ml-1"
                      >
                        <X size={12} />
                      </button>
                    </div>
                    );
                  })}
                  
                  <div
                      onClick={() => setSelectedFile("__preview__")}
                      title="Web Preview"
                      className={`flex items-center gap-2 px-4 h-full cursor-pointer border-r border-border-subtle shrink-0 whitespace-nowrap ${selectedFile === "__preview__"
                          ? "bg-surface-2 text-text-primary"
                          : "bg-surface-1 text-text-secondary"
                        }`}
                  >
                    <Play size={14} className="shrink-0 text-green-400" />
                    <span className="text-sm">Preview</span>
                  </div>

                  {/* Split button — pinned to far right */}
                  <div className="ml-auto flex items-center border-l border-border-subtle px-1 shrink-0">
                    {isSplitMode ? (
                      <button
                        onClick={() => { setIsSplitMode(false); setSecondarySelectedFile(null); setActiveEditorPane("primary"); }}
                        title="Close split view"
                        className="p-1.5 rounded text-accent hover:bg-accent/10 transition-colors"
                      >
                        <X size={13} />
                      </button>
                    ) : (
                      <button
                        onClick={() => { setIsSplitMode(true); setSecondarySelectedFile(selectedFile); setActiveEditorPane("secondary"); }}
                        title="Split editor right"
                        className="p-1.5 rounded text-text-muted hover:text-text-primary hover:bg-surface-hover transition-colors"
                      >
                        <SplitSquareHorizontal size={13} />
                      </button>
                    )}
                  </div>

                </div>

                {/* Breadcrumb bar */}
                {selectedFile && selectedFile !== "__preview__" && (
                  <div className="h-7 bg-surface-1 border-b border-border-subtle flex items-center px-3 gap-1 text-[11px] text-text-muted shrink-0 overflow-x-auto no-scrollbar">
                    {selectedFile.split("/").map((segment, i, arr) => (
                      <React.Fragment key={i}>
                        {i < arr.length - 1 ? (
                          <>
                            <span className="hover:text-text-primary cursor-pointer transition-colors">{segment}</span>
                            <span className="text-border-subtle mx-0.5 select-none">/</span>
                          </>
                        ) : (
                          <span className="text-text-primary font-medium">{segment}</span>
                        )}
                      </React.Fragment>
                    ))}
                    {dirtyTabs.has(selectedFile) && (
                      <span className="ml-1.5 text-yellow-400 text-[9px] font-bold">● UNSAVED</span>
                    )}
                  </div>
                )}

                    <div className="flex-1 relative overflow-hidden">
                    {selectedFile === "__preview__" ? (
                      <PreviewPanel defaultPort={3000} />
                    ) : selectedFile ? (
                      <Editor
                        height="100%"
                        language={editorLanguage}
                        theme="vs-dark"
                        value={fileContents[selectedFile] || ""}
                        onChange={(value) => {
                          if (!selectedFile) return;
                          setFileContents((prev) => ({ ...prev, [selectedFile]: value || "" }));
                          setDirtyTabs((prev) => new Set([...prev, selectedFile]));
                        }}
                        options={{
                          minimap: { enabled: false },
                          fontSize: editorFontSize,
                          wordWrap: "on",
                          lineNumbers: "on",
                          scrollBeyondLastLine: false,
                          padding: { top: 16 },
                          fontFamily: "var(--font-mono)",
                          cursorSmoothCaretAnimation: "on",
                          smoothScrolling: true,
                          renderWhitespace: "selection",
                          automaticLayout: true,
                          // Clean up hover / problem popups ("View Problem (Alt+F8)"):
                          hover: {
                            enabled: true,
                            delay: 500,
                            sticky: true,
                          },
                          quickSuggestions: {
                            other: true,
                            comments: false,
                            strings: false,
                          },
                          lightbulb: {
                            enabled: "off",
                          },
                        }}
                        onMount={(editor, monaco) => {
                          editorRef.current = editor;
                          monacoRef.current = monaco;

                          // Disable client-side TypeScript module resolution errors (e.g. Cannot find module 'mongoose')
                          // which produce intrusive red squiggles and "View Problem (Alt+F8)" tooltips
                          try {
                            monaco.languages.typescript.typescriptDefaults.setDiagnosticsOptions({
                              noSemanticValidation: true,
                              noSyntaxValidation: false,
                            });
                            monaco.languages.typescript.javascriptDefaults.setDiagnosticsOptions({
                              noSemanticValidation: true,
                              noSyntaxValidation: false,
                            });
                          } catch (_) {}

                          // Track cursor position for status bar
                          editor.onDidChangeCursorPosition((e) => {
                            setCursorPosition({ line: e.position.lineNumber, column: e.position.column });
                          });

                          if (selectedFile && fileContents[selectedFile] !== undefined) {
                            const uri = monaco.Uri.file(selectedFile);
                            let model = monaco.editor.getModel(uri);
                            if (!model) {
                              model = monaco.editor.createModel(
                                fileContents[selectedFile],
                                getLanguageFromPath(selectedFile),
                                uri
                              );
                            } else {
                              model.setValue(fileContents[selectedFile]);
                            }
                            monacoModels.current.set(selectedFile, model);
                            editor.setModel(model);
                          }

                          const sendSelectionToAI = (promptPrefix: string) => {
                            const selection = editor.getModel()?.getValueInRange(editor.getSelection()!);
                            if (selection && selection.trim()) {
                              sendPrompt(`${promptPrefix} from ${selectedFile}:\n\`\`\`\n${selection}\n\`\`\``);
                              const panel = chatPanelRef.current;
                              if (panel && panel.isCollapsed()) panel.expand();
                            }
                          };

                          editor.addAction({ id: "ai-explain", label: "AI: Explain Code", contextMenuGroupId: "navigation", contextMenuOrder: 1, run: () => sendSelectionToAI("Explain this code") });
                          editor.addAction({ id: "ai-refactor", label: "AI: Refactor Code", contextMenuGroupId: "navigation", contextMenuOrder: 2, run: () => sendSelectionToAI("Refactor this code to be cleaner and more robust") });
                          editor.addAction({ id: "ai-fix", label: "AI: Fix Bugs", contextMenuGroupId: "navigation", contextMenuOrder: 3, run: () => sendSelectionToAI("Find and fix any bugs in this code") });
                          editor.addAction({ id: "ai-open-diff", label: "AI: View Diff", contextMenuGroupId: "navigation", contextMenuOrder: 4, run: () => { if (selectedFile) setDiffFile(selectedFile); } });
                          editor.addAction({
                            id: "ai-inline-edit",
                            label: "AI: Inline Edit",
                            keybindings: [monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyK],
                            contextMenuGroupId: "navigation",
                            contextMenuOrder: 0,
                            run: (ed) => {
                              const selection = ed.getSelection();
                              if (!selection) return;
                              const position = ed.getScrolledVisiblePosition(selection.getEndPosition());
                              if (position) {
                                setInlineEditPosition({ top: position.top + 30, left: position.left });
                                setInlineEditSelection(selection);
                                setIsInlineEditOpen(true);
                                setTimeout(() => document.getElementById("inline-edit-input")?.focus(), 50);
                              }
                            }
                          });
                        }}
                        loading={<div className="p-6 text-gray-500">Loading editor...</div>}
                      />
                    ) : (
                      <div className="h-full flex flex-col items-center justify-center text-center px-8 gap-5">
                        <div className="w-16 h-16 rounded-2xl bg-surface-2 border border-border-subtle flex items-center justify-center animate-float">
                          <FileCode size={28} className="text-text-muted" />
                        </div>
                        <div>
                          <p className="text-sm font-medium text-text-secondary mb-1">No file open</p>
                          <p className="text-xs text-text-muted max-w-xs leading-relaxed">
                            Select a file from the explorer, or ask the AI agent to create one.
                          </p>
                        </div>
                      </div>
                    )}
                    {isInlineEditOpen && (
                      <div
                        className="absolute z-50 bg-[#1e1e1e] border border-gray-700 shadow-xl rounded-lg p-2 w-[400px] flex flex-col gap-2 transition-all duration-200"
                        style={{ top: Math.max(10, inlineEditPosition.top), left: Math.max(10, Math.min(inlineEditPosition.left, 400)) }}
                      >
                        <div className="flex items-center gap-2 px-1">
                          <Sparkles size={14} className="text-purple-400" />
                          <span className="text-xs font-semibold text-gray-300">Inline AI Edit</span>
                          <button onClick={() => setIsInlineEditOpen(false)} className="ml-auto text-gray-500 hover:text-gray-300">
                            <X size={14} />
                          </button>
                        </div>
                        <div className="flex items-center gap-2">
                          <input
                            id="inline-edit-input"
                            type="text"
                            value={inlineEditPrompt}
                            onChange={(e) => setInlineEditPrompt(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                handleInlineEditSubmit();
                              } else if (e.key === "Escape") {
                                setIsInlineEditOpen(false);
                              }
                            }}
                            disabled={isInlineEditing}
                            placeholder="What do you want to change?"
                            className="flex-1 bg-[#252526] border border-gray-700 rounded p-1.5 text-sm text-gray-200 focus:outline-none focus:border-blue-500 disabled:opacity-50"
                          />
                          <button
                            onClick={handleInlineEditSubmit}
                            disabled={isInlineEditing || !inlineEditPrompt.trim()}
                            className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded p-1.5 transition-colors"
                          >
                            {isInlineEditing ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
                          </button>
                        </div>
                      </div>
                    )}
                    </div>
                  </div>

                  {/* Secondary editor pane (split mode) */}
                  {isSplitMode && (
                    <div
                      className="relative flex-1 overflow-hidden flex flex-col"
                      onClick={() => setActiveEditorPane("secondary")}
                    >
                      <div className={`absolute top-0 left-0 right-0 h-0.5 z-10 transition-all ${activeEditorPane === "secondary" ? "bg-accent" : "bg-transparent"}`} />
                      
                      {/* Secondary tab bar (single tab) */}
                      <div className="h-10 border-b border-gray-800 flex items-center overflow-x-auto overflow-y-hidden no-scrollbar shrink-0" style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}>
                        {secondarySelectedFile ? (
                          <div className="flex items-center gap-2 px-3 h-full cursor-pointer border-r border-border-subtle shrink-0 whitespace-nowrap bg-surface-2 text-text-primary border-t-2 border-t-accent">
                            <FileCode size={13} className={`shrink-0 ${fileIconColor(secondarySelectedFile.split("/").pop() || "")}`} />
                            <span className="text-xs">{secondarySelectedFile.split("/").pop()}</span>
                            {dirtyTabs.has(secondarySelectedFile) && (
                              <span className="w-1.5 h-1.5 rounded-full bg-yellow-400 shrink-0" title="Unsaved changes" />
                            )}
                            <button
                              onClick={(e) => { e.stopPropagation(); setIsSplitMode(false); setSecondarySelectedFile(null); setActiveEditorPane("primary"); }}
                              className="shrink-0 opacity-50 hover:opacity-100 hover:text-white transition-opacity ml-1"
                              title="Close split pane"
                            >
                              <X size={12} />
                            </button>
                          </div>
                        ) : (
                          <div className="px-4 text-sm text-gray-500 shrink-0">
                            No file selected
                          </div>
                        )}
                      </div>

                      {/* Secondary breadcrumb bar */}
                      {secondarySelectedFile && (
                        <div className="h-7 bg-surface-1 border-b border-border-subtle flex items-center px-3 gap-1 text-[11px] text-text-muted shrink-0 overflow-x-auto no-scrollbar">
                          {secondarySelectedFile.split("/").map((segment, i, arr) => (
                            <React.Fragment key={i}>
                              {i < arr.length - 1 ? (
                                <>
                                  <span className="hover:text-text-primary cursor-pointer transition-colors">{segment}</span>
                                  <span className="text-border-subtle mx-0.5 select-none">/</span>
                                </>
                              ) : (
                                <span className="text-text-primary font-medium">{segment}</span>
                              )}
                            </React.Fragment>
                          ))}
                          {dirtyTabs.has(secondarySelectedFile) && (
                            <span className="ml-1.5 text-yellow-400 text-[9px] font-bold">● UNSAVED</span>
                          )}
                        </div>
                      )}

                      {secondarySelectedFile ? (
                        <div className="flex-1 overflow-hidden relative">
                          <Editor
                            height="100%"
                            language={getLanguageFromPath(secondarySelectedFile)}
                          theme="vs-dark"
                          value={fileContents[secondarySelectedFile] || ""}
                          onChange={(value) => {
                            if (!secondarySelectedFile) return;
                            setFileContents((prev) => ({ ...prev, [secondarySelectedFile]: value || "" }));
                            setDirtyTabs((prev) => new Set([...prev, secondarySelectedFile]));
                          }}
                          options={{
                            minimap: { enabled: false },
                            fontSize: 14,
                            wordWrap: "on",
                            lineNumbers: "on",
                            scrollBeyondLastLine: false,
                            padding: { top: 8 },
                            fontFamily: "var(--font-mono)",
                            cursorSmoothCaretAnimation: "on",
                            smoothScrolling: true,
                            renderWhitespace: "selection",
                            automaticLayout: true,
                          }}
                          onMount={(editor) => {
                            secondaryEditorRef.current = editor;
                            const model = monacoModels.current.get(secondarySelectedFile);
                            if (model) editor.setModel(model);
                          }}
                          loading={<div className="p-6 text-gray-500">Loading editor...</div>}
                        />
                        </div>
                      ) : (
                        <div className="h-full flex flex-col items-center justify-center text-center px-8">
                          <SplitSquareHorizontal size={36} className="text-gray-700 mb-3" />
                          <p className="text-sm text-gray-500 mb-1">Split view active</p>
                          <p className="text-xs text-gray-600 max-w-xs">
                            Click a file in the sidebar to open it here.
                          </p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </section>
            </Panel>

            <PanelResizeHandle className="w-1 bg-gray-200 dark:bg-gray-800 hover:bg-blue-500 cursor-col-resize transition-colors" />

<Panel
              ref={repoPanelRef}
              defaultSize={20}
              minSize={15}
              maxSize={35}
              collapsible
              collapsedSize={0}
              onCollapse={() => setIsRepoCollapsed(true)}
              onExpand={() => setIsRepoCollapsed(false)}
            >
              {/* Right Panel: File Explorer + Git */}
              <aside className="h-full border-l border-border-subtle bg-surface-1 flex flex-col">
                {/* Tab bar */}
                <div className="h-9 border-b border-border-subtle flex items-center shrink-0 px-1">
                  <button
                    onClick={() => setRightTab("files")}
                    className={`panel-tab ${rightTab === "files" ? "active" : ""}`}
                  >
                    <Folder size={11} />
                    Files
                  </button>
                  <button
                    onClick={() => setRightTab("search")}
                    title="Search across files (Ctrl+Shift+F)"
                    className={`panel-tab ${rightTab === "search" ? "active" : ""}`}
                  >
                    <Search size={11} />
                    Search
                  </button>
                  <button
                    onClick={() => setRightTab("git")}
                    className={`panel-tab ${rightTab === "git" ? "active" : ""}`}
                  >
                    <GitBranch size={11} />
                    Git
                  </button>
                </div>

                {rightTab === "files" ? (
                  <>
                    <div className="panel-header justify-between">
                      <span>Explorer</span>
                      <div className="flex items-center gap-0.5">
                        <button
                          onClick={() => { setFileInputName(""); setFileActionModal({ type: "create_file", path: "" }); }}
                          className="icon-btn"
                          title="New File"
                        >
                          <FilePlus size={12} />
                        </button>
                        <button
                          onClick={() => { setFileInputName(""); setFileActionModal({ type: "create_folder", path: "" }); }}
                          className="icon-btn"
                          title="New Folder"
                        >
                          <FolderPlus size={12} />
                        </button>
                        <button
                          onClick={() => setIsCommandPaletteOpen(true)}
                          className="icon-btn"
                          title="Go to file (Ctrl+P)"
                        >
                          <Search size={12} />
                        </button>
                        <button
                          onClick={refreshFileTree}
                          className="icon-btn"
                          title="Refresh files"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21 2v6h-6" />
                            <path d="M3 12a9 9 0 0 1 15-6.7L21 8" />
                            <path d="M3 22v-6h6" />
                            <path d="M21 12a9 9 0 0 1-15 6.7L3 16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div className="flex-1 py-1 overflow-y-auto">
                      {isLoadingFiles ? (
                        <div className="flex items-center justify-center h-20">
                          <Loader2 size={14} className="animate-spin text-text-muted" />
                        </div>
                      ) : fileTree.length === 0 ? (
                        <div className="px-4 py-8 text-center flex flex-col items-center gap-2">
                          <div className="w-10 h-10 rounded-xl bg-surface-2 border border-border-subtle flex items-center justify-center">
                            <FileCode size={18} className="text-text-muted" />
                          </div>
                          <p className="text-xs text-text-muted">No files yet.</p>
                          <button
                            onClick={() => { setFileInputName(""); setFileActionModal({ type: "create_file", path: "" }); }}
                            className="text-[11px] text-accent hover:text-accent-hover transition-colors"
                          >
                            + Create first file
                          </button>
                        </div>
                      ) : (
                        fileTree.map((node) => (
                          <FileNodeItem
                            key={node.path}
                            node={node}
                            depth={0}
                            selectedPath={selectedFile}
                            onFileClick={handleFileClick}
                            onCreateFile={(parentPath) => { setFileInputName(""); setFileActionModal({ type: "create_file", path: parentPath || "" }); }}
                            onCreateFolder={(parentPath) => { setFileInputName(""); setFileActionModal({ type: "create_folder", path: parentPath || "" }); }}
                            onRename={(path, name) => { setFileInputName(name); setFileActionModal({ type: "rename", path, name }); }}
                            onDelete={(path) => setFileActionModal({ type: "delete", path })}
                            onContextMenu={handleContextMenu}
                          />
                        ))
                      )}
                    </div>
                  </>
                ) : rightTab === "search" ? (
                  <div className="flex-1 min-h-0 overflow-hidden flex flex-col">
                    <SearchPanel
                      projectId={projectId}
                      onFileOpen={handleFileClick}
                    />
                  </div>
                ) : (
                  <div className="flex-1 min-h-0 overflow-hidden flex flex-col">
                    <GitPanel projectId={projectId} />
                  </div>
                )}
              </aside>
            </Panel>
          </PanelGroup>
        </Panel>

        <PanelResizeHandle className="resize-handle-v" />

        <Panel
          ref={terminalPanelRef}
          defaultSize={isTerminalMaximized ? 80 : 25}
          minSize={10}
          maxSize={isTerminalMaximized ? 85 : 60}
          collapsible
          collapsedSize={0}
          onCollapse={() => setIsTerminalCollapsed(true)}
          onExpand={() => setIsTerminalCollapsed(false)}
        >
          {/* Bottom Panel: Terminal/Logs */}
          <footer className="h-full border-t border-border-subtle bg-surface-1 flex flex-col" style={{ boxShadow: "0 -1px 0 rgba(0,0,0,0.3)" }}>
            {/* Tab bar */}
            <div className="h-9 border-b border-border-subtle flex items-center pl-1 pr-2 gap-0 overflow-x-auto no-scrollbar flex-shrink-0">
              {/* Terminal tabs */}
              <div className="flex items-center flex-1 min-w-0 overflow-x-auto no-scrollbar h-full">
                <div
                  onClick={() => setBottomTab("problems")}
                  className={`panel-tab ${bottomTab === "problems" ? "active" : ""} cursor-pointer`}
                >
                  <AlertCircle size={10} className={bottomTab === "problems" ? "text-red-400" : "text-text-muted"} />
                  <span>Problems</span>
                  {problems.length > 0 && (
                    <span className="animate-badge bg-red-500/20 text-red-400 px-1.5 py-0.5 rounded text-[9px] font-bold ml-0.5">{problems.length}</span>
                  )}
                </div>
                <div className="w-px h-3.5 bg-border-subtle mx-1.5 shrink-0" />

                {terminals.map((t) => {
                  const isRun = t.id.startsWith("run-");
                  const isActive = activeTerminalId === t.id && bottomTab === "terminal";
                  const isEditing = editingTabId === t.id;
                  return (
                    <div
                      key={t.id}
                      onClick={() => { setActiveTerminalId(t.id); setBottomTab("terminal"); }}
                      onDoubleClick={() => {
                        setEditingTabId(t.id);
                        setEditingTabLabel(t.label);
                      }}
                      className={`panel-tab cursor-pointer shrink-0 group ${isActive ? "active" : ""}`}
                    >
                      {isRun
                        ? <Play size={10} className={isActive ? "text-green-500" : "text-text-muted group-hover:text-green-500"} />
                        : <Terminal size={10} className={isActive ? "text-accent" : "text-text-muted group-hover:text-accent"} />}
                      
                      {isEditing ? (
                        <input
                          type="text"
                          value={editingTabLabel}
                          onChange={(e) => setEditingTabLabel(e.target.value)}
                          onKeyDown={(e) => {
                            if (e.key === "Enter") {
                              setTerminals((prev) =>
                                prev.map((item) =>
                                  item.id === t.id ? { ...item, label: editingTabLabel } : item
                                )
                              );
                              setEditingTabId(null);
                            } else if (e.key === "Escape") {
                              setEditingTabId(null);
                            }
                          }}
                          onBlur={() => {
                            setTerminals((prev) =>
                              prev.map((item) =>
                                item.id === t.id ? { ...item, label: editingTabLabel } : item
                              )
                            );
                            setEditingTabId(null);
                          }}
                          className="bg-surface-3 text-text-primary px-1 border border-blue-500 outline-none rounded text-[11px] max-w-[80px]"
                          autoFocus
                          onClick={(e) => e.stopPropagation()}
                        />
                      ) : (
                        <span>{t.label}</span>
                      )}
                      
                      <button
                        onClick={(e) => { e.stopPropagation(); closeTerminal(t.id); }}
                        className="opacity-0 group-hover:opacity-100 hover:text-red-400 transition-opacity ml-0.5 leading-none"
                        title="Close terminal"
                      >
                        <X size={10} />
                      </button>
                    </div>
                  );
                })}
              </div>

              {/* Right-side actions */}
              <div className="flex items-center gap-0.5 flex-shrink-0 ml-auto pl-1">
                {/* Debug Terminal */}
                {terminals.length > 0 && bottomTab === "terminal" && (
                  <button
                    onClick={handleDebugTerminal}
                    title="Debug Terminal Errors with AI"
                    className="p-1.5 flex items-center gap-1.5 rounded bg-accent/10 text-accent hover:bg-accent/20 transition-all font-medium text-[10px]"
                  >
                    <Sparkles size={12} />
                    Debug Terminal
                  </button>
                )}
                {/* Split Terminal */}
                {terminals.length > 0 && bottomTab === "terminal" && (
                  <button
                    onClick={() => activeTerminalId && splitTerminal(activeTerminalId)}
                    title="Split Terminal Side-by-Side"
                    className="p-1.5 rounded text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors"
                  >
                    <SplitSquareHorizontal size={12} />
                  </button>
                )}
                {/* New terminal */}
                <button
                  onClick={createTerminal}
                  title="New terminal (Ctrl+Shift+`)"
                  className="p-1.5 rounded text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19" /><line x1="5" y1="12" x2="19" y2="12" />
                  </svg>
                </button>
                {/* Clear active terminal */}
                {terminals.length > 0 && (
                  <button
                    onClick={clearActiveTerminal}
                    title="Clear terminal (Ctrl+L)"
                    className="p-1.5 rounded text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M18 6 6 18" /><path d="m6 6 12 12" />
                    </svg>
                  </button>
                )}
                {/* Maximize / restore */}
                <button
                  onClick={() => setIsTerminalMaximized((v) => !v)}
                  title={isTerminalMaximized ? "Restore terminal" : "Maximize terminal"}
                  className="p-1.5 rounded text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors"
                >
                  {isTerminalMaximized ? (
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="4 14 10 14 10 20" /><polyline points="20 10 14 10 14 4" />
                      <line x1="10" y1="14" x2="21" y2="3" /><line x1="3" y1="21" x2="14" y2="10" />
                    </svg>
                  ) : (
                    <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="15 3 21 3 21 9" /><polyline points="9 21 3 21 3 15" />
                      <line x1="21" y1="3" x2="14" y2="10" /><line x1="3" y1="21" x2="10" y2="14" />
                    </svg>
                  )}
                </button>
                {/* Collapse */}
                <button
                  onClick={toggleTerminalPanel}
                  title="Hide terminal (Ctrl+`)"
                  className="p-1.5 rounded text-gray-500 hover:text-white hover:bg-gray-800 transition-colors"
                >
                  <PanelBottom size={12} />
                </button>
              </div>
            </div>

            {/* Quick Commands & Command History Bar */}
            {terminals.length > 0 && bottomTab === "terminal" && (
              <div className="flex items-center gap-2 px-3 py-1 bg-surface-2 border-b border-border-subtle flex-shrink-0 select-none overflow-x-auto no-scrollbar">
                <span className="text-[10px] text-text-muted uppercase tracking-wider font-semibold shrink-0">Quick Run:</span>
                
                {/* Git Presets */}
                <button
                  onClick={() => sendCommandToTerminal("git status")}
                  className="quick-run-chip"
                >
                  git status
                </button>
                <button
                  onClick={() => sendCommandToTerminal("git diff")}
                  className="quick-run-chip"
                >
                  git diff
                </button>

                {/* Conditional Node Presets */}
                {hasNode && (
                  <>
                    <button
                      onClick={() => sendCommandToTerminal("npm run dev")}
                      className="quick-run-chip"
                    >
                      npm run dev
                    </button>
                    <button
                      onClick={() => sendCommandToTerminal("npm install")}
                      className="quick-run-chip"
                    >
                      npm install
                    </button>
                  </>
                )}

                {/* Conditional Python Presets */}
                {hasPython && (
                  <>
                    <button
                      onClick={() => sendCommandToTerminal("python main.py")}
                      className="quick-run-chip"
                    >
                      python main.py
                    </button>
                    <button
                      onClick={() => sendCommandToTerminal("pip install -r requirements.txt")}
                      className="quick-run-chip"
                    >
                      pip install
                    </button>
                  </>
                )}

                <div className="w-px h-4 bg-border-subtle mx-1 shrink-0" />

                {/* Mini Custom Command Input */}
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    if (!customCommandInput.trim()) return;
                    sendCommandToTerminal(customCommandInput);
                    setCommandHistory((prev) => {
                      if (prev.includes(customCommandInput)) return prev;
                      return [customCommandInput, ...prev];
                    });
                    setCustomCommandInput("");
                  }}
                  className="flex items-center gap-1.5 min-w-[200px] flex-1 max-w-xs shrink-0"
                >
                  <input
                    type="text"
                    placeholder="Run custom command..."
                    value={customCommandInput}
                    onChange={(e) => setCustomCommandInput(e.target.value)}
                    className="w-full px-2 py-0.5 bg-surface-3 border border-border-subtle text-text-primary text-[10px] rounded focus:border-blue-500 outline-none transition-colors font-mono"
                  />
                </form>

                {/* History dropdown */}
                <div className="relative shrink-0">
                  <button
                    onClick={() => setShowHistoryDropdown((v) => !v)}
                    className="p-1 rounded hover:bg-surface-hover text-text-secondary hover:text-text-primary text-[10px] flex items-center gap-1"
                    title="Command History"
                  >
                    <HistoryIcon size={12} />
                  </button>
                  {showHistoryDropdown && (
                    <div className="absolute bottom-6 right-0 w-48 bg-surface-3 border border-border-subtle rounded-lg shadow-xl py-1 z-30 font-mono text-[10px] max-h-40 overflow-y-auto">
                      <div className="px-2 py-1 border-b border-border-subtle text-text-muted text-[9px] uppercase font-semibold">History</div>
                      {commandHistory.length === 0 ? (
                        <div className="px-2 py-1.5 text-text-muted italic">No history</div>
                      ) : (
                        commandHistory.map((cmd, i) => (
                          <button
                            key={i}
                            onClick={() => {
                              sendCommandToTerminal(cmd);
                              setShowHistoryDropdown(false);
                            }}
                            className="w-full text-left px-2.5 py-1.5 hover:bg-surface-hover text-text-secondary hover:text-text-primary truncate"
                          >
                            {cmd}
                          </button>
                        ))
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Terminal content area */}
            <div className="flex-1 overflow-hidden relative">
              {bottomTab === "problems" ? (
                <div className="flex flex-col h-full bg-surface-1 overflow-y-auto p-2 gap-1.5">
                  {problems.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-center gap-2 text-text-muted">
                      <CheckCircle2 size={24} className="text-green-500/50" />
                      <p className="text-xs">No problems detected in open files.</p>
                    </div>
                  ) : (
                    problems.map((p, i) => {
                      const fileName = p.resource.path.split("/").pop();
                      const isError = p.severity >= 8;
                      return (
                        <div key={i} className="flex items-start gap-3 p-2 rounded-lg bg-surface-2 border border-border-subtle group">
                          <AlertCircle size={14} className={`shrink-0 mt-0.5 ${isError ? "text-red-400" : "text-yellow-400"}`} />
                          <div className="flex-1 min-w-0">
                            <p className="text-xs text-text-primary font-medium">{p.message}</p>
                            <p className="text-[10px] text-text-muted mt-0.5 flex items-center gap-2">
                              <span className="font-mono text-text-secondary">{fileName}</span>
                              <span>Ln {p.startLineNumber}, Col {p.startColumn}</span>
                            </p>
                          </div>
                          <button
                            onClick={() => {
                              const fullPath = p.resource.path.replace(/^\//, "");
                              handleFileClick(fullPath).then(() => {
                                setTimeout(() => {
                                  if (editorRef.current && monacoRef.current) {
                                    const range = new monacoRef.current.Range(p.startLineNumber, p.startColumn, p.endLineNumber, p.endColumn);
                                    editorRef.current.setSelection(range);
                                    editorRef.current.revealRangeInCenter(range);
                                    setInlineEditSelection(range as any );
                                    const topPos = editorRef.current.getScrolledVisiblePosition(range.getEndPosition())?.top || 0;
                                    setInlineEditPosition({ top: topPos + 30, left: 10 });
                                    setInlineEditPrompt(`Fix this error: ${p.message}`);
                                    setIsInlineEditOpen(true);
                                    setTimeout(() => document.getElementById("inline-edit-input")?.focus(), 50);
                                  }
                                }, 300);
                              });
                            }}
                            className="opacity-0 group-hover:opacity-100 flex items-center gap-1.5 px-2 py-1 rounded bg-accent/10 text-accent hover:bg-accent/20 transition-all shrink-0 text-[10px] font-medium"
                          >
                            <Sparkles size={10} />
                            Fix with AI
                          </button>
                        </div>
                      );
                    })
                  )}
                </div>
              ) : terminals.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center gap-3">
                  <div className="w-12 h-12 rounded-xl bg-surface-2 border border-border-subtle flex items-center justify-center animate-float">
                    <Terminal size={22} className="text-text-muted" />
                  </div>
                  <div>
                    <p className="text-xs text-text-secondary font-medium">No terminal open</p>
                    <p className="text-[10px] text-text-muted mt-0.5">Press Ctrl+Shift+` or click + to start one</p>
                  </div>
                  <button
                    onClick={createTerminal}
                    className="text-[11px] px-3 py-1.5 bg-accent hover:bg-accent-hover text-white rounded-md transition-colors font-medium mt-1"
                  >
                    New Terminal
                  </button>
                </div>
              ) : (
                terminals.map((t) => (
                  <div
                    key={t.id}
                    className="absolute inset-0 flex"
                    style={{
                      visibility: activeTerminalId === t.id ? "visible" : "hidden",
                      pointerEvents: activeTerminalId === t.id ? "auto" : "none",
                    }}
                  >
                    {t.panes.map((pane, idx) => (
                      <div
                        key={pane.id}
                        className="relative h-full flex-1 border-r border-border-subtle last:border-r-0"
                      >
                        <IDETerminal
                          sessionId={pane.sessionId}
                          onSessionExpired={() => replaceTerminalSession(t.id, pane.id)}
                          onReady={(actions) => terminalActions.current.set(pane.id, actions)}
                          onFocus={() => setFocusedSessionId(pane.sessionId)}
                        />
                        {t.panes.length > 1 && (
                          <button
                            onClick={() => closeTerminalPane(t.id, pane.id)}
                            className="absolute top-2 right-2 p-1 rounded bg-black/60 hover:bg-red-600/80 text-white transition-colors z-20"
                            title="Close split pane"
                          >
                            <X size={10} />
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                ))
              )}
            </div>
          </footer>
        </Panel>
      </PanelGroup>

      {/* Command Palette Overlay (Ctrl+Shift+P / Ctrl+P) */}
      <CommandPalette
        isOpen={isCommandPaletteOpen}
        onClose={() => setIsCommandPaletteOpen(false)}
        paths={flattenPaths(fileTree)}
        onSelectPath={(path) => handleFileClick(path)}
        commands={[
          { id: "toggle-chat", title: "View: Toggle Chat Panel", category: "View", action: () => setIsChatCollapsed((v) => !v) },
          { id: "toggle-term", title: "View: Toggle Terminal", category: "View", action: () => setIsTerminalCollapsed((v) => !v) },
          { id: "save-file", title: "File: Save Current", category: "File", action: () => saveCurrentFile() },
          { id: "dashboard", title: "View: Project Dashboard", category: "View", action: () => setIsDashboardOpen(true) },
          { id: "onboarding", title: "Setup: Re-run Onboarding", category: "Config", action: () => setIsOnboardingOpen(true) },
          { id: "history", title: "Git: View History", category: "Git", action: () => setIsHistoryOpen(true) },
          { id: "run", title: "Project: Run", category: "Run", action: () => handleRunProject() },
          { id: "index", title: "AI: Rebuild Search Index", category: "AI", action: () => handleIndexProject() },
          { id: "review", title: "AI: Code Review", category: "AI", action: () => handleCodeReview() },
          { id: "split", title: "View: Split Editor", category: "View", action: () => { setIsSplitMode(true); setSecondarySelectedFile(selectedFile); setActiveEditorPane("secondary"); } },
        ]}
      />

      <ProjectDashboardModal 
        isOpen={isDashboardOpen} 
        onClose={() => setIsDashboardOpen(false)} 
        projectId={projectId} 
      />

      <OnboardingWizard
        isOpen={isOnboardingOpen}
        projectId={projectId}
        onComplete={(data) => {
          success(`Project initialized with ${data.language} and ${data.model}`);
          setIsOnboardingOpen(false);
        }}
      />

      {/* File Action Modal (New File / New Folder / Rename / Delete) */}
      {fileActionModal.type && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
          onClick={() => setFileActionModal({ type: null, path: "" })}
        >
          <div
            className="bg-[#1e1e1e] border border-gray-700/80 rounded-xl p-5 w-96 shadow-2xl"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
              {fileActionModal.type === "create_file" && <><FilePlus size={15} className="text-blue-400" /> {fileActionModal.path ? `New File in ${fileActionModal.path}` : "New File"}</>}
              {fileActionModal.type === "create_folder" && <><FolderPlus size={15} className="text-yellow-400" /> {fileActionModal.path ? `New Folder in ${fileActionModal.path}` : "New Folder"}</>}
              {fileActionModal.type === "rename" && <><Edit3 size={15} className="text-green-400" /> Rename '{fileActionModal.name || fileActionModal.path}'</>}
              {fileActionModal.type === "delete" && <><Trash2 size={15} className="text-red-400" /> Delete '{fileActionModal.path}'?</>}
            </h3>

            {fileActionModal.type !== "delete" ? (
              <input
                autoFocus
                type="text"
                value={fileInputName}
                onChange={(e) => setFileInputName(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") handleFileActionSubmit(); }}
                placeholder={
                  fileActionModal.type === "create_file" ? "e.g. index.ts or src/utils.js" :
                  fileActionModal.type === "create_folder" ? "e.g. components or lib" : "New name"
                }
                className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-blue-500 mb-4"
              />
            ) : (
              <p className="text-xs text-gray-400 mb-4">
                Are you sure you want to delete this file/folder? This action cannot be undone.
              </p>
            )}

            <div className="flex justify-end gap-2">
              <button
                onClick={() => setFileActionModal({ type: null, path: "" })}
                className="px-3 py-1.5 text-xs text-gray-400 hover:text-white rounded-lg transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleFileActionSubmit}
                className={`px-3.5 py-1.5 text-xs font-medium rounded-lg text-white transition-colors ${
                  fileActionModal.type === "delete"
                    ? "bg-red-600 hover:bg-red-700"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {fileActionModal.type === "delete" ? "Delete" : "Confirm"}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts overlay (?) */}
      <KeyboardShortcutsModal
        isOpen={isShortcutsOpen}
        onClose={() => setIsShortcutsOpen(false)}
      />
      <ProjectSettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        project={project}
        onSaved={(updated) => setProject(updated)}
      />

      {/* Feature 6: Git commit history & rollback */}
      <GitHistoryModal
        isOpen={isHistoryOpen}
        projectId={projectId}
        onClose={() => setIsHistoryOpen(false)}
        onRolledBack={() => {
          refreshFileTree();
          setSelectedFile(null);
          setOpenTabs([]);
          setFileContents({});
          monacoModels.current.forEach((m) => m.dispose());
          monacoModels.current.clear();
          success("Rolled back successfully.");
        }}
      />

      {/* DiffViewer Full-screen Overlay */}
      {diffFile && (
        <div className="fixed inset-0 z-[60] bg-black/80 flex items-center justify-center p-8 backdrop-blur-sm">
          <div className="w-full max-w-6xl h-full max-h-[85vh] rounded-xl overflow-hidden shadow-2xl border border-gray-700/50">
            <DiffViewer
              projectId={projectId}
              filePath={diffFile}
              onClose={() => setDiffFile(null)}
              onAccept={(filePath, content) => {
                // Update the editor model and file contents state
                setFileContents((prev) => ({ ...prev, [filePath]: content }));
                const model = monacoModels.current.get(filePath);
                if (model) model.setValue(content);
                setDirtyTabs((prev) => { const next = new Set(prev); next.delete(filePath); return next; });
              }}
            />
          </div>
        </div>
      )}

      {/* Right-click Context Menu */}
      {contextMenu && (
        <div
          className="fixed z-[70] bg-[#1e1e1e] border border-gray-700/80 rounded-xl shadow-2xl py-1.5 min-w-[180px] overflow-hidden"
          style={{ top: contextMenu.y, left: contextMenu.x }}
          onClick={(e) => e.stopPropagation()}
        >
          {contextMenu.node.type === "file" && (
            <>
              <button
                onClick={() => { handleFileClick(contextMenu.node.path); setContextMenu(null); }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-gray-300 hover:bg-gray-700/60 transition-colors"
              >
                <FileCode size={13} className="text-gray-400" /> Open
              </button>
              <button
                onClick={() => { setDiffFile(contextMenu.node.path); setContextMenu(null); }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-gray-300 hover:bg-gray-700/60 transition-colors"
              >
                <GitBranch size={13} className="text-yellow-400" /> View Diff
              </button>
              <div className="my-1 border-t border-gray-700/60" />
            </>
          )}
          {contextMenu.node.type === "directory" && (
            <>
              <button
                onClick={() => { setFileInputName(""); setFileActionModal({ type: "create_file", path: contextMenu.node.path }); setContextMenu(null); }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-gray-300 hover:bg-gray-700/60 transition-colors"
              >
                <FilePlus size={13} className="text-blue-400" /> New File Here
              </button>
              <button
                onClick={() => { setFileInputName(""); setFileActionModal({ type: "create_folder", path: contextMenu.node.path }); setContextMenu(null); }}
                className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-gray-300 hover:bg-gray-700/60 transition-colors"
              >
                <FolderPlus size={13} className="text-yellow-400" /> New Folder Here
              </button>
              <div className="my-1 border-t border-gray-700/60" />
            </>
          )}
          <button
            onClick={() => {
              const path = contextMenu.node.path;
              navigator.clipboard.writeText(path);
              setContextMenu(null);
            }}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-gray-300 hover:bg-gray-700/60 transition-colors"
          >
            <Search size={13} className="text-gray-400" /> Copy Path
          </button>
          <button
            onClick={() => { setFileInputName(contextMenu.node.name); setFileActionModal({ type: "rename", path: contextMenu.node.path, name: contextMenu.node.name }); setContextMenu(null); }}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-gray-300 hover:bg-gray-700/60 transition-colors"
          >
            <Edit3 size={13} className="text-green-400" /> Rename
          </button>
          <div className="my-1 border-t border-gray-700/60" />
          <button
            onClick={() => { setFileActionModal({ type: "delete", path: contextMenu.node.path }); setContextMenu(null); }}
            className="w-full flex items-center gap-2.5 px-3 py-2 text-xs text-red-400 hover:bg-red-900/20 transition-colors"
          >
            <Trash2 size={13} /> Delete
          </button>
        </div>
      )}

      {/* ── Status Bar ─────────────────────────────────────────────────────── */}
      <div className="h-6 status-bar flex items-center justify-between px-3 text-[11px] text-white/80 shrink-0 select-none">
        {/* Left side */}
        <div className="flex items-center gap-3">
          {gitBranch && (
            <span className="flex items-center gap-1">
              <GitBranch size={10} />
              {gitBranch}
            </span>
          )}
          {problems.length > 0 && (
            <button
              onClick={() => { setBottomTab("problems"); const panel = terminalPanelRef.current; if (panel?.isCollapsed()) panel.expand(); }}
              className="flex items-center gap-1 hover:text-white transition-colors"
            >
              <AlertCircle size={10} className="text-red-300" />
              <span>{problems.filter(p => p.severity >= 8).length} errors</span>
              {problems.filter(p => p.severity < 8).length > 0 && (
                <span className="ml-1 text-yellow-300">{problems.filter(p => p.severity < 8).length} warnings</span>
              )}
            </button>
          )}
          {problems.length === 0 && (
            <span className="flex items-center gap-1 opacity-60">
              <CheckCircle2 size={10} />
              No problems
            </span>
          )}
        </div>

        {/* Center: active file */}
        {selectedFile && selectedFile !== "__preview__" && (
          <span className="absolute left-1/2 -translate-x-1/2 opacity-70 truncate max-w-xs">
            {selectedFile.split("/").pop()}
            {dirtyTabs.has(selectedFile) ? " ●" : ""}
          </span>
        )}

        {/* Right side */}
        <div className="flex items-center gap-3">
          {selectedFile && selectedFile !== "__preview__" && (
            <>
              <span>Ln {cursorPosition.line}, Col {cursorPosition.column}</span>
              <span className="opacity-80">{editorLanguage}</span>
            </>
          )}
          {isTyping && (
            <span className="flex items-center gap-1 text-[#a5b4fc] animate-pulse">
              <Brain size={10} />
              AI thinking…
            </span>
          )}
          {/* Font size controls */}
          <button
            onClick={() => setEditorFontSize(s => Math.max(10, s - 1))}
            className="opacity-60 hover:opacity-100 transition-opacity leading-none"
            title="Decrease font size"
          >A-</button>
          <span className="opacity-50 tabular-nums">{editorFontSize}px</span>
          <button
            onClick={() => setEditorFontSize(s => Math.min(24, s + 1))}
            className="opacity-60 hover:opacity-100 transition-opacity leading-none"
            title="Increase font size"
          >A+</button>
          {/* Zen mode toggle */}
          <button
            onClick={() => setIsZenMode(v => !v)}
            title={isZenMode ? "Exit Zen Mode (Esc)" : "Enter Zen Mode (Ctrl+Z)"}
            className={`opacity-60 hover:opacity-100 transition-opacity ${isZenMode ? "text-yellow-300 opacity-100" : ""}`}
          >
            {isZenMode ? "✦ Zen" : "✧ Zen"}
          </button>
          <span className="opacity-50">{theme === "dark" ? "Dark" : "Light"}</span>
        </div>
      </div>
    </div>
  );
}