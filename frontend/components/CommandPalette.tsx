"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, FileCode, Play, Terminal, MessageSquare, Zap, Wrench } from "lucide-react";

export type CommandAction = {
  id: string;
  title: string;
  icon?: React.ReactNode;
  category?: string;
  action: () => void;
};

export default function CommandPalette({
  isOpen,
  onClose,
  commands = [],
  paths = [],
  onSelectPath,
}: {
  isOpen: boolean;
  onClose: () => void;
  commands?: CommandAction[];
  paths?: string[];
  onSelectPath?: (path: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setSelectedIndex(0);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  // Handle escape to close
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const q = query.toLowerCase();
  
  // Filter commands
  const filteredCommands = commands.filter((cmd) =>
    cmd.title.toLowerCase().includes(q)
  );

  // Filter files
  const filteredPaths = paths.filter((path) =>
    path.toLowerCase().includes(q)
  ).slice(0, 50); // limit to 50 files

  // Combine items
  const items: { type: "command" | "file"; data: any }[] = [
    ...filteredCommands.map((c) => ({ type: "command" as const, data: c })),
    ...filteredPaths.map((p) => ({ type: "file" as const, data: p })),
  ];

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((i) => (i + 1) % items.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((i) => (i - 1 + items.length) % items.length);
    } else if (e.key === "Enter" && items.length > 0) {
      e.preventDefault();
      const item = items[selectedIndex];
      if (item.type === "command") {
        item.data.action();
        onClose();
      } else if (item.type === "file" && onSelectPath) {
        onSelectPath(item.data);
        onClose();
      }
    }
  };

  return (
    <div
      className="fixed inset-0 z-[100] flex items-start justify-center pt-[15vh] bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="w-full max-w-xl bg-[#1e1e1e] border border-gray-700/80 rounded-xl shadow-2xl overflow-hidden flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-800">
          <Search size={18} className="text-gray-400" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
            onKeyDown={handleKeyDown}
            placeholder="Search files or run commands (e.g., '> AI')..."
            className="flex-1 bg-transparent border-none outline-none text-sm text-gray-200 placeholder:text-gray-600"
          />
        </div>

        <div className="max-h-[60vh] overflow-y-auto p-2">
          {items.length === 0 ? (
            <div className="px-4 py-8 text-center text-sm text-gray-500">
              No results found for "{query}"
            </div>
          ) : (
            <div className="space-y-0.5">
              {items.map((item, index) => {
                const isSelected = index === selectedIndex;
                if (item.type === "command") {
                  const cmd = item.data as CommandAction;
                  return (
                    <button
                      key={cmd.id}
                      onClick={() => { cmd.action(); onClose(); }}
                      onMouseEnter={() => setSelectedIndex(index)}
                      className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-left transition-colors ${
                        isSelected ? "bg-blue-600/20 text-blue-300" : "text-gray-300 hover:bg-gray-800"
                      }`}
                    >
                      <div className={`shrink-0 ${isSelected ? "text-blue-400" : "text-gray-400"}`}>
                        {cmd.icon || <Zap size={15} />}
                      </div>
                      <span className="flex-1 truncate font-medium">{cmd.title}</span>
                      {cmd.category && (
                        <span className="text-[10px] uppercase tracking-wider text-gray-500 border border-gray-700 px-1.5 py-0.5 rounded">
                          {cmd.category}
                        </span>
                      )}
                    </button>
                  );
                } else {
                  const path = item.data as string;
                  const name = path.split("/").pop();
                  return (
                    <button
                      key={path}
                      onClick={() => { if (onSelectPath) onSelectPath(path); onClose(); }}
                      onMouseEnter={() => setSelectedIndex(index)}
                      className={`w-full flex flex-col px-3 py-2 rounded-lg text-left transition-colors ${
                        isSelected ? "bg-blue-600/20" : "hover:bg-gray-800"
                      }`}
                    >
                      <div className="flex items-center gap-2 text-sm text-gray-200">
                        <FileCode size={14} className={isSelected ? "text-blue-400" : "text-gray-500"} />
                        <span className="truncate">{name}</span>
                      </div>
                      <div className="text-[10px] text-gray-500 truncate ml-5 mt-0.5 font-mono">
                        {path}
                      </div>
                    </button>
                  );
                }
              })}
            </div>
          )}
        </div>
        <div className="bg-[#181818] px-4 py-2 text-[10px] text-gray-500 border-t border-gray-800 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 bg-gray-800 rounded border border-gray-700 font-mono text-[9px]">↑↓</kbd> to navigate
            </span>
            <span className="flex items-center gap-1">
              <kbd className="px-1 py-0.5 bg-gray-800 rounded border border-gray-700 font-mono text-[9px]">Enter</kbd> to select
            </span>
          </div>
          <span>Command Palette</span>
        </div>
      </div>
    </div>
  );
}
