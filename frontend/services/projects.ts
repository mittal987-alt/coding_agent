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
export interface SearchResult {
  path: string;
  line: number;
  preview: string;
}
export interface ProjectCreate {
  name: string;
  description?: string;
  repository_url?: string;
  llm_model?: string;
}

export interface ProjectUpdate {
  name?: string;
  repository_url?: string;
  llm_model?: string;
  language?: string;
  framework?: string;
  archived?: boolean;
}

export interface ApiResponse<T> {
  success: boolean;
  message: string;
  data: T;
}

export interface ApiKey {
  id: string;
  label: string;
  provider: string;
  preview: string;
}
export interface SearchResult {
  path: string;
  line: number;
  preview: string;
}


export interface EnvVar {
  id: string;
  key: string;
  value: string;
}


export const ProjectService = {
  getProjects: async (): Promise<Project[]> => {
    const response = await apiClient.get<ApiResponse<Project[]>>("/projects/");
    const data = response.data?.data;
    return Array.isArray(data) ? data : [];
  },
  searchFiles: async (projectId: string, query: string): Promise<SearchResult[]> => {
    const response = await apiClient.get<ApiResponse<SearchResult[]>>(
      `/projects/${projectId}/search`,
      { params: { q: query } }
    );
    return response.data.data || [];
  },


  getProject: async (id: string | number): Promise<Project> => {
    const response = await apiClient.get<ApiResponse<Project>>(`/projects/${id}`);
    return response.data.data;
  },
  
  createProject: async (project: ProjectCreate): Promise<Project> => {
    const response = await apiClient.post<ApiResponse<Project>>("/projects/", project);
    return response.data.data;
  },

  updateProject: async (id: string | number, update: ProjectUpdate): Promise<Project> => {
    const response = await apiClient.patch<ApiResponse<Project>>(`/projects/${id}`, update);
    return response.data.data;
  },

  deleteProject: async (id: string | number): Promise<void> => {
    await apiClient.delete<ApiResponse<null>>(`/projects/${id}`);
  },

  // --- Environment variables ---
  getEnvVars: async (projectId: string): Promise<EnvVar[]> => {
    const response = await apiClient.get<ApiResponse<EnvVar[]>>(`/projects/${projectId}/env-vars`);
    return response.data.data ?? [];
  },

  saveEnvVars: async (projectId: string, vars: EnvVar[]): Promise<void> => {
    // Convert list → plain key:value dict expected by the backend
    const dict: Record<string, string> = {};
    for (const v of vars) {
      if (v.key.trim()) dict[v.key.trim()] = v.value;
    }
    await apiClient.put(`/projects/${projectId}/env-vars`, dict);
  },

  // --- API Keys ---
  getApiKeys: async (projectId: string): Promise<ApiKey[]> => {
    const response = await apiClient.get<ApiResponse<ApiKey[]>>(`/projects/${projectId}/api-keys`);
    return response.data.data ?? [];
  },

  addApiKey: async (
    projectId: string,
    payload: { label: string; provider: string; key_value: string }
  ): Promise<ApiKey> => {
    const response = await apiClient.post<ApiResponse<ApiKey>>(
      `/projects/${projectId}/api-keys`,
      payload
    );
    return response.data.data;
  },

  deleteApiKey: async (projectId: string, keyId: string): Promise<void> => {
    await apiClient.delete(`/projects/${projectId}/api-keys/${keyId}`);
  },
};