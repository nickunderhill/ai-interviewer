import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Mock translations for tests
const translations: Record<string, string> = {
  'sessions.historyItem.questionsAnswered': 'Questions Answered:',
  'sessions.historyItem.completedLabel': 'Completed:',
  'sessions.historyItem.viewDetails': 'View Details',
  'sessions.historyItem.remove': 'Remove',
  'sessions.historyItem.removeError': 'Failed to delete session',
  'sessions.status.completed': 'Completed',
  'sessions.status.active': 'Active',
  'sessions.status.paused': 'Paused',
  'sessions.detail.originalAttempt': 'Original Attempt',
  'sessions.retakeButton.retake': 'Retake',
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
