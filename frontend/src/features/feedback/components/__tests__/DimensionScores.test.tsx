/**
 * Tests for DimensionScores component.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { DimensionScores } from '../DimensionScores';

describe('DimensionScores', () => {
  const defaultProps = {
    overallScore: 75,
    technicalAccuracy: 80,
    communicationClarity: 70,
    problemSolving: 85,
    relevance: 65,
  };

  it('renders the component without crashing', () => {
    render(<DimensionScores {...defaultProps} />);
    expect(screen.getByTestId('dimension-scores')).toBeInTheDocument();
  });

  it('displays the overall score prominently', () => {
    render(<DimensionScores {...defaultProps} />);
    expect(screen.getByTestId('overall-score-value')).toHaveTextContent('75');
  });

  it('displays all four dimension labels', () => {
    render(<DimensionScores {...defaultProps} />);
    expect(screen.getByText('Technical Accuracy')).toBeInTheDocument();
    expect(screen.getByText('Communication Clarity')).toBeInTheDocument();
    expect(screen.getByText('Problem Solving')).toBeInTheDocument();
    expect(screen.getByText('Relevance')).toBeInTheDocument();
  });

  it('displays score values for each dimension', () => {
    render(<DimensionScores {...defaultProps} />);
    expect(screen.getByTestId('score-technical-accuracy')).toHaveTextContent(
      '80/100'
    );
    expect(screen.getByTestId('score-communication-clarity')).toHaveTextContent(
      '70/100'
    );
    expect(screen.getByTestId('score-problem-solving')).toHaveTextContent(
      '85/100'
    );
    expect(screen.getByTestId('score-relevance')).toHaveTextContent('65/100');
  });

  describe('Color coding', () => {
    it('applies red color for scores below 60', () => {
      render(
        <DimensionScores
          {...defaultProps}
          overallScore={45}
          technicalAccuracy={50}
        />
      );
      const overallScore = screen.getByTestId('overall-score-value');
      expect(overallScore).toHaveClass('text-red-600');
    });

    it('applies yellow color for scores between 60 and 79', () => {
      render(<DimensionScores {...defaultProps} overallScore={70} />);
      const overallScore = screen.getByTestId('overall-score-value');
      expect(overallScore).toHaveClass('text-yellow-600');
    });

    it('applies green color for scores 80 and above', () => {
      render(<DimensionScores {...defaultProps} overallScore={85} />);
      const overallScore = screen.getByTestId('overall-score-value');
      expect(overallScore).toHaveClass('text-green-600');
    });

    it('applies correct color to progress bars', () => {
      const { container } = render(
        <DimensionScores
          {...defaultProps}
          technicalAccuracy={50} // red
          communicationClarity={70} // yellow
          problemSolving={85} // green
        />
      );

      // Progress bars have colored div inside
      const progressBars = container.querySelectorAll(
        '[role="progressbar"] > div'
      );
      expect(progressBars[0]).toHaveClass('bg-red-500'); // Technical Accuracy: 50
      expect(progressBars[1]).toHaveClass('bg-yellow-500'); // Communication: 70
      expect(progressBars[2]).toHaveClass('bg-green-500'); // Problem Solving: 85
    });
  });

  describe('Accessibility', () => {
    it('includes proper aria-labels for overall score', () => {
      render(<DimensionScores {...defaultProps} overallScore={75} />);
      const overallScore = screen.getByTestId('overall-score-value');
      expect(overallScore).toHaveAttribute(
        'aria-label',
        'Overall score: 75 out of 100'
      );
    });

    it('includes proper aria-labels for dimension scores', () => {
      render(<DimensionScores {...defaultProps} technicalAccuracy={80} />);
      const techScore = screen.getByTestId('score-technical-accuracy');
      expect(techScore).toHaveAttribute(
        'aria-label',
        'Technical Accuracy: 80 out of 100'
      );
    });

    it('includes role="progressbar" with proper aria attributes', () => {
      render(<DimensionScores {...defaultProps} technicalAccuracy={80} />);
      const progressBars = screen.getAllByRole('progressbar');
      expect(progressBars[0]).toHaveAttribute('aria-valuenow', '80');
      expect(progressBars[0]).toHaveAttribute('aria-valuemin', '0');
      expect(progressBars[0]).toHaveAttribute('aria-valuemax', '100');
    });
  });

  describe('Edge cases', () => {
    it('handles score of 0', () => {
      render(<DimensionScores {...defaultProps} technicalAccuracy={0} />);
      expect(screen.getByTestId('score-technical-accuracy')).toHaveTextContent(
        '0/100'
      );
    });

    it('handles score of 100', () => {
      render(<DimensionScores {...defaultProps} problemSolving={100} />);
      expect(screen.getByTestId('score-problem-solving')).toHaveTextContent(
        '100/100'
      );
    });

    it('handles boundary score of 60 (yellow)', () => {
      render(<DimensionScores {...defaultProps} overallScore={60} />);
      const overallScore = screen.getByTestId('overall-score-value');
      expect(overallScore).toHaveClass('text-yellow-600');
    });

    it('handles boundary score of 80 (green)', () => {
      render(<DimensionScores {...defaultProps} overallScore={80} />);
      const overallScore = screen.getByTestId('overall-score-value');
      expect(overallScore).toHaveClass('text-green-600');
    });
  });
});
