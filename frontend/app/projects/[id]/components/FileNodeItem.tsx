import React, { useState } from "react";
import { FolderOpen, Folder, FilePlus, FolderPlus, Edit3, Trash2, ChevronRight } from "lucide-react";
import { FileNode } from "./types";
import { fileIconColor, statusColor, statusLetter } from "./utils";

// ── File-type icon with rich colour-coding ──────────────────────────────────
function FileIcon({ name, selected }: { name: string; selected: boolean }) {
  const ext = name.split(".").pop()?.toLowerCase() ?? "";

  if (selected) {
    return (
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#a5b4fc" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
      </svg>
    );
  }

  const colors: Record<string, string> = {
    ts: "#3b82f6", tsx: "#60a5fa", js: "#facc15", jsx: "#fbbf24",
    py: "#34d399",  rb: "#f87171",  go: "#67e8f9",  rs: "#fb923c",
    css: "#a78bfa", scss: "#e879f9", html: "#f97316", json: "#fbbf24",
    md: "#94a3b8",  mdx: "#94a3b8", svg: "#4ade80",  png: "#34d399",
    jpg: "#34d399", gif: "#34d399", env: "#fbbf24",  sh: "#a3e635",
    yaml: "#fb923c", yml: "#fb923c", toml: "#fb923c", lock: "#6b7280",
    sql: "#60a5fa", graphql: "#e879f9", prisma: "#60a5fa",
  };

  const color = colors[ext] ?? "#5a5a7a";

  return (
    <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="shrink-0">
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 2 14 8 20 8" />
    </svg>
  );
}

export function FileNodeItem({
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
          className="file-row flex items-center justify-between w-full pr-1 rounded-sm group/row cursor-pointer"
          onContextMenu={(e) => onContextMenu(e, node)}
        >
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="flex items-center gap-1.5 flex-1 min-w-0 text-left py-[5px] px-1.5 text-text-secondary text-xs truncate hover:text-text-primary transition-colors"
            style={{ paddingLeft: `${8 + depth * 12}px` }}
          >
            <ChevronRight
              size={11}
              className={`chevron shrink-0 ${isOpen ? "open" : ""}`}
            />
            {isOpen ? (
              <FolderOpen size={13} className="text-yellow-400/80 shrink-0" />
            ) : (
              <Folder size={13} className="text-yellow-400/60 shrink-0" />
            )}
            <span className="truncate font-normal tracking-tight">{node.name}</span>
          </button>
          <div className="opacity-0 group-hover/row:opacity-100 flex items-center gap-0.5 shrink-0 transition-opacity duration-150">
            <button
              onClick={(e) => { e.stopPropagation(); onCreateFile(node.path); }}
              title="New File"
              className="p-1 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors"
            >
              <FilePlus size={11} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onCreateFolder(node.path); }}
              title="New Folder"
              className="p-1 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors"
            >
              <FolderPlus size={11} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onRename(node.path, node.name); }}
              title="Rename"
              className="p-1 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors"
            >
              <Edit3 size={11} />
            </button>
            <button
              onClick={(e) => { e.stopPropagation(); onDelete(node.path); }}
              title="Delete"
              className="p-1 text-text-muted hover:text-red-400 hover:bg-surface-hover rounded transition-colors"
            >
              <Trash2 size={11} />
            </button>
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
  return (
    <div
      className={`file-row flex items-center justify-between w-full py-[5px] text-xs group/row ${
        isSelected ? "file-row-active" : "text-text-secondary"
      }`}
      style={{ paddingLeft: `${(isSelected ? 10 : 8) + depth * 12}px`, paddingRight: "4px" }}
      onContextMenu={(e) => onContextMenu(e, node)}
    >
      <button
        onClick={() => onFileClick(node.path)}
        className="flex items-center gap-1.5 flex-1 min-w-0 text-left truncate pr-1"
      >
        <FileIcon name={node.name} selected={isSelected} />
        <span className={`truncate tracking-tight ${isSelected ? "font-medium text-[#c7d2fe]" : ""}`}>
          {node.name}
        </span>
        {node.status && (
          <span className={`ml-auto text-[10px] font-bold shrink-0 ${statusColor(node.status)}`}>
            {statusLetter(node.status)}
          </span>
        )}
      </button>
      <div className="opacity-0 group-hover/row:opacity-100 flex items-center gap-0.5 shrink-0 transition-opacity duration-150">
        <button
          onClick={(e) => { e.stopPropagation(); onRename(node.path, node.name); }}
          title="Rename"
          className="p-1 text-text-muted hover:text-text-primary hover:bg-surface-hover rounded transition-colors"
        >
          <Edit3 size={11} />
        </button>
        <button
          onClick={(e) => { e.stopPropagation(); onDelete(node.path); }}
          title="Delete"
          className="p-1 text-text-muted hover:text-red-400 hover:bg-surface-hover rounded transition-colors"
        >
          <Trash2 size={11} />
        </button>
      </div>
    </div>
  );
}
