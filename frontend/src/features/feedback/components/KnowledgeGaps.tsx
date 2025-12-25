/**
 * KnowledgeGaps component - displays identified knowledge gaps from interview feedback.
 * Shows empty state when no gaps are identified.
 */

import React from 'react';
import type { KnowledgeGapsProps } from '../types/feedback';

export const KnowledgeGaps: React.FC<KnowledgeGapsProps> = ({
  knowledgeGaps,
}) => {
  const hasGaps = knowledgeGaps && knowledgeGaps.length > 0;

  return (
    <div className="space-y-3" data-testid="knowledge-gaps">
      <h3 className="text-xl font-bold text-gray-900">Knowledge Gaps</h3>

      {!hasGaps ? (
        <div
          className="bg-green-50 border border-green-200 rounded-lg p-4 text-center"
          data-testid="knowledge-gaps-empty"
        >
          <p className="text-green-800 font-medium">
            No major knowledge gaps identified. Great job!
          </p>
        </div>
      ) : (
        <ul className="space-y-2" data-testid="knowledge-gaps-list" role="list">
          {knowledgeGaps.map((gap, index) => (
            <li
              key={index}
              className="flex items-start gap-3 bg-orange-50 border border-orange-200 rounded-lg p-3"
              data-testid={`knowledge-gap-item-${index}`}
            >
              <span
                className="flex-shrink-0 w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-sm font-semibold"
                aria-hidden="true"
              >
                {index + 1}
              </span>
              <span className="text-gray-800 pt-0.5">{gap}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default KnowledgeGaps;
