import apiClient from "@/lib/api";
import { ApiResponse } from "./projects";

export interface HealthStatus {
  status: string;
  version: string;
  timestamp: string;
}

export const HealthService = {
  getHealth: async (): Promise<HealthStatus> => {
    const response = await apiClient.get<ApiResponse<HealthStatus>>("/health");
    // Depending on backend, it might return data directly or wrapped in ApiResponse
    return response.data.data || response.data;
  },
};
