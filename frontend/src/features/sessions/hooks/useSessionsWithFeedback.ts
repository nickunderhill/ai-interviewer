/**
 * React Query hook for session analytics.
 */
import { useQuery } from '@tanstack/react-query';
import { fetchSessionsWithFeedback } from '../api/analyticsApi';

/**
 * Hook to fetch sessions with feedback scores.
 */
export const useSessionsWithFeedback = () => {
  return useQuery({
    queryKey: ['sessions', 'with-feedback'],
    queryFn: fetchSessionsWithFeedback,
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};
