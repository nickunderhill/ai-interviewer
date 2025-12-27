import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ErrorBoundary } from '../ErrorBoundary';

// Test component that throws an error
const ThrowError = ({ error }: { error?: Error }) => {
  if (error) {
    throw error;
  }
  throw new Error('Test error');
};

// Wrapper with Router for Link component
const renderWithRouter = (ui: React.ReactElement) => {
  return render(<BrowserRouter>{ui}</BrowserRouter>);
};

describe('ErrorBoundary', () => {
  // Suppress console.error in tests
  beforeEach(() => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  it('renders children when there is no error', () => {
    renderWithRouter(
      <ErrorBoundary>
        <div>Test Content</div>
      </ErrorBoundary>
    );

    expect(screen.getByText('Test Content')).toBeInTheDocument();
  });

  it('catches errors and displays fallback UI', () => {
    renderWithRouter(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('displays reload button', () => {
    renderWithRouter(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    const reloadButton = screen.getByRole('button', { name: /reload page/i });
    expect(reloadButton).toBeInTheDocument();
  });

  it('displays go home link', () => {
    renderWithRouter(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    const homeLink = screen.getByRole('link', { name: /go to dashboard/i });
    expect(homeLink).toBeInTheDocument();
    expect(homeLink).toHaveAttribute('href', '/');
  });

  it('reloads page when reload button is clicked', () => {
    const reloadSpy = vi.fn();
    Object.defineProperty(window, 'location', {
      value: { reload: reloadSpy },
      writable: true,
    });

    renderWithRouter(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    const reloadButton = screen.getByRole('button', { name: /reload page/i });
    reloadButton.click();

    expect(reloadSpy).toHaveBeenCalledTimes(1);
  });

  it('logs error to console', () => {
    const consoleErrorSpy = vi.spyOn(console, 'error');

    renderWithRouter(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    expect(consoleErrorSpy).toHaveBeenCalledWith(
      'UI error caught by ErrorBoundary',
      expect.objectContaining({
        name: 'Error',
        message: 'Test error',
        errorType: 'unknown',
      })
    );
  });

  it('detects chunk load errors', () => {
    const chunkError = new Error('Loading chunk 5 failed');

    renderWithRouter(
      <ErrorBoundary>
        <ThrowError error={chunkError} />
      </ErrorBoundary>
    );

    expect(
      screen.getByText(/new version of the application may be available/i)
    ).toBeInTheDocument();
  });

  it('detects auth errors', () => {
    const authError = new Error('401 Unauthorized');

    renderWithRouter(
      <ErrorBoundary>
        <ThrowError error={authError} />
      </ErrorBoundary>
    );

    expect(screen.getByText(/session may have expired/i)).toBeInTheDocument();
  });

  it('detects network errors', () => {
    const networkError = new Error('Network error occurred');

    renderWithRouter(
      <ErrorBoundary>
        <ThrowError error={networkError} />
      </ErrorBoundary>
    );

    expect(
      screen.getByText(/please check your connection and try again/i)
    ).toBeInTheDocument();
  });

  it('displays generic message for unknown errors', () => {
    const unknownError = new Error('Something unexpected happened');

    renderWithRouter(
      <ErrorBoundary>
        <ThrowError error={unknownError} />
      </ErrorBoundary>
    );

    expect(
      screen.getByText(/encountered an unexpected error/i)
    ).toBeInTheDocument();
  });

  it('has accessible error alert', () => {
    renderWithRouter(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    const alert = screen.getByRole('alert');
    expect(alert).toHaveAttribute('aria-live', 'assertive');
  });

  it('displays error icon', () => {
    renderWithRouter(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    );

    // Check for SVG icon presence
    const icon = screen.getByRole('alert').closest('div')?.querySelector('svg');
    expect(icon).toBeInTheDocument();
  });
});
