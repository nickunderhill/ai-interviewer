import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { StatusBadge } from '../StatusBadge';

describe('StatusBadge', () => {
  it('renders label and status text', () => {
    render(<StatusBadge status="processing" />);

    expect(screen.getByRole('status')).toHaveTextContent('Processing...');
    expect(screen.getByLabelText('Status: Processing...')).toBeInTheDocument();
  });
});
