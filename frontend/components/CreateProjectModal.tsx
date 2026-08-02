import React, { useRef, useState } from "react";
import { X, Loader2, FolderOpen, GitFork } from "lucide-react";
import { ProjectCreate } from "@/services/projects";

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ProjectCreate) => Promise<void>;
  onCreated?: () => void; // optional: called after a folder-based project is created + uploaded
}

// Extend the file input type to include the non-standard webkitdirectory attribute
type DirectoryInputProps = React.DetailedHTMLProps<
  React.InputHTMLAttributes<HTMLInputElement>,
  HTMLInputElement
> & { webkitdirectory?: string; directory?: string };

const SKIP_DIR_SEGMENTS = new Set([
  ".git",
  "node_modules",
  "__pycache__",
  ".venv",
  "venv",
  ".next",
]);

// Files per upload request. Sending thousands of files in one multipart
// request is unreliable (browser/dev-server/proxy can drop it silently
// with no server-side log at all). Batching keeps each request small
// and lets us show real progress.
const UPLOAD_BATCH_SIZE = 100;

function shouldSkipFile(relativePath: string): boolean {
  const segments = relativePath.split("/");
  return segments.some((seg) => SKIP_DIR_SEGMENTS.has(seg));
}

export const CreateProjectModal: React.FC<CreateProjectModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  onCreated,
}) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [repositoryUrl, setRepositoryUrl] = useState("");
  const [llmModel, setLlmModel] = useState("mistral");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [sourceMode, setSourceMode] = useState<"git" | "folder">("git");
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [folderName, setFolderName] = useState<string>("");
  const folderInputRef = useRef<HTMLInputElement>(null);

  // Upload progress state
  const [uploadProgress, setUploadProgress] = useState<{
    completed: number;
    total: number;
  } | null>(null);

  if (!isOpen) return null;

  const resetForm = () => {
    setName("");
    setDescription("");
    setRepositoryUrl("");
    setLlmModel("mistral");
    setSourceMode("git");
    setSelectedFiles([]);
    setFolderName("");
    setError(null);
    setUploadProgress(null);
  };

  const handleChooseFolder = () => {
    folderInputRef.current?.click();
  };

  const handleFolderSelected = (e: React.ChangeEvent<HTMLInputElement>) => {
    const fileList = e.target.files;
    if (!fileList || fileList.length === 0) return;

    const allFiles = Array.from(fileList);
    const filtered = allFiles.filter((f) => {
      const relPath = (f as any).webkitRelativePath || f.name;
      return !shouldSkipFile(relPath);
    });

    if (filtered.length === 0) {
      setError("That folder has no files after filtering out node_modules/.git/etc.");
      return;
    }

    const firstRelPath = (filtered[0] as any).webkitRelativePath || filtered[0].name;
    const topLevelFolder = firstRelPath.split("/")[0] || "Selected Folder";

    setSelectedFiles(filtered);
    setFolderName(topLevelFolder);
    setError(null);

    // Pre-fill the project name from the folder name if the user hasn't typed one yet
    if (!name.trim()) {
      setName(topLevelFolder);
    }
  };

  const clearFolderSelection = () => {
    setSelectedFiles([]);
    setFolderName("");
    if (folderInputRef.current) folderInputRef.current.value = "";
  };

  const uploadBatch = async (
    projectId: string,
    batch: File[],
    batchNumber: number,
    totalBatches: number
  ) => {
    const formData = new FormData();
    const relativePaths: string[] = [];

    for (const file of batch) {
      const relPath = (file as any).webkitRelativePath || file.name;
      relativePaths.push(relPath);
      formData.append("files", file);
    }

    formData.append("paths", JSON.stringify(relativePaths));

    const url = `http://localhost:8000/api/v1/projects/${projectId}/upload-folder`;

    let res: Response;
    try {
      res = await fetch(url, {
        method: "POST",
        body: formData,
      });
    } catch (networkErr) {
      throw new Error(
        `Could not reach backend at ${url} while uploading batch ${batchNumber} of ${totalBatches}. Is the backend running on port 8000?`
      );
    }

    if (!res.ok) {
      let detail = "";
      try {
        const json = await res.json();
        detail = json?.detail ? JSON.stringify(json.detail) : JSON.stringify(json);
      } catch {
        detail = await res.text().catch(() => "");
      }
      throw new Error(
        `Folder upload failed (${res.status}) at ${url} on batch ${batchNumber} of ${totalBatches}: ${detail}`
      );
    }
  };

  const uploadFolderToProject = async (projectId: string) => {
    const total = selectedFiles.length;
    const totalBatches = Math.ceil(total / UPLOAD_BATCH_SIZE);

    setUploadProgress({ completed: 0, total });

    for (let start = 0; start < total; start += UPLOAD_BATCH_SIZE) {
      const batch = selectedFiles.slice(start, start + UPLOAD_BATCH_SIZE);
      const batchNumber = Math.floor(start / UPLOAD_BATCH_SIZE) + 1;

      await uploadBatch(projectId, batch, batchNumber, totalBatches);

      setUploadProgress({
        completed: Math.min(start + batch.length, total),
        total,
      });
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;
    if (sourceMode === "folder" && selectedFiles.length === 0) {
      setError("Please choose a folder to import.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      if (sourceMode === "folder") {
        // 1. Create the project first (no repository_url — local folder mode)
        const createUrl = "http://localhost:8000/api/v1/projects/";
        const createRes = await fetch(createUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name,
            description,
            llm_model: llmModel,
          }),
        });

        if (!createRes.ok) {
          const text = await createRes.text().catch(() => "");
          throw new Error(`Failed to create project (${createRes.status}) at ${createUrl}: ${text}`);
        }

        const createJson = await createRes.json();
        const projectId = createJson?.data?.id;

        if (!projectId) {
          throw new Error("Project was created but no project id was returned.");
        }

        // 2. Upload the selected folder's files into that project, in batches
        await uploadFolderToProject(projectId);

        onCreated?.();
      } else {
        // Existing git-based flow, unchanged
        await onSubmit({
          name,
          description,
          repository_url: repositoryUrl || undefined,
          llm_model: llmModel,
        });
      }

      resetForm();
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.message || err.message || "Failed to create project");
    } finally {
      setIsSubmitting(false);
      setUploadProgress(null);
    }
  };

  const directoryInputProps: DirectoryInputProps = {
    webkitdirectory: "",
    directory: "",
  };

  const progressPercent =
    uploadProgress && uploadProgress.total > 0
      ? Math.round((uploadProgress.completed / uploadProgress.total) * 100)
      : 0;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-md shadow-2xl overflow-hidden border border-gray-200 dark:border-gray-800 animate-in zoom-in-95 duration-200">
        <div className="flex items-center justify-between p-6 border-b border-gray-100 dark:border-gray-800">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Create New Project</h2>
          <button
            onClick={() => {
              resetForm();
              onClose();
            }}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 transition-colors"
          >
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6">
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-sm break-words">
              {error}
            </div>
          )}

          {uploadProgress && (
            <div className="mb-4 p-3 rounded-lg bg-blue-50 dark:bg-blue-900/20 text-sm">
              <div className="flex justify-between mb-1.5 text-gray-700 dark:text-gray-300">
                <span>Uploading files…</span>
                <span>
                  {uploadProgress.completed} / {uploadProgress.total}
                </span>
              </div>
              <div className="w-full h-2 rounded-full bg-gray-200 dark:bg-gray-700 overflow-hidden">
                <div
                  className="h-full bg-blue-600 transition-all duration-200"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Project Name *
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                placeholder="e.g. NextJS E-commerce"
                required
                disabled={isSubmitting}
              />
            </div>

            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Description
              </label>
              <textarea
                id="description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all resize-none h-24"
                placeholder="Briefly describe what this project is about..."
                disabled={isSubmitting}
              />
            </div>

            {/* Source mode toggle: GitHub URL vs Local Folder */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Project Source
              </label>
              <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-800 rounded-lg p-1 mb-3">
                <button
                  type="button"
                  onClick={() => setSourceMode("git")}
                  disabled={isSubmitting}
                  className={`flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    sourceMode === "git"
                      ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                      : "text-gray-500 dark:text-gray-400"
                  }`}
                >
                  <GitFork size={14} />
                  GitHub
                </button>
                <button
                  type="button"
                  onClick={() => setSourceMode("folder")}
                  disabled={isSubmitting}
                  className={`flex-1 flex items-center justify-center gap-2 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    sourceMode === "folder"
                      ? "bg-white dark:bg-gray-700 text-gray-900 dark:text-white shadow-sm"
                      : "text-gray-500 dark:text-gray-400"
                  }`}
                >
                  <FolderOpen size={14} />
                  Local Folder
                </button>
              </div>

              {sourceMode === "git" ? (
                <input
                  id="repositoryUrl"
                  type="url"
                  value={repositoryUrl}
                  onChange={(e) => setRepositoryUrl(e.target.value)}
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                  placeholder="https://github.com/owner/repo"
                  disabled={isSubmitting}
                />
              ) : (
                <div>
                  {/* Hidden native input — webkitdirectory makes the browser open the OS folder picker */}
                  <input
                    ref={folderInputRef}
                    type="file"
                    className="hidden"
                    onChange={handleFolderSelected}
                    disabled={isSubmitting}
                    {...directoryInputProps}
                  />

                  {selectedFiles.length === 0 ? (
                    <button
                      type="button"
                      onClick={handleChooseFolder}
                      disabled={isSubmitting}
                      className="w-full flex items-center justify-center gap-2 px-4 py-3 rounded-lg border border-dashed border-gray-300 dark:border-gray-700 text-gray-600 dark:text-gray-300 hover:border-blue-500 hover:text-blue-600 transition-colors text-sm"
                    >
                      <FolderOpen size={16} />
                      Choose a folder from your PC
                    </button>
                  ) : (
                    <div className="flex items-center justify-between px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
                      <div className="flex items-center gap-2 text-sm text-gray-800 dark:text-gray-200 truncate">
                        <FolderOpen size={16} className="text-blue-500 shrink-0" />
                        <span className="truncate">{folderName}</span>
                        <span className="text-gray-400 dark:text-gray-500 shrink-0">
                          ({selectedFiles.length} files)
                        </span>
                      </div>
                      <button
                        type="button"
                        onClick={clearFolderSelection}
                        disabled={isSubmitting}
                        className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 shrink-0 ml-2"
                      >
                        <X size={16} />
                      </button>
                    </div>
                  )}
                  <p className="text-xs text-gray-400 dark:text-gray-500 mt-1.5">
                    node_modules, .git, and build caches are skipped automatically.
                    {selectedFiles.length > UPLOAD_BATCH_SIZE && (
                      <>
                        {" "}
                        Large folders are uploaded in batches of {UPLOAD_BATCH_SIZE} files.
                      </>
                    )}
                  </p>
                </div>
              )}
            </div>

            <div>
              <label htmlFor="llmModel" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                AI Agent Model
              </label>
              <select
                id="llmModel"
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all"
                disabled={isSubmitting}
              >
                <option value="mistral">Mistral (Recommended)</option>
                <option value="claude-3-opus">Claude 3 Opus</option>
                <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                <option value="gpt-4o">GPT-4o</option>
              </select>
            </div>
          </div>

          <div className="mt-8 flex justify-end gap-3">
            <button
              type="button"
              onClick={() => {
                resetForm();
                onClose();
              }}
              className="px-5 py-2 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !name.trim()}
              className="px-5 py-2 rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting && <Loader2 size={16} className="animate-spin" />}
              {sourceMode === "folder" ? "Create & Upload" : "Create Project"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};