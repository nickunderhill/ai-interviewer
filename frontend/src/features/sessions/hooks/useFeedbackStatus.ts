/**
 * React Query hook for checking if feedback exists for a session.
 */
import { useQuery } from '@tanstack/react-query';
import apiClient from '../../../services/apiClient';

/**
 * Check if feedback exists for a session.
 * Returns true if feedback exists, false if 404.
 */
async function checkFeedbackExists(sessionId: string): Promise<boolean> {
  try {
    await apiClient.get(`/api/v1/sessions/${sessionId}/feedback`);
    return true;
  } catch (error: unknown) {
    if (error && typeof error === 'object' && 'response' in error) {
      const axiosError = error as { response?: { status?: number } };
      if (axiosError.response?.status === 404) {
        return false;
      }
    }
    throw error;
  }
}

export function useFeedbackStatus(sessionId: string | undefined) {
  return useQuery({
    queryKey: ['sessions', sessionId, 'feedback-status'],
    queryFn: () => checkFeedbackExists(sessionId!),
    enabled: !!sessionId,
    staleTime: 5 * 60 * 1000, // 5 minutes
    retry: false, // Don't retry on 404
  });
}
