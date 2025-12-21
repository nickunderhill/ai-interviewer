/**
 * Axios API client with request/response interceptors.
 * Automatically attaches JWT tokens and handles auth errors.
 */
import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios';
import { authService } from './authService';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
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
