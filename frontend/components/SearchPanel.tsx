"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { Search, X, FileCode, Loader2, ChevronDown, ChevronRight, CaseSensitive, ReplaceAll } from "lucide-react";
import { apiBaseUrl } from "@/lib/api";

type SearchResult = {
  path: string;
  line: number;
  preview: string;
};

type GroupedResults = Record<string, SearchResult[]>;

function groupByFile(results: SearchResult[]): GroupedResults {
  const groups: GroupedResults = {};
  for (const r of results) {
    if (!groups[r.path]) groups[r.path] = [];
    groups[r.path].push(r);
  }
  return groups;
}

function highlightMatch(text: string, query: string, caseSensitive: boolean): React.ReactNode {
  if (!query) return text;
  const needle = caseSensitive ? query : query.toLowerCase();
  const haystack = caseSensitive ? text : text.toLowerCase();
  const idx = haystack.indexOf(needle);
  if (idx === -1) return text;
  return (
    <>
      {text.slice(0, idx)}
      <mark className="bg-yellow-400/30 text-yellow-300 rounded-sm px-0.5">
        {text.slice(idx, idx + query.length)}
      </mark>
      {text.slice(idx + query.length)}
    </>
  );
}

export default function SearchPanel({
  projectId,
  onFileOpen,
}: {
  projectId: string;
  onFileOpen: (path: string) => void;
}) {
  const [query, setQuery] = useState("");
  const [caseSensitive, setCaseSensitive] = useState(false);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [resultMsg, setResultMsg] = useState<string | null>(null);
  const [replaceStr, setReplaceStr] = useState("");
  const [isReplacing, setIsReplacing] = useState(false);
  const [collapsedFiles, setCollapsedFiles] = useState<Set<string>>(new Set());
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const doSearch = useCallback(
    async (q: string) => {
      if (q.trim().length < 2) {
        setResults([]);
        setResultMsg(null);
        return;
      }
      setIsSearching(true);
      try {
        const url = `${apiBaseUrl}/projects/${projectId}/search?q=${encodeURIComponent(q)}&case_sensitive=${caseSensitive}`;
        const res = await fetch(url);
        const json = await res.json();
        if (json.success) {
          setResults(json.data || []);
          setResultMsg(json.message || null);
        } else {
          setResults([]);
          setResultMsg("Search failed.");
        }
      } catch {
        setResults([]);
        setResultMsg("Could not reach backend.");
      } finally {
        setIsSearching(false);
      }
    },
    [projectId, caseSensitive]
  );

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => doSearch(query), 350);
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
  }, [query, doSearch]);

  const grouped = groupByFile(results);
  const fileCount = Object.keys(grouped).length;

  const toggleFile = (path: string) => {
    setCollapsedFiles((prev) => {
      const next = new Set(prev);
      if (next.has(path)) next.delete(path);
      else next.add(path);
      return next;
    });
  };

  const handleReplace = async () => {
    if (!query.trim()) return;
    if (!confirm(`Are you sure you want to replace all occurrences of '${query}' with '${replaceStr}'? This action cannot be easily undone.`)) return;
    setIsReplacing(true);
    try {
      const res = await fetch(`${apiBaseUrl}/projects/${projectId}/files/replace`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ search: query, replace: replaceStr, case_sensitive: caseSensitive })
      });
      const json = await res.json();
      if (json.success) {
        setResultMsg(json.message);
        doSearch(query); // refresh results
      } else {
        setResultMsg(json.message || "Replace failed");
      }
    } catch {
      setResultMsg("Replace failed to reach backend.");
    } finally {
      setIsReplacing(false);
    }
  };

  return (
    <div className="flex flex-col h-full overflow-hidden text-sm">
      {/* Search input bar */}
      <div className="px-3 py-2.5 border-b border-gray-800 shrink-0">
        <div className="flex items-center gap-1.5 bg-gray-900 border border-gray-700 rounded-lg px-2.5 py-1.5 focus-within:border-blue-500 transition-colors">
          <Search size={13} className="text-gray-500 shrink-0" />
          <input
            ref={inputRef}
            autoFocus
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search in files…"
            className="flex-1 bg-transparent outline-none text-xs text-gray-200 placeholder-gray-600 min-w-0"
          />
          {isSearching && <Loader2 size={12} className="animate-spin text-gray-500 shrink-0" />}
          {query && !isSearching && (
            <button
              onClick={() => { setQuery(""); setResults([]); setResultMsg(null); }}
              className="text-gray-600 hover:text-gray-300 transition-colors shrink-0"
            >
              <X size={12} />
            </button>
          )}
          <button
            onClick={() => setCaseSensitive((p) => !p)}
            title="Case sensitive"
            className={`p-0.5 rounded transition-colors shrink-0 ${caseSensitive ? "text-blue-400" : "text-gray-600 hover:text-gray-300"}`}
          >
            <CaseSensitive size={13} />
          </button>
        </div>
        
        {/* Replace Input - shown if we have a query */}
        {query.trim().length >= 2 && (
          <div className="flex items-center gap-1.5 mt-2 bg-gray-900 border border-gray-700 rounded-lg px-2.5 py-1.5 focus-within:border-blue-500 transition-colors">
            <ReplaceAll size={13} className="text-gray-500 shrink-0" />
            <input
              value={replaceStr}
              onChange={(e) => setReplaceStr(e.target.value)}
              placeholder="Replace with…"
              className="flex-1 bg-transparent outline-none text-xs text-gray-200 placeholder-gray-600 min-w-0"
            />
            {results.length > 0 && (
              <button
                onClick={handleReplace}
                disabled={isReplacing}
                className="bg-blue-600 hover:bg-blue-500 disabled:bg-gray-700 disabled:text-gray-500 text-white text-[10px] px-2 py-0.5 rounded transition-colors"
              >
                {isReplacing ? <Loader2 size={10} className="animate-spin" /> : "Replace All"}
              </button>
            )}
          </div>
        )}

        {resultMsg && query.trim().length >= 2 && !isSearching && (
          <p className="text-[10px] text-gray-500 mt-1.5 px-0.5">
            {resultMsg}
            {fileCount > 0 && !resultMsg.includes("Replaced") && ` — ${fileCount} file${fileCount > 1 ? "s" : ""}`}
          </p>
        )}
      </div>

      {/* Results list */}
      <div className="flex-1 overflow-y-auto">
        {results.length === 0 && !isSearching && query.trim().length >= 2 && (
          <div className="px-4 py-8 text-center">
            <Search size={20} className="mx-auto mb-2 text-gray-700" />
            <p className="text-xs text-gray-600">No matches found for<br /><span className="text-gray-400 font-mono">"{query}"</span></p>
          </div>
        )}

        {Object.entries(grouped).map(([filePath, fileResults]) => {
          const isCollapsed = collapsedFiles.has(filePath);
          const fileName = filePath.split("/").pop() || filePath;
          return (
            <div key={filePath} className="border-b border-gray-800/50 last:border-0">
              {/* File header */}
              <button
                onClick={() => toggleFile(filePath)}
                className="w-full flex items-center gap-1.5 px-3 py-1.5 hover:bg-gray-800/40 transition-colors text-left group"
              >
                {isCollapsed
                  ? <ChevronRight size={11} className="text-gray-500 shrink-0" />
                  : <ChevronDown size={11} className="text-gray-500 shrink-0" />}
                <FileCode size={12} className="text-blue-400 shrink-0" />
                <span className="text-xs text-gray-200 truncate font-medium flex-1" title={filePath}>
                  {fileName}
                </span>
                <span className="text-[10px] text-gray-600 shrink-0 group-hover:text-gray-400">
                  {fileResults.length}
                </span>
              </button>

              {/* Matches */}
              {!isCollapsed && (
                <ul>
                  {fileResults.map((r, i) => (
                    <li key={`${r.path}-${r.line}-${i}`}>
                      <button
                        onClick={() => onFileOpen(r.path)}
                        className="w-full text-left px-3 py-1 hover:bg-blue-600/10 group flex items-start gap-2 transition-colors"
                      >
                        <span className="text-[10px] text-gray-600 font-mono w-7 shrink-0 pt-0.5 text-right">
                          {r.line}
                        </span>
                        <span className="text-xs text-gray-400 font-mono truncate group-hover:text-gray-200 transition-colors leading-relaxed">
                          {highlightMatch(r.preview, query, caseSensitive)}
                        </span>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
