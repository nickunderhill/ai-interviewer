/**
 * JobPostingContext component - displays job posting details in session detail view.
 */
import type { JobPostingDetail } from '../types/session';

interface JobPostingContextProps {
  jobPosting: JobPostingDetail;
}

export default function JobPostingContext({
  jobPosting,
}: JobPostingContextProps) {
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
        <h3 className="text-base sm:text-lg font-semibold text-gray-900 mb-2">
          Job Description
        </h3>
        <p className="text-sm sm:text-base text-gray-700 whitespace-pre-wrap">
          {jobPosting.description}
        </p>
      </div>

      {jobPosting.tech_stack && jobPosting.tech_stack.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Tech Stack
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
