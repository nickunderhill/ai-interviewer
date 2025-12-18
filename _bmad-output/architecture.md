---
stepsCompleted: [1, 2, 3, 4, 5, 6, 7, 8]
inputDocuments:
  - '_bmad-output/prd.md'
  - '_bmad-output/analysis/product-brief-ai-interviewer-2025-12-17.md'
workflowType: 'architecture'
lastStep: 8
status: 'complete'
completedAt: '2025-12-18'
project_name: 'ai-interviewer'
user_name: 'Nick'
date: '2025-12-17'
hasProjectContext: true
projectContextPath: '_bmad-output/project-context.md'
---

# Architecture Decision Document

_This document builds collaboratively through step-by-step discovery. Sections
are appended as we work through each architectural decision together._

## Project Context Analysis

### Requirements Overview

**Functional Requirements:**

**ai-interviewer** implements 66 functional requirements organized into 11 major
capability areas:

1. **User Account Management** (FR1-FR6): Registration, authentication, OpenAI
   API key configuration
2. **Résumé Management** (FR7-FR12): Upload/paste/edit candidate background in
   text format
3. **Job Posting Management** (FR13-FR18): Create/manage multiple job
   descriptions with metadata
4. **Interview Session Management** (FR19-FR24): Create sessions, track state,
   enable resumption
5. **Adaptive Question Generation** (FR25-FR31): Dual-context questions (JD +
   résumé) across technical/behavioral/project types
6. **Answer Submission & Storage** (FR32-FR36): Text-based answers with
   immediate persistence
7. **Answer Analysis & Feedback** (FR37-FR44): Multi-dimensional scoring
   (relevance, completeness, technical correctness, clarity) with learning
   recommendations
8. **Session History & Progress** (FR45-FR51): Complete session history with
   trend visualization
9. **Interview Retake & Improvement** (FR52-FR56): Retake tracking with score
   comparison across attempts
10. **AI Integration & Processing** (FR57-FR62): User-provided API keys,
    graceful error handling, status transparency
11. **Data Privacy & Isolation** (FR63-FR66): User data isolation, API key
    encryption, zero third-party sharing

**Architecturally Critical Requirements:**

- **Dual-Context Adaptation** (FR25, FR29): Questions must synthesize BOTH job
  requirements AND candidate background—this is the core innovation requiring
  sophisticated prompt engineering and context management
- **Multi-Dimensional Analysis** (FR37-FR42): Four-dimension scoring with
  structured feedback and learning recommendations—computationally intensive,
  requires careful LLM integration design
- **Progressive Learning Loop** (FR52-FR56): Retake functionality with
  historical comparison—requires robust data modeling for temporal analysis
- **Real-Time State Persistence** (FR23, FR24, FR34): Auto-save with
  browser-close recovery—demands transaction integrity and session state
  architecture
- **Secure API Proxy** (FR57, FR62, FR64): User API keys never exposed to
  frontend—requires backend proxy pattern with encryption

**Non-Functional Requirements:**

**Performance (NFR-P1 to NFR-P3):**

- UI interactions: < 300ms response time
- AI question generation: < 10 seconds with progress indicators
- AI answer analysis: < 30 seconds with progress indicators
- Initial page load: < 5 seconds
- Non-blocking UI during AI processing

**Security (NFR-S1 to NFR-S5):**

- API keys encrypted at rest (AES-256 equivalent)
- HTTPS-only communication
- JWT authentication with secure token storage
- Backend API proxy (keys never exposed to frontend)
- XSS/CSRF protection
- Input validation and sanitization

**Reliability (NFR-R1 to NFR-R4):**

- 95%+ system uptime during validation period
- Zero data loss for answers and feedback
- Graceful OpenAI API failure handling
- Session recovery after browser close or connection loss
- Retry logic for transient failures

**Maintainability & Reproducibility (NFR-M1 to NFR-M5):**

- Clean, documented code for research iterations
- One-command Docker Compose deployment
- Automated CI/CD pipeline (tests, linting)
- Complete documentation for external validation
- Basic observability (logging, monitoring)

**Accessibility (NFR-A1 to NFR-A3):**

- Basic WCAG compliance (semantic HTML, keyboard navigation, 4.5:1 contrast)
- Screen reader support with ARIA labels
- Responsive design (desktop-first, 1024px+ optimal, down to 768px tablet)

**Browser Compatibility (NFR-B1 to NFR-B2):**

- Modern evergreen browsers only (Chrome, Firefox, Safari, Edge)
- ES6+ features without legacy polyfills
- No IE11 support

**Scale & Complexity:**

- **Complexity Level**: Medium
  - Sophisticated AI integration with multi-stage workflows
  - Clear boundaries and well-defined problem space
  - Not enterprise-scale complexity, but beyond simple CRUD
- **Primary Domain**: Full-Stack Web Application
  - React SPA frontend with client-side routing
  - FastAPI RESTful backend
  - PostgreSQL persistence layer
  - OpenAI API integration via backend proxy
- **Estimated Architectural Components**: 8-10 major components

  1. Authentication & User Management
  2. Profile Management (résumé storage)
  3. Job Posting Management
  4. Session Engine (state machine)
  5. AI Service Gateway (OpenAI integration)
  6. Question Generation Engine
  7. Answer Analysis Engine
  8. History & Analytics Service
  9. API Gateway/Router
  10. Database Access Layer

- **User Scale (MVP)**: 10-50 concurrent users, ~1000 total sessions
- **Data Volume (MVP)**: Moderate (text-based Q&A, no media files)

### Technical Constraints & Dependencies

**Hard Dependencies:**

1. **OpenAI API**: Core innovation depends on GPT-3.5/GPT-4 capabilities

   - User-supplied API keys (BYOK model)
   - Rate limits vary per user account
   - Requires robust error handling and retry logic
   - API cost transparency critical for user trust

2. **Modern Browser Environment**:

   - JavaScript ES6+ features (async/await, promises, modules)
   - React 18+ with hooks and functional components
   - No legacy browser support constraints

3. **PostgreSQL Database**:
   - Relational data model for user accounts, sessions, Q&A pairs
   - Transaction support for data integrity
   - Encryption capabilities for API key storage

**Technical Constraints:**

- **BYOK Model**: All AI operations must route through user-provided
  credentials—no shared API key pool
- **Text-Only MVP**: No voice, video, or rich media in initial version
  (simplifies architecture)
- **Synchronous Workflow**: Question generation and answer analysis are
  sequential blocking operations (no parallel question generation in MVP)
- **Single LLM Provider**: OpenAI-only for MVP (no multi-provider abstraction
  needed initially)
- **Diploma Timeline**: ~3-6 months from architecture to validated MVP—affects
  scope and complexity decisions
- **Solo Developer**: Single developer (Nick) with intermediate skill
  level—prioritize proven tech over novel frameworks

**Infrastructure Constraints:**

- **Docker Compose Deployment**: MVP targets local/single-server deployment (not
  distributed systems)
- **No CDN/Edge Compute**: Simple hosting model for research validation
- **GitLab CI/CD**: Automation constrained to GitLab ecosystem
- **PostgreSQL Scaling**: Vertical scaling only for MVP (no sharding,
  replication, or clustering)

### Cross-Cutting Concerns Identified

**1. API Rate Limiting & Error Handling**

- **Impact**: Every AI operation (question generation, answer analysis) can fail
- **Architecture Need**: Unified retry logic, exponential backoff, graceful
  degradation
- **User Experience**: Transparent error messages, status indicators, retry
  guidance

**2. State Persistence & Synchronization**

- **Impact**: Every user action must be immediately persisted for session
  recovery
- **Architecture Need**: Auto-save pattern, transaction boundaries, idempotent
  operations
- **Data Integrity**: Atomic writes, rollback on failure, consistency validation

**3. Security & Encryption**

- **Impact**: Touches every layer—API keys (storage), data transmission (HTTPS),
  auth (JWT), user isolation (DB queries)
- **Architecture Need**: Security-by-design pattern, encryption service, secure
  configuration management
- **Compliance**: Privacy-first approach (no unnecessary data collection or
  sharing)

**4. Context Management (Dual-Context Flow)**

- **Impact**: Job description + résumé context must flow consistently through
  the entire pipeline
- **Architecture Need**: Context object pattern, consistent data structure
  across services
- **Pipeline**: User Input → Session Creation → Question Generation → Answer
  Analysis → Feedback Generation
- **Data Consistency**: Same context used for all questions in a session,
  versioned for retakes

**5. Progress Tracking & Analytics**

- **Impact**: Every answer/feedback pair contributes to longitudinal analytics
- **Architecture Need**: Consistent scoring data model, temporal queries,
  aggregation logic
- **Features**: Score trends, improvement tracking, retake comparison,
  dimension-level breakdowns
- **Research Validation**: Data must support scientific analysis and
  reproducibility

**6. Asynchronous Processing & Status Management**

- **Impact**: AI operations take 10-30 seconds—UI cannot block
- **Architecture Need**: Background job pattern (simple polling for MVP, not
  WebSocket complexity)
- **User Experience**: Loading states, progress indicators, cancel capability,
  non-blocking UI

**7. Configuration & Environment Management**

- **Impact**: Different behavior for dev/staging/production (API endpoints,
  logging levels, security settings)
- **Architecture Need**: Environment-based config, secrets management, feature
  flags
- **Deployment**: Docker Compose with environment files, automated migrations

## Starter Template Evaluation

### Primary Technology Domain

**Full-Stack Web Application** with separate frontend and backend based on
project requirements:

- **Frontend**: React SPA (Single Page Application)
- **Backend**: FastAPI (Python REST API)
- **Database**: PostgreSQL
- **Infrastructure**: Docker Compose for containerization

### Starter Options Considered

Based on the specified tech stack (React + FastAPI + PostgreSQL), I evaluated
the following approaches:

**Option 1: Vite for React Frontend + Manual FastAPI Backend Setup**

- **Vite React-TS**: Modern, fast build tool with excellent DX
- **FastAPI**: Manual project structure following FastAPI best practices
- **Pros**: Lightweight, full control, modern tooling, fast HMR
- **Cons**: Requires manual configuration for backend structure, auth, DB
  integration

**Option 2: Full-Stack FastAPI Template (Tiangolo's Official Template)**

- **Complete Template**: Pre-configured React + FastAPI + PostgreSQL stack
- **Includes**: Docker Compose, Vite + TypeScript frontend, JWT auth, SQLModel
  ORM, automated testing, CI/CD
- **Pros**: Production-ready patterns, maintained by FastAPI creator,
  comprehensive setup
- **Cons**: More opinionated, includes features beyond MVP scope (may require
  cleanup)

**Option 3: From Scratch (No Starter)**

- **Custom Setup**: Build everything from scratch
- **Pros**: Maximum flexibility, learn every component
- **Cons**: Time-consuming, error-prone, diploma timeline risk

### Selected Starter: Hybrid Approach

**Rationale for Selection:**

Given your intermediate skill level, diploma timeline constraints (~3-6 months),
and need for proven patterns with learning opportunities, I recommend a **hybrid
approach**:

1. **Frontend**: Use Vite's React-TypeScript starter (lightweight, modern,
   flexible)
2. **Backend**: Reference Full-Stack FastAPI Template patterns but implement
   incrementally (learn while building)
3. **Infrastructure**: Docker Compose structure inspired by FastAPI template

**Why This Approach:**

- **Balances Speed & Learning**: Vite gets you productive immediately while you
  learn FastAPI patterns incrementally
- **Reduces Scope Creep**: Avoids inheriting unused features from full template
- **Timeline-Appropriate**: Proven frontend setup saves time for backend
  innovation (dual-context AI engine)
- **Research-Friendly**: Clean, understandable codebase supports academic
  documentation
- **Flexibility**: Easy to adapt patterns without fighting opinionated template
  structure

### Initialization Commands

**Frontend Setup (Vite + React + TypeScript):**

```bash
# Create React frontend with TypeScript
npm create vite@latest frontend -- --template react-ts

cd frontend
npm install

# Install additional dependencies
npm install react-router-dom @tanstack/react-query axios
npm install -D @types/react-router-dom

# Start development server
npm run dev
```

**Backend Setup (FastAPI + PostgreSQL):**

```bash
# Create backend directory
mkdir -p backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install FastAPI with standard dependencies
pip install "fastapi[standard]" sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart

# Create requirements.txt
pip freeze > requirements.txt

# Initialize FastAPI project structure
mkdir -p app/{api,core,models,schemas,services}
touch app/__init__.py app/main.py
```

**Docker Compose Setup:**

```bash
# Create docker-compose.yml at project root
touch docker-compose.yml
```

### Architectural Decisions Provided by Starter

**Frontend (Vite React-TS):**

**Language & Runtime:**

- TypeScript for type safety and better DX
- React 18+ with functional components and hooks
- ES modules with Vite's native ESM support

**Build Tooling:**

- Vite for lightning-fast HMR (Hot Module Replacement)
- esbuild for development, Rollup for production builds
- Automatic code splitting and lazy loading
- Environment variable management via `.env` files

**Development Experience:**

- Instant server start (<100ms)
- Hot Module Replacement with React Fast Refresh
- TypeScript with immediate type checking
- Source maps for debugging

**Project Structure:**

```
frontend/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page-level components
│   ├── services/       # API client layer
│   ├── hooks/          # Custom React hooks
│   ├── types/          # TypeScript type definitions
│   ├── utils/          # Utility functions
│   ├── App.tsx         # Root component
│   └── main.tsx        # Application entry point
├── public/             # Static assets
├── index.html          # HTML entry point
├── vite.config.ts      # Vite configuration
└── tsconfig.json       # TypeScript configuration
```

**Backend (FastAPI Patterns):**

**Language & Runtime:**

- Python 3.11+ with type hints
- Async/await support for concurrent operations
- Pydantic for data validation and settings

**API Architecture:**

- RESTful API design with FastAPI
- Automatic OpenAPI/Swagger documentation
- Request/response validation via Pydantic schemas
- Dependency injection for services

**Database Integration:**

- SQLAlchemy ORM for database operations
- Alembic for database migrations
- Connection pooling and session management
- PostgreSQL-specific optimizations

**Security:**

- JWT token authentication (python-jose)
- Password hashing with bcrypt (passlib)
- CORS middleware configuration
- Environment-based secrets management

**Project Structure:**

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/    # API route handlers
│   │       └── router.py     # API router aggregation
│   ├── core/
│   │   ├── config.py         # Settings and configuration
│   │   ├── security.py       # Auth utilities
│   │   └── database.py       # DB connection
│   ├── models/               # SQLAlchemy models
│   ├── schemas/              # Pydantic schemas
│   ├── services/             # Business logic layer
│   ├── main.py               # FastAPI application
│   └── __init__.py
├── tests/                    # Pytest test suite
├── alembic/                  # Database migrations
├── requirements.txt          # Python dependencies
└── Dockerfile                # Backend container
```

**Infrastructure (Docker Compose):**

**Development Environment:**

- PostgreSQL container with persistent volume
- Backend container with hot-reload
- Frontend dev server (or build served by backend)
- Network isolation between services

**Configuration Management:**

- Environment variables via `.env` files
- Separate configs for dev/staging/production
- Secret management for API keys and passwords
- Health checks and restart policies

**Note:** Project initialization should be broken into implementation stories:

1. Frontend scaffolding with Vite
2. Backend project structure and FastAPI setup
3. Docker Compose configuration
4. Database integration and migrations
5. API client connection between frontend/backend

## Core Architectural Decisions

### Decision Priority Analysis

**Critical Decisions (Block Implementation):**

- Database ORM: SQLAlchemy with asyncio support
- Database Migrations: Alembic
- API Validation: Pydantic schemas + SQLAlchemy models
- Authentication: JWT tokens with bcrypt password hashing
- API Security: Encrypted API keys (AES-256), CORS, HTTPS
- State Management: TanStack Query for server state
- Styling: Tailwind CSS

**Important Decisions (Shape Architecture):**

- Error Handling: Standardized JSON responses with error codes
- API Versioning: URL-based `/api/v1/`
- Long-running Operations: Client polling pattern (2-3s intervals)
- Routing: React Router v6
- Form Handling: React Hook Form
- HTTP Client: Axios with interceptors
- Logging: Python logging with structured JSON

**Deferred Decisions (Post-MVP):**

- Caching Layer: Redis (defer until performance demands)
- Full Monitoring: Basic health checks only for MVP
- Advanced Rate Limiting: Database-tracked user limits sufficient for MVP

### Data Architecture

**ORM & Database Integration:**

- **Technology**: SQLAlchemy 2.0+ with asyncio support
- **Rationale**: Industry-standard ORM with excellent FastAPI integration,
  type-safe with proper configuration, async support for concurrent operations
- **Version**: Latest stable (2.0+)
- **Affects**: All database interactions, data models, query patterns

**Database Migrations:**

- **Technology**: Alembic (latest stable)
- **Rationale**: Official SQLAlchemy migration tool, auto-generates migrations
  from models, supports rollbacks, essential for iterative diploma project
  development
- **Pattern**: Auto-generate migrations from model changes, manual review before
  apply
- **Affects**: Database schema evolution, deployment process

**Data Validation:**

- **API Layer**: Pydantic v2 schemas for request/response validation
- **Database Layer**: SQLAlchemy models with constraints
- **Pattern**: Separate schemas for create/update/read operations, explicit
  mapping between API and DB models
- **Rationale**: Clean separation between API contracts and database
  implementation, FastAPI's native validation approach
- **Affects**: All API endpoints, data transfer objects

**Caching Strategy:**

- **Decision**: Deferred to post-MVP
- **Rationale**: BYOK model means users have individual OpenAI rate limits;
  PostgreSQL sufficient for 10-50 concurrent MVP users; reduces complexity for
  diploma timeline
- **Future**: Add Redis if performance profiling shows bottlenecks
- **Affects**: Current—none; Future—session storage, rate limiting, API response
  caching

### Authentication & Security

**Authentication Method:**

- **Technology**: JWT (JSON Web Tokens) via python-jose
- **Pattern**: Stateless authentication, access tokens with expiration
- **Token Storage**: httpOnly cookies (frontend) + localStorage fallback
- **Rationale**: Stateless, scalable, no server-side session management needed
  for MVP
- **Affects**: User management, protected endpoints, frontend auth flow

**Password Security:**

- **Technology**: passlib with bcrypt hashing
- **Configuration**: 12 rounds (balance security/performance)
- **Rationale**: Industry-standard password hashing, OWASP recommended
- **Affects**: User registration, login, password reset

**API Key Encryption:**

- **Technology**: Cryptography library with Fernet (AES-256)
- **Storage**: Encrypted at rest in PostgreSQL
- **Access**: Backend-only, never exposed to frontend
- **Rationale**: NFR-S2 requirement, protects user OpenAI credentials
- **Affects**: User settings, OpenAI service integration

**Authorization Pattern:**

- **Approach**: Dependency injection for auth checks
- **Pattern**: FastAPI dependencies validate JWT, extract user context
- **Scope**: User-level isolation (users access only their own data)
- **Rationale**: FastAPI-native pattern, composable, testable
- **Affects**: All protected endpoints

**Security Middleware:**

- **CORS**: Configured for frontend origin only, credentials enabled
- **HTTPS**: Enforced in production (HTTPS redirect middleware)
- **Headers**: Security headers (HSTS, X-Frame-Options, CSP)
- **Rationale**: Defense in depth, NFR-S4 requirements
- **Affects**: All HTTP traffic

### API & Communication Patterns

**API Design:**

- **Style**: RESTful with resource-based URLs
- **Versioning**: URL-based (`/api/v1/`) for future compatibility
- **Documentation**: FastAPI auto-generated OpenAPI/Swagger
- **Rationale**: Industry standard, FastAPI native, automatic docs for
  development and validation
- **Affects**: All API endpoints, frontend API client

**Error Handling:**

- **Format**: Standardized JSON error responses
- **Structure**: `{error_code: string, message: string, details?: object}`
- **HTTP Status Codes**: Semantic usage (400 validation, 401 auth, 404 not
  found, 500 server error)
- **Logging**: All errors logged with context (user_id, request_id, stack trace)
- **Rationale**: Consistent client error handling, debugging support
- **Affects**: All endpoints, frontend error displays

**Rate Limiting:**

- **Approach**: Database-tracked per-user limits
- **Pattern**: Track API calls per user per time window
- **Scope**: Protect against abuse, not needed for OpenAI (BYOK handles that)
- **Implementation**: Middleware checks limits before expensive operations
- **Rationale**: Simple MVP implementation, upgrade to Redis post-MVP if needed
- **Affects**: Session creation, question generation, answer analysis endpoints

**Long-Running Operations (AI Calls):**

- **Pattern**: Simple polling (no WebSockets for MVP)
- **Flow**:
  1. Client initiates operation (POST)
  2. Server returns operation ID immediately
  3. Client polls status endpoint every 2-3 seconds (GET)
  4. Server returns status + result when complete
- **Rationale**: Simpler than WebSockets, sufficient for 10-30 second
  operations, reduces architectural complexity
- **Affects**: Question generation, answer analysis workflows

**API Client (Frontend):**

- **Technology**: Axios
- **Configuration**: Base URL, auth interceptor (JWT injection), error
  interceptor
- **Rationale**: Better error handling than fetch, request/response interceptors
  for auth and logging
- **Affects**: All frontend-backend communication

### Frontend Architecture

**State Management:**

- **Server State**: TanStack Query (React Query) v5
- **Rationale**: Purpose-built for server state, automatic caching,
  loading/error states, background refetching, perfect for AI operations with
  status polling
- **Local State**: React useState for UI-only state
- **Global UI State**: React Context (minimal usage)
- **Affects**: All data fetching, AI operation status tracking, session history

**Component Architecture:**

- **Pattern**: Functional components with hooks
- **Organization**: Feature-based folders (pages/components/hooks per feature)
- **Reusability**: Shared UI components in common folder
- **Rationale**: Modern React best practices, hooks enable clean composition
- **Affects**: All frontend code structure

**Routing:**

- **Technology**: React Router v6
- **Pattern**: Route-based code splitting, protected routes HOC
- **Structure**: Nested routes for dashboard sections
- **Rationale**: Industry standard, dynamic routing, nested layouts support
- **Affects**: Navigation, URL structure, auth guards

**Styling:**

- **Technology**: Tailwind CSS v3+
- **Rationale**: Utility-first enables rapid development, small bundle size, no
  CSS-in-JS runtime overhead, perfect for diploma timeline
- **Component Library**: shadcn/ui (optional, copy-paste components)
- **Theming**: CSS variables for colors, support dark mode post-MVP
- **Affects**: All UI styling, development speed

**Form Handling:**

- **Technology**: React Hook Form v7
- **Validation**: Zod schema validation
- **Rationale**: Minimal re-renders, excellent DX, integrates with Zod for
  type-safe validation
- **Affects**: Login, registration, job posting forms, résumé input

**Performance Optimization:**

- **Code Splitting**: React.lazy() for route-based splitting
- **Bundle Analysis**: Vite built-in (rollup-plugin-visualizer)
- **Image Optimization**: Deferred (few images in MVP)
- **Rationale**: Route splitting sufficient for MVP, optimize based on bundle
  analysis later
- **Affects**: Initial load time, lazy-loaded routes

### Infrastructure & Deployment

**Containerization:**

- **Technology**: Docker + Docker Compose
- **Services**: Frontend (Vite dev server), Backend (FastAPI), PostgreSQL,
  (optional) Nginx for production
- **Volumes**: PostgreSQL data persistence, code mounting for hot-reload in dev
- **Rationale**: Consistent environments, easy local development, matches PRD
  specification
- **Affects**: Local development setup, deployment

**Environment Configuration:**

- **Development**: `.env.development` with docker-compose.override.yml
- **Production**: Environment variables injected at runtime
- **Secrets**: Never committed, injected via CI/CD or orchestration
- **Rationale**: 12-factor app principles, environment parity
- **Affects**: Configuration management across environments

**CI/CD:**

- **Platform**: GitLab CI/CD (per PRD)
- **Pipeline Stages**: Build → Test → Lint → Deploy
- **Docker**: Build images, run tests in containers
- **Rationale**: Automated quality checks, consistent builds
- **Affects**: Code quality enforcement, deployment process

**Logging:**

- **Backend**: Python logging module with structured JSON output
- **Format**: `{timestamp, level, message, user_id, request_id, context}`
- **Destination**: stdout (captured by Docker/orchestration)
- **Rationale**: Structured logs enable analysis, JSON parseable by log
  aggregators
- **Affects**: Debugging, monitoring, audit trail

**Monitoring (MVP):**

- **Health Checks**: `/health` endpoint (DB connection, basic checks)
- **Metrics**: Defer to post-MVP (Prometheus/Grafana if needed)
- **Alerting**: Basic error logging, no automated alerting for MVP
- **Rationale**: Minimal overhead for MVP, add comprehensive monitoring
  post-validation
- **Affects**: Operational visibility

**Deployment Target:**

- **MVP**: Single-server deployment with Docker Compose
- **Scaling**: Vertical scaling (bigger server) before horizontal
- **Future**: Kubernetes or cloud-native services if usage demands
- **Rationale**: Simplest deployment for 10-50 concurrent users, defer
  complexity until needed
- **Affects**: Infrastructure costs, operational complexity

### Decision Impact Analysis

**Implementation Sequence:**

1. **Foundation** (Week 1-2):

   - Docker Compose setup (PostgreSQL, backend, frontend services)
   - Backend project structure with FastAPI
   - SQLAlchemy models + Alembic migrations
   - Frontend Vite setup with Tailwind CSS

2. **Core Infrastructure** (Week 2-3):

   - JWT authentication (registration, login, token refresh)
   - API key encryption service
   - User management endpoints
   - Protected route HOC (frontend)

3. **Data Layer** (Week 3-4):

   - Resume management (CRUD)
   - Job posting management (CRUD)
   - Session management (create, track state)
   - Pydantic schemas for all models

4. **AI Integration** (Week 4-6):

   - OpenAI service with API key proxy
   - Question generation with dual-context prompting
   - Answer analysis engine
   - Polling pattern implementation (frontend + backend)

5. **Analytics & History** (Week 6-7):

   - Session history queries
   - Progress tracking calculations
   - Score comparison logic
   - Visualization components (TanStack Query + charts)

6. **Polish & Testing** (Week 7-8):
   - Error handling refinement
   - Form validation (React Hook Form + Zod)
   - E2E testing critical paths
   - Documentation for deployment

**Cross-Component Dependencies:**

- **Authentication → All Protected Features**: JWT must be implemented before
  any user-specific features
- **API Key Encryption → AI Operations**: Encryption service must be ready
  before OpenAI integration
- **Session State Management → Question/Answer Flow**: Session tracking is
  prerequisite for Q&A workflow
- **Polling Pattern → Long Operations**: Generic polling infrastructure enables
  both question generation and answer analysis
- **TanStack Query → All Data Fetching**: Centralizes loading states, error
  handling, caching for entire frontend
- **Pydantic Schemas → API Contracts**: Schema definitions must align with
  frontend TypeScript types

## Implementation Patterns & Consistency Rules

### Pattern Categories Defined

**Critical Conflict Points Identified:** 28 areas where AI agents could make
different implementation choices that would break compatibility

**Purpose:** These patterns ensure all AI agents (and human developers) write
code that integrates seamlessly, preventing naming conflicts, structural
inconsistencies, and communication breakdowns.

### Naming Patterns

**Database Naming Conventions (SQLAlchemy + PostgreSQL):**

- **Tables**: `snake_case` plural → `users`, `job_postings`,
  `interview_sessions`, `session_messages`, `feedback_scores`
- **Columns**: `snake_case` → `user_id`, `created_at`, `api_key_encrypted`,
  `openai_model`, `session_status`
- **Primary Keys**: Always `id` (integer or UUID) → `id`
- **Foreign Keys**: `{referenced_table_singular}_id` → `user_id`, `session_id`,
  `job_posting_id`
- **Boolean Columns**: `is_` or `has_` prefix → `is_active`, `is_completed`,
  `has_feedback`
- **Timestamps**: Always UTC → `created_at`, `updated_at`, `deleted_at` (for
  soft deletes)
- **Indexes**: `idx_{table}_{column(s)}` → `idx_users_email`,
  `idx_sessions_user_id_created_at`
- **Constraints**: `ck_{table}_{constraint}` for checks,
  `uq_{table}_{column(s)}` for unique

**Examples:**

```sql
-- Table: users
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    api_key_encrypted TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Table: interview_sessions
CREATE TABLE interview_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    job_posting_id INTEGER NOT NULL REFERENCES job_postings(id),
    session_status VARCHAR(50) NOT NULL,
    current_question_number INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);
```

**API Naming Conventions (FastAPI REST):**

- **Base Path**: `/api/v1/` for all endpoints
- **Resource Endpoints**: plural nouns → `/users`, `/sessions`, `/job-postings`
- **Nested Resources**: hierarchical → `/sessions/{session_id}/messages`,
  `/sessions/{session_id}/feedback`
- **Actions**: POST to resource → `/sessions/{session_id}/generate-question`
  (action verb in path)
- **Route Parameters**: curly braces, `snake_case` → `{user_id}`,
  `{session_id}`, `{message_id}`
- **Query Parameters**: `snake_case` →
  `?include_feedback=true&page=1&per_page=20`
- **Custom Headers**: `X-` prefix → `X-Request-ID`, `X-User-ID`

**Examples:**

```
GET    /api/v1/users/{user_id}
POST   /api/v1/users
PUT    /api/v1/users/{user_id}
DELETE /api/v1/users/{user_id}

GET    /api/v1/sessions
POST   /api/v1/sessions
GET    /api/v1/sessions/{session_id}
POST   /api/v1/sessions/{session_id}/generate-question
POST   /api/v1/sessions/{session_id}/submit-answer
GET    /api/v1/sessions/{session_id}/messages
GET    /api/v1/sessions/{session_id}/feedback
```

**Code Naming Conventions:**

**Python (Backend):**

- **Modules/Files**: `snake_case` → `user_service.py`, `openai_client.py`,
  `database.py`
- **Classes**: `PascalCase` → `UserService`, `SessionRepository`, `OpenAIClient`
- **Functions/Methods**: `snake_case` → `get_user_by_id()`, `create_session()`,
  `encrypt_api_key()`
- **Variables**: `snake_case` → `user_id`, `session_data`, `encrypted_key`
- **Constants**: `UPPER_SNAKE_CASE` → `MAX_RETRIES`, `DEFAULT_TIMEOUT`,
  `OPENAI_MODEL`
- **Private**: leading underscore → `_internal_method()`, `_helper_function()`

**TypeScript/React (Frontend):**

- **Components**: `PascalCase` → `UserCard`, `SessionHistory`,
  `QuestionDisplay`, `AnswerForm`
- **Component Files**: Match component name → `UserCard.tsx`,
  `SessionHistory.tsx`
- **Hooks**: `camelCase` with `use` prefix → `useAuth`, `useSession`,
  `usePolling`, `useQuestionGenerator`
- **Utilities**: `camelCase` → `formatDate`, `parseError`, `validateEmail`
- **Constants**: `UPPER_SNAKE_CASE` → `API_BASE_URL`, `POLLING_INTERVAL`,
  `MAX_RETRIES`
- **Types/Interfaces**: `PascalCase` with `Type` or `Interface` suffix →
  `UserType`, `SessionType`, `ApiResponseType`
- **Enums**: `PascalCase` for enum, `UPPER_SNAKE_CASE` for values →
  `enum SessionStatus { IN_PROGRESS = 'IN_PROGRESS' }`

**Examples:**

```typescript
// Component
export function SessionHistory({ userId }: { userId: number }) {}

// Hook
export function useSession(sessionId: number) {}

// Type
export interface SessionType {
  id: number;
  user_id: number;
  status: SessionStatus;
  created_at: string;
}

// Utility
export function formatDate(dateString: string): string {}
```

### Structure Patterns

**Backend Project Organization (FastAPI):**

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py          # Aggregate all routes
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── auth.py        # Authentication endpoints
│   │           ├── users.py       # User management
│   │           ├── sessions.py    # Interview sessions
│   │           ├── job_postings.py
│   │           └── operations.py  # Long-running operation status
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings (Pydantic BaseSettings)
│   │   ├── security.py            # JWT, password hashing, encryption
│   │   └── database.py            # DB connection, session management
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── session.py
│   │   ├── job_posting.py
│   │   └── message.py
│   ├── schemas/                   # Pydantic schemas (request/response)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── session.py
│   │   └── common.py              # Shared schemas (pagination, errors)
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── session_service.py
│   │   ├── openai_service.py      # OpenAI API integration
│   │   └── encryption_service.py
│   └── utils/                     # Helper utilities
│       ├── __init__.py
│       ├── logger.py
│       └── validators.py
├── tests/                         # Pytest tests (mirrors app structure)
│   ├── __init__.py
│   ├── conftest.py                # Shared fixtures
│   ├── test_api/
│   ├── test_services/
│   └── test_models/
├── alembic/                       # Database migrations
│   ├── versions/
│   └── env.py
├── requirements.txt
├── Dockerfile
└── .env.example
```

**Frontend Project Organization (React + TypeScript):**

```
frontend/
├── src/
│   ├── main.tsx                   # Application entry point
│   ├── App.tsx                    # Root component with routing
│   ├── components/                # Shared components
│   │   ├── ui/                    # Base UI components
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Card.tsx
│   │   ├── layout/                # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Layout.tsx
│   │   └── common/                # Common components
│   │       ├── LoadingSpinner.tsx
│   │       └── ErrorDisplay.tsx
│   ├── features/                  # Feature-based organization
│   │   ├── auth/
│   │   │   ├── components/
│   │   │   │   ├── LoginForm.tsx
│   │   │   │   └── RegisterForm.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useAuth.ts
│   │   │   ├── api.ts             # Auth API calls
│   │   │   └── types.ts           # Auth-specific types
│   │   ├── sessions/
│   │   │   ├── components/
│   │   │   │   ├── SessionList.tsx
│   │   │   │   ├── SessionDetail.tsx
│   │   │   │   └── QuestionDisplay.tsx
│   │   │   ├── hooks/
│   │   │   │   ├── useSession.ts
│   │   │   │   └── usePolling.ts
│   │   │   ├── api.ts
│   │   │   └── types.ts
│   │   └── profile/
│   │       └── ...
│   ├── services/                  # Shared services
│   │   ├── apiClient.ts           # Axios instance with interceptors
│   │   └── authService.ts         # Auth token management
│   ├── types/                     # Global TypeScript types
│   │   ├── api.ts                 # API response types
│   │   ├── models.ts              # Domain model types
│   │   └── common.ts              # Common types
│   ├── utils/                     # Utility functions
│   │   ├── formatters.ts          # Date, number formatting
│   │   ├── validators.ts          # Validation helpers
│   │   └── constants.ts           # App-wide constants
│   ├── hooks/                     # Shared custom hooks
│   │   └── useLocalStorage.ts
│   └── styles/                    # Global styles (Tailwind config)
│       └── globals.css
├── public/                        # Static assets
├── index.html
├── vite.config.ts
├── tailwind.config.js
├── tsconfig.json
└── package.json
```

**Test Organization:**

- **Backend**: Tests in `/tests/` directory, mirror `app/` structure
  - `tests/test_api/test_users.py` tests `app/api/v1/endpoints/users.py`
  - `tests/test_services/test_session_service.py` tests
    `app/services/session_service.py`
- **Frontend**: Co-located tests next to components
  - `SessionHistory.test.tsx` next to `SessionHistory.tsx`
  - `useSession.test.ts` next to `useSession.ts`

### Format Patterns

**API Response Formats:**

**Success Response (200-299):**

Single Resource:

```json
{
  "id": 123,
  "email": "user@example.com",
  "created_at": "2025-12-17T10:30:00Z",
  "is_active": true
}
```

Collection (with pagination):

```json
{
  "items": [
    { "id": 1, "title": "..." },
    { "id": 2, "title": "..." }
  ],
  "total": 100,
  "page": 1,
  "per_page": 20,
  "pages": 5
}
```

Creation Response (201):

```json
{
  "id": 456,
  "message": "Resource created successfully",
  "created_at": "2025-12-17T10:30:00Z"
}
```

**Error Response (400-599):**

```json
{
  "detail": {
    "error_code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "fields": {
      "email": ["Invalid email format"],
      "password": ["Must be at least 8 characters"]
    }
  }
}
```

Error Codes:

- `VALIDATION_ERROR` - Invalid input data
- `AUTHENTICATION_ERROR` - Invalid credentials
- `AUTHORIZATION_ERROR` - Insufficient permissions
- `NOT_FOUND` - Resource not found
- `CONFLICT` - Resource conflict (duplicate email, etc.)
- `RATE_LIMIT_EXCEEDED` - Too many requests
- `OPENAI_API_ERROR` - OpenAI API failure
- `INTERNAL_ERROR` - Server error

**Long-Running Operation Pattern:**

Initiate (POST `/sessions/{id}/generate-question`):

```json
{
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "estimated_duration_seconds": 10
}
```

Poll Status (GET `/operations/{operation_id}`):

```json
{
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "question_id": 789,
    "question_text": "Tell me about a time...",
    "question_type": "behavioral"
  },
  "completed_at": "2025-12-17T10:30:15Z"
}
```

Failed Operation:

```json
{
  "operation_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "error": {
    "error_code": "OPENAI_API_ERROR",
    "message": "OpenAI API rate limit exceeded"
  },
  "failed_at": "2025-12-17T10:30:05Z"
}
```

**Data Exchange Formats:**

- **Dates/Times**: ISO 8601 strings in UTC → `"2025-12-17T10:30:00Z"` (always
  include 'Z')
- **JSON Fields**: `snake_case` (matches backend) → `user_id`, `session_id`,
  `created_at`
- **Booleans**: `true`/`false` (not `1`/`0` or strings)
- **Null Values**: Explicit `null` in JSON (not `undefined` or missing)
- **IDs**: Integers for database IDs, UUID strings for operations → `123` or
  `"550e8400-..."`
- **Enums**: Uppercase strings → `"IN_PROGRESS"`, `"COMPLETED"`, `"FAILED"`
- **Numbers**: Native JSON numbers (not strings) → `123` not `"123"`

### Communication Patterns

**HTTP Client Configuration (Axios):**

```typescript
// services/apiClient.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Add auth token
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  // Add request ID for tracing
  config.headers['X-Request-ID'] = generateRequestId();
  return config;
});

// Response interceptor: Handle errors
apiClient.interceptors.response.use(
  response => response,
  async error => {
    if (error.response?.status === 401) {
      // Token expired, redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

**TanStack Query Key Conventions:**

- **Format**: Array with resource type, ID, and optional params
- **Examples**:
  - `['users', userId]` - Single user
  - `['sessions']` - All sessions
  - `['sessions', sessionId]` - Single session
  - `['sessions', sessionId, 'messages']` - Session messages
  - `['sessions', { status: 'active', page: 1 }]` - Filtered sessions

**Invalidation Pattern**:

```typescript
// Invalidate all sessions
queryClient.invalidateQueries(['sessions']);

// Invalidate specific session
queryClient.invalidateQueries(['sessions', sessionId]);

// Invalidate all session-related queries
queryClient.invalidateQueries({ queryKey: ['sessions'] });
```

**Polling Pattern (for AI Operations):**

```typescript
// hooks/useOperationPolling.ts
export function useOperationPolling(operationId: string | null) {
  return useQuery({
    queryKey: ['operations', operationId],
    queryFn: () => fetchOperationStatus(operationId!),
    enabled: !!operationId,
    refetchInterval: data => {
      // Poll every 2 seconds if still processing
      if (data?.status === 'processing') {
        return 2000;
      }
      // Stop polling if completed or failed
      return false;
    },
    staleTime: 0, // Always fetch fresh status
  });
}
```

**Loading State Management:**

- **Global Loading (TanStack Query)**: `isLoading`, `isFetching`, `isError`,
  `isSuccess`
- **Local Component State**: `isSubmitting`, `isProcessing`, `isSaving`
- **Never**: `loading` (use `isLoading`), `error` alone (use `isError` +
  `error`)

```typescript
// Good
const { data, isLoading, isError, error } = useQuery(...);

if (isLoading) return <LoadingSpinner />;
if (isError) return <ErrorDisplay error={error} />;

// Bad
const { data, loading, error } = useQuery(...);
if (loading) return <Spinner />;
```

### Process Patterns

**Error Handling Patterns:**

**Backend (FastAPI):**

```python
from fastapi import HTTPException

# Raise with structured error
raise HTTPException(
    status_code=400,
    detail={
        "error_code": "VALIDATION_ERROR",
        "message": "Invalid session state",
        "fields": {"status": ["Cannot transition from COMPLETED to IN_PROGRESS"]}
    }
)

# Catch and wrap external errors
try:
    response = openai_client.chat.completions.create(...)
except OpenAIError as e:
    logger.error(f"OpenAI API error: {e}", extra={"user_id": user.id})
    raise HTTPException(
        status_code=503,
        detail={
            "error_code": "OPENAI_API_ERROR",
            "message": "Failed to generate question. Please try again.",
        }
    )
```

**Frontend (React + TanStack Query):**

```typescript
// Query error handling
const { data, isError, error } = useQuery({
  queryKey: ['sessions', sessionId],
  queryFn: fetchSession,
  onError: (error: AxiosError<ApiError>) => {
    const errorMessage =
      error.response?.data?.detail?.message || 'An unexpected error occurred';
    toast.error(errorMessage);
  },
});

// Mutation error handling
const createSessionMutation = useMutation({
  mutationFn: createSession,
  onError: (error: AxiosError<ApiError>) => {
    const detail = error.response?.data?.detail;
    if (detail?.fields) {
      // Field-level errors
      Object.entries(detail.fields).forEach(([field, messages]) => {
        setError(field, { message: messages[0] });
      });
    } else {
      toast.error(detail?.message || 'Failed to create session');
    }
  },
});
```

**Validation Patterns:**

**Backend (Pydantic):**

```python
from pydantic import BaseModel, EmailStr, field_validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
```

**Frontend (Zod + React Hook Form):**

```typescript
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

const schema = z.object({
  email: z.string().email('Invalid email format'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type FormData = z.infer<typeof schema>;

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  });

  const onSubmit = (data: FormData) => {
    /* ... */
  };
}
```

**Authentication Flow Pattern:**

1. **Login**: POST `/api/v1/auth/login` → Returns
   `{access_token, refresh_token, token_type}`
2. **Store**: Save `access_token` in localStorage + httpOnly cookie (if backend
   sets it)
3. **Use**: Axios interceptor adds `Authorization: Bearer {access_token}` to all
   requests
4. **Refresh**: On 401 error, attempt POST `/api/v1/auth/refresh` with
   refresh_token
5. **Logout**: Clear tokens, invalidate all TanStack Query caches, redirect to
   login

```typescript
// services/authService.ts
export const authService = {
  async login(email: string, password: string) {
    const response = await apiClient.post('/auth/login', { email, password });
    localStorage.setItem('access_token', response.data.access_token);
    return response.data;
  },

  logout() {
    localStorage.removeItem('access_token');
    queryClient.clear(); // Clear all caches
    window.location.href = '/login';
  },

  getToken() {
    return localStorage.getItem('access_token');
  },
};
```

**Database Transaction Pattern:**

```python
from sqlalchemy.orm import Session
from app.core.database import get_db

async def create_session_with_first_question(
    db: Session,
    user_id: int,
    job_posting_id: int
) -> InterviewSession:
    try:
        # Start transaction (implicit with Session)
        session = InterviewSession(
            user_id=user_id,
            job_posting_id=job_posting_id,
            status="IN_PROGRESS"
        )
        db.add(session)
        db.flush()  # Get session.id without committing

        # Generate first question (can fail)
        question = await generate_question(session.id)

        message = SessionMessage(
            session_id=session.id,
            message_type="QUESTION",
            content=question.text
        )
        db.add(message)

        db.commit()  # Commit both session and message
        db.refresh(session)
        return session

    except Exception as e:
        db.rollback()  # Rollback on any error
        logger.error(f"Failed to create session: {e}")
        raise
```

### Enforcement Guidelines

**All AI Agents MUST:**

1. **Follow Naming Conventions**: Use exact naming patterns for tables, columns,
   endpoints, files, functions, and variables as specified above
2. **Match Response Formats**: Return API responses in exact JSON structure
   defined (success, error, pagination, long-running ops)
3. **Use Standardized Errors**: Raise HTTPException with error_code from defined
   list, structured detail format
4. **Implement Polling Pattern**: Use TanStack Query with 2-second
   refetchInterval for all AI operations (question generation, answer analysis)
5. **Organize Code by Pattern**: Place files in correct directories (backend:
   api/services/models/schemas, frontend: features/components/hooks)
6. **Use Type-Safe Schemas**: Define Pydantic schemas (backend) and Zod schemas
   (frontend) for all data validation
7. **Follow Auth Pattern**: Use JWT with interceptor pattern, handle 401 by
   clearing tokens and redirecting
8. **Maintain UTC Timestamps**: All datetime values stored/transmitted in UTC
   ISO 8601 format with 'Z' suffix
9. **Use snake_case in APIs**: All JSON field names in API requests/responses
   use snake_case (not camelCase)
10. **Invalidate Caches Correctly**: Use TanStack Query invalidation by query
    key prefix after mutations

**Pattern Enforcement:**

- **Code Review Checklist**: Each PR checks naming, structure, formats against
  this document
- **Linting**: Configure ESLint (frontend) and Ruff (backend) to enforce naming
  conventions
- **TypeScript Strict Mode**: Catch type mismatches between API responses and
  frontend types
- **API Contract Tests**: Test API response formats match documented structure
- **Documentation**: Reference this architecture doc in all agent prompts when
  implementing features

### Pattern Examples

**Good Examples:**

**Database Model (SQLAlchemy):**

```python
# ✅ Good: Follows all conventions
class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    job_posting_id = Column(Integer, ForeignKey("job_postings.id"), nullable=False)
    session_status = Column(String(50), nullable=False, default="IN_PROGRESS")
    current_question_number = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

**API Endpoint (FastAPI):**

```python
# ✅ Good: Follows all conventions
@router.post("/sessions/{session_id}/generate-question", response_model=OperationResponse)
async def generate_question(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> OperationResponse:
    operation_id = str(uuid.uuid4())
    # Start background task
    background_tasks.add_task(generate_question_task, session_id, operation_id, db)

    return OperationResponse(
        operation_id=operation_id,
        status="processing",
        estimated_duration_seconds=10
    )
```

**React Component:**

```typescript
// ✅ Good: Follows all conventions
export function SessionHistory({ userId }: { userId: number }) {
  const {
    data: sessions,
    isLoading,
    isError,
  } = useQuery({
    queryKey: ['sessions', { user_id: userId }],
    queryFn: () => fetchSessions(userId),
  });

  if (isLoading) return <LoadingSpinner />;
  if (isError) return <ErrorDisplay message="Failed to load sessions" />;

  return (
    <div className="space-y-4">
      {sessions?.items.map(session => (
        <SessionCard key={session.id} session={session} />
      ))}
    </div>
  );
}
```

**Anti-Patterns (What to AVOID):**

```python
# ❌ Bad: Wrong table naming (singular, not snake_case)
class User(Base):
    __tablename__ = "User"  # Should be "users"

    userId = Column(Integer)  # Should be "user_id"
    createdDate = Column(DateTime)  # Should be "created_at"
```

```python
# ❌ Bad: Inconsistent error format
raise HTTPException(
    status_code=400,
    detail="Invalid email"  # Should be structured with error_code
)
```

```typescript
// ❌ Bad: Wrong naming conventions
export function session_card({ SessionId }: Props) {
  // Should be SessionCard, sessionId
  const [Loading, setLoading] = useState(false); // Should be isLoading

  // Wrong query key format
  const { data } = useQuery({
    queryKey: 'sessions', // Should be ['sessions', sessionId]
    queryFn: fetchSession,
  });
}
```

````json
// ❌ Bad: Inconsistent API response (camelCase, missing structure)
{
  "sessionId": 123,
  "userId": 456,
  "createdDate": 1234567890  // Should be ISO string, not timestamp
}
```

## Project Structure & Boundaries

### Complete Project Directory Structure

```
ai-interviewer/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── docker-compose.override.yml      # For local development overrides
│
├── backend/
│   ├── README.md
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── .env
│   ├── .env.example
│   ├── Dockerfile
│   ├── .dockerignore
│   ├── pyproject.toml               # Ruff, pytest config
│   ├── pytest.ini
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app entry point
│   │   │
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │       ├── router.py        # Aggregates all endpoints
│   │   │       └── endpoints/
│   │   │           ├── __init__.py
│   │   │           ├── auth.py           # Login, register, refresh token
│   │   │           ├── users.py          # User profile, API key management
│   │   │           ├── resumes.py        # Resume CRUD
│   │   │           ├── job_postings.py   # Job posting CRUD
│   │   │           ├── sessions.py       # Session CRUD, status
│   │   │           ├── questions.py      # Question generation trigger
│   │   │           ├── answers.py        # Answer submission
│   │   │           ├── feedback.py       # Feedback retrieval
│   │   │           ├── history.py        # Session history, analytics
│   │   │           └── operations.py     # Long-running operation status
│   │   │
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Settings (BaseSettings)
│   │   │   ├── database.py          # DB connection, session factory
│   │   │   ├── security.py          # JWT, password hashing
│   │   │   ├── encryption.py        # API key encryption (Fernet)
│   │   │   └── dependencies.py      # FastAPI dependencies (get_db, get_current_user)
│   │   │
│   │   ├── models/                  # SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # User, API keys
│   │   │   ├── resume.py            # Resume
│   │   │   ├── job_posting.py       # Job postings
│   │   │   ├── session.py           # Interview sessions
│   │   │   ├── message.py           # Session messages (questions/answers)
│   │   │   ├── feedback.py          # Feedback scores
│   │   │   └── operation.py         # Long-running operations tracking
│   │   │
│   │   ├── schemas/                 # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py              # UserCreate, UserUpdate, UserResponse
│   │   │   ├── auth.py              # LoginRequest, TokenResponse
│   │   │   ├── resume.py            # ResumeCreate, ResumeUpdate, ResumeResponse
│   │   │   ├── job_posting.py       # JobPostingCreate, JobPostingResponse
│   │   │   ├── session.py           # SessionCreate, SessionResponse
│   │   │   ├── message.py           # MessageResponse
│   │   │   ├── feedback.py          # FeedbackResponse, ScoreBreakdown
│   │   │   ├── operation.py         # OperationResponse, OperationStatus
│   │   │   └── common.py            # PaginationParams, PaginatedResponse, ErrorResponse
│   │   │
│   │   ├── services/                # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── user_service.py      # User management logic
│   │   │   ├── auth_service.py      # Authentication logic
│   │   │   ├── session_service.py   # Session management logic
│   │   │   ├── openai_service.py    # OpenAI API integration
│   │   │   ├── question_service.py  # Question generation (dual-context)
│   │   │   ├── analysis_service.py  # Answer analysis, feedback generation
│   │   │   ├── encryption_service.py # API key encryption/decryption
│   │   │   └── history_service.py   # Analytics, progress tracking
│   │   │
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py            # Structured logging setup
│   │       ├── validators.py        # Custom validators
│   │       └── retry.py             # Retry logic for OpenAI
│   │
│   ├── alembic/                     # Database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   ├── README
│   │   └── versions/
│   │       └── .gitkeep
│   │
│   └── tests/
│       ├── __init__.py
│       ├── conftest.py              # Pytest fixtures
│       ├── test_api/
│       │   ├── __init__.py
│       │   ├── test_auth.py
│       │   ├── test_users.py
│       │   ├── test_sessions.py
│       │   └── test_operations.py
│       ├── test_services/
│       │   ├── __init__.py
│       │   ├── test_question_service.py
│       │   ├── test_analysis_service.py
│       │   └── test_openai_service.py
│       └── test_models/
│           ├── __init__.py
│           └── test_relationships.py
│
├── frontend/
│   ├── README.md
│   ├── package.json
│   ├── package-lock.json
│   ├── .env
│   ├── .env.example
│   ├── .eslintrc.cjs
│   ├── .prettierrc
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tsconfig.node.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── index.html
│   ├── Dockerfile
│   ├── .dockerignore
│   │
│   ├── public/
│   │   ├── favicon.ico
│   │   └── assets/
│   │       └── .gitkeep
│   │
│   └── src/
│       ├── main.tsx                 # React entry point
│       ├── App.tsx                  # Root component with routing
│       ├── vite-env.d.ts
│       │
│       ├── components/              # Shared components
│       │   ├── ui/                  # Base UI components
│       │   │   ├── Button.tsx
│       │   │   ├── Input.tsx
│       │   │   ├── Card.tsx
│       │   │   ├── Modal.tsx
│       │   │   ├── Spinner.tsx
│       │   │   └── Toast.tsx
│       │   ├── layout/              # Layout components
│       │   │   ├── Header.tsx
│       │   │   ├── Sidebar.tsx
│       │   │   ├── Footer.tsx
│       │   │   └── Layout.tsx
│       │   └── common/              # Common shared components
│       │       ├── LoadingSpinner.tsx
│       │       ├── ErrorDisplay.tsx
│       │       ├── EmptyState.tsx
│       │       └── ProtectedRoute.tsx
│       │
│       ├── features/                # Feature-based modules
│       │   ├── auth/
│       │   │   ├── components/
│       │   │   │   ├── LoginForm.tsx
│       │   │   │   ├── RegisterForm.tsx
│       │   │   │   └── ApiKeySetup.tsx
│       │   │   ├── hooks/
│       │   │   │   └── useAuth.ts
│       │   │   ├── api.ts           # Auth API calls
│       │   │   └── types.ts         # Auth types
│       │   │
│       │   ├── profile/
│       │   │   ├── components/
│       │   │   │   ├── ProfileForm.tsx
│       │   │   │   ├── ResumeEditor.tsx
│       │   │   │   └── ResumeUpload.tsx
│       │   │   ├── hooks/
│       │   │   │   └── useResume.ts
│       │   │   ├── api.ts
│       │   │   └── types.ts
│       │   │
│       │   ├── jobs/
│       │   │   ├── components/
│       │   │   │   ├── JobList.tsx
│       │   │   │   ├── JobCard.tsx
│       │   │   │   ├── JobForm.tsx
│       │   │   │   └── JobDetail.tsx
│       │   │   ├── hooks/
│       │   │   │   └── useJobs.ts
│       │   │   ├── api.ts
│       │   │   └── types.ts
│       │   │
│       │   ├── sessions/
│       │   │   ├── components/
│       │   │   │   ├── SessionList.tsx
│       │   │   │   ├── SessionCard.tsx
│       │   │   │   ├── SessionDetail.tsx
│       │   │   │   ├── QuestionDisplay.tsx
│       │   │   │   ├── AnswerForm.tsx
│       │   │   │   ├── FeedbackPanel.tsx
│       │   │   │   └── SessionStatus.tsx
│       │   │   ├── hooks/
│       │   │   │   ├── useSession.ts
│       │   │   │   ├── useQuestion.ts
│       │   │   │   ├── useAnswer.ts
│       │   │   │   └── usePolling.ts
│       │   │   ├── api.ts
│       │   │   └── types.ts
│       │   │
│       │   └── analytics/
│       │       ├── components/
│       │       │   ├── SessionHistory.tsx
│       │       │   ├── ProgressChart.tsx
│       │       │   ├── ScoreBreakdown.tsx
│       │       │   ├── ImprovementTracker.tsx
│       │       │   └── RetakeComparison.tsx
│       │       ├── hooks/
│       │       │   ├── useHistory.ts
│       │       │   └── useAnalytics.ts
│       │       ├── api.ts
│       │       └── types.ts
│       │
│       ├── services/                # Shared services
│       │   ├── apiClient.ts         # Axios instance with interceptors
│       │   ├── authService.ts       # Token management
│       │   └── queryClient.ts       # TanStack Query client setup
│       │
│       ├── types/                   # Global TypeScript types
│       │   ├── api.ts               # API response wrapper types
│       │   ├── models.ts            # Domain model types
│       │   ├── common.ts            # Common types (pagination, etc.)
│       │   └── index.ts             # Type exports
│       │
│       ├── utils/                   # Utility functions
│       │   ├── formatters.ts        # Date, number, text formatters
│       │   ├── validators.ts        # Validation helpers
│       │   ├── constants.ts         # App constants
│       │   └── helpers.ts           # General helpers
│       │
│       ├── hooks/                   # Shared custom hooks
│       │   ├── useLocalStorage.ts
│       │   ├── useDebounce.ts
│       │   └── useMediaQuery.ts
│       │
│       └── styles/                  # Global styles
│           └── globals.css          # Tailwind directives, global styles
│
├── docs/
│   ├── api/
│   │   └── openapi.json             # Generated OpenAPI spec
│   ├── setup.md
│   ├── development.md
│   └── deployment.md
│
└── .gitlab-ci.yml                   # GitLab CI/CD pipeline
```

### Architectural Boundaries

**API Boundaries:**

**External API Endpoint (`/api/v1/`):**
- **Purpose**: RESTful API serving frontend and potential future clients
- **Authentication**: JWT bearer token (except `/auth/login`, `/auth/register`)
- **Rate Limiting**: User-level database tracking
- **CORS**: Configured for frontend origin only

**Backend Service Boundaries:**

1. **Auth Service** (`app/services/auth_service.py`)
   - JWT token generation/validation
   - Password hashing/verification
   - Isolated from business logic

2. **OpenAI Service** (`app/services/openai_service.py`)
   - Single point of OpenAI API integration
   - Handles user API key decryption
   - Implements retry logic
   - Never exposes API keys to other services

3. **Question Service** (`app/services/question_service.py`)
   - Dual-context prompt assembly (JD + résumé)
   - Depends on OpenAI Service
   - Question type selection logic

4. **Analysis Service** (`app/services/analysis_service.py`)
   - Answer evaluation (4 dimensions)
   - Feedback generation
   - Learning gap identification
   - Depends on OpenAI Service

5. **Encryption Service** (`app/services/encryption_service.py`)
   - API key encryption/decryption only
   - No other business logic
   - Isolated secret management

**Component Boundaries (Frontend):**

**Feature-Based Isolation:**
- Each feature (`auth`, `profile`, `jobs`, `sessions`, `analytics`) is self-contained
- Features communicate via:
  - Shared API client
  - TanStack Query cache
  - React Router navigation
  - No direct feature-to-feature imports

**Shared Component Layer:**
- `components/ui/`: Presentational components only (no business logic)
- `components/layout/`: Layout structure components
- `components/common/`: Cross-cutting components (loading, errors, protected routes)

**Service Layer:**
- `services/apiClient.ts`: Axios instance (all HTTP requests go through this)
- `services/authService.ts`: Token storage/retrieval (used by apiClient interceptor)
- `services/queryClient.ts`: TanStack Query configuration (used by all features)

**Data Boundaries:**

**Database Schema Boundaries:**

1. **Users Domain**
   - Tables: `users`
   - Owns: Authentication, API keys, user profile
   - Relations: One-to-many with resumes, job_postings, sessions

2. **Content Domain**
   - Tables: `resumes`, `job_postings`
   - Owned by: Users
   - Read by: Session/Question services

3. **Session Domain**
   - Tables: `interview_sessions`, `session_messages`, `feedback_scores`
   - Central domain: Most complex relationships
   - Relations: Belongs to user, job_posting; has many messages and scores

4. **Operations Domain**
   - Table: `operations`
   - Tracks: Long-running AI operations (question generation, analysis)
   - Temporary: Can be cleaned up after completion

**Data Access Pattern:**
- All DB access through SQLAlchemy models
- Services layer owns business logic, doesn't expose models directly
- API endpoints use Pydantic schemas (never expose SQLAlchemy models to API)
- Read/write separation: Query optimization for read-heavy operations (history, analytics)

### Requirements to Structure Mapping

**Feature Mapping:**

**User Account Management (FR1-FR6):**
- Backend: `app/api/v1/endpoints/auth.py`, `app/api/v1/endpoints/users.py`
- Services: `app/services/auth_service.py`, `app/services/user_service.py`
- Models: `app/models/user.py`
- Schemas: `app/schemas/user.py`, `app/schemas/auth.py`
- Frontend: `src/features/auth/`
- Tests: `backend/tests/test_api/test_auth.py`, `backend/tests/test_services/test_auth_service.py`

**Résumé Management (FR7-FR12):**
- Backend: `app/api/v1/endpoints/resumes.py`
- Services: `app/services/user_service.py` (résumé CRUD operations)
- Models: `app/models/resume.py`
- Schemas: `app/schemas/resume.py`
- Frontend: `src/features/profile/components/ResumeEditor.tsx`
- Tests: `backend/tests/test_api/test_resumes.py`

**Job Posting Management (FR13-FR18):**
- Backend: `app/api/v1/endpoints/job_postings.py`
- Models: `app/models/job_posting.py`
- Schemas: `app/schemas/job_posting.py`
- Frontend: `src/features/jobs/`
- Tests: `backend/tests/test_api/test_job_postings.py`

**Interview Session Management (FR19-FR24):**
- Backend: `app/api/v1/endpoints/sessions.py`
- Services: `app/services/session_service.py`
- Models: `app/models/session.py`, `app/models/message.py`
- Schemas: `app/schemas/session.py`, `app/schemas/message.py`
- Frontend: `src/features/sessions/`
- Tests: `backend/tests/test_api/test_sessions.py`, `backend/tests/test_services/test_session_service.py`

**Adaptive Question Generation (FR25-FR31):**
- Backend: `app/api/v1/endpoints/questions.py`, `app/api/v1/endpoints/operations.py`
- Services: `app/services/question_service.py`, `app/services/openai_service.py`
- Models: `app/models/message.py`, `app/models/operation.py`
- Schemas: `app/schemas/operation.py`
- Frontend: `src/features/sessions/hooks/useQuestion.ts`, `src/features/sessions/hooks/usePolling.ts`
- Tests: `backend/tests/test_services/test_question_service.py`

**Answer Submission & Storage (FR32-FR36):**
- Backend: `app/api/v1/endpoints/answers.py`
- Services: `app/services/session_service.py`
- Models: `app/models/message.py`
- Frontend: `src/features/sessions/components/AnswerForm.tsx`
- Tests: `backend/tests/test_api/test_answers.py`

**Answer Analysis & Feedback (FR37-FR44):**
- Backend: `app/api/v1/endpoints/feedback.py`, `app/api/v1/endpoints/operations.py`
- Services: `app/services/analysis_service.py`, `app/services/openai_service.py`
- Models: `app/models/feedback.py`, `app/models/operation.py`
- Schemas: `app/schemas/feedback.py`
- Frontend: `src/features/sessions/components/FeedbackPanel.tsx`
- Tests: `backend/tests/test_services/test_analysis_service.py`

**Session History & Progress Tracking (FR45-FR51):**
- Backend: `app/api/v1/endpoints/history.py`
- Services: `app/services/history_service.py`
- Frontend: `src/features/analytics/`
- Tests: `backend/tests/test_api/test_history.py`

**Interview Retake & Improvement (FR52-FR56):**
- Backend: `app/services/history_service.py` (comparison logic)
- Frontend: `src/features/analytics/components/RetakeComparison.tsx`
- Tests: `backend/tests/test_services/test_history_service.py`

**AI Integration & Processing (FR57-FR62):**
- Backend: `app/services/openai_service.py`, `app/core/encryption.py`
- Services: `app/services/encryption_service.py`
- Utils: `app/utils/retry.py`
- Tests: `backend/tests/test_services/test_openai_service.py`

**Data Privacy & Isolation (FR63-FR66):**
- Backend: `app/core/security.py`, `app/core/encryption.py`, `app/core/dependencies.py`
- All endpoints: User context injection via `get_current_user` dependency
- Tests: `backend/tests/test_api/` (authorization tests)

**Cross-Cutting Concerns:**

**Authentication & Authorization:**
- Backend: `app/core/security.py`, `app/core/dependencies.py`
- Frontend: `src/services/authService.ts`, `src/services/apiClient.ts` (interceptors)
- Middleware: `app/api/v1/endpoints/` (dependency injection on protected routes)
- Components: `src/components/common/ProtectedRoute.tsx`
- Affects: All protected features

**Error Handling:**
- Backend: `app/utils/logger.py`, HTTPException with structured detail
- Frontend: `src/services/apiClient.ts` (response interceptor), `src/components/common/ErrorDisplay.tsx`
- TanStack Query: `onError` handlers in all queries/mutations
- Affects: All API calls, all user-facing operations

**Loading States & Long Operations:**
- Backend: `app/models/operation.py`, `app/api/v1/endpoints/operations.py`
- Frontend: `src/features/sessions/hooks/usePolling.ts`, TanStack Query `isLoading`/`isFetching`
- Components: `src/components/common/LoadingSpinner.tsx`
- Affects: Question generation, answer analysis

**Data Validation:**
- Backend: Pydantic schemas in `app/schemas/`
- Frontend: Zod schemas in feature-specific files, React Hook Form
- Affects: All API requests, all form submissions

**Logging & Observability:**
- Backend: `app/utils/logger.py` (structured JSON logs)
- FastAPI: Request/response logging middleware
- Docker: Stdout capture for log aggregation
- Affects: Debugging, auditing, monitoring

### Integration Points

**Internal Communication:**

**Frontend → Backend:**
- Protocol: HTTP/HTTPS (Axios)
- Format: JSON with `snake_case` fields
- Auth: JWT in `Authorization: Bearer {token}` header
- Request ID: `X-Request-ID` for tracing
- Base URL: Environment variable `VITE_API_BASE_URL`

**Backend Services Communication:**
- Direct Python function calls (not microservices)
- Dependency injection for service instantiation
- Shared database session for transactions

**Frontend Feature Communication:**
- TanStack Query cache (shared state)
- React Router (navigation with state passing)
- No direct imports between features (use shared services)

**External Integrations:**

**OpenAI API:**
- Integration Point: `backend/app/services/openai_service.py`
- Authentication: User-provided API keys (decrypted at runtime)
- Endpoints Used:
  - `chat.completions.create()` for question generation
  - `chat.completions.create()` for answer analysis
- Error Handling: Retry logic with exponential backoff
- Rate Limiting: Handled by user's OpenAI account

**PostgreSQL Database:**
- Integration Point: `backend/app/core/database.py`
- Connection: SQLAlchemy async engine
- Pool: Connection pooling (5-20 connections)
- Migrations: Alembic

**Docker Compose (Development):**
- Services: `backend`, `frontend`, `postgres`
- Networks: Shared network for inter-container communication
- Volumes: DB persistence, code mounting for hot-reload

**Data Flow:**

**User Registration Flow:**
```
Frontend (RegisterForm)
  → POST /api/v1/auth/register
  → auth_service.create_user()
  → User model → PostgreSQL
  → Return JWT token
  → Frontend stores token → Redirect to profile setup
```

**Interview Session Flow (Dual-Context Question Generation):**
```
1. Frontend → POST /api/v1/sessions (job_posting_id, resume_id)
   → session_service.create_session() → DB

2. Frontend → POST /api/v1/sessions/{id}/generate-question
   → question_service.generate_question_async()
   → Create operation record → Return operation_id

3. Background task:
   → Fetch session context (job posting + resume)
   → Assemble dual-context prompt
   → Call openai_service.generate_question()
   → Save question as message → Update operation status

4. Frontend polls: GET /api/v1/operations/{operation_id}
   → Return status + result when completed
   → Frontend displays question

5. User submits answer → POST /api/v1/sessions/{id}/answers
   → Save answer as message → DB

6. Frontend → POST /api/v1/sessions/{id}/analyze-answer
   → analysis_service.analyze_answer_async()
   → Similar async pattern with operations

7. Frontend receives feedback → Display with scores + recommendations
```

**Progress Tracking Flow:**
```
Frontend (Analytics)
  → GET /api/v1/history?user_id={id}
  → history_service.get_user_sessions()
  → Query sessions, messages, feedback
  → Calculate score trends, improvement metrics
  → Return aggregated data
  → Frontend renders charts/comparisons
```

### File Organization Patterns

**Configuration Files:**

**Root Level:**
- `docker-compose.yml`: Multi-container orchestration (postgres, backend, frontend)
- `docker-compose.override.yml`: Local dev overrides (volume mounts, ports)
- `.gitignore`: Ignore node_modules, venv, .env, build outputs
- `README.md`: Project overview, setup instructions
- `.env.example`: Template for environment variables

**Backend Configuration:**
- `backend/requirements.txt`: Python dependencies (FastAPI, SQLAlchemy, etc.)
- `backend/requirements-dev.txt`: Dev dependencies (pytest, ruff, etc.)
- `backend/.env`: Database URL, secret keys, OpenAI settings (not committed)
- `backend/pyproject.toml`: Ruff linting, pytest configuration
- `backend/app/core/config.py`: Pydantic BaseSettings (loads from .env)

**Frontend Configuration:**
- `frontend/package.json`: NPM dependencies, scripts
- `frontend/.env`: API base URL, feature flags (not committed)
- `frontend/vite.config.ts`: Vite build config, proxy, plugins
- `frontend/tsconfig.json`: TypeScript compiler options
- `frontend/tailwind.config.js`: Tailwind theme, plugins
- `frontend/.eslintrc.cjs`: ESLint rules
- `frontend/.prettierrc`: Code formatting rules

**Source Organization:**

**Backend (`backend/app/`):**
- Entry: `main.py` creates FastAPI app, includes routers
- Routing: `api/v1/router.py` aggregates all endpoint modules
- Core: `core/` contains config, DB, security (no business logic)
- Models: `models/` SQLAlchemy ORM definitions (DB schema)
- Schemas: `schemas/` Pydantic request/response models (API contracts)
- Services: `services/` business logic (called by endpoints)
- Utils: `utils/` helpers with no business logic

**Frontend (`frontend/src/`):**
- Entry: `main.tsx` renders App into DOM
- Root: `App.tsx` sets up routing, query provider
- Features: `features/{feature}/` self-contained modules
  - `components/`: Feature-specific UI components
  - `hooks/`: Feature-specific custom hooks
  - `api.ts`: Feature-specific API calls
  - `types.ts`: Feature-specific TypeScript types
- Shared: `components/`, `services/`, `utils/`, `hooks/`

**Test Organization:**

**Backend (`backend/tests/`):**
- Structure mirrors `app/` directory
- `conftest.py`: Shared pytest fixtures (test DB, test client, auth tokens)
- `test_api/`: API endpoint tests (HTTP requests, response validation)
- `test_services/`: Service unit tests (mocked dependencies)
- `test_models/`: Model relationship tests

**Frontend (`frontend/src/`):**
- Co-located tests: `ComponentName.test.tsx` next to `ComponentName.tsx`
- Test utilities: Mock API responses, test query client setup
- Coverage: Focus on critical user flows (auth, session creation, Q&A)

**Asset Organization:**

**Backend:**
- No static assets (API only)
- Logs: Stdout (captured by Docker)

**Frontend:**
- `public/`: Static assets served directly (favicon, robots.txt)
- `public/assets/`: Images, fonts (if any)
- Build output: `frontend/dist/` (generated, not committed)

### Development Workflow Integration

**Development Server Structure:**

**Backend Development:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Hot reload on file changes
- API accessible at `http://localhost:8000`
- Docs at `http://localhost:8000/docs`

**Frontend Development:**
```bash
cd frontend
npm install
npm run dev
```
- Vite dev server with HMR
- Accessible at `http://localhost:5173`
- Proxy API requests to backend (if configured)

**Docker Compose Development:**
```bash
docker-compose up
```
- All services start together
- Code mounted as volumes (hot reload)
- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- PostgreSQL: `localhost:5432`

**Build Process Structure:**

**Backend Build:**
- Dockerfile: Multi-stage build
  1. Base: Python image
  2. Dependencies: Install requirements
  3. Copy code: Add app/ directory
  4. Run: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

**Frontend Build:**
```bash
npm run build
```
- Vite builds to `frontend/dist/`
- Optimized bundles, code splitting
- Static assets with content hashes
- TypeScript type checking during build

**Docker Build:**
```bash
docker-compose -f docker-compose.yml build
```
- Builds both backend and frontend images
- Production-ready containers
- Environment variables injected at runtime

**Deployment Structure:**

**Single-Server Deployment (Docker Compose):**
```bash
# On server
git pull
docker-compose -f docker-compose.yml up -d --build
```
- Backend container: Uvicorn with 4 workers
- Frontend: Nginx serves static build from frontend/dist
- PostgreSQL: Persistent volume
- Reverse proxy: Traefik/Nginx for HTTPS (optional)

**Environment Configuration:**
- `.env.production`: Production environment variables
- Secrets: Injected via CI/CD or orchestration platform
- Database migrations: Run before deployment (`alembic upgrade head`)

**CI/CD Structure (GitLab):**
- `.gitlab-ci.yml`: Pipeline definition
- Stages:
  1. **Build**: Install dependencies, compile TypeScript
  2. **Test**: Run backend pytest, frontend tests (if any)
  3. **Lint**: Ruff (backend), ESLint (frontend)
  4. **Deploy**: Build Docker images, push to registry, deploy to server

## Architecture Validation Results

### Coherence Validation ✅

**Decision Compatibility:**
All technology choices work together seamlessly:
- React 18+ with TypeScript, Vite, TanStack Query v5, React Router v6, React Hook Form v7, and Tailwind CSS are all compatible and modern
- FastAPI with Python 3.11+, SQLAlchemy 2.0+, Alembic, Pydantic v2, and PostgreSQL form a coherent backend stack
- Docker Compose orchestrates all services without conflicts
- JWT authentication works across frontend/backend boundary
- All versions specified are stable and compatible

**Pattern Consistency:**
Implementation patterns fully support architectural decisions:
- Database patterns (snake_case, plural tables) align with SQLAlchemy conventions
- API patterns (/api/v1/, plural resources) align with FastAPI and RESTful best practices
- Frontend patterns (PascalCase components, feature-based organization) align with React ecosystem conventions
- Communication patterns (Axios interceptors, TanStack Query keys, polling) are consistent across all features
- Error handling, validation, and transaction patterns support the technology choices

**Structure Alignment:**
Project structure fully supports all architectural decisions:
- Backend layered structure (api/models/schemas/services) enables clean separation aligned with SQLAlchemy+Pydantic split
- Frontend feature-based structure supports TanStack Query cache isolation and React Router navigation
- Service layer boundaries enable proper business logic encapsulation
- Integration points properly structured for Axios interceptors and JWT authentication flow

### Requirements Coverage Validation ✅

**Functional Requirements Coverage (All 66 FRs):**
- ✅ FR1-6 (User Account): Supported by auth endpoints, JWT, bcrypt, API key encryption
- ✅ FR7-12 (Résumé): Supported by resume endpoints, file storage consideration
- ✅ FR13-18 (Job Postings): Supported by job posting endpoints, CRUD operations
- ✅ FR19-24 (Sessions): Supported by session endpoints, message storage, status tracking
- ✅ FR25-31 (Question Generation): Supported by async operations, OpenAI service, dual-context patterns
- ✅ FR32-36 (Answer Submission): Supported by answer endpoints, message persistence
- ✅ FR37-44 (Feedback Analysis): Supported by analysis service, 4-dimension scoring, feedback endpoints
- ✅ FR45-51 (History): Supported by history service, analytics queries
- ✅ FR52-56 (Retake): Supported by comparison logic in history service
- ✅ FR57-62 (AI Integration): Supported by OpenAI service, encryption service, retry logic
- ✅ FR63-66 (Security): Supported by user context injection, JWT validation, data isolation

**Non-Functional Requirements Coverage (All 22 NFRs):**
- ✅ **Performance**: TanStack Query caching, PostgreSQL connection pooling, polling pattern, stateless JWT
- ✅ **Security**: JWT authentication, bcrypt (12 rounds), AES-256 encryption, HTTPS, CORS, user isolation
- ✅ **Reliability**: Retry logic for OpenAI, transaction management, error handling patterns, structured logging
- ✅ **Maintainability**: TypeScript types, feature-based organization, layered backend, comprehensive patterns
- ✅ **Accessibility**: Tailwind CSS supports WCAG patterns, semantic HTML via React components

### Implementation Readiness Validation ✅

**Decision Completeness:**
All critical decisions documented with versions:
- ✅ All technology choices include versions (React 18+, FastAPI, SQLAlchemy 2.0+, Pydantic v2, etc.)
- ✅ Database patterns fully specified (snake_case, plural tables, explicit foreign keys, UTC timestamps)
- ✅ Authentication patterns complete (JWT, bcrypt, AES-256 with specific parameters)
- ✅ API patterns comprehensive (RESTful, versioning, polling, error standardization)
- ✅ Frontend patterns detailed (TanStack Query keys, React Hook Form, Axios interceptors)

**Structure Completeness:**
Project structure is specific and complete:
- ✅ Complete directory tree showing all subdirectories and key files for backend/ and frontend/
- ✅ All integration files specified (main.py, App.tsx, apiClient.ts, router.py)
- ✅ Configuration files enumerated (docker-compose.yml, .env, tsconfig.json, etc.)
- ✅ Test structure mirrors implementation structure
- ✅ Requirements explicitly mapped to specific files/directories

**Pattern Completeness:**
28 conflict points addressed with comprehensive examples:
- ✅ Naming conventions cover database, API, frontend, variables
- ✅ Structure patterns define backend layers, frontend features, service boundaries
- ✅ Format patterns specify JSON responses, error codes, dates
- ✅ Communication patterns detail HTTP, caching, polling, real-time considerations
- ✅ Process patterns cover error handling, validation, auth flow, transactions
- ✅ Anti-patterns provided with good/bad examples

### Gap Analysis Results

**No Critical Gaps Found** - Architecture is implementation-ready.

**Minor Enhancements (Post-MVP):**
- Redis caching deliberately deferred to post-MVP (architectural decision documented)
- WebSocket real-time updates deferred to post-MVP (polling sufficient for MVP)
- File storage strategy for résumé uploads mentioned but not fully specified (can use local filesystem or cloud storage, both compatible with current architecture)

**Validation Issues:** None found - all architectural elements are coherent and complete.

### Architecture Completeness Checklist

**✅ Requirements Analysis**
- [x] Project context thoroughly analyzed (66 FRs, 22 NFRs)
- [x] Scale and complexity assessed (intermediate, MVP: 10-50 concurrent users)
- [x] Technical constraints identified (OpenAI BYOK, modern browsers, 3-6 month timeline)
- [x] Cross-cutting concerns mapped (7 areas: rate limiting, persistence, security, context, progress, async, config)

**✅ Architectural Decisions**
- [x] Critical decisions documented with versions (complete tech stack)
- [x] Technology stack fully specified (React+FastAPI+PostgreSQL)
- [x] Integration patterns defined (RESTful, JWT, polling, Axios interceptors)
- [x] Performance considerations addressed (connection pooling, TanStack Query caching, stateless JWT)

**✅ Implementation Patterns**
- [x] Naming conventions established (28 conflict points)
- [x] Structure patterns defined (backend layers, frontend features)
- [x] Communication patterns specified (Axios, TanStack Query, polling)
- [x] Process patterns documented (error handling, validation, auth, transactions)

**✅ Project Structure**
- [x] Complete directory structure defined (backend/frontend with all subdirectories)
- [x] Component boundaries established (API, service, component, data boundaries)
- [x] Integration points mapped (frontend-backend, backend-DB, backend-OpenAI)
- [x] Requirements to structure mapping complete (all 66 FRs mapped to specific files)

### Architecture Readiness Assessment

**Overall Status:** ✅ **READY FOR IMPLEMENTATION**

**Confidence Level:** **HIGH** - All elements validated and coherent

**Key Strengths:**
- Complete requirements coverage with explicit FR mappings to structure
- Comprehensive implementation patterns preventing AI agent conflicts
- Coherent technology stack appropriate for intermediate skill level and diploma timeline
- Detailed project structure with all files/directories specified
- Clear architectural boundaries and integration points
- Anti-patterns documented to prevent common mistakes
- Deferred complexity properly documented (Redis, WebSockets post-MVP)

**Areas for Future Enhancement (Post-MVP):**
- Redis caching for high-traffic scenarios
- WebSocket real-time updates for better UX
- Advanced analytics with data aggregation layer
- Multi-region deployment considerations
- Advanced monitoring/observability tooling

### Implementation Handoff

**AI Agent Guidelines:**
- Follow all architectural decisions exactly as documented
- Use implementation patterns consistently across all components (28 conflict points addressed)
- Respect project structure and boundaries (no cross-feature imports, use shared services)
- Refer to this document for all architectural questions
- Follow anti-patterns section to avoid common mistakes

**First Implementation Priority:**
Generate starter template using Vite React-TS template + FastAPI project structure, then set up core infrastructure:
1. Initialize Vite React-TS project in frontend/
2. Initialize FastAPI project in backend/
3. Configure Docker Compose with postgres, backend, frontend services
4. Set up database connection and Alembic migrations
5. Implement JWT authentication (backend core + frontend auth service)
6. Create base project structure (directories, configuration files)

## Architecture Completion Summary

### Workflow Completion

**Architecture Decision Workflow:** COMPLETED ✅
**Total Steps Completed:** 8
**Date Completed:** 2025-12-18
**Document Location:** /_bmad-output/architecture.md

### Final Architecture Deliverables

**📋 Complete Architecture Document**

- All architectural decisions documented with specific versions
- Implementation patterns ensuring AI agent consistency
- Complete project structure with all files and directories
- Requirements to architecture mapping
- Validation confirming coherence and completeness

**🏗️ Implementation Ready Foundation**

- Core architectural decisions made across 5 categories (data, auth, API, frontend, infrastructure)
- 28 implementation patterns defined preventing AI agent conflicts
- Complete project structure specified for React+FastAPI+PostgreSQL stack
- 66 functional requirements and 22 non-functional requirements fully supported

**📚 AI Agent Implementation Guide**

- Technology stack with verified versions (React 18+, FastAPI, Python 3.11+, SQLAlchemy 2.0+, Pydantic v2, PostgreSQL)
- Consistency rules that prevent implementation conflicts (naming, structure, format, communication, process patterns)
- Project structure with clear boundaries (API, service, component, data boundaries)
- Integration patterns and communication standards (RESTful, JWT, polling, Axios interceptors)

### Implementation Handoff

**For AI Agents:**
This architecture document is your complete guide for implementing ai-interviewer. Follow all decisions, patterns, and structures exactly as documented.

**First Implementation Priority:**
Initialize project using Vite React-TS template + FastAPI project structure hybrid approach.

**Development Sequence:**

1. Initialize Vite React-TS project in frontend/
2. Initialize FastAPI project structure in backend/
3. Set up Docker Compose orchestration (postgres, backend, frontend services)
4. Configure database connection and Alembic migrations
5. Implement JWT authentication core (backend security + frontend auth service)
6. Create base project structure (all directories, configuration files per documented structure)
7. Build features following established patterns

### Quality Assurance Checklist

**✅ Architecture Coherence**

- [x] All decisions work together without conflicts
- [x] Technology choices are compatible
- [x] Patterns support the architectural decisions
- [x] Structure aligns with all choices

**✅ Requirements Coverage**

- [x] All 66 functional requirements are supported
- [x] All 22 non-functional requirements are addressed
- [x] Cross-cutting concerns are handled (7 areas identified and addressed)
- [x] Integration points are defined (frontend-backend, backend-DB, backend-OpenAI)

**✅ Implementation Readiness**

- [x] Decisions are specific and actionable (all technology versions specified)
- [x] Patterns prevent agent conflicts (28 conflict points addressed)
- [x] Structure is complete and unambiguous (complete directory tree with all files)
- [x] Examples are provided for clarity (good/bad patterns documented)

### Project Success Factors

**🎯 Clear Decision Framework**
Every technology choice was made collaboratively with clear rationale, ensuring all stakeholders understand the architectural direction. Decisions aligned with intermediate skill level and 3-6 month diploma timeline.

**🔧 Consistency Guarantee**
Implementation patterns and rules ensure that multiple AI agents will produce compatible, consistent code that works together seamlessly. 28 conflict points explicitly addressed with examples.

**📋 Complete Coverage**
All project requirements are architecturally supported, with clear mapping from business needs to technical implementation. 66 FRs explicitly mapped to specific files and directories.

**🏗️ Solid Foundation**
The chosen Vite React-TS + FastAPI hybrid approach provides a production-ready foundation following current best practices for full-stack TypeScript/Python applications.

---

**Architecture Status:** READY FOR IMPLEMENTATION ✅

**Next Phase:** Begin implementation using the architectural decisions and patterns documented herein.

**Document Maintenance:** Update this architecture when major technical decisions are made during implementation. are appended as we work through each architectural
  decision together.\_
````
