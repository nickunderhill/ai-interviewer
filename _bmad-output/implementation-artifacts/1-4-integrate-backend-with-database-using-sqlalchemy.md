# Story 1.4: Integrate Backend with Database using SQLAlchemy

Status: ready-for-dev

## Story

As a developer, I want to configure SQLAlchemy 2.0+ with async support to
connect to PostgreSQL, so that the backend can perform database operations using
the ORM.

## Acceptance Criteria

1. **Given** PostgreSQL is running via Docker Compose **When** I configure
   database.py in app/core/ with async SQLAlchemy engine and session factory
   **Then** the backend successfully connects to PostgreSQL on startup

2. **Given** the database connection is configured **Then** a get_db dependency
   function provides database sessions to API endpoints **And** the connection
   uses the async engine with proper connection pooling (5-20 connections)

3. **Given** database sessions are configured **Then** database connections are
   properly closed after each request **And** the backend startup logs confirm
   successful database connection

## Tasks / Subtasks

- [ ] Task 1: Verify PostgreSQL is running and accessible (AC: #1)

  - [ ] Ensure PostgreSQL container is running: `docker-compose ps`
  - [ ] Verify connection from host:
        `psql -h localhost -p 5432 -U ai_interviewer_user`
  - [ ] Confirm environment variables are set in .env

- [ ] Task 2: Install additional Python dependencies (AC: #1)

  - [ ] Add asyncpg to requirements.txt (async PostgreSQL driver)
  - [ ] Add greenlet to requirements.txt (required for SQLAlchemy async)
  - [ ] Install dependencies: `pip install -r requirements.txt`
  - [ ] Verify installations: `pip list | grep -E 'asyncpg|greenlet'`

- [ ] Task 3: Create configuration module with database settings (AC: #1)

  - [ ] Create `app/core/config.py` with Pydantic Settings
  - [ ] Load database credentials from environment variables
  - [ ] Construct async database URL (postgresql+asyncpg://)
  - [ ] Configure logging and debug settings

- [ ] Task 4: Create database connection module (AC: #1, #2)

  - [ ] Create `app/core/database.py`
  - [ ] Configure async SQLAlchemy engine with connection pooling
  - [ ] Create async session factory (AsyncSession)
  - [ ] Define base class for ORM models (declarative_base)
  - [ ] Set pool size: min 5, max 20 connections

- [ ] Task 5: Implement get_db dependency for FastAPI (AC: #2, #3)

  - [ ] Create async get_db() function that yields database sessions
  - [ ] Ensure proper session cleanup with try/finally
  - [ ] Handle connection errors gracefully
  - [ ] Add type hints for dependency injection

- [ ] Task 6: Add database initialization to FastAPI app (AC: #1, #3)

  - [ ] Update `app/main.py` with startup event
  - [ ] Test database connection on application startup
  - [ ] Log successful connection or error details
  - [ ] Add graceful shutdown to close engine

- [ ] Task 7: Create health check endpoint (AC: #3)

  - [ ] Create `/health` endpoint that tests database connectivity
  - [ ] Return success response if database is reachable
  - [ ] Return error response with details if connection fails
  - [ ] Test endpoint: `curl http://localhost:8000/health`

- [ ] Task 8: Verify database integration (AC: #1, #2, #3)
  - [ ] Start backend server: `uvicorn app.main:app --reload`
  - [ ] Check startup logs for "Database connected successfully"
  - [ ] Test health endpoint returns 200 OK
  - [ ] Verify connection pool created with correct settings
  - [ ] Test session cleanup by checking connection count

## Dev Notes

### Critical Architecture Requirements

**Technology Stack (from architecture.md & project-context.md):**

- SQLAlchemy 2.0+ with async support
- asyncpg driver for PostgreSQL async operations
- Pydantic Settings v2 for configuration management
- Connection pooling: 5-20 connections
- Async/await pattern throughout
- Type hints for all functions

**Database Configuration Standards:**

- **Connection URL Format**:
  `postgresql+asyncpg://user:password@host:port/database`
- **Engine Configuration**: Async engine with connection pooling
- **Session Factory**: AsyncSession for dependency injection
- **Connection Pool**: min=5, max=20, pool_recycle=3600
- **Isolation Level**: Default (READ COMMITTED)
- **Echo SQL**: False in production, optional True in development

### Technical Implementation Details

**Step 1: Update requirements.txt**

Add these dependencies to `backend/requirements.txt`:

```txt
# Already installed from Story 1.2:
# fastapi==0.108.0
# uvicorn[standard]==0.25.0
# sqlalchemy==2.0.23
# pydantic==2.5.3
# pydantic-settings==2.1.0
# python-dotenv==1.0.0

# NEW - Add these for async PostgreSQL support:
asyncpg==0.29.0       # Async PostgreSQL driver (if not already present)
greenlet==3.0.3       # Required for SQLAlchemy async (if not already present)
```

Then install:

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Step 2: Create app/core/config.py**

```python
"""
Application configuration using Pydantic Settings.
Loads environment variables and provides typed configuration.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    DB_HOST: str = "postgres"
    DB_PORT: int = 5432
    DB_NAME: str = "ai_interviewer_db"
    DB_USER: str = "ai_interviewer_user"
    DB_PASSWORD: str

    # Application Configuration
    APP_NAME: str = "AI Interviewer API"
    DEBUG: bool = False

    # Security Configuration (to be used in Epic 2)
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
        extra="ignore"
    )

    @property
    def database_url(self) -> str:
        """Construct async PostgreSQL connection URL."""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def database_url_sync(self) -> str:
        """Construct sync PostgreSQL connection URL (for Alembic migrations)."""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Uses lru_cache to avoid reading .env file multiple times.
    """
    return Settings()


# Global settings instance
settings = get_settings()
```

**Key Implementation Notes:**

1. **Pydantic Settings v2**: Uses `SettingsConfigDict` (new v2 syntax)
2. **Type Hints**: All fields properly typed for IDE support
3. **Environment Variables**: Automatically loads from `.env` file
4. **Async URL Property**: Uses `postgresql+asyncpg://` for async operations
5. **Sync URL Property**: Provides sync URL for Alembic migrations (Story 1.5)
6. **LRU Cache**: Settings loaded once and cached for performance
7. **Security Defaults**: SECRET_KEY included for future Epic 2 authentication

**Step 3: Create app/core/database.py**

```python
"""
Database connection and session management using SQLAlchemy async.
Provides async engine, session factory, and dependency injection for FastAPI.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url,
    echo=settings.DEBUG,  # Log SQL queries in debug mode
    pool_size=5,          # Minimum number of connections
    max_overflow=15,      # Maximum connections beyond pool_size (total max = 20)
    pool_recycle=3600,    # Recycle connections after 1 hour
    pool_pre_ping=True,   # Verify connections before using
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for ORM models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that provides database sessions to FastAPI routes.

    Usage in FastAPI endpoint:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            ...

    Yields:
        AsyncSession: Database session for the request

    Ensures:
        - Session is properly closed after request
        - Connections are returned to the pool
        - Errors are handled gracefully
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """
    Initialize database connection on application startup.
    Tests connectivity and logs success/failure.
    """
    try:
        # Test database connection
        async with engine.begin() as conn:
            # Execute simple query to verify connection
            await conn.run_sync(lambda sync_conn: sync_conn.execute("SELECT 1"))

        logger.info("✓ Database connected successfully")
        logger.info(f"✓ Connection URL: {settings.database_url.split('@')[1]}")  # Log without credentials
        logger.info(f"✓ Pool size: 5-20 connections")

    except Exception as e:
        logger.error(f"✗ Database connection failed: {str(e)}")
        raise


async def close_db() -> None:
    """
    Close database connection on application shutdown.
    Ensures all connections are properly closed.
    """
    await engine.dispose()
    logger.info("✓ Database connections closed")
```

**Key Implementation Notes:**

1. **Async Engine**: Uses `create_async_engine` with `postgresql+asyncpg://`
2. **Connection Pooling**:
   - `pool_size=5`: Always keep 5 connections ready
   - `max_overflow=15`: Can create up to 15 additional connections (total 20)
   - `pool_recycle=3600`: Recycle connections hourly to avoid stale connections
   - `pool_pre_ping=True`: Test connection validity before use
3. **Session Factory**: `async_sessionmaker` creates async sessions
4. **expire_on_commit=False**: Objects remain accessible after commit
5. **get_db Dependency**: Yields session, ensures cleanup with try/finally
6. **init_db Function**: Tests connection on startup, logs success/failure
7. **close_db Function**: Properly disposes engine on shutdown

**Step 4: Update app/main.py**

```python
"""
FastAPI application entry point.
Configures API, middleware, and lifecycle events.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.core.config import settings
from app.core.database import init_db, close_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered mock interview system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    Initializes database connection and performs health checks.
    """
    logger.info(f"Starting {settings.APP_NAME}")
    await init_db()
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    Closes database connections gracefully.
    """
    logger.info("Shutting down application")
    await close_db()
    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint - basic health check."""
    return {
        "message": "AI Interviewer API",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    Verifies database connectivity and application status.
    """
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal

    try:
        # Test database connection
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            db_status = "connected"
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        db_status = f"error: {str(e)}"

    return {
        "status": "healthy" if db_status == "connected" else "unhealthy",
        "database": db_status,
        "api": "operational"
    }
```

**Key Implementation Notes:**

1. **Startup Event**: Calls `init_db()` to test connection and log status
2. **Shutdown Event**: Calls `close_db()` to gracefully close connections
3. **CORS Middleware**: Configured for Vite dev server on port 5173
4. **Health Endpoint**: Tests actual database query execution
5. **Logging**: Structured logs for debugging and monitoring
6. **Error Handling**: Health check catches exceptions and reports status

**Step 5: Update .env file**

Ensure your `.env` file (in backend directory) contains:

```env
# Database Configuration
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ai_interviewer_db
DB_USER=ai_interviewer_user
DB_PASSWORD=dev_password_change_in_production

# Application Configuration
DEBUG=true
SECRET_KEY=dev-secret-key-change-in-production

# Note: When running backend outside Docker, use:
# DB_HOST=localhost
```

**Step 6: Verification Steps**

```bash
# 1. Ensure PostgreSQL is running
docker-compose ps

# Expected output: postgres container shows "Up" status

# 2. Start backend server
cd backend
source venv/bin/activate
uvicorn app.main:app --reload

# Expected startup logs:
# INFO:     Will watch for changes in these directories: ['/path/to/backend']
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
# INFO:     Started server process
# INFO:     Waiting for application startup.
# INFO:     Starting AI Interviewer API
# INFO:     ✓ Database connected successfully
# INFO:     ✓ Connection URL: postgres:5432/ai_interviewer_db
# INFO:     ✓ Pool size: 5-20 connections
# INFO:     Application startup complete
# INFO:     Application startup complete.

# 3. Test root endpoint
curl http://localhost:8000/

# Expected response:
# {"message":"AI Interviewer API","status":"running","version":"1.0.0"}

# 4. Test health check endpoint
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","database":"connected","api":"operational"}

# 5. Test OpenAPI docs
# Open browser: http://localhost:8000/docs
# Should see Swagger UI with root and health endpoints
```

### Database Connection from Backend Container vs Host

**Important Context:**

- **Story 1.4 (this story)**: Backend runs on **host machine** (not in Docker)
  - Use `DB_HOST=localhost` in `.env`
  - Connect to `localhost:5432`
- **Story 1.6**: Backend will run **inside Docker container**
  - Use `DB_HOST=postgres` in `.env`
  - Connect via Docker network using service name

**Current Configuration for Story 1.4:**

```env
# .env - Backend running on host
DB_HOST=localhost  # Use localhost when backend not in Docker
DB_PORT=5432
DB_NAME=ai_interviewer_db
DB_USER=ai_interviewer_user
DB_PASSWORD=dev_password_change_in_production
```

**Future Configuration for Story 1.6:**

```env
# .env - Backend running in Docker
DB_HOST=postgres  # Use service name when backend in Docker
DB_PORT=5432
DB_NAME=ai_interviewer_db
DB_USER=ai_interviewer_user
DB_PASSWORD=dev_password_change_in_production
```

### Previous Story Learnings

**From Story 1.1 (Frontend Setup):**

- Frontend uses pnpm for package management
- Runs on port 5173 (Vite default)
- TypeScript strict mode enabled

**From Story 1.2 (Backend Setup):**

- Backend structure: `app/api`, `app/core`, `app/models`, `app/schemas`,
  `app/services`
- Python 3.11+ with virtual environment
- FastAPI with uvicorn development server
- Requirements.txt includes SQLAlchemy 2.0.23

**From Story 1.3 (PostgreSQL Docker Compose):**

- PostgreSQL 15-alpine running in Docker
- Service name: `postgres`
- Port: 5432
- Database: `ai_interviewer_db`
- User: `ai_interviewer_user`
- Named volume: `postgres_data` for persistence
- Health check configured with `pg_isready`

**Integration Points:**

- Backend now connects to PostgreSQL database
- Connection string format:
  `postgresql+asyncpg://user:password@host:port/database`
- Async sessions ready for Epic 2 (User authentication, models)
- Story 1.5 will add Alembic migrations using this database connection
- Story 1.6 will containerize backend and update connection to use `postgres`
  hostname

### Common Issues & Solutions

**Issue: "Cannot connect to database" on startup**

- **Cause**: PostgreSQL container not running or wrong DB_HOST
- **Solution 1**: Verify PostgreSQL is running: `docker-compose ps`
- **Solution 2**: Check DB_HOST in .env:
  - Use `localhost` when backend runs on host
  - Use `postgres` when backend runs in Docker (Story 1.6)
- **Solution 3**: Test connection manually:
  `psql -h localhost -p 5432 -U ai_interviewer_user`

**Issue: "ModuleNotFoundError: No module named 'asyncpg'"**

- **Cause**: asyncpg not installed
- **Solution**: Install dependencies: `pip install -r requirements.txt`
- **Verify**: `pip list | grep asyncpg`

**Issue: "greenlet.error: cannot switch to a different thread"**

- **Cause**: Missing greenlet package (required for SQLAlchemy async)
- **Solution**: Install greenlet: `pip install greenlet`
- **Verify**: `pip list | grep greenlet`

**Issue: "sqlalchemy.exc.OperationalError: password authentication failed"**

- **Cause**: Incorrect database credentials in .env
- **Solution**: Verify POSTGRES_PASSWORD in docker-compose.yml matches
  DB_PASSWORD in .env
- **Reset**: Stop PostgreSQL, remove volume, restart fresh:
  ```bash
  docker-compose down -v
  docker-compose up -d postgres
  ```

**Issue: "Connection pool is full"**

- **Cause**: Too many concurrent requests or sessions not being closed
- **Solution**:
  - Verify get_db() properly closes sessions with async context manager
  - Check max pool size configuration (currently 20)
  - Monitor active connections: `SELECT count(*) FROM pg_stat_activity;`

**Issue: "asyncio event loop is closed"**

- **Cause**: Trying to use async operations outside async context
- **Solution**: Ensure all database operations use `async`/`await`
- **Check**: Functions using database should be `async def`, not `def`

### Testing Requirements

**Manual Testing Checklist:**

1. **Database Connection**

   - [ ] Backend starts without errors
   - [ ] Startup logs show "Database connected successfully"
   - [ ] No error messages in terminal

2. **Endpoints**

   - [ ] Root endpoint returns JSON: `curl http://localhost:8000/`
   - [ ] Health endpoint returns healthy status:
         `curl http://localhost:8000/health`
   - [ ] OpenAPI docs accessible: http://localhost:8000/docs

3. **Connection Pool**

   - [ ] Backend logs show "Pool size: 5-20 connections"
   - [ ] Check PostgreSQL connections:
     ```bash
     docker-compose exec postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "SELECT count(*) FROM pg_stat_activity WHERE datname='ai_interviewer_db';"
     ```
   - [ ] Connection count should be 5-6 (pool_size + 1 for monitoring)

4. **Session Management**

   - [ ] Multiple requests don't exhaust connection pool
   - [ ] Test with:
         `for i in {1..50}; do curl http://localhost:8000/health & done; wait`
   - [ ] All requests should succeed

5. **Error Handling**

   - [ ] Stop PostgreSQL: `docker-compose stop postgres`
   - [ ] Health endpoint returns unhealthy status
   - [ ] Backend doesn't crash
   - [ ] Restart PostgreSQL: `docker-compose start postgres`
   - [ ] Health endpoint returns healthy status again

6. **Hot Reload**
   - [ ] Edit app/main.py (add comment)
   - [ ] Uvicorn auto-reloads
   - [ ] Database connection re-established after reload

### Future Considerations

**Dependencies for Upcoming Stories:**

- **Story 1.5 (Alembic)**: Will use `settings.database_url_sync` for migrations
- **Story 1.6 (Docker Compose Full Stack)**: Backend will run in container,
  change DB_HOST to `postgres`
- **Epic 2 (Authentication)**: Will create first ORM models inheriting from
  `Base`
- **Epic 2+**: All endpoints will use `db: AsyncSession = Depends(get_db)` for
  database access

**Production Considerations (Post-MVP):**

- Increase pool size based on load testing
- Configure connection pool timeout settings
- Add connection retry logic with exponential backoff
- Implement read replicas for scaling (separate engine for reads)
- Monitor connection pool metrics (active, idle, overflow)
- Configure statement timeout to prevent long-running queries

**Security Considerations:**

- Never log database passwords (already handled in init_db)
- Use environment-specific credentials (different for dev/prod)
- Rotate database passwords regularly in production
- Configure SSL/TLS for database connections in production

### Project Structure Notes

**Alignment with Architecture:**

- SQLAlchemy 2.0+ with async support matches architecture requirements
- Connection pooling (5-20) matches architecture specification
- Pydantic Settings v2 for configuration matches tech stack
- Async/await pattern throughout matches modern Python best practices
- Dependency injection pattern matches FastAPI standards

**Files Created/Modified:**

```
backend/
├── app/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # NEW - Pydantic Settings configuration
│   │   └── database.py     # NEW - SQLAlchemy async engine and session
│   └── main.py             # MODIFIED - Added startup/shutdown events, health endpoint
├── requirements.txt        # MODIFIED - Added asyncpg, greenlet (if not present)
└── .env                    # MODIFIED - Added DB_HOST=localhost for host-based backend
```

**No Conflicts Detected:**

- Story 1.2 created the backend structure, this story adds database integration
- Story 1.3 created PostgreSQL, this story connects to it
- get_db() dependency pattern will be used by all future endpoints
- Base class ready for model definitions in Epic 2

**Integration Preview (Story 1.5 - Alembic):**

```python
# alembic/env.py will use:
from app.core.config import settings
from app.core.database import Base

# Migration configuration:
config.set_main_option("sqlalchemy.url", settings.database_url_sync)
target_metadata = Base.metadata
```

**Integration Preview (Epic 2 - First Model):**

```python
# app/models/user.py
from sqlalchemy import Column, Integer, String, DateTime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    # ... more fields
```

**Integration Preview (Epic 2 - First Endpoint):**

```python
# app/api/v1/endpoints/users.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/users")
async def get_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users
```

### References

- [Source: _bmad-output/architecture.md - Section "Data Architecture"]
- [Source: _bmad-output/architecture.md - Section "Core Architectural
  Decisions"]
- [Source: _bmad-output/project-context.md - Technology Stack & Versions]
- [Source:
  _bmad-output/implementation-artifacts/1-2-initialize-backend-fastapi-project-structure.md
  - Backend structure]
- [Source:
  _bmad-output/implementation-artifacts/1-3-configure-postgresql-database-with-docker-compose.md
  - PostgreSQL connection details]

## Dev Agent Record

### Agent Model Used

_To be filled by Dev agent during implementation_

### Debug Log References

_To be filled by Dev agent during implementation_

### Completion Notes List

_To be filled by Dev agent during implementation_

- [ ] asyncpg and greenlet added to requirements.txt and installed
- [ ] app/core/config.py created with Pydantic Settings
- [ ] app/core/database.py created with async engine and session factory
- [ ] app/main.py updated with startup/shutdown events
- [ ] /health endpoint created and tested
- [ ] Backend starts successfully with database connection
- [ ] Startup logs show successful connection
- [ ] Health check returns healthy status
- [ ] Connection pool configured with 5-20 connections
- [ ] get_db dependency ready for future endpoints

### File List

_To be filled by Dev agent during implementation_

Expected files created/modified:

- `backend/app/core/config.py` (create)
- `backend/app/core/database.py` (create)
- `backend/app/core/__init__.py` (verify exists)
- `backend/app/main.py` (modify - add startup/shutdown, health endpoint)
- `backend/requirements.txt` (modify - add asyncpg, greenlet if missing)
- `backend/.env` (verify - DB_HOST=localhost for host-based backend)
