import { FileNode, FileStatus } from "./types";

export const FILE_EXT_COLOR: Record<string, string> = {
  ts: "text-blue-400", tsx: "text-blue-300", js: "text-yellow-400", jsx: "text-yellow-300",
  py: "text-green-400", json: "text-yellow-500", md: "text-gray-300", css: "text-pink-400",
  html: "text-orange-400", sh: "text-teal-400", yaml: "text-red-400", yml: "text-red-400",
  toml: "text-orange-300", rs: "text-orange-500", go: "text-cyan-400", java: "text-red-500",
  cpp: "text-blue-500", c: "text-blue-500", rb: "text-red-400", php: "text-purple-400",
  sql: "text-green-300", env: "text-yellow-300", gitignore: "text-gray-400",
  lock: "text-gray-500", txt: "text-gray-400",
};

export function fileIconColor(name: string): string {
  const ext = name.split(".").pop()?.toLowerCase() || "";
  if (name === ".env" || name.startsWith(".env.")) return FILE_EXT_COLOR.env;
  if (name === ".gitignore") return FILE_EXT_COLOR.gitignore;
  return FILE_EXT_COLOR[ext] || "text-gray-400";
}

export function normalizePath(path: string): string {
  return path.replace(/^\/+/, "").replace(/\/+/g, "/").trim();
}

export function applyGitStatus(
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

export function getLanguageFromPath(path: string): string {
  const ext = path.split(".").pop()?.toLowerCase() || "";
  const map: Record<string, string> = {
    ts: "typescript", tsx: "typescript", js: "javascript", jsx: "javascript",
    py: "python", json: "json", md: "markdown", css: "css", html: "html",
    sh: "shell", yaml: "yaml", yml: "yaml", toml: "toml", rs: "rust",
    go: "go", java: "java", cpp: "cpp", c: "c",
  };
  return map[ext] || "plaintext";
}

export function getFileNameFromPath(path: string | null): string {
  if (!path) return "No file selected";
  const parts = path.split("/");
  return parts[parts.length - 1] || path;
}

export function getTabLabel(path: string, allOpenPaths: string[]): string {
  const name = getFileNameFromPath(path);
  const dupes = allOpenPaths.filter((p) => getFileNameFromPath(p) === name);
  if (dupes.length <= 1) return name;
  const parts = path.split("/");
  const parent = parts.length > 1 ? parts[parts.length - 2] : "";
  return parent ? `${parent}/${name}` : name;
}

export function statusColor(status?: FileStatus): string {
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

export function statusLetter(status?: FileStatus): string {
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

export function flattenPaths(nodes: FileNode[]): string[] {
  const out: string[] = [];
  for (const n of nodes) {
    if (n.type === "file") out.push(n.path);
    if (n.children) out.push(...flattenPaths(n.children));
  }
  return out;
}
