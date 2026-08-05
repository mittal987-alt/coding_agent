"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2, MessageSquare, Terminal, FileCode, Play, Folder, Settings, Send, PanelLeft, PanelRight, PanelBottom, Save, GitBranch, Search } from "lucide-react";
import { ProjectService, Project } from "@/services/projects";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import remarkGfm from "remark-gfm";
import Editor from "@monaco-editor/react";
import dynamic from "next/dynamic";
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
}: {
  node: FileNode;
  depth?: number;
  selectedPath: string | null;
  onFileClick: (path: string) => void;
}) {
  const [isOpen, setIsOpen] = useState(node.type === "directory" && depth === 0);

  if (node.type === "directory") {
    return (
      <div>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="flex items-center gap-1.5 w-full text-left py-0.5 px-2 rounded hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300 text-xs transition-colors"
          style={{ paddingLeft: `${8 + depth * 12}px` }}
        >
          <span className={`transition-transform text-gray-400 text-[10px] ${isOpen ? "rotate-90" : ""}`}>▶</span>
          <Folder size={13} className="text-yellow-400 shrink-0" />
          <span className="truncate">{node.name}</span>
        </button>
        {isOpen && node.children && (
          <div>
            {node.children.map((child) => (
              <FileNodeItem key={child.path} node={child} depth={depth + 1} selectedPath={selectedPath} onFileClick={onFileClick} />
            ))}
          </div>
        )}
      </div>
    );
  }

  const isSelected = selectedPath === node.path;
  return (
    <button
      onClick={() => onFileClick(node.path)}
      className={`flex items-center gap-1.5 w-full text-left py-0.5 px-2 rounded text-xs transition-colors ${isSelected
          ? "bg-blue-600/20 text-blue-400"
          : "hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-600 dark:text-gray-400"
        }`}
      style={{ paddingLeft: `${8 + depth * 12}px` }}
    >
      <FileCode size={13} className={isSelected ? "text-blue-400" : "text-gray-400"} />
      <span className="truncate">{node.name}</span>
      {node.status && (
        <span className={`ml-auto text-[10px] font-bold shrink-0 ${statusColor(node.status)}`}>
          {statusLetter(node.status)}
        </span>
      )}
    </button>
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

// ---------------------------------------------------------------------------
// Fuzzy file finder modal (Ctrl+P)
// ---------------------------------------------------------------------------
function FileFinder({
  paths,
  onSelect,
  onClose,
}: {
  paths: string[];
  onSelect: (path: string) => void;
  onClose: () => void;
}) {
  const [query, setQuery] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);
  const [cursor, setCursor] = useState(0);

  const filtered = query
    ? paths.filter((p) => p.toLowerCase().includes(query.toLowerCase())).slice(0, 20)
    : paths.slice(0, 20);

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  useEffect(() => {
    setCursor(0);
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setCursor((c) => Math.min(c + 1, filtered.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setCursor((c) => Math.max(c - 1, 0));
    } else if (e.key === "Enter") {
      if (filtered[cursor]) onSelect(filtered[cursor]);
    } else if (e.key === "Escape") {
      onClose();
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-[560px] bg-[#1e1e1e] border border-gray-700 rounded-xl shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-700">
          <Search size={15} className="text-gray-400 shrink-0" />
          <input
            ref={inputRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Go to file…"
            className="flex-1 bg-transparent outline-none text-sm text-gray-100 placeholder-gray-500"
          />
          <span className="text-xs text-gray-600">ESC to close</span>
        </div>
        <ul className="max-h-80 overflow-y-auto">
          {filtered.length === 0 && (
            <li className="px-4 py-6 text-center text-xs text-gray-600">No files match</li>
          )}
          {filtered.map((p, i) => (
            <li key={p}>
              <button
                onClick={() => onSelect(p)}
                className={`w-full text-left px-4 py-2 text-xs font-mono transition-colors ${
                  i === cursor
                    ? "bg-blue-600/30 text-blue-300"
                    : "text-gray-300 hover:bg-gray-800"
                }`}
              >
                {p}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default function WorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [chatInput, setChatInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const [editorLanguage, setEditorLanguage] = useState("markdown");
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  const [openTabs, setOpenTabs] = useState<string[]>([]);

  const [fileContents, setFileContents] = useState<Record<string, string>>({});
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);

  const [terminals, setTerminals] = useState<TerminalSession[]>([]);
  const [activeTerminalId, setActiveTerminalId] = useState<string | null>(null);

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

  // Fuzzy file finder
  const [isFileFinderOpen, setIsFileFinderOpen] = useState(false);

  // Keyboard shortcuts overlay
  const [isShortcutsOpen, setIsShortcutsOpen] = useState(false);

  const toggleChatPanel = () => {
    const panel = chatPanelRef.current;
    if (!panel) return;
    if (panel.isCollapsed()) panel.expand();
    else panel.collapse();
  };

  const toggleRepoPanel = () => {
    const panel = repoPanelRef.current;
    if (!panel) return;
    if (panel.isCollapsed()) panel.expand();
    else panel.collapse();
  };

  const toggleTerminalPanel = () => {
    const panel = terminalPanelRef.current;
    if (!panel) return;
    if (panel.isCollapsed()) panel.expand();
    else panel.collapse();
  };

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I am your autonomous AI agent. How can I help you today?",
    },
  ]);

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
    const content = fileContents[selectedFile];
    if (content === undefined) return;
    setIsSavingFile(true);
    try {
      await fetch(
        `http://localhost:8000/api/v1/projects/${projectId}/files/content?path=${encodeURIComponent(selectedFile)}`,
        {
          method: "PUT",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ content }),
        }
      );
      setFileSaveMsg("Saved");
      setTimeout(() => setFileSaveMsg(null), 2000);
    } catch {
      setFileSaveMsg("Save failed");
      setTimeout(() => setFileSaveMsg(null), 2500);
    } finally {
      setIsSavingFile(false);
    }
  }, [selectedFile, fileContents, projectId]);

  // Keyboard shortcuts: Ctrl+S save | Ctrl+P file finder | Ctrl+Shift+F search | ? help
  useEffect(() => {
    const onKeyDown = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName?.toLowerCase();
      const isEditing = tag === "input" || tag === "textarea" || (e.target as HTMLElement)?.isContentEditable;

      if ((e.ctrlKey || e.metaKey) && e.key === "s") {
        e.preventDefault();
        saveCurrentFile();
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "p") {
        e.preventDefault();
        setIsFileFinderOpen((prev) => !prev);
      }
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toLowerCase() === "f") {
        e.preventDefault();
        setRightTab("search");
        // Ensure the right panel is expanded
        const panel = repoPanelRef.current;
        if (panel?.isCollapsed()) panel.expand();
      }
      if (e.key === "?" && !isEditing) {
        setIsShortcutsOpen((prev) => !prev);
      }
      if (e.key === "Escape") {
        setIsFileFinderOpen(false);
        setIsShortcutsOpen(false);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [saveCurrentFile]);

  const createTerminal = async () => {
    try {
      const res = await fetch(
        `http://localhost:8000/api/v1/terminal/projects/${projectId}`,
        {
          method: "POST",
        }
      );

      if (!res.ok) {
        throw new Error(`HTTP ${res.status}`);
      }

      const json = await res.json();
      const sessionId: string = json.session_id;

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
    }
  };

  const closeTerminal = (id: string) => {
    setTerminals((prev) => {
      const remaining = prev.filter((t) => t.id !== id);
      if (activeTerminalId === id) {
        setActiveTerminalId(remaining.length > 0 ? remaining[remaining.length - 1].id : null);
      }
      return remaining;
    });
  };

  const sendPrompt = async (text: string) => {
    if (!text.trim()) return;

    const userContent = text;
    const newUserMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: userContent,
    };

    setMessages((prev) => [...prev, newUserMsg]);
    setChatInput("");
    setIsTyping(true);

    try {
      const historyToSend = messages.map((msg) => ({ role: msg.role, content: msg.content }));
      historyToSend.push({ role: "user", content: userContent });

      const response = await fetch(`http://localhost:8000/api/v1/projects/${projectId}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: historyToSend,
          model: project?.llm_model || "gpt-4o",
          temperature: 0.2,
          project_id: projectId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API returned status: ${response.status}`);
      }

      const data = await response.json();

      const aiResponse: Message = {
        id: Date.now().toString(),
        role: "assistant",
        content: data.message || "Done!",
        modifiedFiles: data.modified_files || [],
      };
      setMessages((prev) => [...prev, aiResponse]);

      // If files were written, refresh the tree and open the first file
      if (data.modified_files && data.modified_files.length > 0) {
        const treeRes = await fetch(`http://localhost:8000/api/v1/projects/${projectId}/files`);
        const treeJson = await treeRes.json();
        if (treeJson.success) setFileTree(treeJson.data || []);

        handleFileClick(data.modified_files[0]);
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

    // Already opened / already have content -> just ensure tab exists
    if (fileContents[path] !== undefined) {
      openTab(path);
      return;
    }

    try {
      const res = await fetch(
        `http://localhost:8000/api/v1/projects/${projectId}/files/content?path=${encodeURIComponent(
          path
        )}`
      );

      const json = await res.json();

      const content =
        json.success && json.data?.content !== undefined
          ? json.data.content
          : `// Could not load file: ${path}`;

      setFileContents((prev) => ({
        ...prev,
        [path]: content,
      }));

      openTab(path);
    } catch {
      setFileContents((prev) => ({
        ...prev,
        [path]: `// Error loading file: ${path}`,
      }));
      openTab(path);
    }
  };

  const refreshFileTree = () => {
    setIsLoadingFiles(true);
    fetch(`http://localhost:8000/api/v1/projects/${projectId}/files`)
      .then((r) => r.json())
      .then((json) => {
        if (json.success) setFileTree(json.data || []);
      })
      .catch(() => {})
      .finally(() => setIsLoadingFiles(false));
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
        const res = await fetch(`http://localhost:8000/api/v1/projects/${projectId}/files`);
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
        fetch(`http://localhost:8000/api/v1/projects/${projectId}/git/status`)
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
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-[#0e0e0e] text-gray-900 dark:text-gray-200 overflow-hidden font-sans">
      <style jsx global>{`
        .no-scrollbar::-webkit-scrollbar {
          display: none;
        }
      `}</style>

      {/* Top Navbar */}
      <header className="h-14 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-[#151515] flex items-center justify-between px-4 shrink-0">
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
          <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-1.5 rounded-full">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            Agent Idle
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
          <button
            onClick={() => setIsShortcutsOpen(true)}
            title="Keyboard shortcuts (?)"
            className="p-2 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors text-base font-bold leading-none"
          >
            ?
          </button>
          <Link
            href={`/projects/${projectId}/settings`}
            title="Settings"
            className="p-2 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
          >
            <Settings size={18} />
          </Link>
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
              <aside className="h-full border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-[#151515] flex flex-col">
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
                            <div className="flex flex-col gap-0.5">
                              {msg.modifiedFiles.map((f) => (
                                <button
                                  key={f}
                                  onClick={() => handleFileClick(f)}
                                  className="text-left text-xs text-blue-400 hover:text-blue-300 hover:underline truncate font-mono"
                                >
                                  📄 {f}
                                </button>
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
                  <div className="relative">
                    <textarea
                      value={chatInput}
                      onChange={(e) => setChatInput(e.target.value)}
                      onKeyDown={handleKeyDown}
                      placeholder="Ask the agent to do something..."
                      className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl pl-4 pr-12 py-3 text-sm resize-none h-20 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={!chatInput.trim() || isTyping}
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
                      className="shrink-0 flex items-center gap-1.5 px-3 h-full text-xs border-r border-gray-700 text-gray-400 hover:text-white transition-colors disabled:opacity-50"
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

                  {openTabs.map((path) => (
                    <div
                      key={path}
                      onClick={() => {
                        setSelectedFile(path);
                        setEditorLanguage(getLanguageFromPath(path));
                      }}
                      title={path}
                      className={`flex items-center gap-2 px-4 h-full cursor-pointer border-r border-gray-700 shrink-0 whitespace-nowrap ${selectedFile === path
                          ? "bg-[#1e1e1e] text-white"
                          : "bg-[#252526] text-gray-400"
                        }`}
                    >
                      <FileCode size={14} className="shrink-0" />

                      <span className="text-sm">
                        {getTabLabel(path, openTabs)}
                      </span>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();

                          const tabs = openTabs.filter((t) => t !== path);

                          setOpenTabs(tabs);

                          if (selectedFile === path) {
                            if (tabs.length > 0) {
                              setSelectedFile(tabs[tabs.length - 1]);
                              setEditorLanguage(
                                getLanguageFromPath(tabs[tabs.length - 1])
                              );
                            } else {
                              setSelectedFile(null);
                            }
                          }
                        }}
                        className="shrink-0 hover:text-white"
                      >
                        ✕
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex-1 relative overflow-hidden">
                  {selectedFile ? (
                    <Editor
                      height="100%"
                      language={editorLanguage}
                      theme="vs-dark"
                      value={fileContents[selectedFile] || ""}
                      onChange={(value) => {
                        setFileContents((prev) => ({
                          ...prev,
                          [selectedFile]: value || "",
                        }));
                      }}
                      options={{
                        minimap: { enabled: false },
                        fontSize: 14,
                        wordWrap: "on",
                        lineNumbers: "on",
                        scrollBeyondLastLine: false,
                        padding: { top: 16 },
                        fontFamily: "var(--font-mono)",
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
              <aside className="h-full border-l border-gray-200 dark:border-gray-800 bg-white dark:bg-[#151515] flex flex-col">
                {/* Tab bar */}
                <div className="h-10 border-b border-gray-200 dark:border-gray-800 flex items-center shrink-0">
                  <button
                    onClick={() => setRightTab("files")}
                    className={`flex items-center gap-1.5 px-3 h-full text-xs border-r border-gray-700 transition-colors ${
                      rightTab === "files"
                        ? "text-white bg-[#1e1e1e]"
                        : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30"
                    }`}
                  >
                    <Folder size={12} />
                    Files
                  </button>
                  <button
                    onClick={() => setRightTab("search")}
                    title="Search across files (Ctrl+Shift+F)"
                    className={`flex items-center gap-1.5 px-3 h-full text-xs border-r border-gray-700 transition-colors ${
                      rightTab === "search"
                        ? "text-white bg-[#1e1e1e]"
                        : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30"
                    }`}
                  >
                    <Search size={12} />
                    Search
                  </button>
                  <button
                    onClick={() => setRightTab("git")}
                    className={`flex items-center gap-1.5 px-3 h-full text-xs transition-colors ${
                      rightTab === "git"
                        ? "text-white bg-[#1e1e1e]"
                        : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/30"
                    }`}
                  >
                    <GitBranch size={12} />
                    Git
                  </button>
                </div>

                {rightTab === "files" ? (
                  <>
                    <div className="flex items-center justify-between px-3 py-1.5 border-b border-gray-800 shrink-0">
                      <span className="text-xs text-gray-500">Explorer</span>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => setIsFileFinderOpen(true)}
                          className="p-1 text-gray-500 hover:text-gray-200 rounded transition-colors"
                          title="Go to file (Ctrl+P)"
                        >
                          <Search size={12} />
                        </button>
                        <button
                          onClick={refreshFileTree}
                          className="p-1 text-gray-400 hover:text-gray-200 rounded transition-colors"
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
                    <div className="flex-1 py-2 overflow-y-auto text-sm">
                      {isLoadingFiles ? (
                        <div className="flex items-center justify-center h-20">
                          <Loader2 size={16} className="animate-spin text-gray-400" />
                        </div>
                      ) : fileTree.length === 0 ? (
                        <div className="px-4 py-8 text-center">
                          <FileCode size={32} className="text-gray-600 mx-auto mb-2" />
                          <p className="text-xs text-gray-500">No files yet.</p>
                          <p className="text-xs text-gray-600 mt-1">Ask the AI agent to create some!</p>
                        </div>
                      ) : (
                        fileTree.map((node) => (
                          <FileNodeItem
                            key={node.path}
                            node={node}
                            depth={0}
                            selectedPath={selectedFile}
                            onFileClick={handleFileClick}
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
          defaultSize={25}
          minSize={10}
          maxSize={60}
          collapsible
          collapsedSize={0}
          onCollapse={() => setIsTerminalCollapsed(true)}
          onExpand={() => setIsTerminalCollapsed(false)}
        >
          {/* Bottom Panel: Terminal/Logs */}
          <footer className="h-full border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-[#111111] flex flex-col">
            <div className="h-10 border-b border-gray-200 dark:border-gray-800 flex items-center px-2 gap-1 overflow-x-auto no-scrollbar">
              {terminals.map((t) => (
                <div
                  key={t.id}
                  onClick={() => setActiveTerminalId(t.id)}
                  className={`flex items-center gap-2 px-3 py-1.5 rounded-md cursor-pointer text-xs shrink-0 whitespace-nowrap ${activeTerminalId === t.id
                      ? "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white"
                      : "text-gray-500 hover:text-gray-800 dark:hover:text-gray-300"
                    }`}
                >
                  <Terminal size={13} />
                  <span>{t.label}</span>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      closeTerminal(t.id);
                    }}
                    className="hover:text-red-400"
                  >
                    ✕
                  </button>
                </div>
              ))}
              <button
                onClick={createTerminal}
                title="New terminal"
                className="ml-1 p-1.5 rounded-md text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors shrink-0"
              >
                +
              </button>
            </div>
            <div className="flex-1 overflow-hidden relative">
              {terminals.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-full text-center gap-2">
                  <Terminal size={28} className="text-gray-700" />
                  <p className="text-xs text-gray-500">No terminal open</p>
                  <button
                    onClick={createTerminal}
                    className="text-xs text-blue-400 hover:underline"
                  >
                    Start one
                  </button>
                </div>
              ) : (
                terminals.map((t) => (
                  <div
                    key={t.id}
                    className="absolute inset-0"
                    style={{
                      // visibility (not display:none) keeps the container's
                      // real size intact while hidden, which xterm needs to
                      // compute cell/font dimensions without crashing.
                      visibility: activeTerminalId === t.id ? "visible" : "hidden",
                      pointerEvents: activeTerminalId === t.id ? "auto" : "none",
                    }}
                  >
                    <IDETerminal sessionId={t.sessionId} />
                  </div>
                ))
              )}
            </div>
          </footer>
        </Panel>
      </PanelGroup>

      {/* Fuzzy File Finder overlay (Ctrl+P) */}
      {isFileFinderOpen && (
        <FileFinder
          paths={flattenPaths(fileTree)}
          onSelect={(path) => {
            setIsFileFinderOpen(false);
            handleFileClick(path);
          }}
          onClose={() => setIsFileFinderOpen(false)}
        />
      )}

      {/* Keyboard Shortcuts overlay (press ?) */}
      <KeyboardShortcutsModal
        isOpen={isShortcutsOpen}
        onClose={() => setIsShortcutsOpen(false)}
      />
    </div>
  );
}