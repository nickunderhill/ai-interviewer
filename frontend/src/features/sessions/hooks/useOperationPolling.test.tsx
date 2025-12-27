import React from 'react';
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { act, render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useOperationPolling } from './useOperationPolling';
import { fetchOperation } from '../../../services/operationsApi';

vi.mock('../../../services/operationsApi', () => ({
  fetchOperation: vi.fn(),
}));

function Wrapper({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}

function TestComponent({ operationId }: { operationId: string | null }) {
  const {
    operation,
    elapsedSeconds,
    showTimeoutWarning,
    isProcessing,
    isFetching,
  } = useOperationPolling(operationId);

  return (
    <div>
      <div data-testid="status">{operation?.status ?? 'none'}</div>
      <div data-testid="elapsed">{elapsedSeconds}</div>
      <div data-testid="timeout">{showTimeoutWarning ? 'yes' : 'no'}</div>
      <div data-testid="processing">{isProcessing ? 'yes' : 'no'}</div>
      <div data-testid="fetching">{isFetching ? 'yes' : 'no'}</div>
    </div>
  );
}

async function flushMicrotasks() {
  // React Query + React state updates often require a couple of microtask turns.
  await Promise.resolve();
  await vi.advanceTimersByTimeAsync(0);
  await Promise.resolve();
}

describe('useOperationPolling', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('polls while pending/processing and stops when completed', async () => {
    const mockFetch = vi.mocked(fetchOperation);

    mockFetch
      .mockResolvedValueOnce({
        id: 'op-1',
        operation_type: 'question_generation',
        status: 'pending',
        result: null,
        error_message: null,
        created_at: '2025-12-26T00:00:00Z',
        updated_at: '2025-12-26T00:00:00Z',
      })
      .mockResolvedValueOnce({
        id: 'op-1',
        operation_type: 'question_generation',
        status: 'completed',
        result: {},
        error_message: null,
        created_at: '2025-12-26T00:00:00Z',
        updated_at: '2025-12-26T00:00:03Z',
      });

    render(
      <Wrapper>
        <TestComponent operationId="op-1" />
      </Wrapper>
    );

    await act(async () => {
      await flushMicrotasks();
    });

    expect(screen.getByTestId('status')).toHaveTextContent('pending');

    // Next poll at ~2.5s
    await act(async () => {
      await vi.advanceTimersByTimeAsync(2500);
      await flushMicrotasks();
    });

    expect(mockFetch).toHaveBeenCalledTimes(2);
    expect(screen.getByTestId('status')).toHaveTextContent('completed');
    expect(screen.getByTestId('processing')).toHaveTextContent('no');
  });

  it('shows timeout warning after 30 seconds', async () => {
    const mockFetch = vi.mocked(fetchOperation);

    mockFetch.mockResolvedValue({
      id: 'op-1',
      operation_type: 'feedback_analysis',
      status: 'processing',
      result: null,
      error_message: null,
      created_at: '2025-12-26T00:00:00Z',
      updated_at: '2025-12-26T00:00:00Z',
    });

    render(
      <Wrapper>
        <TestComponent operationId="op-1" />
      </Wrapper>
    );

    await act(async () => {
      await flushMicrotasks();
    });

    expect(screen.getByTestId('status')).toHaveTextContent('processing');

    await act(async () => {
      await vi.advanceTimersByTimeAsync(30000);
      await flushMicrotasks();
    });

    expect(screen.getByTestId('timeout')).toHaveTextContent('yes');
    expect(
      Number(screen.getByTestId('elapsed').textContent)
    ).toBeGreaterThanOrEqual(30);
  });
});
