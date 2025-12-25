/**
 * Tests for SessionHistory component.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { SessionHistory } from '../SessionHistory';
import * as useSessions from '../../hooks/useSessions';
import type { Session } from '../../types/session';

// Mock the useSessions hook
vi.mock('../../hooks/useSessions');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{component}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('SessionHistory', () => {
  const mockSessions: Session[] = [
    {
      id: '1',
      job_posting: {
        id: 'job1',
        title: 'Senior Backend Engineer',
        company: 'TechCorp',
      },
      status: 'completed',
      current_question_number: 8,
      created_at: '2025-12-20T10:00:00Z',
      updated_at: '2025-12-20T11:00:00Z',
    },
    {
      id: '2',
      job_posting: {
        id: 'job2',
        title: 'Frontend Developer',
        company: 'StartupXYZ',
      },
      status: 'completed',
      current_question_number: 5,
      created_at: '2025-12-19T10:00:00Z',
      updated_at: '2025-12-19T11:00:00Z',
    },
  ];

  it('displays loading spinner while fetching sessions', () => {
    vi.spyOn(useSessions, 'useSessions').mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    } as any);

    const { container } = renderWithProviders(<SessionHistory />);
    // Check for skeleton loading state (animate-pulse instead of animate-spin)
    const skeleton = container.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('displays error message when fetch fails', () => {
    const errorMessage = 'Failed to fetch sessions';
    vi.spyOn(useSessions, 'useSessions').mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error(errorMessage),
    } as any);

    renderWithProviders(<SessionHistory />);
    expect(screen.getByText('Error loading sessions')).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('displays empty state when no sessions exist', () => {
    vi.spyOn(useSessions, 'useSessions').mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderWithProviders(<SessionHistory />);
    expect(screen.getByText('No completed interviews yet')).toBeInTheDocument();
    expect(
      screen.getByText(/Start your first mock interview/i)
    ).toBeInTheDocument();
  });

  it('displays list of completed sessions', () => {
    vi.spyOn(useSessions, 'useSessions').mockReturnValue({
      data: mockSessions,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderWithProviders(<SessionHistory />);

    expect(screen.getByText('Session History')).toBeInTheDocument();
    expect(screen.getByText('Senior Backend Engineer')).toBeInTheDocument();
    expect(screen.getByText('TechCorp')).toBeInTheDocument();
    expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    expect(screen.getByText('StartupXYZ')).toBeInTheDocument();
  });

  it('displays question count for each session', () => {
    vi.spyOn(useSessions, 'useSessions').mockReturnValue({
      data: mockSessions,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    const { container } = renderWithProviders(<SessionHistory />);

    // Check that the specific counts appear in the document
    expect(container.textContent).toContain('Questions Answered: 8');
    expect(container.textContent).toContain('Questions Answered: 5');
  });

  it('displays view details links for each session', () => {
    vi.spyOn(useSessions, 'useSessions').mockReturnValue({
      data: mockSessions,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    renderWithProviders(<SessionHistory />);

    const viewDetailsLinks = screen.getAllByText('View Details');
    expect(viewDetailsLinks).toHaveLength(2);
  });
});
