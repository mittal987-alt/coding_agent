"use client";

import React, { useEffect, useRef, useState, useCallback, useLayoutEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2, MessageSquare, Terminal, FileCode, Play, Folder, Settings, Send, PanelLeft, PanelRight, PanelBottom, Save, GitBranch, Search, FilePlus, FolderPlus, Trash2, Edit3, Brain, Zap, Circle, X, Sun, Moon, BarChart3, Database, Command, History as HistoryIcon, RotateCcw } from "lucide-react";
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
import { ProjectSettingsModal } from "@/components/projectSettingModel";
import { SearchModal } from "@/components/searchModel";
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

type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  modifiedFiles?: string[];
  activities?: string[];
  images?: string[];
};

type FileStatus = "modified" | "untracked" | "staged" | "deleted";

type FileNode = {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: FileNode[];
  status?: FileStatus;
};

type TerminalSession = {
  id: string;
  sessionId: string;
  label: string;
};

type ContextMenuState = {
  x: number;
  y: number;
  node: FileNode;
} | null;

/* ─── File-type icon colours ─── */
const FILE_EXT_COLOR: Record<string, string> = {
  ts: "text-blue-400", tsx: "text-blue-300", js: "text-yellow-400", jsx: "text-yellow-300",
  py: "text-green-400", json: "text-yellow-500", md: "text-gray-300", css: "text-pink-400",
  html: "text-orange-400", sh: "text-teal-400", yaml: "text-red-400", yml: "text-red-400",
  toml: "text-orange-300", rs: "text-orange-500", go: "text-cyan-400", java: "text-red-500",
  cpp: "text-blue-500", c: "text-blue-500", rb: "text-red-400", php: "text-purple-400",
  sql: "text-green-300", env: "text-yellow-300", gitignore: "text-gray-400",
  lock: "text-gray-500", txt: "text-gray-400",
};

function fileIconColor(name: string): string {
  const ext = name.split(".").pop()?.toLowerCase() || "";
  if (name === ".env" || name.startsWith(".env.")) return FILE_EXT_COLOR.env;
  if (name === ".gitignore") return FILE_EXT_COLOR.gitignore;
  return FILE_EXT_COLOR[ext] || "text-gray-400";
}

const SUGGESTED_PROMPTS = [
  "Set up the project structure",
  "Add a login page",
  "Explain this repo",
  "Fix the last error",
];

function normalizePath(path: string): string {
  return path.replace(/^\/+/, "").replace(/\/+/g, "/").trim();
}

function applyGitStatus(
  nodes: FileNode[],
  statuses: Record<string, string>
): FileNode[] {
  return nodes.map((node) => {
    if (node.type === "file") {
      return { ...node, status: (statuses[node.path] as FileStatus) || undefined };
    }
    return {
      ...node,
      children: node.children ? applyGitStatus(node.children, statuses) : undefined,
    };
  });
}

function getLanguageFromPath(path: string): string {
  const ext = path.split(".").pop()?.toLowerCase() || "";
  const map: Record<string, string> = {
    ts: "typescript", tsx: "typescript", js: "javascript", jsx: "javascript",
    py: "python", json: "json", md: "markdown", css: "css", html: "html",
    sh: "shell", yaml: "yaml", yml: "yaml", toml: "toml", rs: "rust",
    go: "go", java: "java", cpp: "cpp", c: "c",
  };
  return map[ext] || "plaintext";
}

function getFileNameFromPath(path: string | null): string {
  if (!path) return "No file selected";
  const parts = path.split("/");
  return parts[parts.length - 1] || path;
}

function getTabLabel(path: string, allOpenPaths: string[]): string {
  const name = getFileNameFromPath(path);
  const dupes = allOpenPaths.filter((p) => getFileNameFromPath(p) === name);
  if (dupes.length <= 1) return name;
  const parts = path.split("/");
  const parent = parts.length > 1 ? parts[parts.length - 2] : "";
  return parent ? `${parent}/${name}` : name;
}

function statusColor(status?: FileStatus): string {
  switch (status) {
    case "modified":
      return "text-yellow-500";
    case "untracked":
      return "text-green-500";
    case "staged":
      return "text-blue-400";
    case "deleted":
      return "text-red-500";
    default:
      return "";
  }
}

function statusLetter(status?: FileStatus): string {
  switch (status) {
    case "modified":
      return "M";
    case "untracked":
      return "U";
    case "staged":
      return "A";
    case "deleted":
      return "D";
    default:
      return "";
  }
}

function FileNodeItem({
  node,
  depth = 0,
  selectedPath,
  onFileClick,
  onCreateFile,
  onCreateFolder,
  onRename,
  onDelete,
  onContextMenu,
}: {
  node: FileNode;
  depth?: number;
  selectedPath: string | null;
  onFileClick: (path: string) => void;
  onCreateFile: (parentPath?: string) => void;
  onCreateFolder: (parentPath?: string) => void;
  onRename: (path: string, currentName: string) => void;
  onDelete: (path: string) => void;
  onContextMenu: (e: React.MouseEvent, node: FileNode) => void;
}) {
  const [isOpen, setIsOpen] = useState(node.type === "directory" && depth === 0);

  if (node.type === "directory") {
    return (
      <div className="group">
        <div
          className="flex items-center justify-between w-full hover:bg-gray-800/50 rounded-sm pr-1 transition-colors group/row"
          onContextMenu={(e) => onContextMenu(e, node)}
        >
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-1.5 flex-1 min-w-0 text-left py-1 px-1.5 text-text-primary text-xs truncate"
            style={{ paddingLeft: `${8 + depth * 12}px` }}
          >
            <span className={`transition-transform text-text-muted text-[9px] shrink-0 ${isOpen ? "rotate-90" : ""}`}>▶</span>
            <Folder size={13} className="text-yellow-400 shrink-0" />
            <span className="truncate font-normal">{node.name}</span>
          </button>
          <div className="opacity-0 group-hover/row:opacity-100 flex items-center gap-0.5 shrink-0 transition-opacity">
            <button onClick={(e) => { e.stopPropagation(); onCreateFile(node.path); }} title="New File" className="p-1 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors"><FilePlus size={12} /></button>
            <button onClick={(e) => { e.stopPropagation(); onCreateFolder(node.path); }} title="New Folder" className="p-1 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors"><FolderPlus size={12} /></button>
            <button onClick={(e) => { e.stopPropagation(); onRename(node.path, node.name); }} title="Rename" className="p-1 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors"><Edit3 size={12} /></button>
            <button onClick={(e) => { e.stopPropagation(); onDelete(node.path); }} title="Delete" className="p-1 text-text-muted hover:text-red-500 hover:bg-surface-hover rounded transition-colors"><Trash2 size={12} /></button>
          </div>
        </div>
        {isOpen && node.children && (
          <div>
            {node.children.map((child) => (
              <FileNodeItem
                key={child.path}
                node={child}
                depth={depth + 1}
                selectedPath={selectedPath}
                onFileClick={onFileClick}
                onCreateFile={onCreateFile}
                onCreateFolder={onCreateFolder}
                onRename={onRename}
                onDelete={onDelete}
                onContextMenu={onContextMenu}
              />
            ))}
          </div>
        )}
      </div>
    );
  }

  const isSelected = selectedPath === node.path;
  const iconColor = fileIconColor(node.name);
  return (
    <div
      className={`flex items-center justify-between w-full py-1 px-1.5 rounded-sm text-xs group/row transition-colors ${
        isSelected ? "bg-accent/20 text-accent font-medium" : "hover:bg-surface-hover text-text-secondary"
      }`}
      style={{ paddingLeft: `${8 + depth * 12}px` }}
      onContextMenu={(e) => onContextMenu(e, node)}
    >
      <button
        onClick={() => onFileClick(node.path)}
        className="flex items-center gap-1.5 flex-1 min-w-0 text-left truncate pr-1"
      >
        <FileCode size={13} className={`shrink-0 ${isSelected ? "text-blue-400" : iconColor}`} />
        <span className="truncate">{node.name}</span>
        {node.status && (
          <span className={`ml-1 text-[10px] font-bold shrink-0 ${statusColor(node.status)}`}>
            {statusLetter(node.status)}
          </span>
        )}
      </button>
      <div className="opacity-0 group-hover/row:opacity-100 flex items-center gap-0.5 shrink-0 transition-opacity">
        <button onClick={(e) => { e.stopPropagation(); onRename(node.path, node.name); }} title="Rename" className="p-1 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors"><Edit3 size={12} /></button>
        <button onClick={(e) => { e.stopPropagation(); onDelete(node.path); }} title="Delete" className="p-1 text-text-muted hover:text-red-500 hover:bg-surface-hover rounded transition-colors"><Trash2 size={12} /></button>
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Flat list of all file paths for the fuzzy file finder
// ---------------------------------------------------------------------------
function flattenPaths(nodes: FileNode[]): string[] {
  const out: string[] = [];
  for (const n of nodes) {
    if (n.type === "file") out.push(n.path);
    if (n.children) out.push(...flattenPaths(n.children));
  }
  return out;
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
  // Current agent name shown in the navbar pill (parsed from latest activity)
  const [currentAgentLabel, setCurrentAgentLabel] = useState<string | null>(null);

  const [editorLanguage, setEditorLanguage] = useState("markdown");
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  
  const [diffFile, setDiffFile] = useState<string | null>(null);

  const [openTabs, setOpenTabs] = useState<string[]>([]);
  // Track which tabs have unsaved edits (dirty state)
  const [dirtyTabs, setDirtyTabs] = useState<Set<string>>(new Set());

  const [fileContents, setFileContents] = useState<Record<string, string>>({});
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);

  const [terminals, setTerminals] = useState<TerminalSession[]>([]);
  const [activeTerminalId, setActiveTerminalId] = useState<string | null>(null);
  const [isTerminalMaximized, setIsTerminalMaximized] = useState(false);
  // Map from terminal tab id → a function the IDETerminal component exposes to clear its output
  const terminalClearFns = useRef<Map<string, () => void>>(new Map());

  // Monaco editor instance and per-file model registry
  const monacoRef = useRef<typeof Monaco | null>(null);
  const editorRef = useRef<Monaco.editor.IStandaloneCodeEditor | null>(null);
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
    
    acceptedFiles.forEach((file: any) => {
      formData.append("files", file);
      // use path from react-dropzone if available, fallback to filename
      const relPath = file.path ? file.path.replace(/^\//, "") : file.name;
      relativePaths.push(relPath);
    });
    formData.append("paths", JSON.stringify(relativePaths));

    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/upload-folder`, {
        method: "POST",
        body: formData,
      });
      const json = await res.json();
      if (json.success) {
        success(`Successfully uploaded ${acceptedFiles.length} file(s)`);
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
          sessionId: result.run_id,
          label: `▶ ${result.label}`,
        };
        setActiveTerminalId(newTerminal.id);
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
          sessionId,
          label: `Terminal ${prev.length + 1}`,
        };
        setActiveTerminalId(newTerminal.id);
        return [...prev, newTerminal];
      });
    } catch (err) {
      console.error("Failed to create terminal", err);
      error("Failed to start terminal. Is the backend running?");
    }
  };

  const replaceTerminalSession = async (oldId: string) => {
    try {
      const res = await fetch(
        `${apiBaseUrl}/terminal/projects/${projectId}`,
        { method: "POST" }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      const newSessionId: string = json.session_id;

      // Remove the clear fn for the old tab since its xterm instance will remount
      terminalClearFns.current.delete(oldId);

      setTerminals((prev) =>
        prev.map((t) => (t.id === oldId ? { ...t, sessionId: newSessionId } : t))
      );

      const storageKey = `terminal-sessions-${projectId}`;
      try {
        const updatedIds = terminals.map((t) =>
          t.id === oldId ? newSessionId : t.sessionId
        );
        sessionStorage.setItem(storageKey, JSON.stringify(updatedIds));
      } catch { /* ignore */ }
    } catch (err) {
      console.error("Failed to replace expired terminal session", err);
      error("Failed to start a new terminal. Is the backend running?");
    }
  };

  const closeTerminal = (id: string) => {
    terminalClearFns.current.delete(id);
    setTerminals((prev) => {
      const remaining = prev.filter((t) => t.id !== id);
      if (activeTerminalId === id) {
        setActiveTerminalId(remaining.length > 0 ? remaining[remaining.length - 1].id : null);
      }
      return remaining;
    });
  };

  const clearActiveTerminal = () => {
    if (!activeTerminalId) return;
    const clearFn = terminalClearFns.current.get(activeTerminalId);
    if (clearFn) clearFn();
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
      const historyToSend = messages.map((msg) => ({ role: msg.role, content: msg.content, images: msg.images }));
      historyToSend.push({ role: "user", content: userContent, images: chatImages.length > 0 ? chatImages : undefined });

      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/chat/stream`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: historyToSend,
          model: project?.llm_model || "gpt-4o",
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
    } catch (error) {
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

    setSelectedFile(path);
    setEditorLanguage(getLanguageFromPath(path));

    // Already have content in state -> just switch model
    if (fileContents[path] !== undefined) {
      openTab(path);
      // Switch Monaco model immediately if editor is mounted
      const model = monacoModels.current.get(path);
      if (editorRef.current && model) {
        editorRef.current.setModel(model);
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
        }
        monacoModels.current.set(path, model);
        if (editorRef.current) {
          editorRef.current.setModel(model);
        }
      }

      openTab(path);
    } catch {
      const content = `// Error loading file: ${path}`;
      setFileContents((prev) => ({ ...prev, [path]: content }));
      openTab(path);
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
            sessionId: sid,
            label: `Terminal ${i + 1}`,
          }));
          setTerminals(restored_sessions);
          setActiveTerminalId(restored_sessions[restored_sessions.length - 1].id);
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

  if (isLoading) {
    return (
      <div className="h-screen bg-gray-50 dark:bg-black flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  if (!project) {
    return (
      <div className="h-screen bg-gray-50 dark:bg-black flex flex-col items-center justify-center p-8 text-center">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Project not found</h1>
        <p className="text-gray-500 mb-6">The project you are looking for does not exist or has been deleted.</p>
        <Link href="/projects" className="text-blue-600 hover:underline">
          &larr; Back to Projects
        </Link>
      </div>
    );
  }

  return (
    <div {...getRootProps()} className="h-screen flex flex-col bg-background text-foreground overflow-hidden font-sans relative">
      <input {...getInputProps()} />
      {/* Drag & Drop Overlay */}
      {isDragActive && (
        <div className="absolute inset-0 z-50 bg-blue-500/20 backdrop-blur-[2px] flex items-center justify-center border-4 border-blue-500 border-dashed m-2 rounded-xl transition-all">
          <div className="bg-gray-900 text-white px-6 py-4 rounded-xl shadow-2xl flex flex-col items-center gap-3 animate-in fade-in zoom-in duration-200">
            <div className="p-3 bg-blue-600 rounded-full">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" x2="12" y1="3" y2="15"/></svg>
            </div>
            <div className="text-center">
              <h3 className="font-bold text-lg">Drop files to upload</h3>
              <p className="text-sm text-gray-400 mt-1">Files and folders will be added to the project workspace</p>
            </div>
          </div>
        </div>
      )}
      
      {isUploading && (
        <div className="absolute top-16 right-4 z-50 bg-gray-900 border border-gray-700 shadow-xl rounded-lg px-4 py-3 flex items-center gap-3 animate-in slide-in-from-right-8">
          <Loader2 size={16} className="animate-spin text-blue-400" />
          <span className="text-sm font-medium text-white">Uploading files...</span>
        </div>
      )}

      <style jsx global>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
      `}</style>

      {/* Top Navbar */}
      <header className="h-14 border-b border-border-subtle bg-surface-1 flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-4">
          <Link href="/projects" className="text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors">
            <ArrowLeft size={18} />
          </Link>
          <div className="flex flex-col">
            <h1 className="text-sm font-semibold text-gray-900 dark:text-white">
              {project.name}
            </h1>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {project.repository_url || "Local Workspace"}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* Unified status pill: agent state + model, one place to look */}
          <div className={`flex items-center gap-2 text-xs px-3 py-1.5 rounded-full transition-all duration-300 ${
              isTyping
                ? "bg-blue-950/70 border border-blue-700/40 text-blue-300"
                : "bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400"
            }`}>
            <span className={`w-2 h-2 rounded-full shrink-0 ${
              isTyping ? "bg-blue-400 animate-pulse" : "bg-green-500"
            }`} />
            {isTyping ? (
              <span className="flex items-center gap-1.5 font-medium">
                <Brain size={11} className="text-blue-400" />
                {currentAgentLabel
                  ? currentAgentLabel.length > 30
                    ? currentAgentLabel.slice(0, 28) + "…"
                    : currentAgentLabel
                  : "Agent Working…"}
              </span>
            ) : (
              <span>Agent Idle</span>
            )}
            <span className="w-px h-3 bg-gray-300 dark:bg-gray-700 mx-1" />
            <span className="text-blue-500 dark:text-blue-400 font-medium uppercase tracking-wide">
              {project.llm_model || "Mistral"}
            </span>
          </div>
          <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1">
            <button
              onClick={toggleChatPanel}
              title="Toggle AI Assistant panel"
              className={`p-1.5 rounded-md transition-colors ${isChatCollapsed
                  ? "text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                  : "bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                }`}
            >
              <PanelLeft size={15} />
            </button>
            <button
              onClick={toggleTerminalPanel}
              title="Toggle Terminal panel"
              className={`p-1.5 rounded-md transition-colors ${isTerminalCollapsed
                  ? "text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                  : "bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                }`}
            >
              <PanelBottom size={15} />
            </button>
            <button
              onClick={toggleRepoPanel}
              title="Toggle Repository panel"
              className={`p-1.5 rounded-md transition-colors ${isRepoCollapsed
                  ? "text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
                  : "bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                }`}
            >
              <PanelRight size={15} />
            </button>
          </div>

          {/* Feature 7: Run project */}
          <button
            onClick={handleRunProject}
            disabled={isRunning}
            title="Run project"
            className="flex items-center gap-1.5 px-3 py-1.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-xs font-medium transition-colors disabled:opacity-50"
          >
            {isRunning ? <Loader2 size={13} className="animate-spin" /> : <Play size={13} />}
            Run
          </button>

          {/* Feature 8: Rebuild AI search index */}
          <button
            onClick={handleIndexProject}
            disabled={isIndexing}
            title="Rebuild AI search index"
            className="p-2 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors disabled:opacity-50"
          >
            {isIndexing ? <Loader2 size={16} className="animate-spin" /> : <Database size={16} />}
          </button>

          {/* Feature 6: Commit history & rollback */}
          <button
            onClick={() => setIsHistoryOpen(true)}
            title="Commit history & rollback"
            className="p-2 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <HistoryIcon size={16} />
          </button>

          <button
            onClick={() => setTheme(theme === "dark" ? "light" : "dark")}
            title="Toggle Theme"
            className="p-2 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          <button
            onClick={() => setIsDashboardOpen(true)}
            title="Project Dashboard"
            className="p-2 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <BarChart3 size={16} />
          </button>
          <button
            onClick={() => setIsShortcutsOpen(true)}
            title="Keyboard shortcuts (?)"
            className="p-2 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors text-base font-bold leading-none"
          >
            ?
          </button>
          <button
            onClick={() => setIsSettingsOpen(true)}
            title="Settings"
            className="p-2 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <Settings size={18} />
          </button>
        </div>
      </header>

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
                <div className="h-12 border-b border-gray-200 dark:border-gray-800 flex items-center px-4">
                  <h2 className="text-sm font-semibold flex items-center gap-2">
                    <MessageSquare size={16} />
                    AI Assistant
                  </h2>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-4 scroll-smooth">
                  {messages.map((msg) => (
                    <div key={msg.id} className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}>
                      <div
                        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white text-xs font-bold ${msg.role === "user" ? "bg-purple-600" : "bg-blue-600"
                          }`}
                      >
                        {msg.role === "user" ? "U" : "AI"}
                      </div>
                      <div
                        className={`rounded-2xl p-3 text-sm max-w-[85%] ${msg.role === "user"
                            ? "bg-purple-600 text-white rounded-tr-none"
                            : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-200 rounded-tl-none"
                          }`}
                      >
                        {msg.images && msg.images.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-2">
                            {msg.images.map((img, idx) => (
                              <img key={idx} src={img} alt="attached" className="max-w-full h-auto rounded-lg max-h-48 object-contain border border-white/20" />
                            ))}
                          </div>
                        )}
                        <div className="prose prose-sm dark:prose-invert max-w-none space-y-2 break-words">
                          <ReactMarkdown
                            remarkPlugins={[remarkGfm]}
                            components={{
                              code({ node, className, children, ...props }: any) {
                                const match = /language-(\w+)/.exec(className || "");
                                const isInline = !className && !String(children).includes("\n");

                                return !isInline && match ? (
                                  <div className="mt-2 mb-2 rounded-md overflow-hidden border border-gray-700">
                                    <div className="bg-gray-800 text-gray-400 text-xs px-3 py-1 flex justify-between">
                                      <span>{match[1]}</span>
                                    </div>
                                    <SyntaxHighlighter
                                      style={vscDarkPlus as any}
                                      language={match[1]}
                                      PreTag="div"
                                      customStyle={{ margin: 0, borderRadius: 0 }}
                                      {...props}
                                    >
                                      {String(children).replace(/\n$/, "")}
                                    </SyntaxHighlighter>
                                  </div>
                                ) : (
                                  <code
                                    className={`px-1 py-0.5 rounded-md ${msg.role === "user" ? "bg-purple-700" : "bg-gray-200 dark:bg-gray-700"
                                      } ${className || ""}`}
                                    {...props}
                                  >
                                    {children}
                                  </code>
                                );
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
                          <div className="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                            <p className="text-xs text-green-500 dark:text-green-400 font-medium mb-1 flex items-center gap-1">
                              <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="11"
                                height="11"
                                viewBox="0 0 24 24"
                                fill="none"
                                stroke="currentColor"
                                strokeWidth="2.5"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                              >
                                <polyline points="20 6 9 17 4 12" />
                              </svg>
                              {msg.modifiedFiles.length} file{msg.modifiedFiles.length > 1 ? "s" : ""} written
                            </p>
                            <div className="flex flex-col gap-0.5 mt-2">
                              {msg.modifiedFiles.map((f) => (
                                <div key={f} className="flex items-center justify-between text-xs font-mono group/file">
                                  <button
                                    onClick={() => handleFileClick(f)}
                                    className="text-blue-400 hover:text-blue-300 hover:underline truncate"
                                  >
                                    📄 {f}
                                  </button>
                                  <button 
                                    onClick={() => setDiffFile(f)}
                                    className="opacity-0 group-hover/file:opacity-100 text-gray-500 hover:text-gray-300 transition-opacity ml-2 px-1 rounded hover:bg-gray-700/50"
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
                    <div className="flex flex-wrap gap-2 pl-11">
                      {SUGGESTED_PROMPTS.map((s) => (
                        <button
                          key={s}
                          onClick={() => sendPrompt(s)}
                          className="text-xs px-3 py-1.5 rounded-full border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-blue-500 hover:text-blue-400 transition-colors"
                        >
                          {s}
                        </button>
                      ))}
                    </div>
                  )}

                  {isTyping && (
                    <div className="flex gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center shrink-0 text-white text-xs font-bold">
                        AI
                      </div>
                      <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-tl-none p-4 text-sm flex items-center gap-1">
                        <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
                        <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
                        <span className="w-1.5 h-1.5 bg-gray-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
                      </div>
                    </div>
                  )}
                  <div ref={chatEndRef} />
                </div>
                <div className="p-4 border-t border-gray-200 dark:border-gray-800">
                  {chatImages.length > 0 && (
                    <div className="flex gap-2 mb-2 overflow-x-auto pb-1">
                      {chatImages.map((img, idx) => (
                        <div key={idx} className="relative shrink-0">
                          <img src={img} alt="upload preview" className="h-16 w-16 object-cover rounded-lg border border-gray-700" />
                          <button
                            onClick={() => setChatImages(prev => prev.filter((_, i) => i !== idx))}
                            className="absolute -top-1.5 -right-1.5 bg-gray-800 hover:bg-gray-700 text-white rounded-full p-0.5 border border-gray-600 transition-colors"
                          >
                            <X size={12} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                  <div className="relative">
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
                      placeholder="Ask the agent to do something... (Paste images)"
                      className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl pl-11 pr-12 py-3 text-sm resize-none h-20 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    <label className="absolute left-3 bottom-3 p-1.5 text-gray-400 hover:text-white cursor-pointer transition-colors">
                      <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
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
                    <button
                      onClick={handleSendMessage}
                      disabled={(!chatInput.trim() && chatImages.length === 0) || isTyping}
                      className="absolute right-3 bottom-3 p-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 text-white rounded-lg transition-colors"
                    >
                      <Send size={16} />
                    </button>
                  </div>
                </div>
              </aside>
            </Panel>

            <PanelResizeHandle className="w-1 bg-gray-200 dark:bg-gray-800 hover:bg-blue-500 cursor-col-resize transition-colors" />

            <Panel defaultSize={60} minSize={30}>
              {/* Center Panel: Editor */}
              <section className="h-full flex flex-col min-w-0 bg-gray-50 dark:bg-[#0e0e0e]">
                <div
                  className="h-10 border-b border-gray-800 flex items-center overflow-x-auto overflow-y-hidden no-scrollbar"
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
                  
                  {/* Web Preview Tab (fake path) */}
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

                </div>
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
                        // Mark tab as dirty
                        setDirtyTabs((prev) => new Set([...prev, selectedFile]));
                      }}
                      options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        wordWrap: "on",
                        lineNumbers: "on",
                        scrollBeyondLastLine: false,
                        padding: { top: 16 },
                        fontFamily: "var(--font-mono)",
                        // smooth cursor animation
                        cursorSmoothCaretAnimation: "on",
                        smoothScrolling: true,
                        // Better tab rendering
                        renderWhitespace: "selection",
                      }}
                      onMount={(editor, monaco) => {
                        editorRef.current = editor;
                        monacoRef.current = monaco;

                        // Create initial model for the already-selected file
                        if (selectedFile && fileContents[selectedFile] !== undefined) {
                          const uri = monaco.Uri.file(selectedFile);
                          let model = monaco.editor.getModel(uri);
                          if (!model) {
                            model = monaco.editor.createModel(
                              fileContents[selectedFile],
                              getLanguageFromPath(selectedFile),
                              uri
                            );
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
                      }}
                      loading={<div className="p-6 text-gray-500">Loading editor...</div>}
                    />
                  ) : (
                    <div className="h-full flex flex-col items-center justify-center text-center px-8">
                      <FileCode size={40} className="text-gray-700 mb-3" />
                      <p className="text-sm text-gray-500 mb-1">No file open</p>
                      <p className="text-xs text-gray-600 max-w-xs">
                        Select a file from the repository panel, or ask the AI agent to create one for you.
                      </p>
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
                <div className="h-10 border-b border-gray-200 dark:border-gray-800 flex items-center shrink-0">
                  <button
                    onClick={() => setRightTab("files")}
                    className={`flex items-center gap-1.5 px-3 h-full text-xs border-r border-border-subtle transition-colors ${
                      rightTab === "files"
                        ? "text-text-primary bg-surface-2"
                        : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
                    }`}
                  >
                    <Folder size={12} />
                    Files
                  </button>
                  <button
                    onClick={() => setRightTab("search")}
                    title="Search across files (Ctrl+Shift+F)"
                    className={`flex items-center gap-1.5 px-3 h-full text-xs border-r border-border-subtle transition-colors ${
                      rightTab === "search"
                        ? "text-text-primary bg-surface-2"
                        : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
                    }`}
                  >
                    <Search size={12} />
                    Search
                  </button>
                  <button
                    onClick={() => setRightTab("git")}
                    className={`flex items-center gap-1.5 px-3 h-full text-xs transition-colors ${
                      rightTab === "git"
                        ? "text-text-primary bg-surface-2"
                        : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
                    }`}
                  >
                    <GitBranch size={12} />
                    Git
                  </button>
                </div>

                {rightTab === "files" ? (
                  <>
                    <div className="flex items-center justify-between px-3 py-1.5 border-b border-gray-800 shrink-0">
                      <span className="text-xs text-gray-500 font-semibold uppercase tracking-wider">Explorer</span>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => { setFileInputName(""); setFileActionModal({ type: "create_file", path: "" }); }}
                          className="p-1 text-gray-400 hover:text-white rounded transition-colors"
                          title="New File"
                        >
                          <FilePlus size={13} />
                        </button>
                        <button
                          onClick={() => { setFileInputName(""); setFileActionModal({ type: "create_folder", path: "" }); }}
                          className="p-1 text-gray-400 hover:text-white rounded transition-colors"
                          title="New Folder"
                        >
                          <FolderPlus size={13} />
                        </button>
                        <button
                          onClick={() => setIsCommandPaletteOpen(true)}
                          className="p-1 text-gray-400 hover:text-white rounded transition-colors"
                          title="Go to file (Ctrl+P)"
                        >
                          <Search size={13} />
                        </button>
                        <button
                          onClick={refreshFileTree}
                          className="p-1 text-gray-400 hover:text-white rounded transition-colors"
                          title="Refresh files"
                        >
                          <svg xmlns="http://www.w3.org/2000/svg" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M21 2v6h-6" />
                            <path d="M3 12a9 9 0 0 1 15-6.7L21 8" />
                            <path d="M3 22v-6h6" />
                            <path d="M21 12a9 9 0 0 1-15 6.7L3 16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    <div className="flex-1 py-2 overflow-y-auto text-sm">
                      {isLoadingFiles ? (
                        <div className="flex items-center justify-center h-20">
                          <Loader2 size={16} className="animate-spin text-gray-400" />
                        </div>
                      ) : fileTree.length === 0 ? (
                        <div className="px-4 py-8 text-center">
                          <FileCode size={32} className="text-gray-600 mx-auto mb-2" />
                          <p className="text-xs text-gray-500">No files yet.</p>
                          <button
                            onClick={() => { setFileInputName(""); setFileActionModal({ type: "create_file", path: "" }); }}
                            className="text-xs text-blue-400 hover:underline mt-2"
                          >
                            Create first file
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

        <PanelResizeHandle className="h-1 bg-gray-200 dark:bg-gray-800 hover:bg-blue-500 cursor-row-resize transition-colors" />

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
          <footer className="h-full border-t border-border-subtle bg-surface-1 flex flex-col">
            {/* Tab bar */}
            <div className="h-9 border-b border-border-subtle flex items-center px-1 gap-0.5 overflow-x-auto no-scrollbar flex-shrink-0">
              {/* Terminal tabs */}
              <div className="flex items-center gap-0.5 flex-1 min-w-0 overflow-x-auto no-scrollbar">
                {terminals.map((t) => {
                  const isRun = t.id.startsWith("run-");
                  const isActive = activeTerminalId === t.id;
                  return (
                    <div
                      key={t.id}
                      onClick={() => setActiveTerminalId(t.id)}
                      className={`group flex items-center gap-1.5 px-2.5 py-1 rounded-md cursor-pointer text-[11px] shrink-0 whitespace-nowrap transition-colors ${
                        isActive
                          ? "bg-surface-2 text-text-primary shadow-sm"
                          : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
                      }`}
                    >
                      {isRun
                        ? <Play size={10} className={isActive ? "text-green-500" : "text-text-muted group-hover:text-green-500"} />
                        : <Terminal size={10} className={isActive ? "text-accent" : "text-text-muted group-hover:text-accent"} />}
                      <span>{t.label}</span>
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

            {/* Terminal content area */}
            <div className="flex-1 overflow-hidden relative">
              {terminals.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-gray-800/60 flex items-center justify-center">
                    <Terminal size={20} className="text-gray-500" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-400 font-medium">No terminal open</p>
                    <p className="text-[10px] text-gray-600 mt-0.5">Press Ctrl+Shift+` or click + to start one</p>
                  </div>
                  <button
                    onClick={createTerminal}
                    className="text-[11px] px-3 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-md transition-colors font-medium"
                  >
                    New Terminal
                  </button>
                </div>
              ) : (
                terminals.map((t) => (
                  <div
                    key={t.id}
                    className="absolute inset-0"
                    style={{
                      visibility: activeTerminalId === t.id ? "visible" : "hidden",
                      pointerEvents: activeTerminalId === t.id ? "auto" : "none",
                    }}
                  >
                    <IDETerminal
                      sessionId={t.sessionId}
                      onSessionExpired={() => replaceTerminalSession(t.id)}
                      onReady={(clearFn) => terminalClearFns.current.set(t.id, clearFn)}
                    />
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
    </div>
  );
}