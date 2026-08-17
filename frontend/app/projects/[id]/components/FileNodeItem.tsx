import React, { useState } from "react";
import { Folder, FileCode, FilePlus, FolderPlus, Edit3, Trash2 } from "lucide-react";
import { FileNode } from "./types";
import { fileIconColor, statusColor, statusLetter } from "./utils";

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
