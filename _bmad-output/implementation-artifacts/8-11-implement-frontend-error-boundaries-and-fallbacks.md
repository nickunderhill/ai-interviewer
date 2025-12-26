# Story 8.11: Implement Frontend Error Boundaries and Fallbacks

Status: ready-for-dev

## Story

As a developer, I want to implement error boundaries in React, so that UI errors
don't crash the entire application.

## Acceptance Criteria

1. **Given** the React frontend is implemented **When** a component throws an
   error **Then** an error boundary catches it and displays a fallback UI
   **And** the error is logged to the console (and optionally to a logging
   service) **And** the user sees a friendly error message with a "Reload" or
   "Go Home" button **And** other parts of the application continue to function
   **And** critical errors (auth failures, API unavailability) show specific
   messages **And** the app never displays a blank screen or crashes completely
   (NFR21) ✅

## Tasks / Subtasks

- [ ] Task 1: Add a global Error Boundary component (AC: #1)

  - [ ] Implement `ErrorBoundary` as a class component (required by React)
  - [ ] Capture error + component stack via `componentDidCatch`
  - [ ] Provide fallback UI with Reload + Go Home actions
  - [ ] Ensure fallback UI is accessible (role=alert)

- [ ] Task 2: Add route-level boundary integration (AC: #1)

  - [ ] Wrap app router root in ErrorBoundary
  - [ ] Optionally wrap high-risk routes (session detail, analytics) in nested
        boundaries

- [ ] Task 3: Distinguish error types for better messaging (AC: #1)

  - [ ] Provide friendly default message
  - [ ] Detect common errors (chunk load failure, auth 401 redirect loop)
  - [ ] Show specific recovery suggestions

- [ ] Task 4: Ensure logging does not leak sensitive data (AC: #1)

  - [ ] Log to console with structured fields
  - [ ] Never log tokens, API keys, or user PII
  - [ ] (Optional) add hook to forward to backend logging endpoint later

- [ ] Task 5: Add tests (AC: #1)
  - [ ] Verify boundary catches thrown errors
  - [ ] Verify fallback renders and buttons work

## Dev Notes

### Critical Architecture Requirements

**Frontend:**

- React 18+ with TypeScript
- Functional components everywhere except ErrorBoundary (React requires class
  for boundaries)
- Tailwind CSS v3+ styling
- React Router v6 integration

### File Structure

```
frontend/src/
├── components/
│   └── common/
│       └── ErrorBoundary.tsx
├── components/
│   └── layout/
│       └── AppShell.tsx        # If exists, boundary can wrap shell
└── main.tsx / App.tsx          # Wrap router root
```

### Implementation Details

**Error Boundary:**

```tsx
// frontend/src/components/common/ErrorBoundary.tsx
import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';

type ErrorBoundaryProps = {
  children: ReactNode;
};

type ErrorBoundaryState = {
  hasError: boolean;
  error?: Error;
};

export class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Keep logging minimal and non-sensitive
    // eslint-disable-next-line no-console
    console.error('UI error caught by ErrorBoundary', {
      name: error.name,
      message: error.message,
      stack: errorInfo.componentStack,
    });
  }

  private handleReload = () => {
    window.location.reload();
  };

  render() {
    if (!this.state.hasError) return this.props.children;

    return (
      <div className="max-w-2xl mx-auto p-6">
        <div className="border rounded-lg p-6 bg-white">
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            Something went wrong
          </h1>
          <p className="text-sm text-gray-700 mb-6" role="alert">
            The page encountered an unexpected error. You can try reloading or
            return to the dashboard.
          </p>
          <div className="flex gap-3">
            <button
              type="button"
              onClick={this.handleReload}
              className="px-4 py-2 border rounded-md text-sm font-medium"
            >
              Reload
            </button>
            <Link
              to="/"
              className="px-4 py-2 border rounded-md text-sm font-medium"
            >
              Go Home
            </Link>
          </div>
        </div>
      </div>
    );
  }
}
```

**Integration (example):**

```tsx
// frontend/src/main.tsx (or App.tsx)
import { ErrorBoundary } from '@/components/common/ErrorBoundary';

root.render(
  <ErrorBoundary>
    <App />
  </ErrorBoundary>
);
```

### Testing Requirements

- Create
  [frontend/src/components/common/ErrorBoundary.test.tsx](frontend/src/components/common/ErrorBoundary.test.tsx)
  using Vitest + RTL
- Test that a child component throwing renders fallback
- Test that Reload button is present

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.11]
- [Source: _bmad-output/project-context.md#Frontend-Patterns]
- NFR21 (Frontend error resilience)

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Adds global ErrorBoundary with safe fallback UI
- Provides route integration pattern and tests
