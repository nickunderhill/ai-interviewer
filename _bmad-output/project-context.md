---
project_name: 'ai-interviewer'
user_name: 'Nick'
date: '2025-12-18'
sections_completed:
  [
    'technology_stack',
    'language_rules',
    'framework_rules',
    'testing_rules',
    'quality_rules',
    'workflow_rules',
    'anti_patterns',
  ]
workflow_type: 'project-context'
status: 'complete'
optimized_for_llm: true
---

# Project Context: ai-interviewer

_This document provides critical implementation rules and patterns for AI agents
working on this project. Focus is on unobvious details and project-specific
conventions that prevent implementation mistakes._

## Technology Stack & Versions

**Frontend Stack:**

- React 18+ (functional components and hooks only)
- TypeScript (strict mode)
- Vite (latest stable) - build tool
- Tailwind CSS v3+
- TanStack Query v5 - server state management
- React Router v6 - routing
- React Hook Form v7 with Zod validation
- Axios - HTTP client with interceptors

**Backend Stack:**

- Python 3.11+
- FastAPI - API framework
- SQLAlchemy 2.0+ with async support
- Alembic - database migrations
- Pydantic v2 - schemas and validation
- python-jose - JWT implementation
- passlib with bcrypt (12 rounds) - password hashing
- cryptography (Fernet/AES-256) - API key encryption

**Database:**

- PostgreSQL - relational database
- All timestamps UTC
- snake_case naming: tables plural, columns snake_case

**Infrastructure:**

- Docker Compose - orchestration
- GitHub Actions - CI/CD workflow

## Critical Implementation Rules

### Database & Backend Patterns

**Naming Conventions (STRICT):**

- Database tables: `plural_snake_case` (e.g., `interview_sessions`, `users`)
- Table columns: `snake_case` (e.g., `created_at`, `user_id`)
- Foreign keys: explicit naming (e.g., `user_id`, not `userId`)
- Python variables/functions: `snake_case`
- Python classes: `PascalCase`

**SQLAlchemy Patterns:**

- Use SQLAlchemy 2.0+ async patterns (`AsyncSession`, `select()`)
- Models in `backend/app/models/` - ORM definitions only
- Schemas in `backend/app/schemas/` - Pydantic request/response models
- **NEVER expose SQLAlchemy models directly to API** - always use Pydantic
  schemas
- Relationships: Use `relationship()` with explicit back_populates
- All timestamps: `DateTime(timezone=True)` with UTC

**API Patterns:**

- Base path: `/api/v1/`
- Plural resources: `/api/v1/users`, `/api/v1/sessions`
- RESTful verbs: GET/POST/PUT/DELETE
- Long operations: Return operation_id, client polls `/api/v1/operations/{id}`
  every 2-3 seconds
- Error responses:
  `{"detail": {"code": "ERROR_CODE", "message": "description"}}`

**Authentication:**

- JWT in `Authorization: Bearer {token}` header
- Stateless tokens (no server-side session storage)
- Protected routes use `get_current_user` dependency
- API keys encrypted with AES-256 before database storage

### Frontend Patterns

**Naming Conventions (STRICT):**

- React components: `PascalCase` (e.g., `LoginForm.tsx`, `SessionCard.tsx`)
- Hooks: `useCamelCase` (e.g., `useAuth.ts`, `usePolling.ts`)
- Utilities/helpers: `camelCase`
- API functions: `camelCase` (e.g., `fetchSessions`, `createUser`)

**React Patterns:**

- **Functional components only** - no class components
- Hooks for all state and effects
- Feature-based organization: `src/features/{feature}/`
- Each feature has: `components/`, `hooks/`, `api.ts`, `types.ts`
- **No cross-feature imports** - use shared services in `src/services/`

**TanStack Query Patterns:**

- Query keys: array format `['resource', id, filters]`
  - Example: `['sessions', sessionId]`, `['users', 'me']`
- Use `useQuery` for GET operations
- Use `useMutation` for POST/PUT/DELETE
- Invalidate related queries after mutations
- All API calls go through `src/services/apiClient.ts` (Axios instance)

**State Management:**

- Server state: TanStack Query (queries/mutations)
- Auth state: localStorage for tokens, managed by `src/services/authService.ts`
- Form state: React Hook Form with Zod validation
- **No Redux, MobX, or global state libraries** - TanStack Query handles server
  state

### API Communication

**Axios Configuration:**

- Base URL from environment variable `VITE_API_BASE_URL`
- Request interceptor adds JWT token to headers
- Response interceptor handles 401 (refresh/logout), 403, 5xx errors
- All requests use the shared `apiClient` from `src/services/apiClient.ts`

**Long-Running Operations:**

- Question generation and answer analysis are async
- Backend returns: `{"operation_id": "uuid", "status": "pending"}`
- Frontend polls: `GET /api/v1/operations/{operation_id}` every 2-3 seconds
- Use `src/features/sessions/hooks/usePolling.ts` for polling logic
- Stop polling when status is `"completed"` or `"failed"`

**Error Handling:**

- Backend errors:
  `{"detail": {"code": "ERROR_CODE", "message": "user-friendly message"}}`
- Frontend displays errors in `<ErrorDisplay>` component
- TanStack Query `onError` handlers for all mutations
- Log errors to console (structured logging for production)

### Testing Rules

**Backend Testing:**

- Tests in `backend/tests/` mirror `backend/app/` structure
- Use pytest with fixtures in `conftest.py`
- Mock OpenAI API calls (never call real API in tests)
- Use test database (separate from development DB)
- Test endpoints: HTTP request/response validation
- Test services: Unit tests with mocked dependencies

**Frontend Testing:**

- Co-located tests: `ComponentName.test.tsx` next to `ComponentName.tsx`
- Mock API calls using MSW or similar
- Test user interactions and form submissions
- **Do not test implementation details** - test user-visible behavior

### Code Organization Rules

**Backend Structure:**

```
backend/app/
├── api/v1/endpoints/  # FastAPI route handlers
├── core/              # Config, DB, security (no business logic)
├── models/            # SQLAlchemy ORM models
├── schemas/           # Pydantic request/response schemas
├── services/          # Business logic (called by endpoints)
└── utils/             # Helpers (no business logic)
```

**Frontend Structure:**

```
frontend/src/
├── components/        # Shared UI components
│   ├── ui/           # Base components (Button, Input)
│   ├── layout/       # Layout components
│   └── common/       # Common components (LoadingSpinner, ErrorDisplay)
├── features/          # Feature modules (auth, sessions, jobs, etc.)
│   └── {feature}/
│       ├── components/
│       ├── hooks/
│       ├── api.ts
│       └── types.ts
├── services/          # Shared services (apiClient, authService, queryClient)
├── types/             # Global TypeScript types
└── utils/             # Utility functions
```

### Anti-Patterns to AVOID

**Backend:**

- ❌ Exposing SQLAlchemy models in API responses (use Pydantic schemas)
- ❌ camelCase in database or Python code (use snake_case)
- ❌ Storing passwords in plain text (always hash with bcrypt)
- ❌ Storing API keys unencrypted (use AES-256 encryption)
- ❌ Synchronous database operations (use async SQLAlchemy)

**Frontend:**

- ❌ Class components (use functional components with hooks)
- ❌ Direct cross-feature imports (use shared services)
- ❌ Multiple API client instances (use shared apiClient)
- ❌ snake_case in TypeScript/React (use camelCase/PascalCase)
- ❌ Fetching data in useEffect (use TanStack Query)
- ❌ Inline API calls without error handling (always use try-catch or onError)

**API Communication:**

- ❌ Long-running operations without operation IDs (use async pattern with
  polling)
- ❌ Inconsistent error response formats (always use
  `{"detail": {"code": ..., "message": ...}}`)
- ❌ Missing JWT token on protected routes (always add via interceptor)

---

## Usage Guidelines

**For AI Agents:**

- Read this file before implementing any code
- Follow ALL rules exactly as documented
- When in doubt, prefer the more restrictive option
- Refer to the architecture document for detailed decisions

**For Humans:**

- Keep this file lean and focused on agent needs
- Update when technology stack changes or new patterns emerge
- Review periodically to remove rules that become obvious
- Ensure consistency with architecture.md

**Last Updated:** 2025-12-18
