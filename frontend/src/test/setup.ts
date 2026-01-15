import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock translations for tests - comprehensive list
const translations: Record<string, string> = {
  // Sessions
  'sessions.historyItem.questionsAnswered': 'Questions Answered:',
  'sessions.historyItem.completedLabel': 'Completed:',
  'sessions.historyItem.viewDetails': 'View Details',
  'sessions.historyItem.remove': 'Remove',
  'sessions.historyItem.removeError': 'Failed to delete session',
  'sessions.status.completed': 'Completed',
  'sessions.status.active': 'Active',
  'sessions.status.paused': 'Paused',
  'sessions.history.title': 'Session History',
  'sessions.history.error': 'Error loading sessions',
  'sessions.history.filterByDate': 'Filter by Date',
  'sessions.history.last7Days': 'Last 7 days',
  'sessions.history.last30Days': 'Last 30 days',
  'sessions.history.last3Months': 'Last 3 months',
  'sessions.history.from': 'From',
  'sessions.history.to': 'To',
  'sessions.emptyState.title': 'No completed interviews yet',
  'sessions.emptyState.message':
    'Start your first mock interview to see your progress and feedback here.',
  'sessions.emptyState.buttonText': 'Start Interview',
  'sessions.detail.originalAttempt': 'Original Attempt',
  'sessions.detail.error': 'Failed to load session',
  'sessions.detail.noMessagesYet': 'No messages yet',
  'sessions.detail.generateNextQuestion': 'Generate Next Question',
  'sessions.detail.completeSession': 'Complete Session',
  'sessions.detail.jobDescription': 'Job Description',
  'sessions.detail.techStack': 'Tech Stack',
  'sessions.detail.interviewQA': 'Interview Q&A',
  'sessions.detail.viewAllAttempts': 'View All Attempts',
  'sessions.detail.show': 'Show',
  'sessions.retakeButton.retake': 'Retake',
  'sessions.questionType.technical': 'Technical',
  'sessions.questionType.behavioral': 'Behavioral',
  'sessions.questionType.situational': 'Situational',
  'sessions.answer.label': 'Your Answer',
  'sessions.answer.placeholder': 'Type your answer here...',
  'sessions.answer.submit': 'Submit Answer',
  'sessions.feedbackLink.generate': 'Generate AI Feedback',
  'sessions.feedbackLink.generateDescription':
    'Feedback has not been generated for this session yet.',
  'sessions.feedbackLink.generateButton': 'Generate Feedback',
  // Feedback
  'feedback.recommendations.title': 'Learning Recommendations',
  'feedback.recommendations.empty':
    'No specific recommendations provided. Keep up the great work!',
  'feedback.knowledgeGaps.title': 'Knowledge Gaps',
  'feedback.knowledgeGaps.empty':
    'No major knowledge gaps identified. Great job!',
  'feedback.backToHistory': 'Back to History',
  'feedback.backToSession': 'Back to Session',
  'feedback.title': 'Interview Feedback',
  'feedback.generating': 'Generating feedback...',
  'feedback.generateButton': 'Generate Feedback',
  'feedback.technicalAccuracy': 'Technical Accuracy',
  'feedback.communicationClarity': 'Communication Clarity',
  'feedback.problemSolving': 'Problem-Solving Approach',
  'feedback.relevance': 'Relevance to Job Requirements',
  'feedback.overallScore': 'Overall Score',
  'feedback.detailedBreakdown': 'Detailed Breakdown',
  'feedback.dimensionScores.technicalAccuracy': 'Technical Accuracy',
  'feedback.dimensionScores.communicationClarity': 'Communication Clarity',
  'feedback.dimensionScores.problemSolving': 'Problem Solving',
  'feedback.dimensionScores.relevance': 'Relevance to Job',
  // Operation status
  'operation.generatingQuestion': 'Generating question...',
  'operation.questionReady': 'Question ready!',
  'operation.generationFailed': 'Generation failed',
  'operation.analyzingFeedback': 'Analyzing feedback...',
  'operation.feedbackReady': 'Feedback ready!',
  'operation.analysisFailed': 'Analysis failed',
  'operation.processing': 'Processing...',
  'operation.completed': 'Completed',
  'operation.failed': 'Failed',
  'operation.queued': 'Queued',
  'operation.pending': 'Pending',
  'operation.seconds': 'seconds',
  'operation.thisUsuallyTakes': 'This usually takes 5-10 seconds',
  'operation.takingLonger': 'Taking longer than expected. Still processing...',
  // Navigation
  'nav.appTitle': 'AI Interviewer',
  'nav.dashboard': 'Dashboard',
  'nav.history': 'History',
  'nav.logout': 'Logout',
  // App
  'app.title': 'AI Interviewer',
};

// Mock react-i18next
vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string) => translations[key] || key,
    i18n: {
      language: 'en',
      changeLanguage: vi.fn(),
    },
  }),
  Trans: ({ children }: { children: React.ReactNode }) => children,
  initReactI18next: {
    type: '3rdParty',
    init: vi.fn(),
  },
}));
