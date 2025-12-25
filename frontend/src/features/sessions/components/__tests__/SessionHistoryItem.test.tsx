/**
 * Tests for SessionHistoryItem component.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { SessionHistoryItem } from '../SessionHistoryItem';
import type { Session } from '../../types/session';

const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('SessionHistoryItem', () => {
  const mockSession: Session = {
    id: 'session-123',
    job_posting: {
      id: 'job-456',
      title: 'Senior Backend Engineer',
      company: 'TechCorp',
    },
    status: 'completed',
    current_question_number: 8,
    created_at: '2025-12-20T10:00:00Z',
    updated_at: '2025-12-20T11:30:00Z',
  };

  it('renders job posting title and company', () => {
    renderWithRouter(<SessionHistoryItem session={mockSession} />);

    expect(screen.getByText('Senior Backend Engineer')).toBeInTheDocument();
    expect(screen.getByText('TechCorp')).toBeInTheDocument();
  });

  it('displays completed status badge', () => {
    renderWithRouter(<SessionHistoryItem session={mockSession} />);

    expect(screen.getByText('Completed')).toBeInTheDocument();
  });

  it('formats and displays completion date correctly', () => {
    renderWithRouter(<SessionHistoryItem session={mockSession} />);

    // Check for formatted date (Dec 20, 2025)
    expect(screen.getByText(/Dec 20, 2025/)).toBeInTheDocument();
  });

  it('displays number of questions answered', () => {
    renderWithRouter(<SessionHistoryItem session={mockSession} />);

    expect(screen.getByText(/Questions Answered:/)).toBeInTheDocument();
    expect(screen.getByText(/8/)).toBeInTheDocument();
  });

  it('renders View Details link with correct href', () => {
    renderWithRouter(<SessionHistoryItem session={mockSession} />);

    const link = screen.getByRole('link', { name: /View Details/i });
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute('href', '/sessions/session-123');
  });

  it('applies hover styles to card', () => {
    const { container } = renderWithRouter(
      <SessionHistoryItem session={mockSession} />
    );

    const card = container.querySelector('.hover\\:shadow-md');
    expect(card).toBeInTheDocument();
  });

  it('handles different question counts', () => {
    const sessionWith5Questions = {
      ...mockSession,
      current_question_number: 5,
    };
    const { container } = renderWithRouter(
      <SessionHistoryItem session={sessionWith5Questions} />
    );

    // Check that the question count is displayed correctly
    expect(container.textContent).toContain('Questions Answered: 5');
  });

  it('handles different job postings', () => {
    const differentSession: Session = {
      ...mockSession,
      job_posting: {
        id: 'job-789',
        title: 'Frontend Developer',
        company: 'StartupXYZ',
      },
    };

    renderWithRouter(<SessionHistoryItem session={differentSession} />);

    expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    expect(screen.getByText('StartupXYZ')).toBeInTheDocument();
  });
});
