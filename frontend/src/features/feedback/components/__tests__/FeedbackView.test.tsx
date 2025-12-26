import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import FeedbackView from '../FeedbackView';
import { fetchFeedback } from '../../api/feedbackApi';
import { generateFeedback } from '../../../../services/sessionAiApi';
import { fetchOperation } from '../../../../services/operationsApi';

// Mock router params
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: 'session-123' }),
    Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
      <a href={to}>{children}</a>
    ),
  };
});

// Mock APIs (to be implemented)
vi.mock('../../api/feedbackApi', () => ({
  fetchFeedback: vi.fn(),
}));

vi.mock('../../../../services/sessionAiApi', () => ({
  generateFeedback: vi.fn(),
}));

vi.mock('../../../../services/operationsApi', () => ({
  fetchOperation: vi.fn(),
}));

const renderWithProviders = (component: React.ReactElement) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        {component}
      </QueryClientProvider>
    </BrowserRouter>
  );
};

describe('FeedbackView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows operation error message when feedback generation fails', async () => {
    vi.mocked(fetchFeedback).mockRejectedValue({
      response: {
        status: 404,
        data: {
          detail: { code: 'FEEDBACK_NOT_FOUND', message: 'Not generated yet' },
        },
      },
    });

    vi.mocked(generateFeedback).mockResolvedValue({
      id: 'op-1',
      operation_type: 'feedback_analysis',
      status: 'pending',
      result: null,
      error_message: null,
      created_at: '2025-12-20T10:30:00Z',
      updated_at: '2025-12-20T10:30:00Z',
    });

    vi.mocked(fetchOperation).mockResolvedValue({
      id: 'op-1',
      operation_type: 'feedback_analysis',
      status: 'failed',
      result: null,
      error_message:
        'Unable to generate feedback.\n\nWhat to do: Try again in a few minutes.',
      created_at: '2025-12-20T10:30:00Z',
      updated_at: '2025-12-20T10:31:00Z',
    });

    const user = userEvent.setup();
    renderWithProviders(<FeedbackView />);

    const generateButton = await screen.findByRole('button', {
      name: /generate feedback/i,
    });
    await user.click(generateButton);

    await waitFor(() => {
      expect(
        screen.getByText(/unable to generate feedback/i)
      ).toBeInTheDocument();
      expect(screen.getByText(/what to do:/i)).toBeInTheDocument();
    });
  });

  it('allows retry when generation fails', async () => {
    vi.mocked(fetchFeedback).mockRejectedValue({
      response: {
        status: 404,
        data: {
          detail: { code: 'FEEDBACK_NOT_FOUND', message: 'Not generated yet' },
        },
      },
    });

    vi.mocked(generateFeedback)
      .mockResolvedValueOnce({
        id: 'op-1',
        operation_type: 'feedback_analysis',
        status: 'pending',
        result: null,
        error_message: null,
        created_at: '2025-12-20T10:30:00Z',
        updated_at: '2025-12-20T10:30:00Z',
      })
      .mockResolvedValueOnce({
        id: 'op-2',
        operation_type: 'feedback_analysis',
        status: 'pending',
        result: null,
        error_message: null,
        created_at: '2025-12-20T10:35:00Z',
        updated_at: '2025-12-20T10:35:00Z',
      });

    vi.mocked(fetchOperation).mockResolvedValue({
      id: 'op-1',
      operation_type: 'feedback_analysis',
      status: 'failed',
      result: null,
      error_message:
        'Unable to generate feedback.\n\nWhat to do: Try again in a few minutes.',
      created_at: '2025-12-20T10:30:00Z',
      updated_at: '2025-12-20T10:31:00Z',
    });

    const user = userEvent.setup();
    renderWithProviders(<FeedbackView />);

    const generateButton = await screen.findByRole('button', {
      name: /generate feedback/i,
    });
    await user.click(generateButton);

    const retryButton = await screen.findByRole('button', { name: /retry/i });
    await user.click(retryButton);

    await waitFor(() => {
      expect(generateFeedback).toHaveBeenCalledTimes(2);
    });
  });
});
