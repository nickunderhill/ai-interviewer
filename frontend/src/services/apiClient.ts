/**
 * Axios API client with request/response interceptors.
 * Automatically attaches JWT tokens and handles auth errors.
 */
import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { authService } from './authService';

function normalizeApiBaseUrl(rawBaseUrl: string): string {
  // Call sites in this codebase use paths like `/api/v1/...`.
  // To avoid accidentally producing `/api/v1/api/v1/...`, ensure the base URL
  // is the backend origin (no `/api/v1` suffix).
  return rawBaseUrl.replace(/\/+$/, '').replace(/\/api\/v1$/, '');
}

const apiClient = axios.create({
  baseURL: normalizeApiBaseUrl(
    import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  ),
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Attach JWT token to all requests
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = authService.getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle 401/403 errors
apiClient.interceptors.response.use(
  response => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expired or invalid - logout and redirect
      try {
        authService.logout();
        // Note: Using window.location as a fallback since we can't access React Router here.
        // Consider implementing an event-based logout mechanism for better UX.
        window.location.href = '/login';
      } catch (logoutError) {
        console.error('Error during automatic logout:', logoutError);
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
