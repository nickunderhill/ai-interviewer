/**
 * API service for interview sessions.
 */
import apiClient from '../../../services/apiClient';
import type {
  Session,
  SessionDetail,
  SessionFilters,
  Message,
} from '../types/session';

const BASE_URL = '/api/v1/sessions';

/**
 * Create a new interview session for a job posting.
 */
export const createSession = async (jobPostingId: string): Promise<Session> => {
  const response = await apiClient.post<Session>(BASE_URL, {
    job_posting_id: jobPostingId,
  });
  return response.data;
};

/**
 * Fetch all sessions for the authenticated user.
 */
export const fetchSessions = async (
  filters?: SessionFilters
): Promise<Session[]> => {
  const params = new URLSearchParams();

  if (filters?.status) {
    params.append('status', filters.status);
  }
  if (filters?.startDate) {
    params.append('start_date', filters.startDate);
  }
  if (filters?.endDate) {
    params.append('end_date', filters.endDate);
  }
  if (filters?.jobPostingId) {
    params.append('job_posting_id', filters.jobPostingId);
  }
  if (filters?.originalSessionId) {
    params.append('original_session_id', filters.originalSessionId);
  }

  const url = params.toString() ? `${BASE_URL}?${params}` : BASE_URL;
  const response = await apiClient.get<Session[]>(url);
  return response.data;
};

/**
 * Fetch detailed session by ID including job posting details.
 */
export const fetchSessionById = async (id: string): Promise<SessionDetail> => {
  const response = await apiClient.get<SessionDetail>(`${BASE_URL}/${id}`);
  return response.data;
};

/**
 * Fetch all messages for a session.
 */
export const fetchSessionMessages = async (
  sessionId: string
): Promise<Message[]> => {
  const response = await apiClient.get<Message[]>(
    `${BASE_URL}/${sessionId}/messages`
  );
  return response.data;
};

/**
 * Submit an answer to the current interview question.
 */
export const submitAnswer = async (
  sessionId: string,
  answerText: string
): Promise<Message> => {
  const response = await apiClient.post<Message>(
    `${BASE_URL}/${sessionId}/answers`,
    {
      answer_text: answerText,
    }
  );
  return response.data;
};

/**
 * Create a retake (new session) from an existing completed session.
 */
export const retakeInterview = async (sessionId: string): Promise<Session> => {
  const response = await apiClient.post<Session>(
    `${BASE_URL}/${sessionId}/retake`
  );
  return response.data;
};

/**
 * Mark a session as completed.
 */
export const completeSession = async (sessionId: string): Promise<Session> => {
  const response = await apiClient.post<Session>(
    `${BASE_URL}/${sessionId}/complete`
  );
  return response.data;
};

/**
 * Delete a session.
 */
export const deleteSession = async (sessionId: string): Promise<void> => {
  await apiClient.delete(`${BASE_URL}/${sessionId}`);
};
