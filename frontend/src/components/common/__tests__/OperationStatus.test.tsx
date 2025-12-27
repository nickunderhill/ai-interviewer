import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { OperationStatus } from '../OperationStatus';

describe('OperationStatus', () => {
  it('shows question generation pending status text', () => {
    render(
      <OperationStatus
        status="pending"
        operationType="question_generation"
        elapsedSeconds={0}
        showTimeoutWarning={false}
      />
    );

    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('Generating question...')).toBeInTheDocument();
  });

  it('shows question generation completed status text', () => {
    render(
      <OperationStatus
        status="completed"
        operationType="question_generation"
        elapsedSeconds={0}
        showTimeoutWarning={false}
      />
    );

    expect(screen.getByText('Question ready!')).toBeInTheDocument();
  });

  it('shows timeout warning text when enabled', () => {
    render(
      <OperationStatus
        status="processing"
        operationType="feedback_analysis"
        elapsedSeconds={31}
        showTimeoutWarning
      />
    );

    expect(
      screen.getByText(/taking longer than expected/i)
    ).toBeInTheDocument();
  });
});
