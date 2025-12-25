/**
 * LearningRecommendations component - displays personalized learning recommendations.
 * Shows empty state when no recommendations are provided.
 */

import React from 'react';
import type { LearningRecommendationsProps } from '../types/feedback';

export const LearningRecommendations: React.FC<
  LearningRecommendationsProps
> = ({ learningRecommendations }) => {
  const hasRecommendations =
    learningRecommendations && learningRecommendations.length > 0;

  return (
    <div className="space-y-3" data-testid="learning-recommendations">
      <h3 className="text-xl font-bold text-gray-900">
        Learning Recommendations
      </h3>

      {!hasRecommendations ? (
        <div
          className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center"
          data-testid="learning-recommendations-empty"
        >
          <p className="text-blue-800 font-medium">
            No specific recommendations provided. Keep up the great work!
          </p>
        </div>
      ) : (
        <div className="grid gap-3" data-testid="learning-recommendations-list">
          {learningRecommendations.map((recommendation, index) => (
            <div
              key={index}
              className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4 shadow-sm"
              data-testid={`learning-recommendation-item-${index}`}
            >
              <div className="flex items-start gap-3">
                <div
                  className="flex-shrink-0 w-8 h-8 bg-blue-500 text-white rounded-lg flex items-center justify-center font-bold shadow-sm"
                  aria-hidden="true"
                >
                  {index + 1}
                </div>
                <p className="text-gray-800 pt-1 flex-1">{recommendation}</p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default LearningRecommendations;
