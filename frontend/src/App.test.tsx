import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from './App';

describe('App Component', () => {
  it('renders without crashing', () => {
    render(<App />);
    expect(screen.getByText(/Vite \+ React/i)).toBeInTheDocument();
  });

  it('displays the counter button', () => {
    render(<App />);
    const button = screen.getByRole('button', { name: /count is 0/i });
    expect(button).toBeInTheDocument();
  });

  it('renders Vite logo', () => {
    render(<App />);
    const viteLogo = screen.getByAltText(/Vite logo/i);
    expect(viteLogo).toBeInTheDocument();
  });

  it('renders React logo', () => {
    render(<App />);
    const reactLogo = screen.getByAltText(/React logo/i);
    expect(reactLogo).toBeInTheDocument();
  });
});
