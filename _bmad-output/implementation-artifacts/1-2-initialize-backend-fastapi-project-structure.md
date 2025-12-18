# Story 1.2: Initialize Backend FastAPI Project Structure

Status: review

## Story

As a developer, I want to set up the FastAPI backend with the complete project
structure defined in the architecture, so that I have organized directories for
all backend components following architectural patterns.

## Acceptance Criteria

1. **Given** I have Python 3.11+ installed **When** I create the backend
   directory with subdirectories (app/api, app/core, app/models, app/schemas,
   app/services, app/utils) **Then** the complete backend structure per
   architecture document exists

2. **Given** the backend directory structure is created **When** I install
   FastAPI and core dependencies (SQLAlchemy, Pydantic v2, psycopg2-binary,
   python-jose, passlib, cryptography) **Then** all dependencies are listed in
   requirements.txt and installed in a virtual environment

3. **Given** dependencies are installed **When** I create a basic main.py
   FastAPI app and start it with `uvicorn app.main:app --reload` **Then** the
   server starts successfully without errors

4. **Given** the FastAPI server is running **When** I navigate to
   http://localhost:8000/docs **Then** I can access the auto-generated
   OpenAPI/Swagger documentation interface

## Tasks / Subtasks

- [x] Task 1: Verify Python 3.11+ installation (AC: #1)

  - [ ] Check Python version: `python3 --version` or `python --version`
  - [ ] Ensure pip is available: `pip3 --version`

- [x] Task 2: Create backend directory structure (AC: #1)

  - [ ] Create `/backend` directory at project root
  - [ ] Create subdirectories following architecture:
    - [ ] `backend/app/` (main application package)
    - [ ] `backend/app/api/v1/endpoints/` (API route handlers)
    - [ ] `backend/app/core/` (configuration, security, database)
    - [ ] `backend/app/models/` (SQLAlchemy ORM models)
    - [ ] `backend/app/schemas/` (Pydantic request/response schemas)
    - [ ] `backend/app/services/` (business logic layer)
    - [ ] `backend/app/utils/` (utility functions)
    - [ ] `backend/tests/` (pytest test suite)
  - [ ] Create `__init__.py` files to make directories Python packages

- [x] Task 3: Create requirements.txt with dependencies (AC: #2)

  - [ ] Add FastAPI with uvicorn
  - [ ] Add SQLAlchemy 2.0+ with asyncpg
  - [ ] Add Pydantic v2
  - [ ] Add database drivers (psycopg2-binary)
  - [ ] Add security libraries (python-jose, passlib[bcrypt], cryptography)
  - [ ] Pin versions for reproducibility

- [x] Task 4: Set up Python virtual environment (AC: #2)

  - [ ] Create virtual environment: `python3 -m venv venv`
  - [ ] Activate: `source venv/bin/activate` (macOS/Linux)
  - [ ] Install dependencies: `pip install -r requirements.txt`
  - [ ] Verify installation: `pip list`

- [x] Task 5: Create basic FastAPI application (AC: #3)

  - [ ] Create `backend/app/main.py` with FastAPI instance
  - [ ] Add basic root endpoint for health check
  - [ ] Configure CORS middleware for frontend integration
  - [ ] Set API version prefix `/api/v1`

- [x] Task 6: Verify server startup and API docs (AC: #3, #4)
  - [ ] Start server: `uvicorn app.main:app --reload` from backend directory
  - [ ] Verify startup logs show no errors
  - [ ] Access http://localhost:8000 (root endpoint)
  - [ ] Access http://localhost:8000/docs (Swagger UI)
  - [ ] Access http://localhost:8000/redoc (ReDoc alternative)
  - [ ] Verify hot reload works (edit main.py, server auto-restarts)

## Dev Notes

### Critical Architecture Requirements

**Technology Stack (from project-context.md & architecture.md):**

- Python 3.11+ with type hints and async/await
- FastAPI - API framework with automatic OpenAPI docs
- SQLAlchemy 2.0+ with async support (asyncpg driver)
- Pydantic v2 - data validation and schemas
- Alembic - database migrations (Story 1.5)
- python-jose - JWT implementation
- passlib[bcrypt] - password hashing (12 rounds)
- cryptography - API key encryption (Fernet/AES-256)

**Project Structure Standards (STRICT):**

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/         # API route handlers (future stories)
│   │       │   └── __init__.py
│   │       └── router.py          # API router aggregation (future)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # Settings and configuration (future)
│   │   ├── security.py            # Auth utilities (Epic 2)
│   │   └── database.py            # DB connection (Story 1.4)
│   ├── models/                    # SQLAlchemy ORM models (Epic 2+)
│   │   └── __init__.py
│   ├── schemas/                   # Pydantic request/response schemas (Epic 2+)
│   │   └── __init__.py
│   ├── services/                  # Business logic layer (Epic 2+)
│   │   └── __init__.py
│   └── utils/                     # Utility functions (as needed)
│       └── __init__.py
├── tests/                         # Pytest test suite (Epic 8)
│   └── __init__.py
├── alembic/                       # Database migrations (Story 1.5)
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template (future)
└── README.md                      # Backend documentation (optional)
```

### Technical Implementation Details

**Step 1: Verify Python Installation**

```bash
python3 --version  # Should be 3.11 or higher
pip3 --version     # Verify pip is available
```

**Step 2: Create Directory Structure**

```bash
# From project root
mkdir -p backend/app/api/v1/endpoints
mkdir -p backend/app/core
mkdir -p backend/app/models
mkdir -p backend/app/schemas
mkdir -p backend/app/services
mkdir -p backend/app/utils
mkdir -p backend/tests

# Create __init__.py files to make them Python packages
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/api/v1/endpoints/__init__.py
touch backend/app/core/__init__.py
touch backend/app/models/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/services/__init__.py
touch backend/app/utils/__init__.py
touch backend/tests/__init__.py
```

**Step 3: Create requirements.txt**

Create `backend/requirements.txt` with:

```txt
# Web Framework
fastapi==0.108.0
uvicorn[standard]==0.25.0

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0
psycopg2-binary==2.9.9
alembic==1.13.1

# Data Validation
pydantic==2.5.3
pydantic-settings==2.1.0

# Security
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
cryptography==41.0.7
python-multipart==0.0.6

# Utilities
python-dotenv==1.0.0
```

**Notes on versions:**

- Use stable versions that are production-ready
- FastAPI 0.108+ includes Pydantic v2 support
- SQLAlchemy 2.0+ required for modern async patterns
- asyncpg is the async PostgreSQL driver
- psycopg2-binary for sync operations (used by Alembic)

**Step 4: Set Up Virtual Environment**

```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate (macOS/Linux)
source venv/bin/activate

# Activate (Windows)
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
pip list | grep sqlalchemy
```

**Step 5: Create Basic FastAPI Application**

Create `backend/app/main.py`:

```python
"""
FastAPI Application Entry Point
ai-interviewer - Interview Practice Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="ai-interviewer API",
    description="AI-powered interview practice platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware configuration for frontend integration
# TODO: Update origins in production with specific frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
async def root():
    """
    Root endpoint - API health check
    """
    return {
        "status": "ok",
        "message": "ai-interviewer API is running",
        "version": "0.1.0"
    }

@app.get("/api/v1/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint
    Returns API status and version
    """
    return {
        "status": "healthy",
        "version": "0.1.0",
        "api_prefix": "/api/v1"
    }
```

**Key points:**

- FastAPI instance with automatic OpenAPI doc generation
- CORS configured for Vite dev server (localhost:5173)
- Two health check endpoints: `/` and `/api/v1/health`
- Async functions throughout (required for SQLAlchemy async later)
- Clear docstrings for auto-generated documentation
- Version tracking for API versioning

**Step 6: Start and Verify Server**

```bash
# From backend directory with venv activated
uvicorn app.main:app --reload

# Server should start on http://127.0.0.1:8000
# --reload enables hot reload for development
```

**Verification checklist:**

- [x] Server starts without errors
- [x] Console shows: "Application startup complete"
- [x] Console shows: "Uvicorn running on http://127.0.0.1:8000"
- [x] Access http://localhost:8000 → JSON response with status
- [x] Access http://localhost:8000/docs → Swagger UI loads
- [x] Swagger UI shows two endpoints: GET `/` and GET `/api/v1/health`
- [x] Try both endpoints in Swagger UI - both return 200 OK
- [x] Edit main.py (add a comment) → server auto-reloads
- [x] Access http://localhost:8000/redoc → ReDoc UI loads

### Naming Conventions (CRITICAL)

From project-context.md, MUST follow these rules:

- Python variables/functions: `snake_case`
- Python classes: `PascalCase`
- Database tables: `plural_snake_case` (e.g., `users`, `interview_sessions`)
- Database columns: `snake_case` (e.g., `created_at`, `user_id`)
- API endpoints: lowercase with hyphens (e.g., `/api/v1/job-postings`)

### Common Issues & Solutions

**Issue: Python 3.11+ not available**

- Solution: Install Python 3.11 or 3.12 via official installer, Homebrew
  (macOS), or system package manager
- Check: `python3.11 --version`

**Issue: pip not found**

- Solution: Install pip: `python3 -m ensurepip --upgrade`

**Issue: Virtual environment activation fails**

- Solution (macOS/Linux): Ensure correct path `source venv/bin/activate`
- Solution (Windows): Use `venv\Scripts\activate`
- Verify active: `which python` should show venv path

**Issue: psycopg2-binary installation fails**

- Solution: Install system dependencies first (macOS: `brew install postgresql`)
- Alternative: Use `psycopg2` instead (requires PostgreSQL dev headers)

**Issue: Port 8000 already in use**

- Solution: Specify different port: `uvicorn app.main:app --reload --port 8001`
- Or kill process using port 8000

**Issue: Module not found when starting uvicorn**

- Solution: Ensure you're in `backend/` directory
- Verify `app/__init__.py` exists
- Check virtual environment is activated

**Issue: CORS errors when testing from frontend**

- Solution: Verify `allow_origins` includes frontend URL
- For development: `allow_origins=["http://localhost:5173"]`
- Ensure `allow_credentials=True` is set

### Testing Requirements

**Manual Testing:**

1. Server startup test:

   - Start server with `uvicorn app.main:app --reload`
   - Check console for startup messages
   - No errors or warnings should appear

2. Health check tests:

   - GET http://localhost:8000 → 200 OK with JSON
   - GET http://localhost:8000/api/v1/health → 200 OK with JSON
   - Verify response structure matches expected format

3. API documentation tests:

   - Access http://localhost:8000/docs → Swagger UI loads
   - Verify title: "ai-interviewer API"
   - Verify version: "0.1.0"
   - Test each endpoint via "Try it out" button
   - Access http://localhost:8000/redoc → ReDoc alternative loads

4. Hot reload test:

   - Edit `main.py` (add a comment)
   - Console should show "Detected file change"
   - Server auto-restarts
   - Endpoints still work after reload

5. CORS test (requires frontend running):
   - Start frontend on localhost:5173
   - Make API call from frontend console
   - Verify no CORS errors in browser console

**Automated Testing (Optional for this story, required in Epic 8):**

- pytest test file in `backend/tests/test_main.py`
- Test health check endpoints
- Test CORS headers

### Future Considerations

**Dependencies to Add in Future Stories:**

- **Story 1.4**: Database models will use SQLAlchemy async patterns
- **Story 1.5**: Alembic for migrations (already in requirements.txt)
- **Epic 2**: JWT authentication with python-jose, passlib
- **Epic 4**: OpenAI API client (openai package)
- **Epic 8**: Testing with pytest, coverage

**Configuration Management (Story 1.4+):**

- Create `.env` file for environment variables
- Use pydantic-settings for configuration management
- Store: DATABASE_URL, SECRET_KEY, CORS_ORIGINS

**DO NOT implement these now** - they'll be added in subsequent stories.

### Project Structure Notes

**Alignment with Architecture:**

- Backend structure exactly matches architecture.md specification
- FastAPI provides automatic OpenAPI documentation (NFR-M4)
- Async support built-in for future database operations (NFR-P1)
- CORS configured for frontend integration
- Modular structure supports future testing (NFR-M3)

**Preparation for Future Stories:**

- Empty directories ready for models, schemas, services
- API versioning structure (`/api/v1/`) prepared
- Configuration module location defined (`core/config.py`)
- Database module location defined (`core/database.py`)

**No Conflicts Detected:**

- Backend is independent from frontend (Story 1.1)
- Will integrate with Docker Compose in Story 1.6
- Will connect to PostgreSQL in Story 1.4

### References

- [Source: _bmad-output/architecture.md - Section "2. Technology Stack
  Selection" - Backend Structure]
- [Source: _bmad-output/architecture.md - Section "5. API Architecture & Service
  Design"]
- [Source: _bmad-output/project-context.md - Section "Technology Stack &
  Versions" - Backend Stack]
- [Source: _bmad-output/project-context.md - Section "Database & Backend
  Patterns"]
- [Source: _bmad-output/epics.md - Epic 1, Story 1.2]
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Documentation](https://docs.sqlalchemy.org/en/20/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/latest/)

## Dev Agent Record

### Agent Model Used

Claude Sonnet 4.5 (Dev Agent - BMM)

### Debug Log References

- Python 3.12.7 verified (exceeds 3.11+ requirement)
- Backend directory structure created with mkdir -p and touch commands
- Virtual environment created successfully with python3 -m venv
- All dependencies installed successfully (FastAPI 0.108.0, SQLAlchemy 2.0.23, etc.)
- FastAPI server started successfully on http://localhost:8000
- Root endpoint and health check endpoint verified working
- .gitignore created to exclude venv and Python artifacts

### Completion Notes List

- [x] Backend directory structure created successfully
- [x] All **init**.py files present
- [x] requirements.txt created with correct dependencies
- [x] Virtual environment created and activated
- [x] Dependencies installed without errors
- [x] main.py created with FastAPI application
- [x] Server starts successfully with uvicorn
- [x] Health check endpoints working
- [x] OpenAPI docs accessible at /docs
- [x] ReDoc accessible at /redoc
- [x] Hot reload verified working
- [x] CORS configured for frontend
- [x] No import errors or warnings

### File List

_Expected files created by this story:_

```
backend/
├── .gitignore
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           └── __init__.py
│   ├── core/
│   │   └── __init__.py
│   ├── models/
│   │   └── __init__.py
│   ├── schemas/
│   │   └── __init__.py
│   ├── services/
│   │   └── __init__.py
│   └── utils/
│       └── __init__.py
├── tests/
│   └── __init__.py
├── requirements.txt
└── venv/  (virtual environment - excluded by .gitignore)
```

**Implementation Notes:**
- Python 3.12.7 used (exceeds 3.11+ requirement)
- FastAPI 0.108.0 with Pydantic v2 support
- SQLAlchemy 2.0.23 with async support
- All dependencies pinned for reproducibility
- CORS configured for frontend at http://localhost:5173
- Server runs on default port 8000
- .gitignore added to exclude venv and Python artifacts

---

**Story Context Completeness:** ✅ Comprehensive

- All acceptance criteria documented with BDD format
- Complete directory structure specified
- requirements.txt with all dependencies and versions
- Step-by-step virtual environment setup
- Full main.py implementation provided
- Detailed verification checklist
- Common issues and solutions documented
- Architecture alignment verified
- Future dependencies clearly noted (to prevent premature additions)
- Testing procedures defined
- CORS configuration for frontend integration

**Ready for Dev Agent Implementation**
