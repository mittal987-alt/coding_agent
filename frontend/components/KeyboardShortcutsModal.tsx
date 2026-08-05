"use client";

import { useEffect } from "react";
import { X, Keyboard } from "lucide-react";

type ShortcutEntry = {
  keys: string[];
  label: string;
};

type ShortcutGroup = {
  group: string;
  shortcuts: ShortcutEntry[];
};

const SHORTCUTS: ShortcutGroup[] = [
  {
    group: "File",
    shortcuts: [
      { keys: ["Ctrl", "S"], label: "Save current file" },
      { keys: ["Ctrl", "P"], label: "Go to file (fuzzy finder)" },
    ],
  },
  {
    group: "Search",
    shortcuts: [
      { keys: ["Ctrl", "Shift", "F"], label: "Search across all files" },
    ],
  },
  {
    group: "Terminal",
    shortcuts: [
      { keys: ["Ctrl", "`"], label: "Toggle terminal panel" },
    ],
  },
  {
    group: "Panels",
    shortcuts: [
      { keys: ["Ctrl", "B"], label: "Toggle AI chat panel" },
      { keys: ["Ctrl", "E"], label: "Toggle file explorer panel" },
    ],
  },
  {
    group: "Editor",
    shortcuts: [
      { keys: ["Ctrl", "Z"], label: "Undo" },
      { keys: ["Ctrl", "Shift", "Z"], label: "Redo" },
      { keys: ["Alt", "↑/↓"], label: "Move line up / down" },
      { keys: ["Ctrl", "/"], label: "Toggle comment" },
      { keys: ["Ctrl", "D"], label: "Select next occurrence" },
    ],
  },
  {
    group: "General",
    shortcuts: [
      { keys: ["?"], label: "Show this keyboard shortcuts overlay" },
      { keys: ["Esc"], label: "Close any open modal / overlay" },
    ],
  },
];

function Kbd({ children }: { children: React.ReactNode }) {
  return (
    <kbd className="inline-flex items-center justify-center min-w-[1.5rem] px-1.5 py-0.5 rounded-md text-[10px] font-mono font-semibold bg-gray-800 border border-gray-600 text-gray-300 shadow-[inset_0_-1px_0_0_rgba(255,255,255,0.1)]">
      {children}
    </kbd>
  );
}

export function KeyboardShortcutsModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  useEffect(() => {
    if (!isOpen) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-[#1a1a1a] border border-gray-700/60 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
          <div className="flex items-center gap-2.5">
            <Keyboard size={16} className="text-blue-400" />
            <h2 className="text-sm font-semibold text-white">Keyboard Shortcuts</h2>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-gray-500 hover:text-gray-200 hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X size={15} />
          </button>
        </div>

        {/* Shortcut grid */}
        <div className="overflow-y-auto max-h-[70vh] p-6 grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-6">
          {SHORTCUTS.map((group) => (
            <div key={group.group}>
              <p className="text-[10px] font-semibold uppercase tracking-widest text-gray-500 mb-2.5">
                {group.group}
              </p>
              <ul className="space-y-2">
                {group.shortcuts.map((s) => (
                  <li key={s.label} className="flex items-center justify-between gap-4">
                    <span className="text-xs text-gray-300 leading-tight">{s.label}</span>
                    <div className="flex items-center gap-1 shrink-0">
                      {s.keys.map((k, i) => (
                        <span key={i} className="flex items-center gap-1">
                          <Kbd>{k}</Kbd>
                          {i < s.keys.length - 1 && (
                            <span className="text-gray-600 text-[9px]">+</span>
                          )}
                        </span>
                      ))}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-gray-800 flex items-center justify-between">
          <p className="text-[10px] text-gray-600">Press <Kbd>?</Kbd> anytime to reopen this overlay</p>
          <button
            onClick={onClose}
            className="text-xs text-gray-500 hover:text-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
