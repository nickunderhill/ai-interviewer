/**
 * Tests for KnowledgeGaps component.
 */

import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { KnowledgeGaps } from '../KnowledgeGaps';

describe('KnowledgeGaps', () => {
  it('renders the component without crashing', () => {
    render(<KnowledgeGaps knowledgeGaps={[]} />);
    expect(screen.getByTestId('knowledge-gaps')).toBeInTheDocument();
  });

  it('displays the heading', () => {
    render(<KnowledgeGaps knowledgeGaps={[]} />);
    expect(screen.getByText('Knowledge Gaps')).toBeInTheDocument();
  });

  describe('Empty state', () => {
    it('shows empty state message when no gaps provided', () => {
      render(<KnowledgeGaps knowledgeGaps={[]} />);
      expect(screen.getByTestId('knowledge-gaps-empty')).toBeInTheDocument();
      expect(
        screen.getByText(/No major knowledge gaps identified. Great job!/i)
      ).toBeInTheDocument();
    });

    it('does not show the list when gaps are empty', () => {
      render(<KnowledgeGaps knowledgeGaps={[]} />);
      expect(
        screen.queryByTestId('knowledge-gaps-list')
      ).not.toBeInTheDocument();
    });
  });

  describe('With gaps', () => {
    const sampleGaps = [
      'Advanced algorithms and data structures',
      'System design patterns',
      'Cloud infrastructure (AWS, Azure)',
    ];

    it('displays all knowledge gaps', () => {
      render(<KnowledgeGaps knowledgeGaps={sampleGaps} />);

      sampleGaps.forEach(gap => {
        expect(screen.getByText(gap)).toBeInTheDocument();
      });
    });

    it('renders the list container', () => {
      render(<KnowledgeGaps knowledgeGaps={sampleGaps} />);
      expect(screen.getByTestId('knowledge-gaps-list')).toBeInTheDocument();
    });

    it('does not show empty state when gaps exist', () => {
      render(<KnowledgeGaps knowledgeGaps={sampleGaps} />);
      expect(
        screen.queryByTestId('knowledge-gaps-empty')
      ).not.toBeInTheDocument();
    });

    it('renders numbered items for each gap', () => {
      render(<KnowledgeGaps knowledgeGaps={sampleGaps} />);

      sampleGaps.forEach((_, index) => {
        expect(
          screen.getByTestId(`knowledge-gap-item-${index}`)
        ).toBeInTheDocument();
      });
    });

    it('displays numbers starting from 1', () => {
      render(<KnowledgeGaps knowledgeGaps={sampleGaps} />);

      const listItems = screen.getAllByTestId(/knowledge-gap-item-\d+/);
      expect(listItems[0]).toHaveTextContent('1');
      expect(listItems[1]).toHaveTextContent('2');
      expect(listItems[2]).toHaveTextContent('3');
    });

    it('renders with correct semantic list markup', () => {
      render(<KnowledgeGaps knowledgeGaps={sampleGaps} />);
      expect(screen.getByRole('list')).toBeInTheDocument();
    });
  });

  describe('Edge cases', () => {
    it('handles single gap', () => {
      render(<KnowledgeGaps knowledgeGaps={['Single knowledge gap']} />);
      expect(screen.getByText('Single knowledge gap')).toBeInTheDocument();
      expect(screen.getByTestId('knowledge-gap-item-0')).toBeInTheDocument();
    });

    it('handles long gap text', () => {
      const longGap =
        'Deep understanding of distributed systems architecture, including CAP theorem, consensus algorithms, event sourcing, and CQRS patterns';
      render(<KnowledgeGaps knowledgeGaps={[longGap]} />);
      expect(screen.getByText(longGap)).toBeInTheDocument();
    });

    it('handles special characters in gaps', () => {
      const gapsWithSpecialChars = [
        'C++ & low-level programming',
        'Docker/Kubernetes orchestration',
        'RESTful API design (OAuth 2.0)',
      ];
      render(<KnowledgeGaps knowledgeGaps={gapsWithSpecialChars} />);

      gapsWithSpecialChars.forEach(gap => {
        expect(screen.getByText(gap)).toBeInTheDocument();
      });
    });

    it('handles many gaps (10+)', () => {
      const manyGaps = Array.from({ length: 15 }, (_, i) => `Gap ${i + 1}`);
      render(<KnowledgeGaps knowledgeGaps={manyGaps} />);

      expect(screen.getAllByTestId(/knowledge-gap-item-\d+/)).toHaveLength(15);
      expect(screen.getByText('Gap 1')).toBeInTheDocument();
      expect(screen.getByText('Gap 15')).toBeInTheDocument();
    });
  });
});
