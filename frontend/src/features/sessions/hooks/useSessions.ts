/**
 * React Query hooks for session management.
 */
import { useQuery } from '@tanstack/react-query';
import { fetchSessions } from '../api/sessionApi';
import type { SessionFilters } from '../types/session';

/**
 * Hook to fetch sessions with optional filtering.
 */
export const useSessions = (filters?: SessionFilters) => {
  return useQuery({
    queryKey: ['sessions', filters],
    queryFn: () => fetchSessions(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes - reduce unnecessary refetches
  });
};
