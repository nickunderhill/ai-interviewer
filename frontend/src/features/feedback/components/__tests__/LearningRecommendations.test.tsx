/**
 * Tests for LearningRecommendations component.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { LearningRecommendations } from '../LearningRecommendations';

describe('LearningRecommendations', () => {
  it('renders the component without crashing', () => {
    render(<LearningRecommendations learningRecommendations={[]} />);
    expect(screen.getByTestId('learning-recommendations')).toBeInTheDocument();
  });

  it('displays the heading', () => {
    render(<LearningRecommendations learningRecommendations={[]} />);
    expect(screen.getByText('Learning Recommendations')).toBeInTheDocument();
  });

  describe('Empty state', () => {
    it('shows empty state message when no recommendations provided', () => {
      render(<LearningRecommendations learningRecommendations={[]} />);
      expect(
        screen.getByTestId('learning-recommendations-empty')
      ).toBeInTheDocument();
      expect(
        screen.getByText(
          /No specific recommendations provided. Keep up the great work!/i
        )
      ).toBeInTheDocument();
    });

    it('does not show the list when recommendations are empty', () => {
      render(<LearningRecommendations learningRecommendations={[]} />);
      expect(
        screen.queryByTestId('learning-recommendations-list')
      ).not.toBeInTheDocument();
    });
  });

  describe('With recommendations', () => {
    const sampleRecommendations = [
      'Review data structures and algorithms, focusing on trees and graphs',
      'Practice system design interviews with mock scenarios',
      'Study design patterns and their practical applications',
      'Work on open-source projects to gain real-world experience',
    ];

    it('displays all learning recommendations', () => {
      render(
        <LearningRecommendations
          learningRecommendations={sampleRecommendations}
        />
      );

      sampleRecommendations.forEach(recommendation => {
        expect(screen.getByText(recommendation)).toBeInTheDocument();
      });
    });

    it('renders the list container', () => {
      render(
        <LearningRecommendations
          learningRecommendations={sampleRecommendations}
        />
      );
      expect(
        screen.getByTestId('learning-recommendations-list')
      ).toBeInTheDocument();
    });

    it('does not show empty state when recommendations exist', () => {
      render(
        <LearningRecommendations
          learningRecommendations={sampleRecommendations}
        />
      );
      expect(
        screen.queryByTestId('learning-recommendations-empty')
      ).not.toBeInTheDocument();
    });

    it('renders card for each recommendation', () => {
      render(
        <LearningRecommendations
          learningRecommendations={sampleRecommendations}
        />
      );

      sampleRecommendations.forEach((_, index) => {
        expect(
          screen.getByTestId(`learning-recommendation-item-${index}`)
        ).toBeInTheDocument();
      });
    });

    it('displays numbers starting from 1', () => {
      render(
        <LearningRecommendations
          learningRecommendations={sampleRecommendations}
        />
      );

      const recommendationCards = screen.getAllByTestId(
        /learning-recommendation-item-\d+/
      );
      expect(recommendationCards[0]).toHaveTextContent('1');
      expect(recommendationCards[1]).toHaveTextContent('2');
      expect(recommendationCards[2]).toHaveTextContent('3');
      expect(recommendationCards[3]).toHaveTextContent('4');
    });
  });

  describe('Edge cases', () => {
    it('handles single recommendation', () => {
      render(
        <LearningRecommendations
          learningRecommendations={['Practice more coding challenges']}
        />
      );
      expect(
        screen.getByText('Practice more coding challenges')
      ).toBeInTheDocument();
      expect(
        screen.getByTestId('learning-recommendation-item-0')
      ).toBeInTheDocument();
    });

    it('handles long recommendation text', () => {
      const longRecommendation =
        'Deep dive into distributed systems architecture by reading "Designing Data-Intensive Applications" by Martin Kleppmann, implementing sample microservices with Kubernetes, and practicing system design problems on platforms like Educative or SystemDesign.one';
      render(
        <LearningRecommendations
          learningRecommendations={[longRecommendation]}
        />
      );
      expect(screen.getByText(longRecommendation)).toBeInTheDocument();
    });

    it('handles special characters and links in recommendations', () => {
      const recommendationsWithSpecialChars = [
        'Complete the "Python for Data Science" course on Coursera',
        'Read "Clean Code" by Robert C. Martin',
        'Contribute to open-source projects on GitHub (suggested: React, Node.js)',
      ];
      render(
        <LearningRecommendations
          learningRecommendations={recommendationsWithSpecialChars}
        />
      );

      recommendationsWithSpecialChars.forEach(recommendation => {
        expect(screen.getByText(recommendation)).toBeInTheDocument();
      });
    });

    it('handles many recommendations (8+)', () => {
      const manyRecommendations = Array.from(
        { length: 10 },
        (_, i) => `Recommendation ${i + 1}`
      );
      render(
        <LearningRecommendations
          learningRecommendations={manyRecommendations}
        />
      );

      expect(
        screen.getAllByTestId(/learning-recommendation-item-\d+/)
      ).toHaveLength(10);
      expect(screen.getByText('Recommendation 1')).toBeInTheDocument();
      expect(screen.getByText('Recommendation 10')).toBeInTheDocument();
    });

    it('handles recommendations with line breaks in text', () => {
      const recommendation = 'First, study algorithms.\nThen, practice daily.';
      render(
        <LearningRecommendations learningRecommendations={[recommendation]} />
      );
      // Text may be normalized with whitespace, so check it's present
      const card = screen.getByTestId('learning-recommendation-item-0');
      expect(card).toHaveTextContent('First, study algorithms.');
      expect(card).toHaveTextContent('Then, practice daily.');
    });
  });

  describe('Visual structure', () => {
    it('renders cards with gradient background', () => {
      render(
        <LearningRecommendations
          learningRecommendations={['Test recommendation']}
        />
      );
      const card = screen.getByTestId('learning-recommendation-item-0');
      expect(card).toHaveClass('bg-gradient-to-r');
    });

    it('renders numbered badges', () => {
      render(
        <LearningRecommendations
          learningRecommendations={['Test recommendation']}
        />
      );
      const card = screen.getByTestId('learning-recommendation-item-0');
      const badge = card.querySelector('div[aria-hidden="true"]');
      expect(badge).toHaveClass('bg-blue-500');
      expect(badge).toHaveTextContent('1');
    });
  });
});
