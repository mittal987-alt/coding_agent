import React from "react";
import Link from "next/link";
import { Project } from "@/services/projects";
import { Folder, ArrowRight, Trash2, Loader2 } from "lucide-react";

interface ProjectCardProps {
  project: Project;
  onDelete?: (projectId: string) => void;
  isDeleting?: boolean;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({
  project,
  onDelete,
  isDeleting = false,
}) => {
  const handleDeleteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    onDelete?.(project.id);
  };

  return (
    <Link href={`/projects/${project.id}`}>
      <div className="group relative border border-gray-200 dark:border-gray-800 rounded-xl p-6 hover:shadow-lg transition-all duration-300 bg-white dark:bg-gray-900 cursor-pointer h-full flex flex-col hover:-translate-y-1">
        {onDelete && (
          <button
            onClick={handleDeleteClick}
            disabled={isDeleting}
            title="Delete project"
            className="absolute top-4 right-4 p-2 rounded-lg text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 opacity-0 group-hover:opacity-100 transition-all disabled:opacity-100 disabled:cursor-not-allowed z-10"
          >
            {isDeleting ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Trash2 size={16} />
            )}
          </button>
        )}

        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
            <Folder size={24} />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors pr-8">
            {project.name}
          </h3>
        </div>
        <p className="text-gray-600 dark:text-gray-400 text-sm line-clamp-3 mb-6 flex-grow">
          {project.description || "No description provided."}
        </p>
        <div className="flex items-center justify-between mt-auto">
          <span className="text-xs font-medium px-2.5 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-300 rounded-full">
            {project.language || project.status}
          </span>
          <span className="text-blue-600 dark:text-blue-400 flex items-center gap-1 text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
            View Details <ArrowRight size={16} />
          </span>
        </div>
      </div>
    </Link>
  );
};