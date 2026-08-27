"use client";

import React, { useEffect, useMemo, useState } from "react";
import {
  Plus,
  LayoutGrid,
  Loader2,
  FolderGit2,
  Trash2,
  ArrowUpRight,
  Sparkles,
  Layers,
  Search,
  GitBranch,
  Clock3,
  Code2,
  ChevronDown,
  Bot,
} from "lucide-react";
import Link from "next/link";

import {
  ProjectService,
  Project,
  ProjectCreate,
} from "@/services/projects";

import { CreateProjectModal } from "@/components/CreateProjectModal";

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "compact">("grid");

  /* =========================================================
     FETCH PROJECTS
  ========================================================= */

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

  /* =========================================================
     CREATE PROJECT
  ========================================================= */

  const handleCreateProject = async (data: ProjectCreate) => {
    try {
      await ProjectService.createProject(data);
      await fetchProjects();
      setIsModalOpen(false);
    } catch (error) {
      console.error("Failed to create project:", error);
      alert("Failed to create workspace.");
    }
  };

  /* =========================================================
     DELETE PROJECT
  ========================================================= */

  const handleDeleteProject = async (projectId: string) => {
    if (deletingId === projectId) return;

    const confirmed = window.confirm(
      "Delete this workspace? This will permanently remove its files and vector memory."
    );

    if (!confirmed) return;

    setDeletingId(projectId);

    const previousProjects = projects;

    setProjects((prev) =>
      prev.filter((project) => project.id !== projectId)
    );

    try {
      await ProjectService.deleteProject(projectId);
      await fetchProjects();
    } catch (error: any) {
      if (error?.response?.status === 404) {
        return;
      }

      setProjects(previousProjects);

      alert("Failed to delete workspace.");
    } finally {
      setDeletingId(null);
    }
  };

  /* =========================================================
     SEARCH
  ========================================================= */

  const filteredProjects = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();

    if (!query) {
      return projects;
    }

    return projects.filter((project) => {
      return (
        project.name.toLowerCase().includes(query) ||
        project.description?.toLowerCase().includes(query) ||
        project.language?.toLowerCase().includes(query) ||
        project.framework?.toLowerCase().includes(query)
      );
    });
  }, [projects, searchQuery]);

  /* =========================================================
     STATS
  ========================================================= */

  const totalProjects = projects.length;

  const activeProjects = projects.length;

  const languages = new Set(
    projects
      .map((project) => project.language)
      .filter(Boolean)
  ).size;

  /* =========================================================
     UI
  ========================================================= */

  return (
    <div className="min-h-screen overflow-hidden bg-[#f8f8fc] text-[#111118]">

      {/* =====================================================
          BACKGROUND
      ===================================================== */}

      <div className="pointer-events-none fixed inset-0 overflow-hidden">

        <div className="absolute left-1/2 top-[-200px] h-[500px] w-[800px] -translate-x-1/2 rounded-full bg-indigo-400/10 blur-[140px]" />

        <div className="absolute right-[-100px] top-[40%] h-[350px] w-[350px] rounded-full bg-cyan-300/10 blur-[130px]" />

        <div
          className="absolute inset-0 opacity-[0.025]"
          style={{
            backgroundImage:
              "linear-gradient(#6366f1 1px, transparent 1px), linear-gradient(90deg, #6366f1 1px, transparent 1px)",
            backgroundSize: "48px 48px",
          }}
        />

      </div>

      {/* =====================================================
          NAVBAR
      ===================================================== */}

      <header className="sticky top-0 z-50 border-b border-gray-200/80 bg-[#f8f8fc]/90 backdrop-blur-xl">

        <div className="mx-auto flex h-[68px] max-w-7xl items-center justify-between px-6 sm:px-10">

          {/* Logo */}

          <Link
            href="/"
            className="group flex items-center gap-3"
          >

            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-[#17171f] text-indigo-400 shadow-sm transition group-hover:scale-105">
              <Bot size={18} />
            </div>

            <div className="flex items-center">

              <span className="text-[16px] font-bold tracking-[-0.02em]">
                CodeVerse
              </span>

              <span className="mx-2 text-gray-300">
                /
              </span>

              <span className="text-sm font-medium text-gray-400">
                Workspaces
              </span>

            </div>

          </Link>

          {/* Right */}

          <div className="flex items-center gap-3">

            <div className="hidden items-center gap-2 rounded-full border border-gray-200 bg-white px-3 py-1.5 text-xs font-medium text-gray-500 shadow-sm sm:flex">

              <span className="h-2 w-2 animate-pulse rounded-full bg-emerald-500" />

              Agents Ready

            </div>

            <button
              onClick={() => setIsModalOpen(true)}
              className="flex items-center gap-2 rounded-xl bg-indigo-600 px-4 py-2.5 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:-translate-y-0.5 hover:bg-indigo-700"
            >

              <Plus size={16} />

              <span>
                New Project
              </span>

            </button>

          </div>

        </div>

      </header>

      {/* =====================================================
          MAIN
      ===================================================== */}

      <main className="relative z-10 mx-auto max-w-7xl px-6 py-10 sm:px-10">

        {/* ===================================================
            PAGE HEADER
        =================================================== */}

        <section className="mb-8">

          <div className="flex flex-col justify-between gap-6 lg:flex-row lg:items-end">

            <div>

              {/* Badge */}

              <div className="mb-4 inline-flex items-center gap-2 rounded-full border border-indigo-200 bg-white px-3 py-1.5 text-xs font-semibold text-indigo-600 shadow-sm">

                <Sparkles size={13} />

                Autonomous Development

              </div>

              <h1 className="text-3xl font-extrabold tracking-[-0.04em] text-gray-950 sm:text-4xl">

                Your Workspaces

              </h1>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-gray-500 sm:text-base">

                Connect your repositories and let CodeVerse agents
                understand, build, debug, test, and improve your codebase.

              </p>

            </div>

            {/* Active workspace */}

            <div className="flex items-center gap-3 rounded-2xl border border-gray-200 bg-white px-4 py-3 shadow-sm">

              <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">

                <Layers size={17} />

              </div>

              <div>

                <div className="text-[11px] font-medium text-gray-400">
                  Active Workspaces
                </div>

                <div className="text-lg font-bold text-gray-950">
                  {totalProjects}
                </div>

              </div>

            </div>

          </div>

        </section>

        {/* ===================================================
            STATS
        =================================================== */}

        <section className="mb-7 grid grid-cols-1 gap-3 sm:grid-cols-3">

          {/* Total */}

          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">

            <div className="flex items-center justify-between">

              <div>

                <div className="text-xs font-medium text-gray-400">
                  Total Projects
                </div>

                <div className="mt-1 text-2xl font-bold tracking-tight">
                  {totalProjects}
                </div>

              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600">
                <FolderGit2 size={18} />
              </div>

            </div>

          </div>

          {/* Active */}

          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">

            <div className="flex items-center justify-between">

              <div>

                <div className="text-xs font-medium text-gray-400">
                  Agent Ready
                </div>

                <div className="mt-1 text-2xl font-bold tracking-tight">
                  {activeProjects}
                </div>

              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-50 text-emerald-600">
                <Bot size={18} />
              </div>

            </div>

          </div>

          {/* Languages */}

          <div className="rounded-2xl border border-gray-200 bg-white p-4 shadow-sm">

            <div className="flex items-center justify-between">

              <div>

                <div className="text-xs font-medium text-gray-400">
                  Tech Stacks
                </div>

                <div className="mt-1 text-2xl font-bold tracking-tight">
                  {languages}
                </div>

              </div>

              <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-cyan-50 text-cyan-600">
                <Code2 size={18} />
              </div>

            </div>

          </div>

        </section>

        {/* ===================================================
            SEARCH + FILTER BAR
        =================================================== */}

        <section className="mb-7 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">

          {/* Search */}

          <div className="relative w-full sm:max-w-md">

            <Search
              size={17}
              className="absolute left-3.5 top-1/2 -translate-y-1/2 text-gray-400"
            />

            <input
              type="text"
              value={searchQuery}
              onChange={(event) =>
                setSearchQuery(event.target.value)
              }
              placeholder="Search workspaces..."
              className="h-11 w-full rounded-xl border border-gray-200 bg-white pl-10 pr-4 text-sm text-gray-900 outline-none shadow-sm transition placeholder:text-gray-400 focus:border-indigo-400 focus:ring-4 focus:ring-indigo-500/10"
            />

          </div>

          {/* Controls */}

          <div className="flex items-center gap-2">

            <button
              className="flex h-11 items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 text-xs font-medium text-gray-600 shadow-sm transition hover:border-gray-300"
            >

              <Layers size={14} />

              All Projects

              <ChevronDown size={13} />

            </button>

            <button
              onClick={() =>
                setViewMode(
                  viewMode === "grid"
                    ? "compact"
                    : "grid"
                )
              }
              className="flex h-11 items-center gap-2 rounded-xl border border-gray-200 bg-white px-4 text-xs font-medium text-gray-600 shadow-sm transition hover:border-gray-300"
            >

              <LayoutGrid size={14} />

              {viewMode === "grid"
                ? "Grid"
                : "Compact"}

            </button>

          </div>

        </section>

        {/* ===================================================
            LOADING
        =================================================== */}

        {isLoading && (

          <div className="flex flex-col items-center justify-center py-32">

            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">

              <Loader2
                size={22}
                className="animate-spin"
              />

            </div>

            <p className="mt-4 text-sm font-medium text-gray-600">
              Loading your workspaces...
            </p>

            <p className="mt-1 text-xs text-gray-400">
              Preparing your development environment
            </p>

          </div>

        )}

        {/* ===================================================
            EMPTY STATE
        =================================================== */}

        {!isLoading && projects.length === 0 && (

          <div className="relative overflow-hidden rounded-3xl border border-gray-200 bg-white px-6 py-20 text-center shadow-sm">

            <div className="absolute left-1/2 top-0 h-40 w-72 -translate-x-1/2 rounded-full bg-indigo-500/10 blur-[80px]" />

            <div className="relative">

              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50 text-indigo-600">

                <FolderGit2 size={28} />

              </div>

              <h3 className="mt-6 text-xl font-bold text-gray-950">
                No workspaces yet
              </h3>

              <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">

                Connect your first repository and let CodeVerse
                create an autonomous development environment for it.

              </p>

              <button
                onClick={() => setIsModalOpen(true)}
                className="mt-7 inline-flex items-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white shadow-lg shadow-indigo-500/20 transition hover:-translate-y-0.5 hover:bg-indigo-700"
              >

                <Plus size={16} />

                Create Workspace

              </button>

            </div>

          </div>

        )}

        {/* ===================================================
            NO SEARCH RESULTS
        =================================================== */}

        {!isLoading &&
          projects.length > 0 &&
          filteredProjects.length === 0 && (

            <div className="rounded-2xl border border-gray-200 bg-white px-6 py-16 text-center shadow-sm">

              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100 text-gray-500">

                <Search size={21} />

              </div>

              <h3 className="mt-4 text-base font-bold">
                No matching workspaces
              </h3>

              <p className="mt-1 text-sm text-gray-500">
                Try searching with a different project name or technology.
              </p>

            </div>

          )}

        {/* ===================================================
            PROJECT GRID
        =================================================== */}

        {!isLoading &&
          filteredProjects.length > 0 && (

            <div
              className={
                viewMode === "grid"
                  ? "grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-3"
                  : "grid grid-cols-1 gap-3"
              }
            >

              {filteredProjects.map((project) => (

                <div
                  key={project.id}
                  className={`group relative overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm transition duration-300 hover:-translate-y-1 hover:border-indigo-200 hover:shadow-xl hover:shadow-indigo-500/5 ${
                    viewMode === "grid"
                      ? "p-5"
                      : "p-4"
                  }`}
                >

                  {/* Top gradient */}

                  <div className="absolute inset-x-0 top-0 h-[2px] bg-gradient-to-r from-indigo-500 via-blue-500 to-cyan-400 opacity-0 transition group-hover:opacity-100" />

                  {/* Card */}

                  <div>

                    {/* Top row */}

                    <div className="flex items-center justify-between">

                      <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-50 text-indigo-600 transition group-hover:scale-105">

                        <FolderGit2 size={19} />

                      </div>

                      <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-1 font-mono text-[10px] text-gray-400">

                        {project.id.slice(0, 8)}

                      </span>

                    </div>

                    {/* Project name */}

                    <h3 className="mt-5 truncate text-lg font-bold tracking-tight text-gray-950 transition group-hover:text-indigo-600">

                      {project.name}

                    </h3>

                    {/* Description */}

                    <p className="mt-2 line-clamp-2 min-h-[40px] text-xs leading-5 text-gray-500">

                      {project.description ||
                        "No description provided for this codebase workspace."}

                    </p>

                    {/* Metadata */}

                    <div className="mt-5 flex flex-wrap gap-2">

                      {project.language && (

                        <span className="inline-flex items-center gap-1.5 rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-[10px] font-medium text-gray-600">

                          <Code2 size={11} />

                          {project.language}

                        </span>

                      )}

                      {project.framework && (

                        <span className="rounded-md border border-gray-200 bg-gray-50 px-2 py-1 text-[10px] font-medium text-gray-600">

                          {project.framework}

                        </span>

                      )}

                    </div>

                    {/* Agent status */}

                    <div className="mt-5 flex items-center gap-2 rounded-xl border border-emerald-100 bg-emerald-50/60 px-3 py-2">

                      <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />

                      <span className="text-[10px] font-semibold text-emerald-700">

                        AI agents ready

                      </span>

                    </div>

                  </div>

                  {/* Footer */}

                  <div className="mt-5 flex items-center justify-between border-t border-gray-100 pt-4">

                    <Link
                      href={`/projects/${project.id}`}
                      className="inline-flex items-center gap-1.5 text-xs font-semibold text-gray-600 transition hover:text-indigo-600"
                    >

                      Open workspace

                      <ArrowUpRight
                        size={14}
                        className="transition-transform group-hover:translate-x-0.5 group-hover:-translate-y-0.5"
                      />

                    </Link>

                    <div className="flex items-center gap-1">

                      <span className="mr-2 hidden items-center gap-1 text-[10px] text-gray-400 sm:flex">

                        <Clock3 size={11} />

                        Active

                      </span>

                      <button
                        onClick={() =>
                          handleDeleteProject(project.id)
                        }
                        disabled={
                          deletingId === project.id
                        }
                        className="rounded-lg p-2 text-gray-400 transition hover:bg-red-50 hover:text-red-500"
                        title="Delete workspace"
                      >

                        {deletingId === project.id ? (

                          <Loader2
                            size={14}
                            className="animate-spin"
                          />

                        ) : (

                          <Trash2 size={14} />

                        )}

                      </button>

                    </div>

                  </div>

                </div>

              ))}

            </div>

          )}

        {/* ===================================================
            BOTTOM INFO
        =================================================== */}

        {!isLoading && projects.length > 0 && (

          <div className="mt-8 flex flex-col items-center justify-between gap-3 rounded-2xl border border-indigo-100 bg-indigo-50/50 px-5 py-4 sm:flex-row">

            <div className="flex items-center gap-3">

              <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-indigo-600 shadow-sm">

                <Bot size={15} />

              </div>

              <div>

                <p className="text-xs font-semibold text-indigo-950">
                  CodeVerse agents are ready.
                </p>

                <p className="text-[11px] text-indigo-700/60">
                  Select a workspace to start coding with AI.
                </p>

              </div>

            </div>

            <button
              onClick={() => setIsModalOpen(true)}
              className="text-xs font-semibold text-indigo-600 transition hover:text-indigo-800"
            >
              + Create another workspace
            </button>

          </div>

        )}

      </main>

      {/* =====================================================
          MODAL
      ===================================================== */}

      <CreateProjectModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSubmit={handleCreateProject}
      />

    </div>
  );
}
