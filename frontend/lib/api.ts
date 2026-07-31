import axios from "axios";

// Setup base configuration for Axios
const apiClient = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
  // Prevent silent failures when axios doesn't re-POST on 307 redirects.
  // All URLs should include trailing slashes to match FastAPI routes directly.
  maxRedirects: 0,
});


// Interceptor for responses to unwrap data if you use a standard structure like { data: ... }
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Basic error logging
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default apiClient;
