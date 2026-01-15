/**
 * DimensionScores component - displays interview feedback scores with visual progress bars.
 * Color codes scores: <60 red, 60-79 yellow, ≥80 green.
 */

import React from 'react';
import { useTranslation } from 'react-i18next';
import type { DimensionScoresProps } from '../types/feedback';

/**
 * Determines the color class for a given score.
 * @param score - Score value (0-100)
 * @returns Tailwind CSS background color class
 */
const getScoreColor = (score: number): string => {
  if (score < 60) return 'bg-red-500';
  if (score < 80) return 'bg-yellow-500';
  return 'bg-green-500';
};

/**
 * Dimension data for rendering individual scores.
 */
interface DimensionData {
  label: string;
  score: number;
}

export const DimensionScores: React.FC<DimensionScoresProps> = ({
  overallScore,
  technicalAccuracy,
  communicationClarity,
  problemSolving,
  relevance,
}) => {
  const { t } = useTranslation();

  const dimensions: DimensionData[] = [
    {
      label: t('feedback.dimensionScores.technicalAccuracy'),
      score: technicalAccuracy,
    },
    {
      label: t('feedback.dimensionScores.communicationClarity'),
      score: communicationClarity,
    },
    {
      label: t('feedback.dimensionScores.problemSolving'),
      score: problemSolving,
    },
    { label: t('feedback.dimensionScores.relevance'), score: relevance },
  ];

  return (
    <div className="space-y-6" data-testid="dimension-scores">
      {/* Overall Score - Prominent Display */}
      <div className="border-b pb-4">
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          {t('feedback.overallScore')}
        </h3>
        <div className="flex items-center gap-4">
          <div
            className={`text-5xl font-bold ${
              overallScore < 60
                ? 'text-red-600'
                : overallScore < 80
                ? 'text-yellow-600'
                : 'text-green-600'
            }`}
            data-testid="overall-score-value"
            aria-label={`Overall score: ${overallScore} out of 100`}
          >
            {overallScore}
            <span className="text-2xl text-gray-500">/100</span>
          </div>
        </div>
      </div>

      {/* Individual Dimension Scores */}
      <div className="space-y-4">
        <h4 className="text-lg font-semibold text-gray-800">
          {t('feedback.detailedBreakdown')}
        </h4>
        {dimensions.map(({ label, score }) => (
          <div
            key={label}
            data-testid={`dimension-${label
              .toLowerCase()
              .replace(/\s+/g, '-')}`}
          >
            <div className="flex justify-between mb-1">
              <span className="text-sm font-medium text-gray-700">{label}</span>
              <span
                className="text-sm font-semibold text-gray-900"
                data-testid={`score-${label
                  .toLowerCase()
                  .replace(/\s+/g, '-')}`}
                aria-label={`${label}: ${score} out of 100`}
              >
                {score}/100
              </span>
            </div>
            <div
              className="w-full bg-gray-200 rounded-full h-3 overflow-hidden"
              role="progressbar"
              aria-valuenow={score}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label={`${label} progress bar`}
            >
              <div
                className={`h-full ${getScoreColor(
                  score
                )} transition-all duration-300`}
                style={{ width: `${score}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default DimensionScores;
