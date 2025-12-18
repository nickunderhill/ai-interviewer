---
stepsCompleted: [1, 2, 3, 4]
status: 'complete'
completedAt: '2025-12-18'
inputDocuments:
  - '_bmad-output/prd.md'
  - '_bmad-output/architecture.md'
totalEpics: 8
totalStories: 82
---

# ai-interviewer - Epic Breakdown

## Overview

This document provides the complete epic and story breakdown for ai-interviewer,
decomposing the requirements from the PRD and Architecture into implementable
stories.

## Requirements Inventory

### Functional Requirements

- **FR1**: Users can register for an account with email and password
- **FR2**: Users can log in to access their account
- **FR3**: Users can log out of their account
- **FR4**: Users can configure and store their OpenAI API key securely
- **FR5**: Users can view their profile information
- **FR6**: Users can update their stored OpenAI API key
- **FR7**: Users can upload a résumé in text format
- **FR8**: Users can paste résumé content directly into the system
- **FR9**: Users can view their stored résumé
- **FR10**: Users can edit their stored résumé
- **FR11**: Users can delete their résumé
- **FR12**: System stores résumé content associated with user account
- **FR13**: Users can create a new job posting with description, role title,
  experience level, and tech stack
- **FR14**: Users can view all their saved job postings
- **FR15**: Users can edit existing job postings
- **FR16**: Users can delete job postings
- **FR17**: Users can select a job posting to start a new interview session
- **FR18**: System stores multiple job postings per user
- **FR19**: Users can create a new interview session by selecting a job posting
  and using their stored résumé
- **FR20**: Users can view all their interview sessions (active and completed)
- **FR21**: Users can resume an incomplete interview session
- **FR22**: Users can view session details (job posting used, date created,
  status)
- **FR23**: System tracks session state (current question number, answered
  questions, pending questions)
- **FR24**: System persists session state to allow resumption after browser
  close
- **FR25**: System generates interview questions based on both job description
  and candidate résumé (dual-context)
- **FR26**: System generates questions across multiple types: technical,
  behavioral, and project experience
- **FR27**: System presents one question at a time to the user
- **FR28**: System tracks which questions have been answered in each session
- **FR29**: System generates follow-up questions that adapt based on previous
  answers
- **FR30**: Users can view the current question text
- **FR31**: Users can view question type (technical/behavioral/project)
- **FR32**: Users can type and submit text-based answers to questions
- **FR33**: Users can edit their answer before final submission
- **FR34**: System saves each answer with timestamp immediately upon submission
- **FR35**: Users can view their previously submitted answers in the current
  session
- **FR36**: System associates each answer with its corresponding question and
  session
- **FR37**: System analyzes each answer across multiple dimensions: job
  relevance, completeness, technical correctness, and clarity/structure
- **FR38**: System generates a numerical score for each evaluation dimension
- **FR39**: System generates structured feedback identifying answer strengths
- **FR40**: System generates structured feedback identifying areas for
  improvement
- **FR41**: System identifies specific knowledge gaps based on answer analysis
- **FR42**: System generates actionable learning recommendations with specific
  topics and resources
- **FR43**: Users can view complete feedback for each answered question
- **FR44**: System stores all scores and feedback with each answer
- **FR45**: Users can view a list of all their completed interview sessions
- **FR46**: Users can view details of any past session (questions, answers,
  scores, feedback)
- **FR47**: Users can compare scores across multiple sessions for the same job
  posting
- **FR48**: System displays score trends over time by evaluation criteria
- **FR49**: System visualizes progress improvement across retakes
- **FR50**: Users can filter session history by job posting or date range
- **FR51**: Users can view aggregate statistics (total sessions, average scores,
  improvement trends)
- **FR52**: Users can create a new session for the same job posting to retake an
  interview
- **FR53**: System tracks retake number for each job posting (attempt 1, 2, 3,
  etc.)
- **FR54**: System enables comparison of scores between original and retake
  sessions
- **FR55**: Users can view their improvement trajectory across multiple retakes
- **FR56**: System highlights which evaluation dimensions improved vs. declined
  in retakes
- **FR57**: System uses user-provided OpenAI API keys to make API calls
- **FR58**: System handles OpenAI API errors gracefully and informs users
- **FR59**: System displays processing status during question generation (e.g.,
  "AI is generating your question...")
- **FR60**: System displays processing status during answer analysis (e.g.,
  "Analyzing your response...")
- **FR61**: System implements retry logic for transient API failures
- **FR62**: System never exposes user API keys to the frontend
- **FR63**: System ensures each user can only access their own data (sessions,
  résumés, job postings)
- **FR64**: System encrypts stored OpenAI API keys at rest
- **FR65**: System does not share résumé content with any third parties beyond
  user's OpenAI account
- **FR66**: System isolates session data per user with no cross-user visibility

### Non-Functional Requirements

**Performance:**

- **NFR-P1**: Standard UI interactions must complete within 300ms; page initial
  load within 5 seconds; API data retrieval within 500ms
- **NFR-P2**: Question generation within 10 seconds with progress indication;
  answer analysis within 30 seconds with progress indication
- **NFR-P3**: UI remains responsive during background AI processing; polling
  occurs every 2-3 seconds without impacting performance

**Security:**

- **NFR-S1**: All access requires authentication; JWT-based auth with secure
  token storage; per-user session data isolation
- **NFR-S2**: OpenAI API keys encrypted at rest (AES-256); all transmission over
  HTTPS; sensitive data never logged in plain text
- **NFR-S3**: User API keys never exposed to frontend; backend proxy for all
  OpenAI calls; restricted access to stored keys
- **NFR-S4**: Résumé content not shared beyond user's OpenAI account; no
  privacy-compromising tracking in MVP; private session data
- **NFR-S5**: XSS protection via React escaping; CSRF tokens for state changes;
  secure cookies; input validation and sanitization

**Reliability:**

- **NFR-R1**: 95%+ uptime; graceful degradation when OpenAI unavailable;
  transactional database operations
- **NFR-R2**: Zero data loss for answers/feedback; auto-save on submission;
  atomic operations with rollback; persistent session state
- **NFR-R3**: Graceful OpenAI API failure handling; retry logic (3 retries,
  exponential backoff); actionable error messages
- **NFR-R4**: Session resumption after browser close or connection loss;
  real-time session state synchronization

**Maintainability:**

- **NFR-M1**: Clean, documented code; modular architecture; consistent coding
  standards
- **NFR-M2**: One-command deployment via Docker Compose; environment-based
  configuration; automated migrations
- **NFR-M3**: Automated test suite covering critical paths; GitLab CI/CD
  pipeline; build failures prevent deployment
- **NFR-M4**: Complete setup, API, architecture, and user documentation
- **NFR-M5**: Basic logging; API failure monitoring; session completion tracking

**Accessibility:**

- **NFR-A1**: Semantic HTML; keyboard navigation; visible focus indicators;
  4.5:1 color contrast
- **NFR-A2**: ARIA labels for dynamic content; proper form labels; screen reader
  accessible error messages
- **NFR-A3**: Desktop-first (1024px+); responsive to 768px (tablet); functional
  on mobile (not optimized)

**Browser Compatibility:**

- **NFR-B1**: Chrome, Firefox, Safari, Edge (evergreen versions); modern
  JavaScript (ES6+); no IE11 support
- **NFR-B2**: Core functionality with JavaScript disabled warning; graceful
  fallbacks

**Scalability:**

- **NFR-SC1**: 10-50 concurrent users; 1000+ sessions without optimization;
  user-specific OpenAI rate limit handling
- **NFR-SC2**: Architecture supports horizontal scaling; database schema
  efficient at 10x scale; no hard-coded limits

### Additional Requirements

**From Architecture Document:**

- **Starter Template**: Vite React-TS template for frontend
  (`npm create vite@latest frontend -- --template react-ts`)
- **Backend Setup**: FastAPI with manual project structure following
  architectural patterns
- **Database**: PostgreSQL with SQLAlchemy 2.0+ (async support) and Alembic
  migrations
- **Authentication**: JWT-based with stateless tokens, bcrypt password hashing
  (12 rounds)
- **API Key Encryption**: AES-256 (Fernet) for OpenAI API keys at rest
- **Infrastructure**: Docker Compose for development and deployment
  orchestration
- **Frontend Architecture**: Feature-based organization, TanStack Query v5,
  React Router v6, React Hook Form v7, Tailwind CSS v3+
- **Backend Architecture**: Layered structure (api/models/schemas/services),
  Pydantic v2 for validation
- **API Patterns**: RESTful with `/api/v1/` base path, polling for long-running
  operations (2-3 second intervals)
- **Testing**: pytest for backend, co-located tests for frontend, mock OpenAI
  API calls
- **CI/CD**: GitLab CI/CD pipeline with build, test, lint, and deploy stages
- **Project Context**: Comprehensive implementation rules documented in
  project-context.md

### FR Coverage Map

**Epic 1 - Project Foundation & Infrastructure Setup:**

- Architecture Requirements: Vite React-TS starter, FastAPI setup, Docker
  Compose, PostgreSQL, CI/CD pipeline, project structure

**Epic 2 - User Authentication & Profile Management:**

- FR1: User registration with email and password
- FR2: User login
- FR3: User logout
- FR4: Configure and store OpenAI API key securely
- FR5: View profile information
- FR6: Update stored OpenAI API key

**Epic 3 - Interview Content Preparation:**

- FR7: Upload résumé in text format
- FR8: Paste résumé content directly
- FR9: View stored résumé
- FR10: Edit stored résumé
- FR11: Delete résumé
- FR12: System stores résumé with user account
- FR13: Create job posting (description, role, experience level, tech stack)
- FR14: View all saved job postings
- FR15: Edit existing job postings
- FR16: Delete job postings
- FR17: Select job posting to start interview session
- FR18: System stores multiple job postings per user

**Epic 4 - Interactive Interview Sessions:**

- FR19: Create interview session by selecting job posting and résumé
- FR20: View all interview sessions (active and completed)
- FR21: Resume incomplete interview session
- FR22: View session details (job posting, date, status)
- FR23: System tracks session state (question number, answered/pending
  questions)
- FR24: System persists session state for resumption
- FR25: Generate questions based on job description and résumé (dual-context)
- FR26: Generate questions across types (technical, behavioral, project)
- FR27: Present one question at a time
- FR28: Track answered questions in session
- FR29: Generate adaptive follow-up questions
- FR30: View current question text
- FR31: View question type
- FR32: Type and submit text-based answers
- FR33: Edit answer before submission
- FR34: Save answer with timestamp immediately
- FR35: View previously submitted answers in current session
- FR36: Associate answer with question and session

**Epic 5 - AI-Powered Feedback & Analysis:**

- FR37: Analyze answers across dimensions (relevance, completeness, correctness,
  clarity)
- FR38: Generate numerical score for each dimension
- FR39: Generate structured feedback on strengths
- FR40: Generate structured feedback on improvements
- FR41: Identify specific knowledge gaps
- FR42: Generate actionable learning recommendations
- FR43: View complete feedback for each question
- FR44: Store all scores and feedback with answers

**Epic 6 - Progress Tracking & Session History:**

- FR45: View list of completed interview sessions
- FR46: View details of past sessions (questions, answers, scores, feedback)
- FR47: Compare scores across sessions for same job posting
- FR48: Display score trends over time by criteria
- FR49: Visualize progress improvement across retakes
- FR50: Filter session history by job posting or date
- FR51: View aggregate statistics (total sessions, average scores, trends)

**Epic 7 - Interview Retakes & Improvement Tracking:**

- FR52: Create new session for same job posting (retake)
- FR53: Track retake number per job posting
- FR54: Compare scores between original and retake sessions
- FR55: View improvement trajectory across retakes
- FR56: Highlight which dimensions improved vs. declined

**Epic 8 - System Reliability & Error Handling:**

- FR57: Use user-provided OpenAI API keys
- FR58: Handle OpenAI API errors gracefully
- FR59: Display processing status during question generation
- FR60: Display processing status during answer analysis
- FR61: Implement retry logic for transient failures
- FR62: Never expose API keys to frontend
- FR63: Ensure users only access their own data
- FR64: Encrypt stored OpenAI API keys at rest
- FR65: Don't share résumé content with third parties
- FR66: Isolate session data per user
- All NFRs: Performance, Security, Reliability, Maintainability, Accessibility,
  Browser Compatibility, Scalability

## Epic List

### Epic 1: Project Foundation & Infrastructure Setup

Development environment is ready with complete project structure, deployment
pipeline, and all core infrastructure components operational. This establishes
the foundation for all subsequent development work.

**FRs covered:** Architecture requirements (Vite React-TS starter template,
FastAPI setup, Docker Compose orchestration, PostgreSQL database, GitLab CI/CD
pipeline, complete project structure per architecture document)

### Epic 2: User Authentication & Profile Management

Users can securely register, authenticate, manage their profile, and configure
their OpenAI API key for personalized AI-powered interviews.

**FRs covered:** FR1, FR2, FR3, FR4, FR5, FR6

### Epic 3: Interview Content Preparation

Users can prepare for interviews by managing their résumé and creating job
postings they want to practice for, establishing the dual-context foundation for
AI-powered interview sessions.

**FRs covered:** FR7, FR8, FR9, FR10, FR11, FR12, FR13, FR14, FR15, FR16, FR17,
FR18

### Epic 4: Interactive Interview Sessions

Users can start, conduct, and resume AI-powered interview sessions with
real-time question generation and answer submission, experiencing the core
dual-context adaptive interview functionality.

**FRs covered:** FR19, FR20, FR21, FR22, FR23, FR24, FR25, FR26, FR27, FR28,
FR29, FR30, FR31, FR32, FR33, FR34, FR35, FR36

### Epic 5: AI-Powered Feedback & Analysis

Users receive detailed, multi-dimensional feedback on their interview answers
with actionable improvement recommendations, transforming raw Q&A into valuable
learning insights.

**FRs covered:** FR37, FR38, FR39, FR40, FR41, FR42, FR43, FR44

### Epic 6: Progress Tracking & Session History

Users can review their complete interview history, track progress over time, and
visualize performance trends across multiple sessions and job postings.

**FRs covered:** FR45, FR46, FR47, FR48, FR49, FR50, FR51

### Epic 7: Interview Retakes & Improvement Tracking

Users can retake interviews for the same job posting and compare performance
across attempts to measure specific improvements and track their learning
journey.

**FRs covered:** FR52, FR53, FR54, FR55, FR56

### Epic 8: System Reliability & Error Handling

Users experience a robust system with graceful error handling, transparent AI
processing status, secure data isolation, and comprehensive reliability features
ensuring production-quality operation.

**FRs covered:** FR57, FR58, FR59, FR60, FR61, FR62, FR63, FR64, FR65, FR66 +
All Non-Functional Requirements (Performance, Security, Reliability,
Maintainability, Accessibility, Browser Compatibility, Scalability)

## Epic 1: Project Foundation & Infrastructure Setup

Development environment is ready with complete project structure, deployment
pipeline, and all core infrastructure components operational. This establishes
the foundation for all subsequent development work.

### Story 1.1: Initialize Frontend with Vite React-TS Template

As a developer, I want to initialize the frontend application using Vite's
React-TypeScript template, So that I have a modern, fast development environment
with TypeScript support.

**Acceptance Criteria:**

**Given** I have Node.js installed **When** I run
`npm create vite@latest frontend -- --template react-ts` **Then** a frontend
directory is created with React 18+ and TypeScript configured **And** the
project includes vite.config.ts, tsconfig.json, and package.json **And** I can
start the dev server with `npm run dev` **And** the application loads
successfully at http://localhost:5173

### Story 1.2: Initialize Backend FastAPI Project Structure

As a developer, I want to set up the FastAPI backend with the complete project
structure defined in the architecture, So that I have organized directories for
all backend components following architectural patterns.

**Acceptance Criteria:**

**Given** I have Python 3.11+ installed **When** I create the backend directory
with subdirectories (app/api, app/core, app/models, app/schemas, app/services,
app/utils) **Then** the complete backend structure per architecture document
exists **And** I install FastAPI and core dependencies (SQLAlchemy, Pydantic v2,
psycopg2-binary, python-jose, passlib, cryptography) **And** a basic main.py
FastAPI app starts successfully with `uvicorn app.main:app --reload` **And** I
can access the auto-generated API docs at http://localhost:8000/docs

### Story 1.3: Configure PostgreSQL Database with Docker Compose

As a developer, I want to set up PostgreSQL database using Docker Compose, So
that the application has a reliable database for development and can be deployed
with one command.

**Acceptance Criteria:**

**Given** I have Docker and Docker Compose installed **When** I create
docker-compose.yml with PostgreSQL service configuration **Then** running
`docker-compose up postgres` starts a PostgreSQL container **And** the database
is accessible on localhost:5432 **And** environment variables are configured for
database connection (POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB) **And** the
database persists data using a Docker volume **And** I can connect to the
database from the backend application

### Story 1.4: Integrate Backend with Database using SQLAlchemy

As a developer, I want to configure SQLAlchemy 2.0+ with async support to
connect to PostgreSQL, So that the backend can perform database operations using
the ORM.

**Acceptance Criteria:**

**Given** PostgreSQL is running via Docker Compose **When** I configure
database.py in app/core/ with async SQLAlchemy engine and session factory
**Then** the backend successfully connects to PostgreSQL on startup **And** a
get_db dependency function provides database sessions to API endpoints **And**
the connection uses the async engine with proper connection pooling (5-20
connections) **And** database connections are properly closed after each request

### Story 1.5: Set Up Alembic for Database Migrations

As a developer, I want to configure Alembic for database migrations, So that
schema changes can be version-controlled and applied consistently across
environments.

**Acceptance Criteria:**

**Given** SQLAlchemy is configured and connected to PostgreSQL **When** I
initialize Alembic with `alembic init alembic` **Then** an alembic/ directory is
created with env.py and versions/ folder **And** alembic.ini is configured with
the database connection string **And** env.py is configured to use async engine
and import all models **And** I can generate migrations with
`alembic revision --autogenerate` **And** I can apply migrations with
`alembic upgrade head`

### Story 1.6: Configure Docker Compose for Full Stack Development

As a developer, I want to configure Docker Compose to orchestrate frontend,
backend, and database services, So that the entire application can start with
one command.

**Acceptance Criteria:**

**Given** I have frontend, backend, and database configured individually
**When** I update docker-compose.yml with services for frontend, backend, and
postgres **Then** running `docker-compose up` starts all three services **And**
the backend service depends on postgres service (starts after database is ready)
**And** the frontend is accessible at http://localhost:3000 **And** the backend
API is accessible at http://localhost:8000 **And** code changes trigger hot
reload in both frontend (Vite HMR) and backend (uvicorn reload) **And**
environment variables are properly configured for each service

### Story 1.7: Set Up GitLab CI/CD Pipeline

As a developer, I want to configure a GitLab CI/CD pipeline with build, test,
lint, and deploy stages, So that code quality is maintained and deployments are
automated.

**Acceptance Criteria:**

**Given** the project is in a GitLab repository **When** I create .gitlab-ci.yml
with four stages (build, test, lint, deploy) **Then** the build stage installs
dependencies for frontend and backend **And** the test stage runs pytest for
backend tests **And** the lint stage runs Ruff for backend and ESLint for
frontend **And** the deploy stage builds Docker images and pushes to registry
(for main branch only) **And** build failures prevent progression to later
stages **And** the pipeline runs automatically on every commit

## Epic 2: User Authentication & Profile Management

Users can securely register, authenticate, manage their profile, and configure
their OpenAI API key for personalized AI-powered interviews.

### Story 2.1: Create User Model and Database Schema

As a developer, I want to create the User database model with fields for
authentication and profile, So that user data can be securely stored in
PostgreSQL.

**Acceptance Criteria:**

**Given** Alembic is configured for migrations **When** I create a User model in
app/models/user.py with fields (id, email, hashed_password, created_at,
updated_at) **Then** the User model uses SQLAlchemy 2.0+ declarative syntax
**And** email field has a unique constraint **And** timestamps use
DateTime(timezone=True) with UTC **And** I generate a migration with
`alembic revision --autogenerate -m "create users table"` **And** running
`alembic upgrade head` creates the users table in PostgreSQL **And** the table
follows snake_case naming convention

### Story 2.2: Implement Password Hashing with Bcrypt

As a developer, I want to implement secure password hashing using bcrypt with 12
rounds, So that user passwords are never stored in plain text.

**Acceptance Criteria:**

**Given** passlib with bcrypt is installed **When** I create password hashing
functions in app/core/security.py **Then** a
`hash_password(password: str) -> str` function uses bcrypt with 12 rounds
**And** a `verify_password(plain_password: str, hashed_password: str) -> bool`
function verifies passwords **And** the hashed passwords are never reversible to
plain text **And** password verification returns True for correct passwords and
False for incorrect ones

### Story 2.3: Implement JWT Token Generation and Validation

As a developer, I want to implement JWT token generation and validation for
stateless authentication, So that users can securely authenticate API requests.

**Acceptance Criteria:**

**Given** python-jose is installed **When** I create JWT functions in
app/core/security.py **Then** a `create_access_token(data: dict) -> str`
function generates JWT tokens **And** tokens include user_id and expiration time
(24 hours from creation) **And** a `decode_access_token(token: str) -> dict`
function validates and decodes tokens **And** expired tokens are rejected with
appropriate error **And** tokens are signed with a SECRET_KEY from environment
variables **And** the implementation uses HS256 algorithm

### Story 2.4: Create User Registration Endpoint

As a user, I want to register for an account with my email and password, So that
I can access the AI interview system.

**Acceptance Criteria:**

**Given** the User model and password hashing are implemented **When** I POST to
`/api/v1/auth/register` with email and password **Then** the system validates
that the email is unique **And** the password is hashed using bcrypt before
storage **And** a new user record is created in the database **And** the
endpoint returns 201 Created with user data (excluding password) **And**
attempting to register with a duplicate email returns 409 Conflict **And**
invalid email format returns 422 Validation Error

### Story 2.5: Create User Login Endpoint

As a user, I want to log in with my email and password, So that I can access my
account and interview sessions.

**Acceptance Criteria:**

**Given** a user has registered an account **When** I POST to
`/api/v1/auth/login` with correct email and password **Then** the system
verifies the password against the hashed password in the database **And** a JWT
access token is generated and returned **And** the response includes
`{"access_token": "...", "token_type": "bearer"}` **And** incorrect password
returns 401 Unauthorized **And** non-existent email returns 401 Unauthorized
**And** the token can be used to authenticate subsequent API requests

### Story 2.6: Implement Authentication Middleware with JWT

As a developer, I want to create a dependency that validates JWT tokens on
protected endpoints, So that only authenticated users can access their data.

**Acceptance Criteria:**

**Given** JWT token functions are implemented **When** I create a
`get_current_user` dependency in app/core/dependencies.py **Then** the
dependency extracts the JWT token from the Authorization header **And** the
token is validated and decoded to get the user_id **And** the user is loaded
from the database and returned **And** missing token returns 401 Unauthorized
**And** invalid token returns 401 Unauthorized **And** expired token returns 401
Unauthorized **And** protected endpoints can use this dependency to require
authentication

### Story 2.7: Create User Profile Viewing Endpoint

As a user, I want to view my profile information, So that I can see my account
details.

**Acceptance Criteria:**

**Given** I am authenticated with a valid JWT token **When** I GET
`/api/v1/users/me` with my JWT token in the Authorization header **Then** the
system returns my user profile (id, email, created_at) **And** the password hash
is never included in the response **And** requests without a token return 401
Unauthorized **And** the endpoint uses the `get_current_user` dependency for
authentication

### Story 2.8: Add API Key Storage to User Model

As a developer, I want to add encrypted API key storage to the User model, So
that users can securely store their OpenAI API keys.

**Acceptance Criteria:**

**Given** the User model exists **When** I add an `encrypted_api_key` field to
the User model **Then** the field is a String type that can store encrypted data
**And** the field is nullable (users may not have configured their API key yet)
**And** I generate a migration with
`alembic revision --autogenerate -m "add encrypted_api_key to users"` **And**
running `alembic upgrade head` adds the column to the users table

### Story 2.9: Implement API Key Encryption Service

As a developer, I want to implement API key encryption and decryption using
AES-256, So that OpenAI API keys are never stored in plain text.

**Acceptance Criteria:**

**Given** cryptography library with Fernet is installed **When** I create
encryption functions in app/services/encryption_service.py **Then** an
`encrypt_api_key(api_key: str) -> str` function encrypts keys using AES-256
(Fernet) **And** a `decrypt_api_key(encrypted_key: str) -> str` function
decrypts keys **And** the encryption key is loaded from environment variable
ENCRYPTION_KEY **And** encrypted keys cannot be decrypted without the correct
encryption key **And** the same API key encrypted twice produces different
ciphertext (includes IV/nonce)

### Story 2.10: Create API Key Configuration Endpoint

As a user, I want to securely configure and store my OpenAI API key, So that the
system can make AI-powered interview calls on my behalf.

**Acceptance Criteria:**

**Given** I am authenticated **When** I POST to `/api/v1/users/me/api-key` with
my OpenAI API key **Then** the API key is encrypted using AES-256 before storage
**And** the encrypted key is stored in the encrypted_api_key field **And** the
endpoint returns 200 OK with a success message **And** the plain text API key is
never stored in the database **And** the API key is never included in any
response **And** unauthenticated requests return 401 Unauthorized

### Story 2.11: Create API Key Update Endpoint

As a user, I want to update my stored OpenAI API key, So that I can change it if
needed.

**Acceptance Criteria:**

**Given** I am authenticated and have previously stored an API key **When** I
PUT to `/api/v1/users/me/api-key` with a new API key **Then** the new API key is
encrypted and replaces the old encrypted key **And** the endpoint returns 200 OK
with a success message **And** subsequent AI operations use the new API key
**And** the old API key is overwritten and no longer accessible

### Story 2.12: Create User Logout (Frontend Token Invalidation)

As a user, I want to log out of my account, So that my session is ended
securely.

**Acceptance Criteria:**

**Given** I am authenticated with a JWT token stored in the frontend **When** I
click the logout button in the UI **Then** the frontend removes the JWT token
from localStorage **And** the user is redirected to the login page **And**
subsequent API requests without a token return 401 Unauthorized **And** the JWT
remains valid until expiration (stateless design) but is no longer accessible to
the frontend

## Epic 3: Interview Content Preparation

Users can prepare for interviews by managing their résumé and creating job
postings they want to practice for, establishing the dual-context foundation for
AI-powered interview sessions.

### Story 3.1: Create Resume Model and Database Schema

As a developer, I want to create the Resume database model with user
association, So that users can store their résumé content in the system.

**Acceptance Criteria:**

**Given** the User model exists **When** I create a Resume model in
app/models/resume.py with fields (id, user_id, content, created_at, updated_at)
**Then** the Resume model uses SQLAlchemy 2.0+ declarative syntax **And**
user_id is a foreign key to the users table **And** content field is Text type
to store large résumé content **And** a one-to-one relationship is established
between User and Resume **And** I generate and apply a migration to create the
resumes table **And** cascading delete is configured (deleting user deletes
résumé)

### Story 3.2: Create Resume Upload/Paste Endpoint

As a user, I want to upload or paste my résumé content in text format, So that I
can use it as context for AI-generated interview questions.

**Acceptance Criteria:**

**Given** I am authenticated **When** I POST to `/api/v1/resumes` with résumé
content (text) **Then** the system validates the content is not empty **And** a
Resume record is created associated with my user_id **And** the endpoint returns
201 Created with the résumé data **And** if I already have a résumé, it returns
409 Conflict (one résumé per user) **And** unauthenticated requests return 401
Unauthorized

### Story 3.3: Create Resume Viewing Endpoint

As a user, I want to view my stored résumé, So that I can verify the content is
correct.

**Acceptance Criteria:**

**Given** I am authenticated and have uploaded a résumé **When** I GET
`/api/v1/resumes/me` **Then** the system returns my résumé content with metadata
(id, created_at, updated_at) **And** if I don't have a résumé, it returns 404
Not Found **And** other users cannot access my résumé (enforced by
authentication)

### Story 3.4: Create Resume Update Endpoint

As a user, I want to edit my stored résumé, So that I can keep my information up
to date.

**Acceptance Criteria:**

**Given** I am authenticated and have a résumé **When** I PUT to
`/api/v1/resumes/me` with updated content **Then** my existing résumé content is
replaced with the new content **And** the updated_at timestamp is updated
**And** the endpoint returns 200 OK with the updated résumé **And** if I don't
have a résumé, it returns 404 Not Found

### Story 3.5: Create Resume Delete Endpoint

As a user, I want to delete my résumé, So that I can remove my information from
the system.

**Acceptance Criteria:**

**Given** I am authenticated and have a résumé **When** I DELETE
`/api/v1/resumes/me` **Then** my résumé is permanently removed from the database
**And** the endpoint returns 204 No Content **And** subsequent GET requests
return 404 Not Found **And** if I don't have a résumé, it returns 404 Not Found

### Story 3.6: Create Job Posting Model and Database Schema

As a developer, I want to create the JobPosting database model with user
association, So that users can store multiple job postings they want to practice
for.

**Acceptance Criteria:**

**Given** the User model exists **When** I create a JobPosting model in
app/models/job_posting.py with fields (id, user_id, title, company, description,
experience_level, tech_stack, created_at, updated_at) **Then** the JobPosting
model uses SQLAlchemy 2.0+ declarative syntax **And** user_id is a foreign key
to the users table **And** a one-to-many relationship is established (User has
many JobPostings) **And** description field is Text type for job descriptions
**And** tech_stack field stores comma-separated or JSON array of technologies
**And** I generate and apply a migration to create the job_postings table

### Story 3.7: Create Job Posting Creation Endpoint

As a user, I want to create a new job posting with description, role title,
experience level, and tech stack, So that I can practice interviews for specific
positions.

**Acceptance Criteria:**

**Given** I am authenticated **When** I POST to `/api/v1/job-postings` with job
posting data **Then** the system validates all required fields (title,
description) are present **And** a JobPosting record is created associated with
my user_id **And** the endpoint returns 201 Created with the job posting data
**And** experience_level and tech_stack are optional fields **And**
unauthenticated requests return 401 Unauthorized

### Story 3.8: Create Job Posting List Endpoint

As a user, I want to view all my saved job postings, So that I can see which
positions I can practice for.

**Acceptance Criteria:**

**Given** I am authenticated and have created job postings **When** I GET
`/api/v1/job-postings` **Then** the system returns a list of all my job postings
**And** each posting includes id, title, company, experience_level, tech_stack,
created_at **And** only my job postings are returned (filtered by user_id)
**And** if I have no job postings, it returns an empty array **And** the list is
ordered by created_at descending (newest first)

### Story 3.9: Create Job Posting Detail Endpoint

As a user, I want to view a specific job posting's complete details, So that I
can review the full description before starting an interview.

**Acceptance Criteria:**

**Given** I am authenticated and have created a job posting **When** I GET
`/api/v1/job-postings/{id}` **Then** the system returns the complete job posting
including description **And** if the job posting doesn't exist or belongs to
another user, it returns 404 Not Found **And** all fields are returned (id,
title, company, description, experience_level, tech_stack, created_at,
updated_at)

### Story 3.10: Create Job Posting Update Endpoint

As a user, I want to edit an existing job posting, So that I can correct or
update the job information.

**Acceptance Criteria:**

**Given** I am authenticated and have created a job posting **When** I PUT to
`/api/v1/job-postings/{id}` with updated data **Then** the system validates I
own the job posting **And** the specified fields are updated (title, company,
description, experience_level, tech_stack) **And** the updated_at timestamp is
updated **And** the endpoint returns 200 OK with the updated job posting **And**
if the job posting doesn't exist or belongs to another user, it returns 404 Not
Found

### Story 3.11: Create Job Posting Delete Endpoint

As a user, I want to delete a job posting, So that I can remove positions I'm no
longer interested in.

**Acceptance Criteria:**

**Given** I am authenticated and have created a job posting **When** I DELETE
`/api/v1/job-postings/{id}` **Then** the system validates I own the job posting
**And** the job posting is permanently removed from the database **And** the
endpoint returns 204 No Content **And** if the job posting doesn't exist or
belongs to another user, it returns 404 Not Found **And** any interview sessions
using this job posting reference it correctly (foreign key behavior)

---

### Epic 4: Interactive Interview Sessions

**Goal:** Enable users to conduct AI-powered mock interviews with dynamically
generated questions based on dual-context (job description + résumé).

**Covers FRs:** FR19, FR20, FR21, FR22, FR23, FR24, FR25, FR26, FR27, FR28,
FR29, FR30, FR31, FR32, FR33, FR34, FR35, FR36

**Stories:**

#### Story 4.1: Create Session and Message Models

**As a** developer **I want to** create database models for interview sessions
and session messages **So that** we can persist interview state and conversation
history

**Acceptance Criteria:**

**Given** I'm implementing the data layer **When** I create the InterviewSession
model **Then** it includes fields: id (UUID), user_id (FK to User),
job_posting_id (FK to JobPosting), status (enum: 'active', 'paused',
'completed'), current_question_number (integer), created_at, updated_at **And**
I create the SessionMessage model **And** it includes fields: id (UUID),
session_id (FK to InterviewSession), message_type (enum: 'question', 'answer'),
content (Text), question_type (Text nullable -
technical/behavioral/situational), created_at **And** both use snake_case naming
with plural table names **And** foreign keys are explicit with ondelete behavior
defined **And** timestamps use UTC

#### Story 4.2: Create Session Creation Endpoint

**As a** user **I want to** start a new interview session for a job posting **So
that** I can begin practicing interview questions

**Acceptance Criteria:**

**Given** I am authenticated and have a job posting **When** I POST to
`/api/v1/sessions` with `job_posting_id` **Then** the system validates I own the
job posting **And** creates a new InterviewSession with status='active' and
current_question_number=0 **And** returns 201 Created with the session object
including id, job_posting_id, status, current_question_number, created_at
**And** if the job posting doesn't exist or belongs to another user, returns 404
Not Found

#### Story 4.3: Create Session List Endpoint

**As a** user **I want to** view my interview sessions **So that** I can see
sessions grouped by status (active/paused/completed)

**Acceptance Criteria:**

**Given** I am authenticated **When** I GET `/api/v1/sessions` **Then** the
system returns all my sessions ordered by created_at DESC **And** supports
optional query parameter `status` to filter (active/paused/completed) **And**
each session includes: id, job_posting (with title, company), status,
current_question_number, created_at **And** returns 200 OK with array of
sessions

#### Story 4.4: Create Session Detail Endpoint

**As a** user **I want to** view full details of a specific session **So that**
I can see the context needed to resume or review an interview

**Acceptance Criteria:**

**Given** I am authenticated and have a session **When** I GET
`/api/v1/sessions/{id}` **Then** the system validates I own the session **And**
returns the session with full job_posting details (title, company, description,
tech_stack) and my resume content **And** returns 200 OK **And** if the session
doesn't exist or belongs to another user, returns 404 Not Found

#### Story 4.5: Create Operation Model for Long-Running AI Tasks

**As a** developer **I want to** create an Operation model to track asynchronous
AI operations **So that** we can implement polling patterns for long-running
tasks like question generation

**Acceptance Criteria:**

**Given** I'm implementing async task tracking **When** I create the Operation
model **Then** it includes fields: id (UUID), operation_type (Text -
'question_generation', 'feedback_analysis'), status (enum: 'pending',
'processing', 'completed', 'failed'), result (JSON nullable), error_message
(Text nullable), created_at, updated_at **And** uses snake_case naming with
plural table name **And** timestamps use UTC **And** the model supports querying
by status

#### Story 4.6: Implement OpenAI Service for API Calls

**As a** developer **I want to** create a service layer for OpenAI API calls
**So that** we have centralized error handling and retry logic for AI operations

**Acceptance Criteria:**

**Given** I'm implementing AI integration **When** I create the OpenAI service
class **Then** it loads the API key from encrypted user storage (using Fernet
decryption) **And** implements retry logic with exponential backoff for
transient failures **And** handles rate limiting (429) and server errors (5xx)
gracefully **And** never logs or exposes the raw API key **And** returns
structured responses or raises specific exceptions **And** uses the user's
configured OpenAI API key (not a system-wide key)

#### Story 4.7: Implement Question Generation Service with Dual-Context

**As a** developer **I want to** create a service to generate interview
questions using dual-context **So that** questions are relevant to both the job
requirements and candidate's résumé

**Acceptance Criteria:**

**Given** I'm implementing question generation **When** the service receives a
session context **Then** it fetches the job posting (title, company,
description, tech_stack, experience_level) **And** fetches the user's résumé
content **And** constructs a prompt with both contexts asking for a relevant
interview question **And** rotates question types (technical, behavioral,
situational) based on current_question_number **And** calls OpenAI API (via
OpenAI service) to generate the question **And** returns the generated question
text and question_type **And** handles errors if OpenAI call fails

#### Story 4.8: Create Question Generation Endpoint with Async Pattern

**As a** user **I want to** request a new interview question **So that** I can
progress through the interview session

**Acceptance Criteria:**

**Given** I am authenticated with an active session **When** I POST to
`/api/v1/sessions/{id}/generate-question` **Then** the system validates I own
the session and it's active **And** creates an Operation record with
status='pending' and type='question_generation' **And** returns 202 Accepted
with operation_id immediately **And** starts a background task to generate the
question (using dual-context service) **And** updates the Operation status to
'processing' then 'completed' with result, or 'failed' with error_message
**And** if the session is not active, returns 400 Bad Request

#### Story 4.9: Create Operation Status Polling Endpoint

**As a** user **I want to** poll the status of question generation **So that** I
know when the AI-generated question is ready

**Acceptance Criteria:**

**Given** I have initiated a question generation operation **When** I GET
`/api/v1/operations/{operation_id}` every 2-3 seconds **Then** the system
returns the operation with current status, result (if completed), or
error_message (if failed) **And** returns 200 OK **And** the frontend polls
until status is 'completed' or 'failed' **And** if the operation doesn't exist,
returns 404 Not Found

#### Story 4.10: Store Generated Question as Session Message

**As a** developer **I want to** save successfully generated questions to the
session **So that** we persist the conversation history

**Acceptance Criteria:**

**Given** a question generation operation completes successfully **When** the
background task finishes **Then** it creates a SessionMessage record with
session_id, message_type='question', content=(generated question text),
question_type=(technical/behavioral/situational) **And** increments the
session's current_question_number **And** stores the question text in the
Operation result field **And** uses UTC timestamps

#### Story 4.11: Create Answer Submission Endpoint

**As a** user **I want to** submit my answer to an interview question **So
that** the system records my response for future analysis

**Acceptance Criteria:**

**Given** I am authenticated with an active session and a generated question
**When** I POST to `/api/v1/sessions/{id}/answers` with `answer_text` **Then**
the system validates I own the session **And** creates a SessionMessage record
with message_type='answer' and content=answer_text **And** returns 201 Created
with the message object **And** if the session is not active, returns 400 Bad
Request

#### Story 4.12: Create Session Messages Retrieval Endpoint

**As a** user **I want to** retrieve all messages (Q&A) for a session **So
that** I can review the conversation history

**Acceptance Criteria:**

**Given** I am authenticated and have a session **When** I GET
`/api/v1/sessions/{id}/messages` **Then** the system validates I own the session
**And** returns all SessionMessage records ordered by created_at ASC **And**
each message includes: id, message_type, content, question_type (if applicable),
created_at **And** returns 200 OK with array of messages **And** if the session
doesn't exist or belongs to another user, returns 404 Not Found

#### Story 4.13: Create Session Resume Capability

**As a** user **I want to** resume an interrupted interview session **So that**
I don't lose progress if I close my browser

**Acceptance Criteria:**

**Given** I am authenticated and have an active or paused session **When** I
access the session through `/api/v1/sessions/{id}` **Then** the system returns
the full session context including all previous messages **And** the frontend
can reconstruct the UI state from current_question_number and message history
**And** I can continue from where I left off **And** if I manually pause, the
session status updates to 'paused' **And** paused sessions can be resumed later

#### Story 4.14: Create Session Completion Endpoint

**As a** user **I want to** mark an interview session as complete **So that** it
moves to my completed sessions list

**Acceptance Criteria:**

**Given** I am authenticated with an active or paused session **When** I POST to
`/api/v1/sessions/{id}/complete` **Then** the system validates I own the session
**And** updates the session status to 'completed' **And** returns 200 OK with
the updated session **And** the session no longer appears in my active sessions
**And** appears in completed sessions with all Q&A history preserved

---

### Epic 5: AI-Powered Feedback & Analysis

**Goal:** Provide comprehensive AI-generated feedback analyzing answers across
multiple dimensions with actionable improvement recommendations.

**Covers FRs:** FR37, FR38, FR39, FR40, FR41, FR42, FR43, FR44

**Stories:**

#### Story 5.1: Create Feedback Model

**As a** developer **I want to** create a database model for interview feedback
**So that** we can persist AI-generated analysis results

**Acceptance Criteria:**

**Given** I'm implementing the feedback data layer **When** I create the
InterviewFeedback model **Then** it includes fields: id (UUID), session_id (FK
to InterviewSession, unique one-to-one), technical_accuracy_score (Integer
0-100), communication_clarity_score (Integer 0-100), problem_solving_score
(Integer 0-100), relevance_score (Integer 0-100), overall_score (Integer 0-100),
technical_feedback (Text), communication_feedback (Text),
problem_solving_feedback (Text), relevance_feedback (Text), overall_comments
(Text), knowledge_gaps (JSON array), learning_recommendations (JSON array),
created_at, updated_at **And** uses snake_case naming with plural table name
**And** timestamps use UTC **And** the one-to-one relationship ensures each
session has at most one feedback record

#### Story 5.2: Implement Feedback Analysis Service

**As a** developer **I want to** create a service to analyze answers using
OpenAI **So that** we generate comprehensive multi-dimensional feedback

**Acceptance Criteria:**

**Given** I'm implementing feedback generation **When** the service receives a
completed session **Then** it fetches all Q&A pairs (SessionMessages) for the
session **And** constructs a prompt asking OpenAI to analyze across 4
dimensions: technical accuracy, communication clarity, problem-solving approach,
relevance to job requirements **And** the prompt includes the job posting
context and résumé **And** requests structured JSON output with scores (0-100)
and text feedback for each dimension **And** requests identification of
knowledge gaps and learning recommendations **And** calls OpenAI API (via OpenAI
service) to generate feedback **And** parses the response into structured
feedback data **And** handles errors if OpenAI call fails

#### Story 5.3: Create Feedback Generation Endpoint with Async Pattern

**As a** user **I want to** request AI feedback for a completed interview **So
that** I can understand my performance

**Acceptance Criteria:**

**Given** I am authenticated with a completed session **When** I POST to
`/api/v1/sessions/{id}/generate-feedback` **Then** the system validates I own
the session and it's completed **And** validates feedback doesn't already exist
for this session **And** creates an Operation record with status='pending' and
type='feedback_analysis' **And** returns 202 Accepted with operation_id
immediately **And** starts a background task to generate feedback (using
analysis service) **And** updates the Operation status to 'processing' then
'completed' with result, or 'failed' with error_message **And** if the session
is not completed, returns 400 Bad Request **And** if feedback already exists,
returns 409 Conflict

#### Story 5.4: Store Generated Feedback

**As a** developer **I want to** save successfully generated feedback to the
database **So that** we persist the analysis for future retrieval

**Acceptance Criteria:**

**Given** a feedback generation operation completes successfully **When** the
background task finishes **Then** it creates an InterviewFeedback record with
all dimension scores, feedback text, knowledge_gaps array, and
learning_recommendations array **And** calculates overall_score as the average
of the 4 dimension scores **And** links to the session via session_id **And**
stores the complete feedback in the Operation result field **And** uses UTC
timestamps

#### Story 5.5: Create Feedback Retrieval Endpoint

**As a** user **I want to** view AI-generated feedback for a completed interview
**So that** I can understand my performance across all dimensions

**Acceptance Criteria:**

**Given** I am authenticated and have a completed session with feedback **When**
I GET `/api/v1/sessions/{id}/feedback` **Then** the system validates I own the
session **And** returns the InterviewFeedback record with all dimension scores,
feedback text, overall_score, knowledge_gaps, and learning_recommendations
**And** returns 200 OK **And** if feedback doesn't exist yet, returns 404 Not
Found **And** if the session doesn't exist or belongs to another user, returns
404 Not Found

#### Story 5.6: Create Dimension Scores Display Component

**As a** user **I want to** see visual indicators for each feedback dimension
**So that** I can quickly understand my performance breakdown

**Acceptance Criteria:**

**Given** I'm viewing feedback **When** the frontend receives dimension scores
**Then** it displays 4 separate scores: Technical Accuracy, Communication
Clarity, Problem-Solving Approach, Relevance to Job **And** each score is shown
with a progress bar or visual indicator (0-100) **And** the overall score is
prominently displayed **And** color coding indicates performance level (e.g.,
red <60, yellow 60-79, green ≥80) **And** the UI is responsive and clear

#### Story 5.7: Create Knowledge Gaps Display Component

**As a** user **I want to** see identified knowledge gaps **So that** I know
specific areas where I need improvement

**Acceptance Criteria:**

**Given** I'm viewing feedback **When** the frontend receives knowledge_gaps
array **Then** it displays each gap as a list item or card **And** gaps are
clearly labeled and easy to read **And** if no gaps are identified, displays a
positive message **And** the section is visually distinct from other feedback
areas

#### Story 5.8: Create Learning Recommendations Display Component

**As a** user **I want to** see personalized learning recommendations **So
that** I have actionable next steps for improvement

**Acceptance Criteria:**

**Given** I'm viewing feedback **When** the frontend receives
learning_recommendations array **Then** it displays each recommendation as a
list item or card **And** recommendations are actionable and specific **And** if
no recommendations are provided, displays a general encouragement message
**And** the section is visually distinct and easy to scan

---

### Epic 6: Progress Tracking & Session History

**Goal:** Enable users to track their interview history, view past sessions, and
monitor performance trends over time.

**Covers FRs:** FR45, FR46, FR47, FR48, FR49, FR50, FR51

**Stories:**

#### Story 6.1: Create Session History List View

**As a** user **I want to** view all my completed interview sessions **So that**
I can see my practice history

**Acceptance Criteria:**

**Given** I am authenticated **When** I navigate to the session history page
**Then** the frontend fetches GET `/api/v1/sessions?status=completed` **And**
displays a list of completed sessions ordered by created_at DESC **And** each
item shows: job posting (title, company), completion date, number of questions
answered (derived from current_question_number), and a link to view details
**And** the list is paginated if there are many sessions **And** if no completed
sessions exist, displays an empty state message

#### Story 6.2: Create Session Detail View with Full Q&A History

**As a** user **I want to** view a specific past interview session **So that** I
can review all questions and my answers

**Acceptance Criteria:**

**Given** I am authenticated and have a completed session **When** I view the
session detail page **Then** the frontend fetches GET `/api/v1/sessions/{id}`
and GET `/api/v1/sessions/{id}/messages` **And** displays the job posting
context (title, company, description excerpts) **And** displays all Q&A pairs in
chronological order (questions with my answers) **And** clearly distinguishes
questions from answers visually **And** shows timestamps for each message
**And** includes a link to view feedback (if generated) **And** the view is
read-only (no editing)

#### Story 6.3: Create Performance Metrics Dashboard

**As a** user **I want to** see aggregate statistics about my interviews **So
that** I can track my overall progress

**Acceptance Criteria:**

**Given** I am authenticated with completed sessions **When** I navigate to the
dashboard **Then** the system calculates and displays: total number of completed
interviews, average overall score (across all sessions with feedback), total
questions answered (sum of all current_question_numbers), most practiced job
roles (grouped by job_posting title/company) **And** metrics update
automatically as new sessions/feedback are added **And** if no data exists,
displays appropriate zero-state messages

#### Story 6.4: Implement Score Comparison Across Sessions

**As a** user **I want to** compare scores from different interview sessions
**So that** I can see if I'm improving over time

**Acceptance Criteria:**

**Given** I have multiple completed sessions with feedback **When** I view the
comparison feature **Then** the frontend fetches feedback for all my sessions
**And** displays overall scores in a list or table with session dates **And**
sorts by date to show chronological progression **And** highlights improvements
(score increases) and regressions (score decreases) **And** if fewer than 2
sessions have feedback, displays a message encouraging more practice

#### Story 6.5: Create Score Trends Visualization

**As a** user **I want to** see a visual chart of my score trends **So that** I
can easily understand my improvement trajectory

**Acceptance Criteria:**

**Given** I have completed sessions with feedback **When** I view the trends
chart **Then** the frontend renders a line or bar chart with x-axis as session
dates and y-axis as overall scores (0-100) **And** the chart clearly shows the
trend direction (improving, stable, declining) **And** uses a responsive
charting library (e.g., Recharts, Chart.js) **And** includes tooltips showing
session details on hover **And** if data is insufficient (<2 feedback records),
displays a message instead of an empty chart

#### Story 6.6: Implement Session Filtering by Date Range

**As a** user **I want to** filter my session history by date range **So that**
I can focus on recent or specific time periods

**Acceptance Criteria:**

**Given** I'm viewing session history **When** I select a date range filter
(e.g., last 7 days, last 30 days, custom range) **Then** the frontend re-fetches
sessions with query parameters for date filtering **And** the backend filters
sessions where created_at is within the specified range **And** the filtered
results display correctly **And** the filter state persists during the session
**And** a "clear filter" option resets to show all sessions

#### Story 6.7: Implement Session Filtering by Job Posting

**As a** user **I want to** filter sessions by job posting **So that** I can see
all interviews for a specific role

**Acceptance Criteria:**

**Given** I'm viewing session history **When** I select a job posting filter
(dropdown of my job postings) **Then** the frontend re-fetches sessions with
query parameter `job_posting_id` **And** the backend filters sessions where
job_posting_id matches **And** the filtered results display correctly **And**
the filter state persists during the session **And** a "clear filter" option
resets to show all sessions

---

### Epic 7: Interview Retakes & Improvement Tracking

**Goal:** Enable users to retake interviews for the same job posting and track
improvement over multiple attempts.

**Covers FRs:** FR52, FR53, FR54, FR55, FR56

**Stories:**

#### Story 7.1: Add Retake Tracking Fields to Session Model

**As a** developer **I want to** extend the InterviewSession model for retake
tracking **So that** we can link retakes and track attempt numbers

**Acceptance Criteria:**

**Given** I'm enhancing the session model **When** I add retake tracking fields
**Then** the InterviewSession model includes: retake_number (Integer, default
1), original_session_id (UUID nullable, FK to InterviewSession self-reference)
**And** retake_number indicates which attempt this is (1 = first attempt, 2 =
first retake, etc.) **And** original_session_id points to the very first session
for this job posting (null for original attempts) **And** the database migration
adds these fields with default values for existing sessions **And** uses
snake_case naming conventions

#### Story 7.2: Create Retake Creation Endpoint

**As a** user **I want to** retake an interview for a job posting I've already
practiced **So that** I can improve my performance

**Acceptance Criteria:**

**Given** I am authenticated and have a completed session **When** I POST to
`/api/v1/sessions/{id}/retake` **Then** the system validates I own the session
and it's completed **And** creates a new InterviewSession with the same
job_posting_id, status='active', current_question_number=0 **And** sets
retake_number = (previous session's retake_number + 1) **And** sets
original_session_id = (previous session's original_session_id OR previous
session's id if it was the original) **And** returns 201 Created with the new
session object **And** if the session is not completed, returns 400 Bad Request

#### Story 7.3: Display Retake Information in Session Views

**As a** user **I want to** see retake numbers in my session history **So that**
I can identify which attempt each session represents

**Acceptance Criteria:**

**Given** I'm viewing sessions **When** a session is a retake
(retake_number > 1) **Then** the UI displays a badge or label indicating
"Attempt #X" or "Retake #X" **And** the original session and all its retakes are
visually linked (e.g., grouped or indicated with icons) **And** first attempts
(retake_number = 1) are clearly distinguished from retakes **And** the display
is consistent across session list and detail views

#### Story 7.4: Create Score Comparison Across Retakes

**As a** user **I want to** compare scores across all attempts for the same job
posting **So that** I can see if I'm improving with each retake

**Acceptance Criteria:**

**Given** I have multiple completed sessions for the same job posting with
feedback **When** I view the retake comparison **Then** the frontend fetches all
sessions linked by original_session_id (or with matching original_session_id)
**And** displays scores in chronological order by retake_number **And** shows
score deltas (e.g., +5, -3) between consecutive attempts **And** highlights
improvements in green and regressions in red **And** if only one attempt exists,
displays a message encouraging retakes

#### Story 7.5: Create Dimension-Level Improvement Tracking

**As a** user **I want to** see how each feedback dimension has improved across
retakes **So that** I can identify which skills are getting better

**Acceptance Criteria:**

**Given** I have multiple retakes with feedback **When** I view dimension-level
improvement **Then** the frontend displays a comparison table or chart showing
all 4 dimension scores (Technical Accuracy, Communication Clarity,
Problem-Solving, Relevance) across all attempts **And** each dimension shows the
trend (improving, stable, declining) **And** uses visual indicators (arrows,
color coding) to highlight changes **And** calculates the total improvement
(latest score - first score) for each dimension **And** if data is insufficient,
displays an appropriate message

---

### Epic 8: System Reliability & Error Handling

**Goal:** Ensure robust error handling, security, data isolation, and system
reliability across all features.

**Covers FRs:** FR57, FR58, FR59, FR60, FR61, FR62, FR63, FR64, FR65, FR66  
**Covers NFRs:** All 22 Non-Functional Requirements (NFR1-NFR22)

**Stories:**

#### Story 8.1: Implement Comprehensive OpenAI Integration Error Handling

**As a** developer **I want to** implement robust error handling for OpenAI API
calls **So that** the system gracefully handles all failure scenarios

**Acceptance Criteria:**

**Given** I'm implementing OpenAI integration **When** any OpenAI API call fails
**Then** the system catches and handles: network errors (connection timeout, DNS
failure), authentication errors (401 invalid API key), rate limiting (429),
server errors (5xx), invalid response format, quota exceeded errors **And**
implements exponential backoff retry for transient errors (network, 5xx) with
max 3 retries **And** logs all errors with context (operation type, session id,
error details) without exposing API keys **And** returns user-friendly error
messages **And** updates Operation status to 'failed' with error_message **And**
never crashes or leaves operations in inconsistent state (NFR19, NFR20)

#### Story 8.2: Create User-Friendly Error Messages for AI Failures

**As a** user **I want to** see clear, actionable error messages when AI
operations fail **So that** I understand what went wrong and what to do next

**Acceptance Criteria:**

**Given** an AI operation (question generation or feedback analysis) fails
**When** I check the operation status **Then** the error_message field contains
user-friendly text like "Unable to generate question. Please check your OpenAI
API key configuration." or "Question generation is taking longer than expected.
Please try again." **And** the message avoids technical jargon and API details
**And** provides actionable next steps (e.g., "Check API key", "Try again
later", "Contact support") **And** the frontend displays these messages
prominently **And** the UI provides a retry button where appropriate (FR59,
FR64)

#### Story 8.3: Implement Operation Status Transparency

**As a** user **I want to** always see the current processing status of AI
operations **So that** I know what's happening with my requests

**Acceptance Criteria:**

**Given** I've initiated an AI operation **When** I view the relevant page
(interview session or feedback) **Then** the frontend displays clear status
indicators: "Generating question..." (pending/processing), "Question ready!"
(completed), "Generation failed" (failed) **And** uses visual feedback
(spinners, progress indicators, status badges) **And** the polling mechanism
checks status every 2-3 seconds and updates the UI in real-time **And** the user
never sees stale or unclear states **And** if an operation takes >30 seconds,
displays a message indicating it's still processing (FR58, FR60)

#### Story 8.4: Implement Automatic Retry Logic with User Control

**As a** user **I want to** the system to automatically retry failed AI requests
**And** have the option to manually retry **So that** transient failures are
handled without my intervention

**Acceptance Criteria:**

**Given** an AI operation fails due to a transient error (network timeout, 5xx)
**When** the background task detects the failure **Then** it automatically
retries up to 3 times with exponential backoff (1s, 2s, 4s) **And** if all
retries fail, marks the Operation as 'failed' **And** the user sees a "Retry"
button in the UI **And** clicking Retry initiates a new operation (new
operation_id) **And** the retry attempt is logged **And** users are never
blocked indefinitely by failures (FR61)

#### Story 8.5: Implement Secure API Key Storage and Validation

**As a** developer **I want to** ensure OpenAI API keys are securely stored and
validated **So that** user credentials are protected and functional

**Acceptance Criteria:**

**Given** a user configures their OpenAI API key **When** the key is saved
**Then** it's encrypted using AES-256 (Fernet) before database storage **And**
the encryption key is stored in environment variables (not in code) **And** the
system validates the key format (starts with 'sk-') before encryption **And**
decrypts the key only at runtime when making OpenAI calls **And** the raw key is
never logged or exposed in API responses **And** the database field is encrypted
at rest **And** follows OWASP security best practices (NFR4, NFR5, NFR10, FR62)

#### Story 8.6: Implement Complete Data Isolation Between Users

**As a** developer **I want to** ensure strict data isolation between users **So
that** no user can access another user's data

**Acceptance Criteria:**

**Given** all API endpoints are implemented **When** any endpoint is called
**Then** it uses the `get_current_user` dependency to identify the authenticated
user **And** all database queries filter by user_id (or related user_id via
foreign keys) **And** authorization checks validate ownership before any
read/update/delete operation **And** the system returns 404 Not Found (not 403)
for unauthorized access to hide resource existence **And** SQL queries never
allow cross-user data leakage **And** integration tests verify data isolation
for all endpoints **And** follows OWASP principle of least privilege (NFR3,
NFR10, FR63)

#### Story 8.7: Implement Password Security Best Practices

**As a** developer **I want to** implement secure password handling **So that**
user credentials are protected according to industry standards

**Acceptance Criteria:**

**Given** the authentication system is implemented **When** a user registers or
updates their password **Then** the system validates minimum password
requirements (8+ characters, mix of upper/lower/numbers/symbols recommended but
not enforced for UX) **And** passwords are hashed using bcrypt with cost factor
12 before storage **And** the raw password is never stored or logged **And**
password fields use type='password' in forms **And** password reset uses secure
tokens with expiration **And** brute force protection limits login attempts
**And** follows OWASP password storage guidelines (NFR4, NFR10, FR65)

#### Story 8.8: Implement Session Security with JWT

**As a** developer **I want to** secure user sessions with JWT tokens **So
that** authentication is stateless and secure

**Acceptance Criteria:**

**Given** the authentication system uses JWT **When** a user logs in **Then**
the system generates a JWT with 24-hour expiration using HS256 algorithm **And**
the JWT secret key is stored in environment variables with high entropy
(256-bit) **And** tokens include user_id and expiration claims **And** the
frontend stores tokens in httpOnly cookies (preferred) or localStorage with XSS
protections **And** expired tokens return 401 Unauthorized **And** the
get_current_user dependency validates token signature and expiration on every
request **And** tokens cannot be tampered with or forged **And** follows OWASP
JWT security best practices (NFR4, NFR10, FR66)

#### Story 8.9: Implement API Response Time Performance Standards

**As a** developer **I want to** ensure all API endpoints meet performance
requirements **So that** the user experience is responsive

**Acceptance Criteria:**

**Given** all API endpoints are implemented **When** measuring response times
under normal load **Then** GET endpoints (sessions list, session detail,
feedback retrieval, messages) respond in <300ms **And** POST endpoints (session
creation, answer submission) respond in <500ms **And** Database queries use
proper indexes on foreign keys (user_id, session_id, job_posting_id) **And**
Eager loading (joinedload) is used to avoid N+1 queries **And** Async database
operations (SQLAlchemy async) are used throughout **And** performance tests
validate these thresholds **And** slow queries are logged for optimization
(NFR1, NFR16)

#### Story 8.10: Implement AI Operation Timeout and Resource Management

**As a** developer **I want to** implement timeouts and resource limits for AI
operations **So that** the system remains stable under load

**Acceptance Criteria:**

**Given** AI operations are running **When** processing question generation or
feedback analysis **Then** each OpenAI API call has a 30-second timeout **And**
if timeout is exceeded, the operation is marked as 'failed' with appropriate
error message **And** background tasks have maximum execution time limits (e.g.,
2 minutes) **And** connection pools to OpenAI are properly managed (max
concurrent requests) **And** the system handles concurrent operations gracefully
without resource exhaustion **And** memory usage remains stable during multiple
operations **And** follows NFR16, NFR17, NFR19 for reliability and stability

#### Story 8.11: Implement Frontend Error Boundaries and Fallbacks

**As a** developer **I want to** implement error boundaries in React **So that**
UI errors don't crash the entire application

**Acceptance Criteria:**

**Given** the React frontend is implemented **When** a component throws an error
**Then** an error boundary catches it and displays a fallback UI **And** the
error is logged to the console (and optionally to a logging service) **And** the
user sees a friendly error message with a "Reload" or "Go Home" button **And**
other parts of the application continue to function **And** critical errors
(auth failures, API unavailability) show specific messages **And** the app never
displays a blank screen or crashes completely (NFR21)

#### Story 8.12: Implement Comprehensive Logging and Monitoring

**As a** developer **I want to** implement structured logging throughout the
application **So that** we can diagnose issues and monitor system health

**Acceptance Criteria:**

**Given** the application is running **When** any significant event occurs (user
registration, session creation, AI operation start/complete/fail, errors)
**Then** structured logs are written with timestamp, log level (INFO, WARNING,
ERROR), context (user_id, session_id, operation_id), and message **And**
sensitive data (passwords, API keys, PII) is never logged **And** logs are
written to stdout for container environments **And** log format is JSON for easy
parsing **And** error logs include stack traces **And** logs can be aggregated
and searched for troubleshooting **And** follows NFR21, NFR22 for observability

#### Story 8.13: Implement Database Connection Pooling and Optimization

**As a** developer **I want to** optimize database connections and queries **So
that** the system scales efficiently

**Acceptance Criteria:**

**Given** the application uses PostgreSQL **When** the backend starts **Then**
SQLAlchemy connection pool is configured with min 5, max 20 connections **And**
all database operations use async SQLAlchemy (AsyncSession) **And** proper
indexes exist on all foreign keys and frequently queried fields (user_id,
session_id, status, created_at) **And** complex queries use joins instead of
multiple separate queries **And** database migrations (Alembic) are tested and
reversible **And** connection timeouts and retry logic are configured **And**
the system handles database connection failures gracefully (NFR1, NFR16, NFR19)

#### Story 8.14: Implement CORS and Security Headers

**As a** developer **I want to** configure CORS and security headers **So that**
the application is protected against common web vulnerabilities

**Acceptance Criteria:**

**Given** the FastAPI backend is deployed **When** the application is accessed
**Then** CORS is configured to allow only the frontend origin (not '\*') **And**
security headers are set: X-Content-Type-Options: nosniff, X-Frame-Options:
DENY, Content-Security-Policy with appropriate directives,
Strict-Transport-Security for HTTPS **And** CSRF protection is implemented for
state-changing operations **And** the API rejects requests from unauthorized
origins **And** follows OWASP security headers best practices (NFR5, NFR10)

#### Story 8.15: Implement Input Validation and Sanitization

**As a** developer **I want to** validate and sanitize all user inputs **So
that** the system is protected against injection attacks

**Acceptance Criteria:**

**Given** all API endpoints accept user input **When** a request is received
**Then** Pydantic models validate all input fields (types, required fields,
formats) **And** string inputs are validated for max length to prevent DoS
**And** SQL injection is prevented by using SQLAlchemy ORM (no raw SQL with user
input) **And** XSS is prevented by proper output encoding in the frontend
**And** email format is validated with regex **And** error messages for
validation failures are clear and don't expose system internals **And** follows
OWASP input validation guidelines (NFR5, NFR10)
