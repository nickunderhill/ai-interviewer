/**
 * Session types for the interview sessions feature.
 */

export interface JobPosting {
  id: string;
  title: string;
  company: string;
}

export interface JobPostingDetail extends JobPosting {
  description: string;
  tech_stack?: string[];
  experience_level?: string;
}

export interface Session {
  id: string;
  job_posting: JobPosting;
  status: 'active' | 'paused' | 'completed';
  current_question_number: number;
  created_at: string;
  updated_at: string;
}

export interface SessionDetail extends Omit<Session, 'job_posting'> {
  job_posting: JobPostingDetail;
}

export interface Message {
  id: string;
  message_type: 'question' | 'answer';
  content: string;
  question_type: 'technical' | 'behavioral' | 'situational' | null;
  created_at: string;
}

export interface SessionFilters {
  status?: 'active' | 'paused' | 'completed';
  startDate?: string;
  endDate?: string;
  jobPostingId?: string;
}
