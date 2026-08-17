"use client";

import React, { useEffect, useState } from "react";
import { Plus, LayoutGrid, Loader2, FolderGit2, Trash2, ArrowUpRight, Sparkles, Layers } from "lucide-react";
import { ProjectService, Project, ProjectCreate } from "@/services/projects";
import { CreateProjectModal } from "@/components/CreateProjectModal";
import Link from "next/link";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const fetchProjects = async () => {
    setIsLoading(true);
    try {
      const data = await ProjectService.getProjects();
      setProjects(data);
    } catch (error) {
      console.error("Failed to fetch projects:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreateProject = async (data: ProjectCreate) => {
    await ProjectService.createProject(data);
    await fetchProjects();
  };

  const handleDeleteProject = async (projectId: string) => {
    if (deletingId === projectId) return;

    const confirmed = window.confirm(
      "Delete this workspace? This will permanently remove its files and vector memory."
    );
    if (!confirmed) return;

    setDeletingId(projectId);
    const previousProjects = projects;
    setProjects((prev) => prev.filter((p) => p.id !== projectId));

    try {
      await ProjectService.deleteProject(projectId);
      await fetchProjects();
    } catch (error: any) {
      if (error?.response?.status === 404) return;
      setProjects(previousProjects);
      alert("Failed to delete workspace.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground font-sans selection:bg-blue-600 selection:text-white">
      
      {/* Top Navigation Bar */}
      <header className="border-b border-border-subtle bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 sm:px-10 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-2.5 group">
            <div className="w-8 h-8 rounded-lg bg-blue-600/10 border border-blue-500/20 flex items-center justify-center text-blue-500 group-hover:scale-105 transition-transform">
              <FolderGit2 size={18} />
            </div>
            <span className="font-semibold text-sm tracking-tight text-text-primary">
              AgentCode <span className="text-text-muted font-normal ml-1">/ Workspaces</span>
            </span>
          </Link>

          <div className="flex items-center gap-3">
            <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-surface-2 border border-border-subtle text-xs text-text-secondary">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
              <span>Agents Ready</span>
            </div>
            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-sm hover:shadow-blue-500/25"
            >
              <Plus size={16} />
              <span>New Project</span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-6 sm:px-10 py-12">
        
        {/* Header Title Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-10 pb-6 border-b border-border-subtle">
          <div>
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 text-xs font-medium mb-3 border border-blue-500/20">
              <Sparkles size={12} />
              <span>Autonomous Environments</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary">
              Your Workspaces
            </h1>
            <p className="text-text-secondary text-sm mt-1">
              Select a repository to launch autonomous AI agents, refactor code, and manage execution flows.
            </p>
          </div>
          <div className="flex items-center gap-2 text-xs text-text-muted bg-surface-1 border border-border-subtle px-3 py-2 rounded-lg">
            <Layers size={14} className="text-blue-500" />
            <span>Total Active Workspaces: <strong className="text-text-primary">{projects.length}</strong></span>
          </div>
        </div>

        {/* Content States */}
        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-24 gap-3">
            <Loader2 className="w-7 h-7 animate-spin text-blue-500" />
            <p className="text-text-muted text-xs">Loading workspaces...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="bg-surface-1 border border-border-subtle rounded-2xl p-16 text-center max-w-md mx-auto shadow-sm">
            <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-500 mx-auto mb-4">
              <LayoutGrid size={22} />
            </div>
            <h3 className="text-base font-semibold text-text-primary mb-1">No workspaces found</h3>
            <p className="text-text-muted text-xs mb-6 leading-relaxed">
              Create your first project container to let autonomous agents connect to your codebase.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-lg text-xs font-medium transition-all"
            >
              <Plus size={14} />
              <span>Create Workspace</span>
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
            {projects.map((project) => (
              <div
                key={project.id}
                className="group relative bg-surface-1 hover:bg-surface-2 border border-border-subtle hover:border-blue-500/40 rounded-xl p-5 transition-all duration-200 shadow-sm flex flex-col justify-between"
              >
                <div>
                  {/* Card Top Row */}
                  <div className="flex items-center justify-between mb-3">
                    <div className="w-9 h-9 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-500">
                      <FolderGit2 size={18} />
                    </div>
                    <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-surface-2 border border-border-subtle text-text-muted">
                      {project.id.slice(0, 8)}
                    </span>
                  </div>

                  {/* Project Name & Description */}
                  <h3 className="text-base font-semibold text-text-primary tracking-tight mb-1.5 group-hover:text-blue-400 transition-colors">
                    {project.name}
                  </h3>
                  <p className="text-text-secondary text-xs line-clamp-2 leading-relaxed mb-6">
                    {project.description || "No description provided for this codebase workspace."}
                  </p>
                </div>

                {/* Card Footer Actions */}
                <div className="pt-3 border-t border-border-subtle flex items-center justify-between">
                  <Link
                    href={`/projects/${project.id}`}
                    className="inline-flex items-center gap-1.5 text-xs font-medium text-text-secondary hover:text-blue-400 transition-colors"
                  >
                    <span>Open workspace</span>
                    <ArrowUpRight size={14} />
                  </Link>

                  <button
                    onClick={() => handleDeleteProject(project.id)}
                    disabled={deletingId === project.id}
                    className="p-1.5 text-text-muted hover:text-red-400 hover:bg-red-500/10 rounded-md transition-colors"
                    title="Delete project"
                  >
                    {deletingId === project.id ? (
                      <Loader2 size={14} className="animate-spin text-red-400" />
                    ) : (
                      <Trash2 size={14} />
                    )}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modal Component */}
        <CreateProjectModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreateProject}
        />
      </main>

    </div>
  );
}