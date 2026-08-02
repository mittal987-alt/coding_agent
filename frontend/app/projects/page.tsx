"use client";

import React, { useEffect, useState } from "react";
import { Plus, LayoutGrid, Loader2 } from "lucide-react";
import { ProjectService, Project, ProjectCreate } from "@/services/projects";
import { ProjectCard } from "@/components/ProjectCard";
import { CreateProjectModal } from "@/components/CreateProjectModal";

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
    await fetchProjects(); // Refresh the list
  };

  const handleDeleteProject = async (projectId: string) => {
    // Guard against double-invocation (double-click, re-render, duplicate
    // event firing, etc.) — if a delete for this exact project is already
    // in flight, ignore the second call instead of sending another DELETE.
    if (deletingId === projectId) return;

    const confirmed = window.confirm(
      "Delete this project? This will permanently remove it and its uploaded files. This cannot be undone."
    );
    if (!confirmed) return;

    setDeletingId(projectId);

    // Optimistically remove from the list so it disappears immediately
    const previousProjects = projects;
    setProjects((prev) => prev.filter((p) => p.id !== projectId));

    try {
      await ProjectService.deleteProject(projectId);
      // Re-sync with backend to be safe (in case deletion partially failed server-side)
      await fetchProjects();
    } catch (error: any) {
      // If the backend says it's already gone (404), treat it as a
      // successful outcome rather than a failure — the project is deleted
      // either way, this was likely just a duplicate request.
      const status = error?.response?.status;
      if (status === 404) {
        console.warn("Project already deleted (likely a duplicate request).");
        return;
      }

      console.error("Failed to delete project:", error);
      // Roll back the optimistic removal so it doesn't silently vanish on a real failure
      setProjects(previousProjects);
      alert("Failed to delete project. Check the console/backend logs for details.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-black p-8">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
              <LayoutGrid className="text-blue-600 dark:text-blue-400" />
              Your Projects
            </h1>
            <p className="text-gray-500 dark:text-gray-400 mt-2">
              Manage your AI software engineering workspaces.
            </p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-medium transition-colors shadow-sm shadow-blue-600/20"
          >
            <Plus size={20} />
            New Project
          </button>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-32">
            <Loader2 className="w-8 h-8 animate-spin text-blue-600" />
          </div>
        ) : projects.length === 0 ? (
          <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-2xl p-12 text-center">
            <div className="w-16 h-16 bg-blue-50 dark:bg-blue-900/20 text-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4">
              <LayoutGrid size={32} />
            </div>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No projects yet</h3>
            <p className="text-gray-500 dark:text-gray-400 mb-6 max-w-sm mx-auto">
              Create your first AI software engineering project to get started with autonomous development.
            </p>
            <button
              onClick={() => setIsModalOpen(true)}
              className="inline-flex items-center gap-2 bg-gray-900 dark:bg-white text-white dark:text-black px-6 py-2.5 rounded-xl font-medium hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
            >
              <Plus size={18} />
              Create Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {projects.map((project) => (
              <ProjectCard
                key={project.id}
                project={project}
                onDelete={handleDeleteProject}
                isDeleting={deletingId === project.id}
              />
            ))}
          </div>
        )}

        <CreateProjectModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          onSubmit={handleCreateProject}
        />
      </div>
    </div>
  );
}