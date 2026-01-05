/**
 * Resume-related API calls.
 */
import type { AxiosError } from 'axios';
import apiClient from '../../../services/apiClient';

export interface ResumeResponse {
  id: string;
  user_id: string;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface ResumeCreateRequest {
  content: string;
}

export interface ResumeUpdateRequest {
  content: string;
}

const BASE_URL = '/api/v1/resumes';

/**
 * Get the authenticated user's resume.
 * Returns null if none exists.
 */
export const getMyResume = async (): Promise<ResumeResponse | null> => {
  try {
    const response = await apiClient.get<ResumeResponse>(`${BASE_URL}/me`);
    return response.data;
  } catch (err) {
    const error = err as AxiosError;
    if (error.response?.status === 404) return null;
    throw err;
  }
};

/**
 * Create a resume (one per user).
 */
export const createResume = async (
  payload: ResumeCreateRequest
): Promise<ResumeResponse> => {
  const response = await apiClient.post<ResumeResponse>(
    `${BASE_URL}/`,
    payload
  );
  return response.data;
};

/**
 * Update the authenticated user's resume.
 */
export const updateMyResume = async (
  payload: ResumeUpdateRequest
): Promise<ResumeResponse> => {
  const response = await apiClient.put<ResumeResponse>(
    `${BASE_URL}/me`,
    payload
  );
  return response.data;
};
