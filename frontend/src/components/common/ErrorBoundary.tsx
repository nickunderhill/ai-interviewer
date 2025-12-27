import React, { Component, type ReactNode } from 'react';
import { Link } from 'react-router-dom';

type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  hasError: boolean;
  error?: Error;
  errorType?: 'chunk-load' | 'auth' | 'network' | 'unknown';
};

/**
 * Error Boundary component to catch React errors and display fallback UI.
 * Prevents the entire application from crashing due to component errors.
 *
 * @see Story 8-11: Implement Frontend Error Boundaries and Fallbacks
 */
export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Detect error type for better messaging
    const errorType = ErrorBoundary.detectErrorType(error);

    return { hasError: true, error, errorType };
  }

  /**
   * Detect common error types to provide specific recovery suggestions.
   */
  private static detectErrorType(
    error: Error
  ): ErrorBoundaryState['errorType'] {
    const message = error.message.toLowerCase();

    // Chunk load failures (lazy-loaded components)
    if (
      message.includes('loading chunk') ||
      message.includes('failed to fetch')
    ) {
      return 'chunk-load';
    }

    // Auth/authorization errors
    if (message.includes('401') || message.includes('unauthorized')) {
      return 'auth';
    }

    // Network errors
    if (message.includes('network') || message.includes('failed to fetch')) {
      return 'network';
    }

    return 'unknown';
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Log to console with structured fields (no sensitive data)
    console.error('UI error caught by ErrorBoundary', {
      name: error.name,
      message: error.message,
      errorType: this.state.errorType,
      componentStack: errorInfo.componentStack?.slice(0, 500), // Truncate for safety
      timestamp: new Date().toISOString(),
    });

    // TODO: In production, could send to logging service
    // sendToLoggingService({ error, errorInfo, errorType: this.state.errorType });
  }

  private handleReload = () => {
    window.location.reload();
  };

  private getErrorMessage(): string {
    switch (this.state.errorType) {
      case 'chunk-load':
        return 'A new version of the application may be available. Please reload the page to get the latest version.';
      case 'auth':
        return 'Your session may have expired. Please reload the page to sign in again.';
      case 'network':
        return 'A network error occurred. Please check your connection and try again.';
      default:
        return 'The page encountered an unexpected error. You can try reloading or return to the dashboard.';
    }
  }

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
        <div className="max-w-2xl w-full">
          <div className="border rounded-lg p-8 bg-white shadow-sm">
            {/* Error Icon */}
            <div className="flex items-center justify-center w-12 h-12 mx-auto mb-4 rounded-full bg-red-100">
              <svg
                className="w-6 h-6 text-red-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>

            {/* Error Title */}
            <h1 className="text-2xl font-semibold text-gray-900 text-center mb-2">
              Something went wrong
            </h1>

            {/* Error Message */}
            <p
              className="text-sm text-gray-600 text-center mb-6"
              role="alert"
              aria-live="assertive"
            >
              {this.getErrorMessage()}
            </p>

            {/* Show error details in development */}
            {import.meta.env.DEV && this.state.error && (
              <details className="mb-6 p-4 bg-gray-50 rounded border border-gray-200">
                <summary className="text-sm font-medium text-gray-700 cursor-pointer">
                  Technical Details (Development Only)
                </summary>
                <pre className="mt-2 text-xs text-gray-600 overflow-auto">
                  {this.state.error.message}
                  {'\n\n'}
                  {this.state.error.stack}
                </pre>
              </details>
            )}

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                type="button"
                onClick={this.handleReload}
                className="px-6 py-2.5 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors"
              >
                Reload Page
              </button>
              <Link
                to="/"
                className="px-6 py-2.5 bg-white border border-gray-300 text-gray-700 rounded-md text-sm font-medium hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors text-center"
              >
                Go to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }
}
