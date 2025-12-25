/**
 * React Query hook for fetching session messages.
 */
import { useQuery } from '@tanstack/react-query';
import { fetchSessionMessages } from '../api/sessionApi';

export function useMessages(sessionId: string | undefined) {
  return useQuery({
    queryKey: ['sessions', sessionId, 'messages'],
    queryFn: () => fetchSessionMessages(sessionId!),
    enabled: !!sessionId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
