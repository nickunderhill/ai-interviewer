/**
 * React Query hook for metrics.
 */
import { useQuery } from '@tanstack/react-query';
import { fetchDashboardMetrics } from '../api/metricsApi';

/**
 * Hook to fetch dashboard metrics.
 */
export const useDashboardMetrics = () => {
  return useQuery({
    queryKey: ['metrics', 'dashboard'],
    queryFn: fetchDashboardMetrics,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
