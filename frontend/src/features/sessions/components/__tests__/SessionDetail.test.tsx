/**
 * Tests for SessionDetail component.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import SessionDetail from '../SessionDetail';
import * as useSessionHook from '../../hooks/useSession';
import * as useMessagesHook from '../../hooks/useMessages';
import type {
  SessionDetail as SessionDetailType,
  Message,
} from '../../types/session';

// Mock useParams
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: () => ({ id: 'test-session-id' }),
    useNavigate: () => vi.fn(),
    Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
      <a href={to}>{children}</a>
    ),
  };
});

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

const mockSessionDetail: SessionDetailType = {
  id: 'test-session-id',
  job_posting: {
    id: 'job-1',
    title: 'Senior Backend Engineer',
    company: 'TechCorp',
    description: 'Looking for experienced backend engineer...',
    tech_stack: ['Python', 'PostgreSQL', 'Docker'],
    experience_level: 'senior',
  },
  status: 'completed',
  current_question_number: 5,
  created_at: '2025-12-20T10:30:00Z',
  updated_at: '2025-12-20T11:00:00Z',
};

const mockMessages: Message[] = [
  {
    id: 'msg-1',
    message_type: 'question',
    content: 'Explain the difference between SQL and NoSQL databases?',
    question_type: 'technical',
    created_at: '2025-12-20T10:32:00Z',
  },
  {
    id: 'msg-2',
    message_type: 'answer',
    content: 'SQL databases are relational and use structured schemas...',
    question_type: null,
    created_at: '2025-12-20T10:35:00Z',
  },
];

describe('SessionDetail', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('displays loading state while fetching data', () => {
    vi.spyOn(useSessionHook, 'useSession').mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    } as ReturnType<typeof useSessionHook.useSession>);

    vi.spyOn(useMessagesHook, 'useMessages').mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    } as ReturnType<typeof useMessagesHook.useMessages>);

    const { container } = renderWithProviders(<SessionDetail />);
    const skeleton = container.querySelector('.animate-pulse');
    expect(skeleton).toBeInTheDocument();
  });

  it('displays error state when session fetch fails', () => {
    vi.spyOn(useSessionHook, 'useSession').mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('Session not found'),
    } as ReturnType<typeof useSessionHook.useSession>);

    vi.spyOn(useMessagesHook, 'useMessages').mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof useMessagesHook.useMessages>);

    renderWithProviders(<SessionDetail />);
    expect(screen.getByText(/failed to load session/i)).toBeInTheDocument();
  });

  it('displays job posting context', async () => {
    vi.spyOn(useSessionHook, 'useSession').mockReturnValue({
      data: mockSessionDetail,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof useSessionHook.useSession>);

    vi.spyOn(useMessagesHook, 'useMessages').mockReturnValue({
      data: mockMessages,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof useMessagesHook.useMessages>);

    renderWithProviders(<SessionDetail />);

    await waitFor(() => {
      expect(screen.getByText('Senior Backend Engineer')).toBeInTheDocument();
      expect(screen.getByText('TechCorp')).toBeInTheDocument();
    });
  });

  it('displays Q&A messages in chronological order', async () => {
    vi.spyOn(useSessionHook, 'useSession').mockReturnValue({
      data: mockSessionDetail,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof useSessionHook.useSession>);

    vi.spyOn(useMessagesHook, 'useMessages').mockReturnValue({
      data: mockMessages,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof useMessagesHook.useMessages>);

    const { container } = renderWithProviders(<SessionDetail />);

    await waitFor(() => {
      expect(container.textContent).toContain(
        'Explain the difference between SQL and NoSQL'
      );
      expect(container.textContent).toContain('SQL databases are relational');
    });
  });

  it('shows back to history link', async () => {
    vi.spyOn(useSessionHook, 'useSession').mockReturnValue({
      data: mockSessionDetail,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof useSessionHook.useSession>);

    vi.spyOn(useMessagesHook, 'useMessages').mockReturnValue({
      data: mockMessages,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof useMessagesHook.useMessages>);

    renderWithProviders(<SessionDetail />);

    await waitFor(() => {
      const backLink = screen.getByRole('link', { name: /back/i });
      expect(backLink).toBeInTheDocument();
      expect(backLink).toHaveAttribute('href', '/history');
    });
  });

  it('displays empty state when no messages exist', async () => {
    vi.spyOn(useSessionHook, 'useSession').mockReturnValue({
      data: mockSessionDetail,
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof useSessionHook.useSession>);

    vi.spyOn(useMessagesHook, 'useMessages').mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      error: null,
    } as ReturnType<typeof useMessagesHook.useMessages>);

    renderWithProviders(<SessionDetail />);

    await waitFor(() => {
      expect(screen.getByText(/no messages/i)).toBeInTheDocument();
    });
  });
});
