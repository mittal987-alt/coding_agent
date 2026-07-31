import React from "react";
import Link from "next/link";
import { Project } from "@/services/projects";
import { Folder, ArrowRight } from "lucide-react";

interface ProjectCardProps {
  project: Project;
}

export const ProjectCard: React.FC<ProjectCardProps> = ({ project }) => {
  return (
    <Link href={`/projects/${project.id}`}>
      <div className="group border border-gray-200 dark:border-gray-800 rounded-xl p-6 hover:shadow-lg transition-all duration-300 bg-white dark:bg-gray-900 cursor-pointer h-full flex flex-col hover:-translate-y-1">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 group-hover:bg-blue-100 dark:group-hover:bg-blue-900/50 transition-colors">
            <Folder size={24} />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
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
