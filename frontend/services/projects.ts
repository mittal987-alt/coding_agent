import apiClient from "@/lib/api";

export interface Project {
  id: string;
  name: string;
  description: string;
  repository_path: string;
  repository_url?: string;
  llm_model?: string;
  language: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  repository_url?: string;
  llm_model?: string;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export const ProjectService = {
  getProjects: async (): Promise<Project[]> => {
    const response = await apiClient.get<ApiResponse<Project[]>>("/projects/");
    const data = response.data?.data;
    return Array.isArray(data) ? data : [];
  },

  getProject: async (id: string | number): Promise<Project> => {
    const response = await apiClient.get<ApiResponse<Project>>(`/projects/${id}/`);
    return response.data.data;
  },

  createProject: async (project: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post<ApiResponse<Project>>("/projects/", project);
    return response.data.data;
  },

  deleteProject: async (id: string | number): Promise<void> => {
    await apiClient.delete<ApiResponse<null>>(`/projects/${id}/`);
  },
};
