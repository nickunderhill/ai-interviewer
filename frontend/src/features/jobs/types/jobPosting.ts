/**
 * Job posting types.
 */

export interface JobPosting {
  id: string;
  title: string;
  company: string | null;
  experience_level: string | null;
  tech_stack: string[];
  language: string;
  created_at: string;
}

export interface JobPostingCreateRequest {
  title: string;
  description: string;
  company?: string | null;
  experience_level?: string | null;
  tech_stack?: string[];
  language?: 'en' | 'ua';
}

export interface JobPostingResponse extends JobPosting {
  user_id: string;
  description: string;
  language: string;
  updated_at: string;
}
