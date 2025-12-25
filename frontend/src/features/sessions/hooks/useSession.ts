/**
 * React Query hook for fetching session details.
 */
import { useQuery } from '@tanstack/react-query';
import { fetchSessionById } from '../api/sessionApi';

export function useSession(sessionId: string | undefined) {
  return useQuery({
    queryKey: ['sessions', sessionId],
    queryFn: () => fetchSessionById(sessionId!),
    enabled: !!sessionId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
