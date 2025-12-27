import React from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import { AnswerForm } from '../AnswerForm';
import { submitAnswer } from '../../api/sessionApi';
import { generateFeedback } from '../../../../services/sessionAiApi';
import { fetchOperation } from '../../../../services/operationsApi';

vi.mock('../../api/sessionApi', () => ({
  submitAnswer: vi.fn(),
}));

vi.mock('../../../../services/sessionAiApi', () => ({
  generateFeedback: vi.fn(),
}));

vi.mock('../../../../services/operationsApi', () => ({
  fetchOperation: vi.fn(),
}));

function renderWithClient(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
  );
}

describe('AnswerForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('submits answer and shows feedback analysis status', async () => {
    vi.mocked(submitAnswer).mockResolvedValue({
      id: 'msg-1',
      message_type: 'answer',
      content: 'My answer',
      question_type: null,
      created_at: '2025-12-27T00:00:00Z',
    });

    vi.mocked(generateFeedback).mockResolvedValue({
      id: 'op-feedback-1',
      operation_type: 'feedback_analysis',
      status: 'pending',
      result: null,
      error_message: null,
      created_at: '2025-12-27T00:00:00Z',
      updated_at: '2025-12-27T00:00:00Z',
    });

    vi.mocked(fetchOperation).mockResolvedValue({
      id: 'op-feedback-1',
      operation_type: 'feedback_analysis',
      status: 'pending',
      result: null,
      error_message: null,
      created_at: '2025-12-27T00:00:00Z',
      updated_at: '2025-12-27T00:00:00Z',
    });

    const user = userEvent.setup();

    renderWithClient(<AnswerForm sessionId="session-1" />);

    await user.type(screen.getByLabelText(/your answer/i), 'My answer');
    await user.click(screen.getByRole('button', { name: /submit answer/i }));

    await waitFor(() => {
      expect(submitAnswer).toHaveBeenCalledWith('session-1', 'My answer');
      expect(generateFeedback).toHaveBeenCalledWith('session-1');
    });

    expect(screen.getByText(/analyzing feedback/i)).toBeInTheDocument();
  });
});
