/**
 * Unit tests for AppLayout component with logout functionality
 */
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import AppLayout from '../../../../components/layout/AppLayout';
import { authService } from '../../../../services/authService';

// Mock authService
vi.mock('../../../../services/authService', () => ({
  authService: {
    logout: vi.fn(),
    isAuthenticated: vi.fn(() => true),
  },
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  };
});

describe('AppLayout', () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

  const renderComponent = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AppLayout />
        </BrowserRouter>
      </QueryClientProvider>
    );
  };

  it('should render header with app title', () => {
    renderComponent();
    expect(screen.getByText('AI Interviewer')).toBeInTheDocument();
  });

  it('should render logout button', () => {
    renderComponent();
    expect(screen.getByText('Logout')).toBeInTheDocument();
  });

  it('should call logout and navigate on logout button click', () => {
    renderComponent();

    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);

    expect(authService.logout).toHaveBeenCalledTimes(1);
    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });
});
