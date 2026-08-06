"use client";
import React, { useState, useEffect } from "react";
import { X, Loader2, Trash2, Eye, EyeOff, GitBranch, Key, Code2, Bot, Settings2, AlertTriangle } from "lucide-react";
import { Project, ProjectService, ProjectUpdate } from "@/services/projects";

interface ProjectSettingsModalProps {
  isOpen: boolean;
  project: Project;
  onClose: () => void;
  onSaved: (updated: Project) => void;
}

type Tab = "general" | "git" | "ai" | "env" | "danger";

export const ProjectSettingsModal: React.FC<ProjectSettingsModalProps> = ({
  isOpen,
  project,
  onClose,
  onSaved,
}) => {
  const [tab, setTab] = useState<Tab>("general");

  // General
  const [name, setName] = useState(project.name);
  const [description, setDescription] = useState(project.description || "");
  const [language, setLanguage] = useState(project.language || "");
  const [framework, setFramework] = useState(project.framework || "");

  // Git
  const [repositoryUrl, setRepositoryUrl] = useState(project.repository_url || "");
  const [defaultBranch, setDefaultBranch] = useState(project.default_branch || "main");
  const [githubToken, setGithubToken] = useState(project.github_token || "");
  const [showToken, setShowToken] = useState(false);

  // AI
  const [llmModel, setLlmModel] = useState(project.llm_model || "mistral");
  const [systemPrompt, setSystemPrompt] = useState(project.system_prompt || "");

  // Env vars
  const [envVars, setEnvVars] = useState<{ key: string; value: string }[]>([]);
  const [isLoadingEnv, setIsLoadingEnv] = useState(false);

  // Danger
  const [deleteConfirm, setDeleteConfirm] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  // Shared
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    setName(project.name);
    setDescription(project.description || "");
    setLanguage(project.language || "");
    setFramework(project.framework || "");
    setRepositoryUrl(project.repository_url || "");
    setDefaultBranch(project.default_branch || "main");
    setGithubToken(project.github_token || "");
    setLlmModel(project.llm_model || "mistral");
    setSystemPrompt(project.system_prompt || "");
    setError(null);
    setSuccess(null);
    setDeleteConfirm("");
  }, [project]);

  useEffect(() => {
    if (tab === "env" && isOpen) {
      setIsLoadingEnv(true);
      fetch(`http://localhost:8000/api/v1/projects/${project.id}/env-vars`)
        .then((r) => r.json())
        .then((json) => {
          if (json.success && Array.isArray(json.data)) {
            setEnvVars(json.data.map((e: any) => ({ key: e.key, value: e.value })));
          }
        })
        .catch(() => {})
        .finally(() => setIsLoadingEnv(false));
    }
  }, [tab, isOpen, project.id]);

  if (!isOpen) return null;

  const handleSave = async () => {
    if (!name.trim()) return;
    setIsSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const updates: ProjectUpdate = {
        name,
        description,
        language,
        framework,
        repository_url: repositoryUrl || undefined,
        default_branch: defaultBranch || "main",
        github_token: githubToken || undefined,
        llm_model: llmModel,
        system_prompt: systemPrompt || undefined,
      };
      const updated = await ProjectService.updateProject(project.id, updates);
      onSaved(updated);
      setSuccess("Settings saved!");
      setTimeout(() => setSuccess(null), 3000);
    } catch (err: any) {
      setError(err?.message || "Failed to save settings.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveEnv = async () => {
    setIsSaving(true);
    setError(null);
    try {
      const dict: Record<string, string> = {};
      for (const v of envVars) {
        if (v.key.trim()) dict[v.key.trim()] = v.value;
      }
      await fetch(`http://localhost:8000/api/v1/projects/${project.id}/env-vars`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dict),
      });
      setSuccess("Environment variables saved!");
      setTimeout(() => setSuccess(null), 3000);
    } catch {
      setError("Failed to save environment variables.");
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    if (deleteConfirm !== project.name) return;
    setIsDeleting(true);
    try {
      await ProjectService.deleteProject(project.id);
      window.location.href = "/projects";
    } catch {
      setError("Failed to delete project.");
      setIsDeleting(false);
    }
  };

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: "general", label: "General", icon: <Settings2 size={14} /> },
    { id: "git", label: "Git & GitHub", icon: <GitBranch size={14} /> },
    { id: "ai", label: "AI Agent", icon: <Bot size={14} /> },
    { id: "env", label: "Environment", icon: <Key size={14} /> },
    { id: "danger", label: "Danger Zone", icon: <AlertTriangle size={14} /> },
  ];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-[#161616] border border-gray-700/60 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden flex flex-col"
        style={{ maxHeight: "90vh" }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div>
            <h2 className="text-base font-semibold text-white">Project Settings</h2>
            <p className="text-xs text-gray-500 mt-0.5">{project.name}</p>
          </div>
          <button onClick={onClose} className="text-gray-500 hover:text-white transition-colors p-1">
            <X size={18} />
          </button>
        </div>

        {/* Tabs + Content */}
        <div className="flex flex-1 min-h-0 overflow-hidden">
          {/* Sidebar Tabs */}
          <nav className="w-44 shrink-0 border-r border-gray-800 py-3 flex flex-col gap-0.5 px-2">
            {tabs.map((t) => (
              <button
                key={t.id}
                onClick={() => { setTab(t.id); setError(null); setSuccess(null); }}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors text-left ${
                  tab === t.id
                    ? "bg-blue-600/20 text-blue-400"
                    : "text-gray-400 hover:text-gray-200 hover:bg-gray-800/60"
                } ${t.id === "danger" ? "text-red-500 hover:text-red-400 hover:bg-red-900/20 mt-auto" : ""}`}
              >
                {t.icon}
                {t.label}
              </button>
            ))}
          </nav>

          {/* Tab content */}
          <div className="flex-1 overflow-y-auto p-6 flex flex-col gap-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-900/30 border border-red-700/40 text-red-400 text-xs">
                {error}
              </div>
            )}
            {success && (
              <div className="p-3 rounded-lg bg-green-900/30 border border-green-700/40 text-green-400 text-xs">
                {success}
              </div>
            )}

            {/* ── GENERAL ── */}
            {tab === "general" && (
              <>
                <Field label="Project Name">
                  <input type="text" value={name} onChange={(e) => setName(e.target.value)}
                    className={INPUT} placeholder="My Project" />
                </Field>
                <Field label="Description">
                  <textarea value={description} onChange={(e) => setDescription(e.target.value)}
                    className={`${INPUT} resize-none h-20`} placeholder="What does this project do?" />
                </Field>
                <div className="grid grid-cols-2 gap-3">
                  <Field label="Language">
                    <select value={language} onChange={(e) => setLanguage(e.target.value)} className={INPUT}>
                      <option value="">Select...</option>
                      <option value="python">Python</option>
                      <option value="typescript">TypeScript</option>
                      <option value="javascript">JavaScript</option>
                      <option value="rust">Rust</option>
                      <option value="go">Go</option>
                      <option value="java">Java</option>
                      <option value="cpp">C++</option>
                    </select>
                  </Field>
                  <Field label="Framework">
                    <select value={framework} onChange={(e) => setFramework(e.target.value)} className={INPUT}>
                      <option value="">None / Other</option>
                      <option value="nextjs">Next.js</option>
                      <option value="react">React</option>
                      <option value="fastapi">FastAPI</option>
                      <option value="django">Django</option>
                      <option value="flask">Flask</option>
                      <option value="express">Express</option>
                      <option value="streamlit">Streamlit</option>
                      <option value="vue">Vue</option>
                    </select>
                  </Field>
                </div>
                <SaveBtn onClick={handleSave} loading={isSaving} />
              </>
            )}

            {/* ── GIT ── */}
            {tab === "git" && (
              <>
                <Field label="Repository URL" hint="GitHub HTTPS URL of this project">
                  <input type="url" value={repositoryUrl} onChange={(e) => setRepositoryUrl(e.target.value)}
                    className={INPUT} placeholder="https://github.com/owner/repo" />
                </Field>
                <Field label="Default Branch">
                  <input type="text" value={defaultBranch} onChange={(e) => setDefaultBranch(e.target.value)}
                    className={INPUT} placeholder="main" />
                </Field>
                <Field label="GitHub Personal Access Token (PAT)" hint="Used for git push authentication. Stored securely.">
                  <div className="relative">
                    <input
                      type={showToken ? "text" : "password"}
                      value={githubToken}
                      onChange={(e) => setGithubToken(e.target.value)}
                      className={`${INPUT} pr-10`}
                      placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                    />
                    <button
                      type="button"
                      onClick={() => setShowToken(!showToken)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-300"
                    >
                      {showToken ? <EyeOff size={14} /> : <Eye size={14} />}
                    </button>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">
                    Generate a token at <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="text-blue-400 hover:underline">github.com/settings/tokens</a> with <code className="bg-gray-800 px-1 rounded text-xs">repo</code> scope.
                  </p>
                </Field>
                <SaveBtn onClick={handleSave} loading={isSaving} />
              </>
            )}

            {/* ── AI AGENT ── */}
            {tab === "ai" && (
              <>
                <Field label="AI Model">
                  <select value={llmModel} onChange={(e) => setLlmModel(e.target.value)} className={INPUT}>
                    <option value="mistral">Mistral (Recommended)</option>
                    <option value="claude-3-opus">Claude 3 Opus</option>
                    <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                    <option value="gpt-4o">GPT-4o</option>
                    <option value="gpt-4-turbo">GPT-4 Turbo</option>
                    <option value="gemini-pro">Gemini Pro</option>
                  </select>
                </Field>
                <Field label="System Prompt" hint="Custom instructions for the AI agent for this project. Leave blank to use the default.">
                  <textarea
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                    className={`${INPUT} resize-none h-40 font-mono text-xs`}
                    placeholder={`You are an expert ${language || "software"} developer working on this project.\nAlways write clean, well-documented code.\n...`}
                  />
                </Field>
                <SaveBtn onClick={handleSave} loading={isSaving} />
              </>
            )}

            {/* ── ENV VARS ── */}
            {tab === "env" && (
              <>
                <p className="text-xs text-gray-500">Environment variables are stored server-side and injected at runtime. They are never committed to Git.</p>
                {isLoadingEnv ? (
                  <div className="flex items-center justify-center h-20">
                    <Loader2 size={16} className="animate-spin text-gray-400" />
                  </div>
                ) : (
                  <div className="flex flex-col gap-2">
                    {envVars.map((v, i) => (
                      <div key={i} className="flex gap-2 items-center">
                        <input
                          type="text"
                          value={v.key}
                          onChange={(e) => setEnvVars(envVars.map((x, j) => j === i ? { ...x, key: e.target.value } : x))}
                          placeholder="KEY"
                          className={`${INPUT} flex-1 font-mono text-xs`}
                        />
                        <input
                          type="text"
                          value={v.value}
                          onChange={(e) => setEnvVars(envVars.map((x, j) => j === i ? { ...x, value: e.target.value } : x))}
                          placeholder="value"
                          className={`${INPUT} flex-[2] font-mono text-xs`}
                        />
                        <button
                          onClick={() => setEnvVars(envVars.filter((_, j) => j !== i))}
                          className="p-2 text-gray-600 hover:text-red-400 transition-colors shrink-0"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={() => setEnvVars([...envVars, { key: "", value: "" }])}
                      className="text-xs text-blue-400 hover:underline text-left mt-1"
                    >
                      + Add variable
                    </button>
                  </div>
                )}
                <SaveBtn onClick={handleSaveEnv} loading={isSaving} label="Save Variables" />
              </>
            )}

            {/* ── DANGER ZONE ── */}
            {tab === "danger" && (
              <div className="flex flex-col gap-4">
                <div className="border border-red-700/40 rounded-xl p-4 bg-red-900/10">
                  <h3 className="text-sm font-semibold text-red-400 flex items-center gap-2 mb-2">
                    <AlertTriangle size={15} />
                    Delete Project
                  </h3>
                  <p className="text-xs text-gray-400 mb-3">
                    This will permanently delete <span className="font-semibold text-white">{project.name}</span> including all files, chats, and settings. <span className="text-red-400">This cannot be undone.</span>
                  </p>
                  <p className="text-xs text-gray-500 mb-2">
                    Type <span className="font-mono text-white bg-gray-800 px-1.5 py-0.5 rounded">{project.name}</span> to confirm:
                  </p>
                  <input
                    type="text"
                    value={deleteConfirm}
                    onChange={(e) => setDeleteConfirm(e.target.value)}
                    className={`${INPUT} mb-3`}
                    placeholder={project.name}
                  />
                  <button
                    onClick={handleDelete}
                    disabled={deleteConfirm !== project.name || isDeleting}
                    className="flex items-center gap-2 px-4 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-xs font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
                  >
                    {isDeleting ? <Loader2 size={13} className="animate-spin" /> : <Trash2 size={13} />}
                    Delete Project Forever
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

const INPUT = "w-full px-3 py-2 rounded-lg border border-gray-700 bg-gray-900 text-gray-100 text-xs focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none transition-colors placeholder-gray-600";

function Field({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs font-medium text-gray-300">{label}</label>
      {hint && <p className="text-[11px] text-gray-600 -mt-0.5">{hint}</p>}
      {children}
    </div>
  );
}

function SaveBtn({ onClick, loading, label = "Save Changes" }: { onClick: () => void; loading: boolean; label?: string }) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="self-start mt-2 flex items-center gap-2 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium transition-colors disabled:opacity-50"
    >
      {loading && <Loader2 size={13} className="animate-spin" />}
      {label}
    </button>
  );
}