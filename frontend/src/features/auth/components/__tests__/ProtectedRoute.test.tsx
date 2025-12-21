/**
 * Unit tests for ProtectedRoute component
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ProtectedRoute from '../../../../components/layout/ProtectedRoute';
import { authService } from '../../../../services/authService';

vi.mock('../../../../services/authService', () => ({
  authService: {
    isAuthenticated: vi.fn(),
  },
}));

describe('ProtectedRoute', () => {
  const TestChild = () => <div>Protected Content</div>;

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should render children when authenticated', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(true);

    render(
      <BrowserRouter>
        <ProtectedRoute>
          <TestChild />
        </ProtectedRoute>
      </BrowserRouter>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
  });

  it('should redirect to login when not authenticated', () => {
    vi.mocked(authService.isAuthenticated).mockReturnValue(false);

    const { container } = render(
      <BrowserRouter>
        <ProtectedRoute>
          <TestChild />
        </ProtectedRoute>
      </BrowserRouter>
    );

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
    // Navigate should be called to /login
    expect(container.innerHTML).toBe('');
  });
});
