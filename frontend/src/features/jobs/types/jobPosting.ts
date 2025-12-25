/**
 * Job posting types.
 */

export interface JobPosting {
  id: string;
  title: string;
  company: string | null;
  experience_level: string | null;
  tech_stack: string[];
  created_at: string;
}
