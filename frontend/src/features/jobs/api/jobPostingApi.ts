/**
 * API service for job postings.
 */
import apiClient from '../../../services/apiClient';
import type { JobPosting } from '../types/jobPosting';

const BASE_URL = '/api/v1/job-postings';

/**
 * Fetch all job postings for the authenticated user.
 */
export const fetchJobPostings = async (): Promise<JobPosting[]> => {
  const response = await apiClient.get<JobPosting[]>(BASE_URL);
  return response.data;
};
