import React, { useState, useEffect, useRef } from "react";
import { X, Search, FileCode, Loader2 } from "lucide-react";
import { ProjectService, SearchResult } from "@/services/projects";

interface SearchModalProps {
  isOpen: boolean;
  projectId: string;
  onClose: () => void;
  onSelectResult: (path: string) => void;
}

export const SearchModal: React.FC<SearchModalProps> = ({
  isOpen,
  projectId,
  onClose,
  onSelectResult,
}) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (isOpen) {
      setQuery("");
      setResults([]);
      setTimeout(() => inputRef.current?.focus(), 50);
    }
  }, [isOpen]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);

    if (query.trim().length < 2) {
      setResults([]);
      return;
    }

    debounceRef.current = setTimeout(async () => {
      setIsSearching(true);
      try {
        const data = await ProjectService.searchFiles(projectId, query.trim());
        setResults(data);
      } catch (err) {
        console.error("Search failed:", err);
        setResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 300);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query, projectId]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-24 p-4 bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-900 rounded-2xl w-full max-w-2xl shadow-2xl overflow-hidden border border-gray-200 dark:border-gray-800 max-h-[70vh] flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center gap-3 p-4 border-b border-gray-100 dark:border-gray-800">
          <Search size={18} className="text-gray-400 shrink-0" />
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search across all files in this project..."
            className="flex-1 bg-transparent outline-none text-gray-900 dark:text-white placeholder-gray-400"
          />
          {isSearching && <Loader2 size={16} className="animate-spin text-gray-400 shrink-0" />}
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 shrink-0"
          >
            <X size={18} />
          </button>
        </div>

        <div className="overflow-y-auto flex-1">
          {query.trim().length >= 2 && !isSearching && results.length === 0 && (
            <div className="p-8 text-center text-sm text-gray-500">
              No matches found for "{query}"
            </div>
          )}

          {results.map((result, i) => (
            <button
              key={`${result.path}-${result.line}-${i}`}
              onClick={() => {
                onSelectResult(result.path);
                onClose();
              }}
              className="w-full text-left px-4 py-2.5 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors border-b border-gray-100 dark:border-gray-800/50 last:border-0"
            >
              <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mb-1">
                <FileCode size={12} />
                <span className="font-mono truncate">{result.path}</span>
                <span className="shrink-0">:{result.line}</span>
              </div>
              <div className="text-sm text-gray-800 dark:text-gray-200 font-mono truncate pl-5">
                {result.preview}
              </div>
            </button>
          ))}
        </div>

        <div className="px-4 py-2 border-t border-gray-100 dark:border-gray-800 text-xs text-gray-400 flex items-center gap-3">
          <span>↵ open file</span>
          <span>esc close</span>
        </div>
      </div>
    </div>
  );
};