/**
 * Types for metrics feature.
 */

export interface PracticedRole {
  job_posting_id: string;
  title: string;
  company: string | null;
  count: number;
}

export interface DashboardMetrics {
  completed_interviews: number;
  average_score: number | null;
  total_questions_answered: number;
  most_practiced_roles: PracticedRole[];
}
