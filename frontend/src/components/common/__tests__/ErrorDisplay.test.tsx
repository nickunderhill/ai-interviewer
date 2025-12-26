import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { ErrorDisplay } from '../ErrorDisplay';

describe('ErrorDisplay', () => {
  it('renders main message and actionable next step', () => {
    render(
      <ErrorDisplay message="Unable to generate question.\n\nWhat to do: Try again." />
    );

    expect(
      screen.getByText(/unable to generate question/i)
    ).toBeInTheDocument();
    expect(screen.getByText('What to do:')).toBeInTheDocument();
    expect(screen.getByText('Try again.')).toBeInTheDocument();
  });

  it('renders a retry button and calls onRetry', async () => {
    const user = userEvent.setup();
    const onRetry = vi.fn();

    render(<ErrorDisplay message="Failed." onRetry={onRetry} />);

    await user.click(screen.getByRole('button', { name: 'Retry' }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('applies warning styles when severity is warning', () => {
    const { container } = render(
      <ErrorDisplay message="Warning." severity="warning" />
    );

    expect(container.firstChild).toHaveClass('bg-orange-50');
  });
});
