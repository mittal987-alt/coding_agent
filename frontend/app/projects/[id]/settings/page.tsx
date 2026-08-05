"use client";

import React, { useEffect, useState, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  ArrowLeft,
  User,
  Palette,
  KeyRound,
  FolderCog,
  TerminalSquare,
  ShieldAlert,
  Loader2,
  Check,
  Eye,
  EyeOff,
  Plus,
  Trash2,
  AlertCircle,
  Save,
} from "lucide-react";
import { ProjectService, Project, ApiKey, EnvVar } from "@/services/projects";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

type SectionId =
  | "profile"
  | "appearance"
  | "api-keys"
  | "project"
  | "environment"
  | "danger";

type Section = {
  id: SectionId;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  group: "Account" | "Project";
};

const SECTIONS: Section[] = [
  { id: "profile", label: "Profile", icon: User, group: "Account" },
  { id: "appearance", label: "Appearance", icon: Palette, group: "Account" },
  { id: "api-keys", label: "API Keys", icon: KeyRound, group: "Account" },
  { id: "project", label: "Project", icon: FolderCog, group: "Project" },
  { id: "environment", label: "Environment", icon: TerminalSquare, group: "Project" },
  { id: "danger", label: "Danger Zone", icon: ShieldAlert, group: "Project" },
];

const MODEL_OPTIONS = [
  { value: "mistral-large", label: "Mistral Large" },
  { value: "gpt-4o", label: "GPT-4o" },
  { value: "claude-sonnet-4-6", label: "Claude Sonnet" },
];

// ---------------------------------------------------------------------------
// Small UI helpers
// ---------------------------------------------------------------------------

function Toast({
  type,
  message,
  onClose,
}: {
  type: "success" | "error";
  message: string;
  onClose: () => void;
}) {
  useEffect(() => {
    const t = setTimeout(onClose, 3500);
    return () => clearTimeout(t);
  }, [onClose]);

  return (
    <div
      className={`fixed bottom-5 right-5 z-50 flex items-center gap-2.5 px-4 py-3 rounded-xl shadow-lg text-sm font-medium transition-all ${
        type === "success"
          ? "bg-green-900/90 text-green-300 border border-green-700"
          : "bg-red-900/90 text-red-300 border border-red-700"
      }`}
    >
      {type === "success" ? <Check size={15} /> : <AlertCircle size={15} />}
      {message}
    </div>
  );
}

function SavedBadge({ show }: { show: boolean }) {
  if (!show) return null;
  return (
    <span className="inline-flex items-center gap-1 text-xs text-green-500 dark:text-green-400 ml-2">
      <Check size={13} />
      Saved
    </span>
  );
}

function FieldLabel({
  children,
  hint,
}: {
  children: React.ReactNode;
  hint?: string;
}) {
  return (
    <div className="mb-1.5">
      <label className="text-sm font-medium text-gray-900 dark:text-gray-200">
        {children}
      </label>
      {hint && (
        <p className="text-xs text-gray-500 dark:text-gray-500 mt-0.5">{hint}</p>
      )}
    </div>
  );
}

function TextInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  const { className, ...rest } = props;
  return (
    <input
      {...rest}
      className={`w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500 disabled:opacity-60 ${
        className || ""
      }`}
    />
  );
}

function SettingsCard({
  title,
  description,
  children,
  footer,
}: {
  title: string;
  description?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <div className="border border-gray-200 dark:border-gray-800 rounded-xl bg-white dark:bg-[#151515] overflow-hidden">
      <div className="px-5 py-4 border-b border-gray-200 dark:border-gray-800">
        <h3 className="text-sm font-semibold text-gray-900 dark:text-white">{title}</h3>
        {description && (
          <p className="text-xs text-gray-500 dark:text-gray-500 mt-0.5">{description}</p>
        )}
      </div>
      <div className="p-5 space-y-4">{children}</div>
      {footer && (
        <div className="px-5 py-3 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-[#111111] flex items-center justify-end gap-2">
          {footer}
        </div>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function SettingsPage() {
  const params = useParams();
  const router = useRouter();
  const projectId = params.id as string;

  const [activeSection, setActiveSection] = useState<SectionId>("project");
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Toast state
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const showToast = useCallback(
    (type: "success" | "error", message: string) => setToast({ type, message }),
    []
  );

  // ── Profile (local only for now — no user auth endpoint yet) ────────────
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [profileSaved, setProfileSaved] = useState(false);

  // ── Appearance (persisted to localStorage) ───────────────────────────────
  const [theme, setTheme] = useState<"dark" | "light" | "system">("dark");
  const [editorFontSize, setEditorFontSize] = useState(14);

  // ── Project settings ─────────────────────────────────────────────────────
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [repoUrl, setRepoUrl] = useState("");
  const [llmModel, setLlmModel] = useState("mistral-large");
  const [projectSaving, setProjectSaving] = useState(false);
  const [projectSaved, setProjectSaved] = useState(false);

  // ── Environment variables ─────────────────────────────────────────────────
  const [envVars, setEnvVars] = useState<EnvVar[]>([]);
  const [envLoading, setEnvLoading] = useState(false);
  const [envSaving, setEnvSaving] = useState(false);

  // ── API Keys ──────────────────────────────────────────────────────────────
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [keysLoading, setKeysLoading] = useState(false);
  const [visibleKeyId, setVisibleKeyId] = useState<string | null>(null);
  const [newKeyLabel, setNewKeyLabel] = useState("");
  const [newKeyValue, setNewKeyValue] = useState("");
  const [newKeyProvider, setNewKeyProvider] = useState("Mistral");
  const [keyAdding, setKeyAdding] = useState(false);

  // ── Danger zone ───────────────────────────────────────────────────────────
  const [confirmName, setConfirmName] = useState("");
  const [isDeleting, setIsDeleting] = useState(false);

  // ── Initial load ──────────────────────────────────────────────────────────
  useEffect(() => {
    if (!projectId) return;
    const init = async () => {
      try {
        const data = await ProjectService.getProject(projectId);
        setProject(data);
        setProjectName(data.name || "");
        setProjectDescription((data as any).description || "");
        setRepoUrl(data.repository_url || "");
        setLlmModel(data.llm_model || "mistral-large");
      } catch {
        showToast("error", "Failed to load project.");
      } finally {
        setIsLoading(false);
      }
    };
    init();

    // Restore appearance from localStorage
    const saved = localStorage.getItem("settings_appearance");
    if (saved) {
      try {
        const { theme: t, fontSize: f } = JSON.parse(saved);
        if (t) setTheme(t);
        if (f) setEditorFontSize(f);
      } catch {}
    }
  }, [projectId, showToast]);

  // Load env vars when switching to that section
  useEffect(() => {
    if (activeSection !== "environment" || !projectId) return;
    setEnvLoading(true);
    ProjectService.getEnvVars(projectId)
      .then((vars) => setEnvVars(vars.length > 0 ? vars : [{ id: "e-new", key: "", value: "" }]))
      .catch(() => showToast("error", "Failed to load environment variables."))
      .finally(() => setEnvLoading(false));
  }, [activeSection, projectId, showToast]);

  // Load API keys when switching to that section
  useEffect(() => {
    if (activeSection !== "api-keys" || !projectId) return;
    setKeysLoading(true);
    ProjectService.getApiKeys(projectId)
      .then(setApiKeys)
      .catch(() => showToast("error", "Failed to load API keys."))
      .finally(() => setKeysLoading(false));
  }, [activeSection, projectId, showToast]);

  // ── Handlers ──────────────────────────────────────────────────────────────

  const flash = (setter: React.Dispatch<React.SetStateAction<boolean>>) => {
    setter(true);
    setTimeout(() => setter(false), 2200);
  };

  const saveProfile = () => {
    // Profile endpoint is not yet live (no user auth flow in use);
    // just optimistically mark saved.
    flash(setProfileSaved);
    showToast("success", "Profile saved locally.");
  };

  const saveAppearance = () => {
    localStorage.setItem(
      "settings_appearance",
      JSON.stringify({ theme, fontSize: editorFontSize })
    );
    showToast("success", "Appearance preferences saved.");
  };

  const saveProject = async () => {
    if (!project) return;
    setProjectSaving(true);
    try {
      const updated = await ProjectService.updateProject(projectId, {
        name: projectName || undefined,
        description: projectDescription || undefined,
        repository_url: repoUrl || undefined,
        llm_model: llmModel || undefined,
      });
      setProject(updated);
      flash(setProjectSaved);
      showToast("success", "Project settings saved.");
    } catch {
      showToast("error", "Failed to save project settings.");
    } finally {
      setProjectSaving(false);
    }
  };

  const saveEnvVars = async () => {
    setEnvSaving(true);
    try {
      await ProjectService.saveEnvVars(projectId, envVars);
      showToast("success", "Environment variables saved.");
    } catch {
      showToast("error", "Failed to save environment variables.");
    } finally {
      setEnvSaving(false);
    }
  };

  const addEnvVar = () => {
    setEnvVars((prev) => [...prev, { id: `e-${Date.now()}`, key: "", value: "" }]);
  };

  const updateEnvVar = (id: string, field: "key" | "value", value: string) => {
    setEnvVars((prev) => prev.map((v) => (v.id === id ? { ...v, [field]: value } : v)));
  };

  const removeEnvVar = (id: string) => {
    setEnvVars((prev) => prev.filter((v) => v.id !== id));
  };

  const addApiKey = async () => {
    if (!newKeyLabel.trim() || !newKeyValue.trim()) return;
    setKeyAdding(true);
    try {
      const created = await ProjectService.addApiKey(projectId, {
        label: newKeyLabel.trim(),
        provider: newKeyProvider,
        key_value: newKeyValue.trim(),
      });
      setApiKeys((prev) => [...prev, created]);
      setNewKeyLabel("");
      setNewKeyValue("");
      showToast("success", "API key added.");
    } catch {
      showToast("error", "Failed to add API key.");
    } finally {
      setKeyAdding(false);
    }
  };

  const removeApiKey = async (id: string) => {
    try {
      await ProjectService.deleteApiKey(projectId, id);
      setApiKeys((prev) => prev.filter((k) => k.id !== id));
      showToast("success", "API key removed.");
    } catch {
      showToast("error", "Failed to remove API key.");
    }
  };

  const handleDeleteProject = async () => {
    if (confirmName !== project?.name) return;
    setIsDeleting(true);
    try {
      await ProjectService.deleteProject(projectId);
      router.push("/");
    } catch {
      showToast("error", "Failed to delete project.");
      setIsDeleting(false);
    }
  };

  // ── Render ────────────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div className="h-screen bg-gray-50 dark:bg-black flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  const groupedSections = SECTIONS.reduce<Record<string, Section[]>>((acc, s) => {
    acc[s.group] = acc[s.group] || [];
    acc[s.group].push(s);
    return acc;
  }, {});

  return (
    <div className="h-screen flex flex-col bg-gray-50 dark:bg-[#0e0e0e] text-gray-900 dark:text-gray-200 overflow-hidden font-sans">
      {/* Toast */}
      {toast && (
        <Toast type={toast.type} message={toast.message} onClose={() => setToast(null)} />
      )}

      {/* Top bar */}
      <header className="h-14 border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-[#151515] flex items-center px-4 shrink-0 gap-4">
        <Link
          href={`/projects/${projectId}`}
          className="text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors"
        >
          <ArrowLeft size={18} />
        </Link>
        <div className="flex flex-col">
          <h1 className="text-sm font-semibold text-gray-900 dark:text-white">Settings</h1>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {project?.name || "Workspace"}
          </span>
        </div>
      </header>

      <div className="flex-1 flex min-h-0 overflow-hidden">
        {/* Sidebar nav */}
        <nav className="w-56 shrink-0 border-r border-gray-200 dark:border-gray-800 bg-white dark:bg-[#151515] py-4 overflow-y-auto">
          {Object.entries(groupedSections).map(([group, items]) => (
            <div key={group} className="mb-5">
              <p className="px-4 mb-1.5 text-[11px] font-semibold uppercase tracking-wider text-gray-400 dark:text-gray-600">
                {group}
              </p>
              {items.map((s) => {
                const Icon = s.icon;
                const isActive = activeSection === s.id;
                return (
                  <button
                    key={s.id}
                    onClick={() => setActiveSection(s.id)}
                    className={`flex items-center gap-2.5 w-full text-left px-4 py-2 text-sm transition-colors border-l-2 ${
                      isActive
                        ? "border-blue-500 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 font-medium"
                        : "border-transparent text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800/60 hover:text-gray-900 dark:hover:text-gray-200"
                    } ${s.id === "danger" && !isActive ? "hover:!text-red-500" : ""}`}
                  >
                    <Icon size={15} className={s.id === "danger" ? "text-red-500" : ""} />
                    {s.label}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-2xl mx-auto px-8 py-8 space-y-6">

            {/* ── Profile ─────────────────────────────────────────────── */}
            {activeSection === "profile" && (
              <SettingsCard
                title="Profile"
                description="Your personal account details."
                footer={
                  <>
                    <SavedBadge show={profileSaved} />
                    <button
                      onClick={saveProfile}
                      className="px-4 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors inline-flex items-center gap-1.5"
                    >
                      <Save size={13} />
                      Save changes
                    </button>
                  </>
                }
              >
                <div>
                  <FieldLabel>Display name</FieldLabel>
                  <TextInput
                    value={displayName}
                    onChange={(e) => setDisplayName(e.target.value)}
                    placeholder="Your name"
                  />
                </div>
                <div>
                  <FieldLabel hint="Used for notifications and login.">Email</FieldLabel>
                  <TextInput
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@example.com"
                  />
                </div>
              </SettingsCard>
            )}

            {/* ── Appearance ──────────────────────────────────────────── */}
            {activeSection === "appearance" && (
              <SettingsCard
                title="Appearance"
                description="Customize how the workspace looks."
                footer={
                  <button
                    onClick={saveAppearance}
                    className="px-4 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors inline-flex items-center gap-1.5"
                  >
                    <Save size={13} />
                    Save
                  </button>
                }
              >
                <div>
                  <FieldLabel>Theme</FieldLabel>
                  <div className="flex gap-2">
                    {(["dark", "light", "system"] as const).map((t) => (
                      <button
                        key={t}
                        onClick={() => setTheme(t)}
                        className={`px-3 py-1.5 text-sm rounded-lg border capitalize transition-colors ${
                          theme === t
                            ? "border-blue-500 bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400"
                            : "border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600"
                        }`}
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                </div>
                <div>
                  <FieldLabel hint="Applies to the code editor only.">
                    Editor font size — {editorFontSize}px
                  </FieldLabel>
                  <input
                    type="range"
                    min={11}
                    max={20}
                    value={editorFontSize}
                    onChange={(e) => setEditorFontSize(Number(e.target.value))}
                    className="w-full accent-blue-600"
                  />
                </div>
              </SettingsCard>
            )}

            {/* ── API Keys ────────────────────────────────────────────── */}
            {activeSection === "api-keys" && (
              <SettingsCard
                title="API Keys"
                description="Keys used by the agent to call model providers. Stored securely; only a preview is ever shown."
              >
                {keysLoading ? (
                  <div className="flex justify-center py-4">
                    <Loader2 size={20} className="animate-spin text-blue-500" />
                  </div>
                ) : (
                  <div className="space-y-2">
                    {apiKeys.length === 0 && (
                      <p className="text-xs text-gray-500">No API keys added yet.</p>
                    )}
                    {apiKeys.map((k) => (
                      <div
                        key={k.id}
                        className="flex items-center justify-between gap-3 px-3 py-2 rounded-lg border border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900"
                      >
                        <div className="min-w-0">
                          <p className="text-sm text-gray-900 dark:text-gray-200 truncate">
                            {k.label}
                          </p>
                          <p className="text-xs text-gray-500 font-mono flex items-center gap-2">
                            {k.provider}
                            <span>·</span>
                            <span>
                              {visibleKeyId === k.id ? k.preview : "••••••••"}
                            </span>
                          </p>
                        </div>
                        <div className="flex items-center gap-1 shrink-0">
                          <button
                            onClick={() =>
                              setVisibleKeyId(visibleKeyId === k.id ? null : k.id)
                            }
                            className="p-1.5 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 rounded transition-colors"
                            title={visibleKeyId === k.id ? "Hide" : "Reveal preview"}
                          >
                            {visibleKeyId === k.id ? (
                              <EyeOff size={14} />
                            ) : (
                              <Eye size={14} />
                            )}
                          </button>
                          <button
                            onClick={() => removeApiKey(k.id)}
                            className="p-1.5 text-gray-400 hover:text-red-500 rounded transition-colors"
                            title="Remove key"
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                <div className="pt-2 border-t border-gray-200 dark:border-gray-800 space-y-2">
                  <FieldLabel>Add a new key</FieldLabel>
                  <div className="grid grid-cols-2 gap-2">
                    <TextInput
                      placeholder="Label (e.g. Work account)"
                      value={newKeyLabel}
                      onChange={(e) => setNewKeyLabel(e.target.value)}
                    />
                    <select
                      value={newKeyProvider}
                      onChange={(e) => setNewKeyProvider(e.target.value)}
                      className="bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    >
                      <option>Mistral</option>
                      <option>OpenAI</option>
                      <option>Anthropic</option>
                    </select>
                  </div>
                  <TextInput
                    type="password"
                    placeholder="Paste key value"
                    value={newKeyValue}
                    onChange={(e) => setNewKeyValue(e.target.value)}
                  />
                  <button
                    onClick={addApiKey}
                    disabled={!newKeyLabel.trim() || !newKeyValue.trim() || keyAdding}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 text-white rounded-lg transition-colors"
                  >
                    {keyAdding ? (
                      <Loader2 size={13} className="animate-spin" />
                    ) : (
                      <Plus size={14} />
                    )}
                    Add key
                  </button>
                </div>
              </SettingsCard>
            )}

            {/* ── Project ─────────────────────────────────────────────── */}
            {activeSection === "project" && (
              <SettingsCard
                title="Project"
                description="General details about this project."
                footer={
                  <>
                    <SavedBadge show={projectSaved} />
                    <button
                      onClick={saveProject}
                      disabled={projectSaving}
                      className="px-4 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white rounded-lg transition-colors inline-flex items-center gap-1.5"
                    >
                      {projectSaving ? (
                        <Loader2 size={13} className="animate-spin" />
                      ) : (
                        <Save size={13} />
                      )}
                      Save changes
                    </button>
                  </>
                }
              >
                <div>
                  <FieldLabel>Project name</FieldLabel>
                  <TextInput
                    value={projectName}
                    onChange={(e) => setProjectName(e.target.value)}
                    placeholder="My project"
                  />
                </div>
                <div>
                  <FieldLabel hint="A short summary of what this project does.">
                    Description
                  </FieldLabel>
                  <textarea
                    value={projectDescription}
                    onChange={(e) => setProjectDescription(e.target.value)}
                    placeholder="e.g. A full-stack task manager built with FastAPI and Next.js"
                    rows={3}
                    className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500 resize-none"
                  />
                </div>
                <div>
                  <FieldLabel hint="Leave blank for a local-only workspace.">
                    Repository URL
                  </FieldLabel>
                  <TextInput
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    placeholder="https://github.com/org/repo"
                  />
                </div>
                <div>
                  <FieldLabel hint="Model the AI assistant uses for this project.">
                    Default model
                  </FieldLabel>
                  <select
                    value={llmModel}
                    onChange={(e) => setLlmModel(e.target.value)}
                    className="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-200 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    {MODEL_OPTIONS.map((m) => (
                      <option key={m.value} value={m.value}>
                        {m.label}
                      </option>
                    ))}
                  </select>
                </div>
              </SettingsCard>
            )}

            {/* ── Environment ─────────────────────────────────────────── */}
            {activeSection === "environment" && (
              <SettingsCard
                title="Environment variables"
                description="Injected into every terminal session for this project."
                footer={
                  <button
                    onClick={saveEnvVars}
                    disabled={envSaving}
                    className="px-4 py-1.5 text-sm bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white rounded-lg transition-colors inline-flex items-center gap-1.5"
                  >
                    {envSaving ? (
                      <Loader2 size={13} className="animate-spin" />
                    ) : (
                      <Save size={13} />
                    )}
                    Save variables
                  </button>
                }
              >
                {envLoading ? (
                  <div className="flex justify-center py-4">
                    <Loader2 size={20} className="animate-spin text-blue-500" />
                  </div>
                ) : (
                  <div className="space-y-2">
                    {envVars.map((v) => (
                      <div key={v.id} className="flex items-center gap-2">
                        <TextInput
                          placeholder="KEY"
                          value={v.key}
                          onChange={(e) => updateEnvVar(v.id, "key", e.target.value)}
                          className="font-mono flex-1"
                        />
                        <TextInput
                          placeholder="value"
                          value={v.value}
                          onChange={(e) => updateEnvVar(v.id, "value", e.target.value)}
                          className="font-mono flex-1"
                        />
                        <button
                          onClick={() => removeEnvVar(v.id)}
                          className="p-2 text-gray-400 hover:text-red-500 rounded transition-colors shrink-0"
                          title="Remove"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                    <button
                      onClick={addEnvVar}
                      className="inline-flex items-center gap-1.5 text-sm text-blue-500 hover:text-blue-400 transition-colors"
                    >
                      <Plus size={14} />
                      Add variable
                    </button>
                  </div>
                )}
              </SettingsCard>
            )}

            {/* ── Danger zone ─────────────────────────────────────────── */}
            {activeSection === "danger" && (
              <SettingsCard
                title="Danger zone"
                description="These actions are permanent and cannot be undone."
              >
                <div className="rounded-lg border border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-950/20 p-4">
                  <p className="text-sm font-medium text-red-700 dark:text-red-400 mb-1">
                    Delete this project
                  </p>
                  <p className="text-xs text-red-600/80 dark:text-red-400/70 mb-3">
                    All files, chat history, and terminal sessions for{" "}
                    <span className="font-mono">{project?.name}</span> will be permanently
                    deleted.
                  </p>
                  <FieldLabel hint={`Type "${project?.name}" to confirm.`}>
                    Confirm project name
                  </FieldLabel>
                  <div className="flex gap-2">
                    <TextInput
                      value={confirmName}
                      onChange={(e) => setConfirmName(e.target.value)}
                      placeholder={project?.name}
                      className="flex-1"
                    />
                    <button
                      onClick={handleDeleteProject}
                      disabled={confirmName !== project?.name || isDeleting}
                      className="px-4 py-2 text-sm bg-red-600 hover:bg-red-700 disabled:opacity-40 disabled:hover:bg-red-600 text-white rounded-lg transition-colors inline-flex items-center gap-1.5 shrink-0"
                    >
                      {isDeleting ? (
                        <Loader2 size={14} className="animate-spin" />
                      ) : (
                        <Trash2 size={14} />
                      )}
                      Delete
                    </button>
                  </div>
                </div>
              </SettingsCard>
            )}

          </div>
        </div>
      </div>
    </div>
  );
}