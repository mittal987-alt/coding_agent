"use client";

import React, { useEffect, useState } from "react";
import { Activity, GitCommit, FileCode, CheckCircle, X, BarChart3, Clock, Users } from "lucide-react";
import { ProjectService } from "@/services/projects";

export default function ProjectDashboardModal({
  isOpen,
  onClose,
  projectId
}: {
  isOpen: boolean;
  onClose: () => void;
  projectId: string;
}) {
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    if (isOpen) {
      ProjectService.getProjectStats(projectId).then(setStats).catch(console.error);
    }
  }, [isOpen, projectId]);

  // Handle escape to close
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-[150] flex items-center justify-center bg-black/60 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-[#1e1e1e] border border-gray-700/80 rounded-xl p-6 w-full max-w-2xl shadow-2xl relative"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
        >
          <X size={16} />
        </button>

        <div className="flex items-center gap-3 mb-6">
          <div className="p-2 bg-blue-500/20 rounded-lg text-blue-400 border border-blue-500/30">
            <BarChart3 size={20} />
          </div>
          <div>
            <h2 className="text-lg font-semibold text-white">Project Dashboard</h2>
            <p className="text-xs text-gray-400">Activity and agent metrics for this workspace.</p>
          </div>
        </div>

        {stats ? (
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#252526] border border-gray-700/50 p-4 rounded-xl flex items-center gap-4">
              <div className="p-2 bg-green-500/10 text-green-400 rounded-lg">
                <FileCode size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Lines Changed</p>
                <p className="text-2xl font-bold text-white">{stats.linesChanged}</p>
              </div>
            </div>

            <div className="bg-[#252526] border border-gray-700/50 p-4 rounded-xl flex items-center gap-4">
              <div className="p-2 bg-purple-500/10 text-purple-400 rounded-lg">
                <Activity size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Files Modified</p>
                <p className="text-2xl font-bold text-white">{stats.filesModified}</p>
              </div>
            </div>

            <div className="bg-[#252526] border border-gray-700/50 p-4 rounded-xl flex items-center gap-4">
              <div className="p-2 bg-yellow-500/10 text-yellow-400 rounded-lg">
                <GitCommit size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Agent Commits</p>
                <p className="text-2xl font-bold text-white">{stats.totalCommits}</p>
              </div>
            </div>

            <div className="bg-[#252526] border border-gray-700/50 p-4 rounded-xl flex items-center gap-4">
              <div className="p-2 bg-blue-500/10 text-blue-400 rounded-lg">
                <CheckCircle size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Tests Passed</p>
                <p className="text-2xl font-bold text-white">{stats.testsPassed}</p>
              </div>
            </div>

            <div className="bg-[#252526] border border-gray-700/50 p-4 rounded-xl flex items-center gap-4">
              <div className="p-2 bg-orange-500/10 text-orange-400 rounded-lg">
                <Users size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Active Agents</p>
                <p className="text-2xl font-bold text-white">{stats.activeAgents}</p>
              </div>
            </div>

            <div className="bg-[#252526] border border-gray-700/50 p-4 rounded-xl flex items-center gap-4">
              <div className="p-2 bg-teal-500/10 text-teal-400 rounded-lg">
                <Clock size={20} />
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wider font-semibold">Time Saved</p>
                <p className="text-2xl font-bold text-white">{stats.timeSaved}</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="h-48 flex items-center justify-center">
            <span className="text-gray-500 text-sm">Loading stats...</span>
          </div>
        )}
      </div>
    </div>
  );
}
