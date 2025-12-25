/**
 * Extended session types for analytics and comparisons.
 */

export interface SessionWithFeedbackScore {
  session_id: string;
  created_at: string;
  job_posting: {
    id: string;
    title: string;
    company: string | null;
  };
  overall_score: number;
}

export interface SessionScoreWithDelta extends SessionWithFeedbackScore {
  score_delta?: number; // Undefined for first session
  delta_direction?: 'up' | 'down' | 'none';
}
