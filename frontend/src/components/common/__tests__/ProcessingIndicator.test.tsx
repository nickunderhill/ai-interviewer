import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { ProcessingIndicator } from '../ProcessingIndicator';

describe('ProcessingIndicator', () => {
  it('renders message and optional subMessage', () => {
    render(
      <ProcessingIndicator
        message="Generating your interview question"
        subMessage="This usually takes 5-10 seconds"
      />
    );

    expect(
      screen.getByText('Generating your interview question')
    ).toBeInTheDocument();
    expect(
      screen.getByText('This usually takes 5-10 seconds')
    ).toBeInTheDocument();
  });

  it('renders elapsed time after 10 seconds', () => {
    render(
      <ProcessingIndicator
        message="Processing"
        elapsedSeconds={11}
        showTimeoutWarning={false}
      />
    );

    expect(screen.getByText('11 seconds')).toBeInTheDocument();
  });

  it('renders timeout warning when enabled', () => {
    render(
      <ProcessingIndicator
        message="Processing"
        elapsedSeconds={40}
        showTimeoutWarning
      />
    );

    expect(
      screen.getByText(/taking longer than expected/i)
    ).toBeInTheDocument();
  });
});
