# Story 1.7: Set Up GitLab CI/CD Pipeline

Status: ready-for-dev

## Story

As a developer, I want to configure a GitLab CI/CD pipeline with build, test,
lint, and deploy stages, so that code quality is maintained and deployments are
automated.

## Acceptance Criteria

1. **Given** the project is in a GitLab repository **When** I create
   .gitlab-ci.yml with four stages (build, test, lint, deploy) **Then** the
   build stage installs dependencies for frontend and backend

2. **Given** the pipeline is configured **Then** the test stage runs pytest for
   backend tests **And** the lint stage runs Ruff for backend and ESLint for
   frontend

3. **Given** the pipeline stages are defined **Then** the deploy stage builds
   Docker images and pushes to registry (for main branch only) **And** build
   failures prevent progression to later stages **And** the pipeline runs
   automatically on every commit

## Tasks / Subtasks

- [ ] Task 1: Create .gitlab-ci.yml configuration file (AC: #1)

  - [ ] Define four stages: build, test, lint, deploy
  - [ ] Configure Docker-in-Docker service
  - [ ] Define cache strategy for dependencies
  - [ ] Set up global variables for Docker registry

- [ ] Task 2: Configure build stage jobs (AC: #1)

  - [ ] Create build:backend job to install Python dependencies
  - [ ] Create build:frontend job to install Node.js dependencies
  - [ ] Cache node_modules and Python packages
  - [ ] Verify dependency installation succeeds

- [ ] Task 3: Configure test stage jobs (AC: #2)

  - [ ] Create test:backend job with pytest
  - [ ] Configure database service for integration tests
  - [ ] Generate test coverage reports
  - [ ] Fail pipeline if tests fail

- [ ] Task 4: Configure lint stage jobs (AC: #2)

  - [ ] Create lint:backend job with Ruff
  - [ ] Create lint:frontend job with ESLint
  - [ ] Enforce code quality standards
  - [ ] Fail pipeline if linting fails

- [ ] Task 5: Configure deploy stage job (AC: #3)

  - [ ] Create deploy job to build Docker images
  - [ ] Configure Docker registry authentication
  - [ ] Tag images with commit SHA and branch
  - [ ] Push images to GitLab Container Registry
  - [ ] Run only on main branch

- [ ] Task 6: Add pytest configuration and initial tests (AC: #2)

  - [ ] Create pytest.ini or pyproject.toml config
  - [ ] Create basic test for health endpoint
  - [ ] Ensure tests run in isolated environment
  - [ ] Configure test database connection

- [ ] Task 7: Add linting configuration (AC: #2)

  - [ ] Create .ruff.toml for Python linting
  - [ ] Configure ESLint rules in eslint.config.js
  - [ ] Set up automatic formatting rules
  - [ ] Document linting commands in README

- [ ] Task 8: Test pipeline execution (AC: #3)
  - [ ] Commit .gitlab-ci.yml to GitLab repository
  - [ ] Verify pipeline triggers automatically
  - [ ] Check all stages execute in order
  - [ ] Verify stage failures stop pipeline progression
  - [ ] Test branch-specific deploy job

## Dev Notes

### Critical Architecture Requirements

**Technology Stack (from architecture.md & project-context.md):**

- GitLab CI/CD with .gitlab-ci.yml
- Docker-in-Docker for building images
- pytest for backend testing
- Ruff for Python linting
- ESLint for frontend linting
- GitLab Container Registry for Docker images

**CI/CD Pipeline Standards:**

- **Stages**: build → test → lint → deploy
- **Caching**: node_modules, pip cache for faster builds
- **Testing**: Pytest with coverage reporting
- **Linting**: Ruff (backend), ESLint (frontend)
- **Deploy**: Docker images to GitLab registry (main branch only)
- **Failure Handling**: Stop pipeline on any stage failure

### Technical Implementation Details

**Step 1: Create .gitlab-ci.yml**

Create `.gitlab-ci.yml` at project root:

```yaml
# GitLab CI/CD Pipeline Configuration
# Four stages: build, test, lint, deploy

stages:
  - build
  - test
  - lint
  - deploy

# Global variables
variables:
  DOCKER_DRIVER: overlay2
  DOCKER_TLS_CERTDIR: '/certs'
  PIP_CACHE_DIR: '$CI_PROJECT_DIR/.cache/pip'
  npm_config_cache: '$CI_PROJECT_DIR/.cache/npm'
  POSTGRES_DB: ai_interviewer_test_db
  POSTGRES_USER: test_user
  POSTGRES_PASSWORD: test_password
  DB_HOST: postgres
  DB_PORT: 5432

# Cache configuration for faster builds
cache:
  key: ${CI_COMMIT_REF_SLUG}
  paths:
    - .cache/pip
    - .cache/npm
    - frontend/node_modules
    - backend/.venv

# ============================================================================
# BUILD STAGE - Install dependencies
# ============================================================================

build:backend:
  stage: build
  image: python:3.11-slim
  before_script:
    - cd backend
    - python -m venv .venv
    - source .venv/bin/activate
    - pip install --upgrade pip
  script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov pytest-asyncio ruff
  artifacts:
    paths:
      - backend/.venv
    expire_in: 1 hour
  only:
    - branches
    - merge_requests

build:frontend:
  stage: build
  image: node:20-alpine
  before_script:
    - cd frontend
    - npm install -g pnpm
  script:
    - pnpm install --frozen-lockfile
  artifacts:
    paths:
      - frontend/node_modules
    expire_in: 1 hour
  only:
    - branches
    - merge_requests

# ============================================================================
# TEST STAGE - Run automated tests
# ============================================================================

test:backend:
  stage: test
  image: python:3.11-slim
  services:
    - postgres:15-alpine
  variables:
    POSTGRES_DB: ai_interviewer_test_db
    POSTGRES_USER: test_user
    POSTGRES_PASSWORD: test_password
    DB_HOST: postgres
    DB_NAME: ai_interviewer_test_db
    DB_USER: test_user
    DB_PASSWORD: test_password
  before_script:
    - cd backend
    - source .venv/bin/activate
  script:
    - pytest tests/ -v --cov=app --cov-report=term --cov-report=html
  coverage: '/(?i)total.*? (100(?:\.0+)?\%|[1-9]?\d(?:\.\d+)?\%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: backend/coverage.xml
    paths:
      - backend/htmlcov
    expire_in: 1 week
  dependencies:
    - build:backend
  only:
    - branches
    - merge_requests

# Frontend tests (optional for Story 1.7, expanded in later epics)
test:frontend:
  stage: test
  image: node:20-alpine
  before_script:
    - cd frontend
    - npm install -g pnpm
  script:
    - pnpm test --run
  dependencies:
    - build:frontend
  only:
    - branches
    - merge_requests
  allow_failure: true # Optional until tests are fully implemented

# ============================================================================
# LINT STAGE - Code quality checks
# ============================================================================

lint:backend:
  stage: lint
  image: python:3.11-slim
  before_script:
    - cd backend
    - source .venv/bin/activate
  script:
    - ruff check app/ tests/
    - ruff format --check app/ tests/
  dependencies:
    - build:backend
  only:
    - branches
    - merge_requests

lint:frontend:
  stage: lint
  image: node:20-alpine
  before_script:
    - cd frontend
    - npm install -g pnpm
  script:
    - pnpm run lint
  dependencies:
    - build:frontend
  only:
    - branches
    - merge_requests

# ============================================================================
# DEPLOY STAGE - Build and push Docker images
# ============================================================================

deploy:docker:
  stage: deploy
  image: docker:24-dind
  services:
    - docker:24-dind
  before_script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
  script:
    # Build and tag backend image
    - docker build -t $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA -t
      $CI_REGISTRY_IMAGE/backend:latest ./backend
    - docker push $CI_REGISTRY_IMAGE/backend:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE/backend:latest

    # Build and tag frontend image (production build)
    - docker build -f ./frontend/Dockerfile.prod -t
      $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA -t
      $CI_REGISTRY_IMAGE/frontend:latest ./frontend
    - docker push $CI_REGISTRY_IMAGE/frontend:$CI_COMMIT_SHA
    - docker push $CI_REGISTRY_IMAGE/frontend:latest

    # Build and tag full stack compose (optional)
    - docker-compose build
  only:
    - main
  dependencies: []
```

**Key Configuration Decisions:**

1. **Four Stages**: build → test → lint → deploy (sequential execution)
2. **Caching**: pip and npm caches for faster subsequent builds
3. **Artifacts**: Share dependencies between stages
4. **PostgreSQL Service**: For integration tests in test stage
5. **Branch Protection**: deploy only runs on main branch
6. **Docker-in-Docker**: Required for building and pushing images
7. **Coverage Reporting**: pytest generates coverage reports

**Step 2: Create pytest Configuration**

Create `backend/pytest.ini`:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
addopts =
    -v
    --strict-markers
    --tb=short
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-report=xml
markers =
    unit: Unit tests (fast, no external dependencies)
    integration: Integration tests (database, external services)
    slow: Slow tests (skip in development)
```

**Or using pyproject.toml:**

```toml
# backend/pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
asyncio_mode = "auto"
addopts = [
    "-v",
    "--strict-markers",
    "--tb=short",
    "--cov=app",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (database, external services)",
    "slow: Slow tests (skip in development)",
]
```

**Step 3: Create Initial Backend Test**

Update `backend/tests/test_main.py`:

```python
"""
Test suite for main FastAPI application.
Tests root endpoint, health check, and basic functionality.
"""
import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns correct response."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AI Interviewer API"
    assert data["status"] == "running"
    assert "version" in data


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test health check endpoint returns healthy status."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert "api" in data


@pytest.mark.asyncio
async def test_docs_endpoint():
    """Test OpenAPI docs are accessible."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
```

**Create conftest.py for test fixtures:**

```python
# backend/tests/conftest.py
"""
Pytest configuration and fixtures for testing.
"""
import pytest
import asyncio
from typing import Generator, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Create a test database session.
    Uses test database from environment variables.
    """
    # Use test database URL
    test_database_url = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

    engine = create_async_engine(test_database_url, echo=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with async_session() as session:
        yield session

    # Cleanup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
def override_get_db(db_session: AsyncSession):
    """Override get_db dependency to use test database."""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()
```

**Update backend/requirements.txt:**

```txt
# Testing dependencies (add to existing requirements.txt)
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
httpx==0.25.2  # For async HTTP testing

# Linting dependencies
ruff==0.1.8
```

**Step 4: Create Ruff Configuration**

Create `backend/.ruff.toml`:

```toml
# Ruff configuration for Python linting and formatting
# https://docs.astral.sh/ruff/

# Exclude directories
exclude = [
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    "alembic/versions",
    ".pytest_cache",
]

# Line length
line-length = 120

# Python version
target-version = "py311"

[lint]
# Enable rule categories
select = [
    "E",   # pycodestyle errors
    "W",   # pycodestyle warnings
    "F",   # pyflakes
    "I",   # isort
    "N",   # pep8-naming
    "UP",  # pyupgrade
    "B",   # flake8-bugbear
    "C4",  # flake8-comprehensions
    "SIM", # flake8-simplify
]

# Ignore specific rules
ignore = [
    "E501",  # Line too long (handled by formatter)
    "B008",  # Do not perform function call in argument defaults
]

[lint.per-file-ignores]
"__init__.py" = ["F401"]  # Unused imports in __init__.py
"tests/*" = ["S101"]      # Allow assert in tests

[format]
# Use double quotes for strings
quote-style = "double"

# Indent with spaces
indent-style = "space"

# Respect magic trailing comma
skip-magic-trailing-comma = false
```

**Step 5: Verify ESLint Configuration**

Verify `frontend/eslint.config.js` exists (created by Vite):

```javascript
import js from '@eslint/js';
import globals from 'globals';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import tseslint from 'typescript-eslint';

export default tseslint.config(
  { ignores: ['dist'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
    },
    plugins: {
      'react-hooks': reactHooks,
      'react-refresh': reactRefresh,
    },
    rules: {
      ...reactHooks.configs.recommended.rules,
      'react-refresh/only-export-components': [
        'warn',
        { allowConstantExport: true },
      ],
    },
  }
);
```

**Add lint script to frontend/package.json:**

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "lint:fix": "eslint . --ext ts,tsx --fix",
    "test": "vitest"
  }
}
```

**Step 6: Create Production Frontend Dockerfile**

Create `frontend/Dockerfile.prod` for production builds:

```dockerfile
# Stage 1: Build
FROM node:20-alpine AS builder

# Install pnpm
RUN npm install -g pnpm

WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy source code
COPY . .

# Build for production
RUN pnpm run build

# Stage 2: Production
FROM nginx:alpine

# Copy built assets from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration (optional, create if needed)
# COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

**Step 7: Test Pipeline Locally**

```bash
# Install dependencies
cd backend
pip install pytest pytest-cov pytest-asyncio httpx ruff
cd ../frontend
pnpm install

# Run tests locally
cd ../backend
pytest tests/ -v --cov=app

# Expected output:
# tests/test_main.py::test_root_endpoint PASSED
# tests/test_main.py::test_health_endpoint PASSED
# tests/test_main.py::test_docs_endpoint PASSED
# Coverage: 75%

# Run linting locally
ruff check app/ tests/
ruff format --check app/ tests/

# Expected output:
# All checks passed!

cd ../frontend
pnpm run lint

# Expected output:
# No linting errors
```

**Step 8: Push to GitLab and Verify Pipeline**

```bash
# Initialize git (if not already)
git init
git remote add origin <gitlab-repo-url>

# Add and commit CI/CD configuration
git add .gitlab-ci.yml
git add backend/pytest.ini backend/.ruff.toml backend/tests/
git add frontend/Dockerfile.prod
git commit -m "Add GitLab CI/CD pipeline with build, test, lint, deploy stages"

# Push to GitLab
git push -u origin main
```

**View pipeline in GitLab:**

1. Navigate to CI/CD → Pipelines in GitLab UI
2. Click on latest pipeline
3. Verify all stages execute: build → test → lint → deploy
4. Check job logs for any errors

### GitLab CI/CD Best Practices

**Cache Strategy:**

- Cache dependencies (node_modules, pip cache) between pipeline runs
- Use key: ${CI_COMMIT_REF_SLUG} for per-branch caching
- Cache expires after 7 days of inactivity

**Artifacts:**

- Share build artifacts between stages
- Store test coverage reports
- Expire artifacts after 1 week to save storage

**Docker Registry:**

- Tag images with commit SHA for traceability
- Tag with 'latest' for easy deployment
- Only push on main branch to control deployments

**Testing:**

- Run tests with coverage reporting
- Use PostgreSQL service for integration tests
- Allow frontend tests to fail initially (allow_failure: true)

**Security:**

- Never commit secrets or credentials
- Use GitLab CI/CD variables for sensitive data
- Scan Docker images for vulnerabilities (future enhancement)

### Previous Story Learnings

**From Stories 1.1-1.6:**

- Frontend uses pnpm, Vite, React, TypeScript
- Backend uses Python 3.11, FastAPI, SQLAlchemy
- Docker Compose orchestrates all services
- PostgreSQL for database
- Alembic for migrations

**Integration Points:**

- CI/CD pipeline tests all components
- Docker images built from Dockerfiles created in Story 1.6
- Tests use database service like Story 1.3
- Linting enforces patterns from project-context.md

### Common Issues & Solutions

**Issue: Pipeline fails at build:backend with "ModuleNotFoundError"**

- **Cause**: Missing dependency in requirements.txt
- **Solution**: Add pytest, pytest-cov, pytest-asyncio, httpx, ruff
- **Test locally**: `pip install -r requirements.txt`

**Issue: Tests fail with "connection refused" to postgres**

- **Cause**: Database service not accessible or wrong hostname
- **Solution**: Use DB_HOST=postgres in CI variables
- **Verify**: Check services section in test job

**Issue: Docker build fails with "permission denied"**

- **Cause**: Docker-in-Docker not properly configured
- **Solution**: Use docker:24-dind service with docker:24-dind image
- **Check**: DOCKER_TLS_CERTDIR variable set

**Issue: "docker login" fails in deploy stage**

- **Cause**: Missing CI/CD variables for registry access
- **Solution**: GitLab automatically provides CI*REGISTRY*\* variables
- **Verify**: Check Settings → CI/CD → Variables in GitLab

**Issue: Frontend lint fails with "ESLint not found"**

- **Cause**: ESLint not installed or not in package.json
- **Solution**: Ensure eslint in devDependencies
- **Install**: `pnpm add -D eslint`

**Issue: Coverage report not showing in GitLab**

- **Cause**: Coverage regex or report path incorrect
- **Solution**: Verify coverage: regex matches pytest output
- **Check**: artifacts → reports → coverage_report path

**Issue: Deploy stage runs on every branch**

- **Cause**: Missing "only: - main" rule
- **Solution**: Add only: - main to deploy job
- **Verify**: Pipeline should skip deploy on feature branches

### Testing Requirements

**Manual Testing Checklist:**

1. **GitLab CI/CD Configuration**

   - [ ] .gitlab-ci.yml exists and is valid YAML
   - [ ] Four stages defined: build, test, lint, deploy
   - [ ] All jobs assigned to correct stages

2. **Build Stage**

   - [ ] build:backend installs Python dependencies
   - [ ] build:frontend installs Node.js dependencies
   - [ ] Dependencies cached for faster builds
   - [ ] Artifacts shared with subsequent stages

3. **Test Stage**

   - [ ] test:backend runs pytest successfully
   - [ ] PostgreSQL service accessible during tests
   - [ ] Coverage report generated
   - [ ] test:frontend runs (or allowed to fail)

4. **Lint Stage**

   - [ ] lint:backend runs Ruff checks
   - [ ] lint:frontend runs ESLint
   - [ ] Code quality issues detected
   - [ ] Formatting issues detected

5. **Deploy Stage**

   - [ ] deploy:docker builds backend image
   - [ ] deploy:docker builds frontend image
   - [ ] Images pushed to GitLab registry
   - [ ] Only runs on main branch
   - [ ] Images tagged with SHA and latest

6. **Pipeline Execution**

   - [ ] Pipeline triggers on every commit
   - [ ] Pipeline triggers on merge requests
   - [ ] Stages execute sequentially
   - [ ] Failed stage stops pipeline
   - [ ] Success status shown in GitLab

7. **Local Testing**
   - [ ] Backend tests pass: `pytest tests/`
   - [ ] Backend linting passes: `ruff check app/`
   - [ ] Frontend linting passes: `pnpm run lint`
   - [ ] Docker images build: `docker build -t test ./backend`

### Future Considerations

**Enhanced CI/CD (Post-MVP):**

- Security scanning (SAST, dependency scanning)
- Docker image vulnerability scanning
- Automated deployment to staging/production
- Performance testing
- E2E testing with Playwright/Cypress
- Semantic versioning and changelog generation

**Monitoring & Observability:**

- Pipeline performance metrics
- Test flakiness detection
- Code coverage trends over time
- Build time optimization

**Advanced Deployment:**

- Blue-green deployments
- Canary releases
- Automated rollbacks
- Infrastructure as Code (Terraform)

### Project Structure Notes

**Alignment with Architecture:**

- GitLab CI/CD matches architecture requirements
- Four-stage pipeline: build, test, lint, deploy
- Automated testing and quality checks
- Docker image registry integration

**Files Created/Modified:**

```
ai-interviewer/
├── .gitlab-ci.yml              # NEW - CI/CD pipeline configuration
├── backend/
│   ├── pytest.ini              # NEW - Pytest configuration
│   ├── .ruff.toml              # NEW - Ruff linting configuration
│   ├── pyproject.toml          # ALTERNATIVE - Can use instead of pytest.ini
│   ├── requirements.txt        # MODIFIED - Add test/lint dependencies
│   └── tests/
│       ├── conftest.py         # NEW - Pytest fixtures
│       └── test_main.py        # MODIFIED - Add comprehensive tests
├── frontend/
│   ├── Dockerfile.prod         # NEW - Production build Dockerfile
│   ├── package.json            # MODIFIED - Add lint script
│   └── eslint.config.js        # VERIFY - Exists from Vite init
└── README.md                   # MODIFIED - Add CI/CD section
```

**No Conflicts Detected:**

- Pipeline uses existing Dockerfiles from Story 1.6
- Tests use database patterns from Stories 1.3-1.4
- Linting enforces standards from project-context.md
- Epic 1 foundation complete, ready for Epic 2 development

### References

- [Source: _bmad-output/architecture.md - Section "Infrastructure & Deployment -
  CI/CD"]
- [Source: _bmad-output/project-context.md - Testing and quality rules]
- [Source:
  _bmad-output/implementation-artifacts/1-6-configure-docker-compose-for-full-stack-development.md
  - Docker configuration]

## Dev Agent Record

### Agent Model Used

_To be filled by Dev agent during implementation_

### Debug Log References

_To be filled by Dev agent during implementation_

### Completion Notes List

_To be filled by Dev agent during implementation_

- [ ] .gitlab-ci.yml created with four stages
- [ ] backend/pytest.ini or pyproject.toml configured
- [ ] backend/.ruff.toml created
- [ ] backend/tests/test_main.py updated with tests
- [ ] backend/tests/conftest.py created with fixtures
- [ ] backend/requirements.txt updated with test/lint deps
- [ ] frontend/Dockerfile.prod created
- [ ] frontend/package.json has lint script
- [ ] Pipeline pushed to GitLab
- [ ] All stages execute successfully
- [ ] Tests pass in CI
- [ ] Linting passes in CI
- [ ] Docker images build and push on main branch
- [ ] README.md updated with CI/CD instructions

### File List

_To be filled by Dev agent during implementation_

Expected files created/modified:

- `.gitlab-ci.yml` (create)
- `backend/pytest.ini` (create - or use pyproject.toml)
- `backend/.ruff.toml` (create)
- `backend/tests/conftest.py` (create)
- `backend/tests/test_main.py` (modify - add more tests)
- `backend/requirements.txt` (modify - add pytest, ruff, etc.)
- `frontend/Dockerfile.prod` (create)
- `frontend/package.json` (verify lint script)
- `README.md` (modify - add CI/CD section)
