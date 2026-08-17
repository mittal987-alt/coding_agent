import apiClient from "@/lib/api";

export interface Project {
  id: string;
  name: string;
  description: string;
  repository_path: string;
  repository_url?: string;
  default_branch?: string;
  github_token?: string;
  llm_model?: string;
  system_prompt?: string;
  language: string;
  framework?: string;
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
  description?: string;
  repository_url?: string;
  default_branch?: string;
  github_token?: string;
  llm_model?: string;
  system_prompt?: string;
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

export interface EnvVar {
  id: string;
  key: string;
  value: string;
}

// --- Feature 5/6/7/8 additions ---

export interface GitCommit {
  hash: string;
  author: string;
  email: string;
  date: string;
  message: string;
}

export interface RunResult {
  run_id: string;
  command: string;
  label: string;
}

export interface IndexResult {
  chunks_indexed: number;
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

  getProjectStats: async (id: string | number): Promise<any> => {
    const response = await apiClient.get<ApiResponse<any>>(`/projects/${id}/stats`);
    return response.data.data;
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

  // --- Feature 6: Git history & rollback ---
  getProjectStats: async (projectId: string): Promise<any> => {
    const response = await apiClient.get<ApiResponse<any>>(`/projects/${projectId}/stats`);
    return response.data.data;
  },

  getGitLog: async (projectId: string, n = 20): Promise<GitCommit[]> => {
    const response = await apiClient.get<ApiResponse<GitCommit[]>>(
      `/projects/${projectId}/git/log`,
      { params: { n } }
    );
    return response.data.data || [];
  },

  rollbackCommit: async (projectId: string, commitHash?: string | null): Promise<void> => {
    await apiClient.post(`/projects/${projectId}/git/rollback`, {
      commit_hash: commitHash || null,
    });
  },

  // --- Feature 8: RAG indexing ---
  indexProject: async (projectId: string): Promise<IndexResult> => {
    // Indexing involves downloading a ~90MB SentenceTransformer model (on first run)
    // and running CPU embeddings, which can easily exceed the default 10s timeout.
    // Give it 3 minutes instead.
    const response = await apiClient.post<ApiResponse<IndexResult>>(
      `/projects/${projectId}/index`,
      {},
      { timeout: 180000 }
    );
    return response.data.data;
  },

  // --- Feature 7: Run/Build/Test ---
  runProject: async (projectId: string): Promise<RunResult> => {
    const response = await apiClient.post<ApiResponse<RunResult>>(
      `/projects/${projectId}/run`
    );
    return response.data.data;
  },
};