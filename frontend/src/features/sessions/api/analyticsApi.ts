/**
 * API service for session analytics and comparisons.
 */
import apiClient from '../../../services/apiClient';
import type { SessionWithFeedbackScore } from '../types/analytics';

const BASE_URL = '/api/v1/sessions';

/**
 * Fetch sessions with feedback scores for comparison/trends.
 */
export const fetchSessionsWithFeedback = async (): Promise<
  SessionWithFeedbackScore[]
> => {
  const response = await apiClient.get<SessionWithFeedbackScore[]>(
    `${BASE_URL}/with-feedback`
  );
  return response.data;
};
