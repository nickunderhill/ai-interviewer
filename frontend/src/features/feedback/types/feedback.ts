/**
 * Type definitions for AI-generated interview feedback.
 */

/**
 * Complete feedback data returned from the backend API.
 */
export interface InterviewFeedback {
  id: string;
  session_id: string;

  // Dimension scores (0-100)
  technical_accuracy_score: number;
  communication_clarity_score: number;
  problem_solving_score: number;
  relevance_score: number;
  overall_score: number;

  // Detailed feedback text for each dimension
  technical_feedback: string;
  communication_feedback: string;
  problem_solving_feedback: string;
  relevance_feedback: string;
  overall_comments: string | null;

  // Structured recommendations
  knowledge_gaps: string[];
  learning_recommendations: string[];

  // Metadata
  created_at: string;
  updated_at: string;
}

/**
 * Props for the DimensionScores component.
 */
export interface DimensionScoresProps {
  overallScore: number;
  technicalAccuracy: number;
  communicationClarity: number;
  problemSolving: number;
  relevance: number;
}

/**
 * Props for the KnowledgeGaps component.
 */
export interface KnowledgeGapsProps {
  knowledgeGaps: string[];
}

/**
 * Props for the LearningRecommendations component.
 */
export interface LearningRecommendationsProps {
  learningRecommendations: string[];
}
