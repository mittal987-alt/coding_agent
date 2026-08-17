export type Message = {
  id: string;
  role: "user" | "assistant";
  content: string;
  modifiedFiles?: string[];
  activities?: string[];
  images?: string[];
};

export type FileStatus = "modified" | "untracked" | "staged" | "deleted";

export type FileNode = {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: FileNode[];
  status?: FileStatus;
};

export type TerminalSession = {
  id: string;
  sessionId: string;
  label: string;
};

export type ContextMenuState = {
  x: number;
  y: number;
  node: FileNode;
} | null;
