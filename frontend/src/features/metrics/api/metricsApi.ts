/**
 * API service for metrics.
 */
import apiClient from '../../../services/apiClient';
import type { DashboardMetrics } from '../types/metrics';

const BASE_URL = '/api/v1/metrics';

/**
 * Fetch dashboard metrics for the authenticated user.
 */
export const fetchDashboardMetrics = async (): Promise<DashboardMetrics> => {
  const response = await apiClient.get<DashboardMetrics>(
    `${BASE_URL}/dashboard`
  );
  return response.data;
};
