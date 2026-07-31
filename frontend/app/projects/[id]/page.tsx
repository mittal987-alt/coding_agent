"use client";

import React, { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { ArrowLeft, Loader2, MessageSquare, Terminal, FileCode, Play, Folder, Settings, Send } from "lucide-react";
import { ProjectService, Project } from "@/services/projects";
import Link from "next/link";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { vscDarkPlus } from "react-syntax-highlighter/dist/esm/styles/prism";
import remarkGfm from "remark-gfm";
import Editor from "@monaco-editor/react";
import dynamic from "next/dynamic";

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

type FileNode = {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: FileNode[];
};

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
    </button>
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

  const [editorContent, setEditorContent] = useState("");
  const [editorLanguage, setEditorLanguage] = useState("markdown");
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [isLoadingFiles, setIsLoadingFiles] = useState(false);
  const [terminalSession, setTerminalSession] = useState<string | null>(null);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I am your autonomous AI agent. How can I help you today?",
    },
  ]);

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

      console.log(json);

      setTerminalSession(json.session_id);

    } catch (err) {
      console.error("Failed to create terminal", err);
    }
  };

  const handleSendMessage = async () => {
    if (!chatInput.trim()) return;

    const userContent = chatInput;
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleFileClick = async (filePath: string) => {
    setSelectedFile(filePath);
    setEditorLanguage(getLanguageFromPath(filePath));
    try {
      const res = await fetch(
        `http://localhost:8000/api/v1/projects/${projectId}/files/content?path=${encodeURIComponent(filePath)}`
      );
      const json = await res.json();
      if (json.success && json.data?.content !== undefined) {
        setEditorContent(json.data.content);
      } else {
        setEditorContent(`// Could not load file: ${filePath}`);
      }
    } catch {
      setEditorContent(`// Error loading file: ${filePath}`);
    }
  };

  useEffect(() => {
    const fetchProject = async () => {
      try {
        const data = await ProjectService.getProject(projectId);
        setProject(data);
        setEditorContent(
          `# ${data.name}\n\nWelcome to your AI-assisted workspace.\n\nThis repository is ready for autonomous development. Use the chat panel on the left to instruct the AI agent to write code, refactor existing files, or investigate issues.\n\n## Getting Started\n1. Tell the agent what you want to build.\n2. Watch it edit the files autonomously.\n3. Review changes and collaborate.`
        );
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
      createTerminal();
    }
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
      {/* Top Navbar */}
      <header className="h-14 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-[#151515] flex items-center justify-between px-4 shrink-0">
        <div className="flex items-center gap-4">
          <Link href="/projects" className="text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors">
            <ArrowLeft size={18} />
          </Link>
          <div className="flex flex-col">
            <h1 className="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
              {project.name}
              <span className="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 text-xs font-medium uppercase tracking-wider">
                {project.llm_model || "Mistral"}
              </span>
            </h1>
            <span className="text-xs text-gray-500 dark:text-gray-400">
              {project.repository_url || "Local Workspace"}
            </span>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-3 py-1.5 rounded-full">
            <span className="w-2 h-2 rounded-full bg-green-500"></span>
            Agent Idle
          </div>
          <button className="p-2 text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors">
            <Settings size={18} />
          </button>
        </div>
      </header>

      {/* Main Workspace Layout */}
      <main className="flex-1 flex overflow-hidden">
        {/* Left Panel: Chat Interface */}
        <aside className="w-80 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-[#151515] flex flex-col shrink-0">
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

        {/* Center Panel: Editor */}
        <section className="flex-1 flex flex-col min-w-0 bg-gray-50 dark:bg-[#0e0e0e]">
          <div className="h-10 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-[#1a1a1a] flex items-center px-2">
            <div className="flex items-center gap-2 px-4 py-1.5 bg-gray-100 dark:bg-[#0e0e0e] rounded-t-lg border-t border-x border-gray-200 dark:border-gray-800 text-sm mt-2">
              <FileCode size={14} className="text-blue-500" />
              <span className="truncate max-w-[180px]" title={selectedFile ?? undefined}>
                {getFileNameFromPath(selectedFile)}
              </span>
            </div>
          </div>
          <div className="flex-1 relative overflow-hidden">
            <Editor
              height="100%"
              language={editorLanguage}
              theme="vs-dark"
              value={editorContent}
              onChange={(value) => setEditorContent(value || "")}
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
          </div>
        </section>

        {/* Right Panel: File Explorer */}
        <aside className="w-64 border-l border-gray-200 dark:border-gray-800 bg-white dark:bg-[#151515] hidden lg:flex flex-col shrink-0">
          <div className="h-12 border-b border-gray-200 dark:border-gray-800 flex items-center justify-between px-4">
            <h2 className="text-sm font-semibold flex items-center gap-2">
              <Folder size={16} />
              Repository
            </h2>
            <button
              onClick={() => {
                setIsLoadingFiles(true);
                fetch(`http://localhost:8000/api/v1/projects/${projectId}/files`)
                  .then((r) => r.json())
                  .then((json) => {
                    if (json.success) setFileTree(json.data || []);
                  })
                  .catch(() => { })
                  .finally(() => setIsLoadingFiles(false));
              }}
              className="p-1 text-gray-400 hover:text-gray-200 rounded transition-colors"
              title="Refresh files"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="13"
                height="13"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M21 2v6h-6" />
                <path d="M3 12a9 9 0 0 1 15-6.7L21 8" />
                <path d="M3 22v-6h6" />
                <path d="M21 12a9 9 0 0 1-15 6.7L3 16" />
              </svg>
            </button>
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
        </aside>
      </main>

      {/* Bottom Panel: Terminal/Logs */}
      <footer className="h-48 border-t border-gray-200 dark:border-gray-800 bg-white dark:bg-[#111111] flex flex-col shrink-0">
        <div className="h-10 border-b border-gray-200 dark:border-gray-800 flex items-center px-4 gap-4">
          <button className="text-sm font-medium text-gray-900 dark:text-white flex items-center gap-2 border-b-2 border-blue-500 h-full">
            <Terminal size={14} />
            Terminal
          </button>
          <button className="text-sm font-medium text-gray-500 hover:text-gray-900 dark:hover:text-white flex items-center gap-2 h-full transition-colors">
            Agent Logs
          </button>
        </div>
        <div className="flex-1 overflow-auto">
          {terminalSession ? (
            <IDETerminal sessionId={terminalSession} />
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500 text-xs">
              Creating terminal...
            </div>
          )}
        </div>
      </footer>
    </div>
  );
}