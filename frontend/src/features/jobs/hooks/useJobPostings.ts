/**
 * React Query hook for job postings.
 */
import { useQuery } from '@tanstack/react-query';
import { fetchJobPostings } from '../api/jobPostingApi';

/**
 * Hook to fetch job postings.
 */
export const useJobPostings = () => {
  return useQuery({
    queryKey: ['job-postings'],
    queryFn: fetchJobPostings,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};
