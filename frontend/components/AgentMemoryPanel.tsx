"use client";

import React, { useEffect, useState } from "react";
import { Brain, Loader2, Database, Trash2, ArrowRight } from "lucide-react";

type MemoryItem = {
  id: string;
  content: string;
  created_at: string;
  metadata?: any;
};

export default function AgentMemoryPanel({ projectId }: { projectId: string }) {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    async function loadMemory() {
      setIsLoading(true);
      setError(null);
      try {
        const res = await fetch(`http://localhost:8000/api/v1/memory/session/${projectId}`);
        const data = await res.json();
        if (mounted) {
          // The API returns an array directly, or an ApiResponse format depending on backend.
          // Handle both forms robustly:
          if (Array.isArray(data)) {
            setMemories(data);
          } else if (data && data.success && Array.isArray(data.data)) {
            setMemories(data.data);
          } else {
            // It might be 404 or empty if no memory is stored
            setMemories([]);
          }
        }
      } catch (err: any) {
        if (mounted) {
          console.error("Failed to load memory:", err);
          setError("Could not load agent memory.");
        }
      } finally {
        if (mounted) setIsLoading(false);
      }
    }
    loadMemory();
    return () => { mounted = false; };
  }, [projectId]);

  const clearMemory = async () => {
    if (!confirm("Are you sure you want to clear the agent's memory for this project?")) return;
    setIsLoading(true);
    try {
      await fetch(`http://localhost:8000/api/v1/memory/session/${projectId}`, {
        method: "DELETE",
      });
      setMemories([]);
    } catch (err) {
      console.error(err);
      setError("Failed to clear memory.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500 gap-3">
        <Loader2 size={24} className="animate-spin text-blue-400" />
        <span className="text-sm">Recalling memories...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-gray-500 gap-2 p-6 text-center">
        <Brain size={32} className="text-red-400 opacity-50 mb-2" />
        <span className="text-sm text-red-400">{error}</span>
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full bg-[#1e1e1e]">
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-800 shrink-0">
        <div className="flex items-center gap-2 text-sm font-medium text-gray-200">
          <Database size={15} className="text-pink-400" />
          Agent Memory
        </div>
        {memories.length > 0 && (
          <button
            onClick={clearMemory}
            className="text-[10px] uppercase font-bold tracking-wider text-gray-500 hover:text-red-400 transition-colors px-2 py-1 rounded bg-gray-800 hover:bg-red-950"
          >
            Clear
          </button>
        )}
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {memories.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center text-gray-500 gap-3 max-w-[200px] mx-auto">
            <Brain size={40} className="text-gray-700 mb-2" />
            <p className="text-sm">The agent hasn't learned anything about this project yet.</p>
            <p className="text-xs text-gray-600">Context it discovers during tasks will automatically appear here.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {memories.map((mem) => (
              <div key={mem.id} className="p-3 bg-[#252526] border border-gray-700/50 rounded-lg">
                <div className="flex items-center gap-2 mb-2 text-xs text-gray-500">
                  <ArrowRight size={12} className="text-pink-400" />
                  <span className="font-mono">{new Date(mem.created_at).toLocaleString()}</span>
                </div>
                <div className="text-sm text-gray-300 leading-relaxed whitespace-pre-wrap">
                  {mem.content}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
