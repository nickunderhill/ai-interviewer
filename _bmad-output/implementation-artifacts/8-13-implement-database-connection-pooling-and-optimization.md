# Story 8.13: Implement Database Connection Pooling and Optimization

Status: ready-for-dev

## Story

As a developer, I want to optimize database connections and queries, so that the
system scales efficiently.

## Acceptance Criteria

1. **Given** the application uses PostgreSQL **When** the backend starts
   **Then** SQLAlchemy connection pool is configured with min 5, max 20
   connections **And** all database operations use async SQLAlchemy
   (AsyncSession) **And** proper indexes exist on all foreign keys and
   frequently queried fields (user_id, session_id, status, created_at) **And**
   complex queries use joins instead of multiple separate queries **And**
   database migrations (Alembic) are tested and reversible **And** connection
   timeouts and retry logic are configured **And** the system handles database
   connection failures gracefully (NFR1, NFR16, NFR19) ✅

## Tasks / Subtasks

- [ ] Task 1: Verify SQLAlchemy async engine configuration (AC: #1)

  - [ ] Confirm async engine + AsyncSession are used everywhere
  - [ ] Ensure connection pool parameters: pool_size=5, max_overflow=15
        (total 20)

- [ ] Task 2: Configure connection pool timeouts and recycling (AC: #1)

  - [ ] Add pool_pre_ping=True
  - [ ] Set pool_timeout
  - [ ] Set pool_recycle to avoid stale connections

- [ ] Task 3: Add missing indexes (AC: #1)

  - [ ] user_id FKs indexed
  - [ ] session_id/message_id indexed
  - [ ] status + created_at indexes where used for filtering

- [ ] Task 4: Add graceful DB failure handling (AC: #1)

  - [ ] Catch connection errors at startup with clear logs
  - [ ] Return 503 for DB unavailable

- [ ] Task 5: Add migration reversibility checks (AC: #1)
  - [ ] Ensure new migrations have downgrade
  - [ ] Add CI job or test that applies + downgrades

## Dev Notes

### Critical Architecture Requirements

- SQLAlchemy 2.0 async patterns
- Pool size target: min 5, max 20
- Handle DB outages gracefully

### File Structure

```
backend/app/
└── core/
    └── database.py
backend/tests/
└── test_migrations.py
```

### Implementation Details

**Engine Configuration Example:**

```python
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=5,
    max_overflow=15,
    pool_timeout=30,
    pool_recycle=1800,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
```

**Graceful Failure (startup):**

```python
# backend/app/main.py (startup event)
from sqlalchemy import text

@app.on_event("startup")
async def verify_db():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        logger.error("Database unavailable on startup", exc_info=True)
```

### Testing Requirements

- Verify engine uses pooling settings
- Migration apply + downgrade smoke test

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.13]
- [Source: _bmad-output/project-context.md#SQLAlchemy-Patterns]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Defines pool sizing and reliability defaults
- Adds migration reversibility checks
