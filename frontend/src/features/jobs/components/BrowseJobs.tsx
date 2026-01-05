import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Link, useNavigate } from 'react-router-dom';
import { useJobPostings } from '../hooks/useJobPostings';
import { createJobPosting } from '../api/jobPostingApi';
import { createSession } from '../../sessions/api/sessionApi';

const jobPostingSchema = z.object({
  title: z.string().min(1, 'Title is required').max(255),
  company: z.string().max(255).optional().or(z.literal('')),
  experience_level: z.string().max(50).optional().or(z.literal('')),
  tech_stack: z.string().optional().or(z.literal('')),
  description: z.string().min(1, 'Description is required').max(10_000),
});

type JobPostingFormData = z.infer<typeof jobPostingSchema>;

export default function BrowseJobs() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { data: jobPostings, isLoading, isError } = useJobPostings();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<JobPostingFormData>({
    resolver: zodResolver(jobPostingSchema),
    defaultValues: {
      title: '',
      company: '',
      experience_level: '',
      tech_stack: '',
      description: '',
    },
  });

  const createJobPostingMutation = useMutation({
    mutationFn: (data: JobPostingFormData) =>
      createJobPosting({
        title: data.title,
        description: data.description,
        company: data.company?.trim() ? data.company.trim() : null,
        experience_level: data.experience_level?.trim()
          ? data.experience_level.trim()
          : null,
        tech_stack: data.tech_stack
          ? data.tech_stack
              .split(',')
              .map(t => t.trim())
              .filter(Boolean)
          : [],
      }),
    onSuccess: () => {
      reset();
      void queryClient.invalidateQueries({ queryKey: ['job-postings'] });
    },
  });

  const createSessionMutation = useMutation({
    mutationFn: (jobPostingId: string) => createSession(jobPostingId),
    onSuccess: session => {
      void navigate(`/sessions/${session.id}`);
    },
  });

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 mb-2">Browse Jobs</h1>
      <p className="text-gray-600 mb-6">
        Pick a job posting to start a new mock interview session.
      </p>

      <div className="bg-white border border-gray-200 rounded-lg p-6 mb-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Create Job Posting
        </h2>
        <form
          className="space-y-4"
          onSubmit={handleSubmit(data => createJobPostingMutation.mutate(data))}
        >
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Title
              </label>
              <input
                type="text"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
                placeholder="e.g. Senior Python Developer"
                {...register('title')}
              />
              {errors.title ? (
                <p className="mt-1 text-sm text-red-600">
                  {errors.title.message}
                </p>
              ) : null}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Company (optional)
              </label>
              <input
                type="text"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
                placeholder="e.g. Acme Inc"
                {...register('company')}
              />
              {errors.company ? (
                <p className="mt-1 text-sm text-red-600">
                  {errors.company.message}
                </p>
              ) : null}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Experience level (optional)
              </label>
              <input
                type="text"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
                placeholder="e.g. Junior / Mid / Senior"
                {...register('experience_level')}
              />
              {errors.experience_level ? (
                <p className="mt-1 text-sm text-red-600">
                  {errors.experience_level.message}
                </p>
              ) : null}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Tech stack (optional)
              </label>
              <input
                type="text"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
                placeholder="e.g. Python, FastAPI, PostgreSQL"
                {...register('tech_stack')}
              />
              {errors.tech_stack ? (
                <p className="mt-1 text-sm text-red-600">
                  {errors.tech_stack.message}
                </p>
              ) : null}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              rows={6}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm"
              placeholder="Paste the job description here"
              {...register('description')}
            />
            {errors.description ? (
              <p className="mt-1 text-sm text-red-600">
                {errors.description.message}
              </p>
            ) : null}
          </div>

          <div className="flex items-center justify-between gap-4">
            <button
              type="submit"
              className="inline-flex items-center justify-center bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              disabled={createJobPostingMutation.isPending}
            >
              {createJobPostingMutation.isPending ? 'Creating…' : 'Create'}
            </button>

            <Link
              to="/dashboard"
              className="text-sm text-blue-600 hover:text-blue-800"
            >
              Back to Dashboard
            </Link>
          </div>

          {createJobPostingMutation.isError ? (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              Failed to create job posting. Please check the fields and try
              again.
            </div>
          ) : null}
        </form>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <div
              key={i}
              className="bg-white border border-gray-200 rounded-lg p-6 animate-pulse"
            >
              <div className="h-5 bg-gray-200 rounded w-1/2 mb-2" />
              <div className="h-4 bg-gray-200 rounded w-1/3 mb-4" />
              <div className="h-9 bg-gray-200 rounded w-36" />
            </div>
          ))}
        </div>
      ) : null}

      {isError ? (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Failed to load job postings.
        </div>
      ) : null}

      {!isLoading && !isError && (!jobPostings || jobPostings.length === 0) ? (
        <div className="bg-white border border-gray-200 rounded-lg p-8 text-center">
          <h2 className="text-lg font-semibold text-gray-900 mb-2">
            No job postings yet
          </h2>
          <p className="text-gray-600 mb-4">
            Create a job posting above, then start an interview.
          </p>
        </div>
      ) : null}

      {!isLoading && !isError && jobPostings && jobPostings.length > 0 ? (
        <div className="space-y-4">
          {jobPostings.map(job => (
            <div
              key={job.id}
              className="bg-white border border-gray-200 rounded-lg p-6"
            >
              <div className="flex items-start justify-between gap-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {job.title}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {job.company ?? 'Company not specified'}
                  </p>
                  {job.experience_level ? (
                    <p className="text-sm text-gray-500 mt-1">
                      Experience: {job.experience_level}
                    </p>
                  ) : null}
                  {job.tech_stack?.length ? (
                    <p className="text-sm text-gray-500 mt-1">
                      Tech: {job.tech_stack.join(', ')}
                    </p>
                  ) : null}
                </div>

                <button
                  type="button"
                  className="inline-flex items-center justify-center bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 transition-colors disabled:opacity-50"
                  onClick={() => createSessionMutation.mutate(job.id)}
                  disabled={createSessionMutation.isPending}
                >
                  {createSessionMutation.isPending
                    ? 'Starting…'
                    : 'Start Interview'}
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : null}

      {createSessionMutation.isError ? (
        <div className="mt-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          Failed to start interview. Please try again.
        </div>
      ) : null}
    </div>
  );
}
