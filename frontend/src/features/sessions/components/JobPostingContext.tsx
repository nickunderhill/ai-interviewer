/**
 * JobPostingContext component - displays job posting details in session detail view.
 */
import { useId, useState } from 'react';
import { useTranslation } from 'react-i18next';

import type { JobPostingDetail } from '../types/session';

interface JobPostingContextProps {
  jobPosting: JobPostingDetail;
}

export default function JobPostingContext({
  jobPosting,
}: JobPostingContextProps) {
  const { t } = useTranslation();
  const [isDescriptionOpen, setIsDescriptionOpen] = useState(false);
  const descriptionId = useId();

  return (
    <div className="bg-white shadow-md rounded-lg p-4 sm:p-6 border border-gray-200">
      <h1 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
        {jobPosting.title}
      </h1>
      <p className="text-lg sm:text-xl text-gray-700 mb-4">
        {jobPosting.company}
      </p>

      {jobPosting.experience_level && (
        <div className="mb-4">
          <span className="inline-block bg-blue-100 text-blue-800 text-sm font-medium px-3 py-1 rounded-full">
            {jobPosting.experience_level}
          </span>
        </div>
      )}

      <div className="mb-4">
        <div className="flex items-center justify-between gap-3 mb-2">
          <h3 className="text-base sm:text-lg font-semibold text-gray-900">
            {t('sessions.detail.jobDescription')}
          </h3>
          <button
            type="button"
            className="text-sm font-medium text-gray-700 underline hover:text-gray-900"
            aria-expanded={isDescriptionOpen}
            aria-controls={descriptionId}
            onClick={() => setIsDescriptionOpen(open => !open)}
          >
            {isDescriptionOpen
              ? t('sessions.detail.hide')
              : t('sessions.detail.show')}
          </button>
        </div>

        {isDescriptionOpen && (
          <p
            id={descriptionId}
            className="text-sm sm:text-base text-gray-700 whitespace-pre-wrap"
          >
            {jobPosting.description}
          </p>
        )}
      </div>

      {jobPosting.tech_stack && jobPosting.tech_stack.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {t('sessions.detail.techStack')}
          </h3>
          <div className="flex flex-wrap gap-2">
            {jobPosting.tech_stack.map((tech, index) => (
              <span
                key={index}
                className="inline-block bg-gray-100 text-gray-800 text-sm px-3 py-1 rounded"
              >
                {tech}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
