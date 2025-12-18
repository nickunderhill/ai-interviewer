# Story 1.5: Set Up Alembic for Database Migrations

Status: ready-for-dev

## Story

As a developer, I want to configure Alembic for database migrations, so that
schema changes can be version-controlled and applied consistently across
environments.

## Acceptance Criteria

1. **Given** SQLAlchemy is configured and connected to PostgreSQL **When** I
   initialize Alembic with `alembic init alembic` **Then** an alembic/ directory
   is created with env.py and versions/ folder

2. **Given** Alembic is initialized **Then** alembic.ini is configured with the
   database connection string **And** env.py is configured to use async engine
   and import all models

3. **Given** Alembic is configured **Then** I can generate migrations with
   `alembic revision --autogenerate` **And** I can apply migrations with
   `alembic upgrade head` **And** migrations are tracked in the alembic_version
   table

## Tasks / Subtasks

- [ ] Task 1: Initialize Alembic in backend directory (AC: #1)

  - [ ] Navigate to backend directory
  - [ ] Run `alembic init alembic` command
  - [ ] Verify alembic/ directory created with env.py and versions/ folder
  - [ ] Verify alembic.ini configuration file created

- [ ] Task 2: Configure alembic.ini with database connection (AC: #2)

  - [ ] Update sqlalchemy.url to use environment variables
  - [ ] Set script_location to alembic directory
  - [ ] Configure file_template for migration naming
  - [ ] Set timezone to UTC

- [ ] Task 3: Configure env.py for async SQLAlchemy and model imports (AC: #2)

  - [ ] Import Base from app.core.database
  - [ ] Import settings for database URL
  - [ ] Set target_metadata = Base.metadata
  - [ ] Configure async engine for migrations
  - [ ] Import all model files to ensure metadata discovery

- [ ] Task 4: Create initial migration (test setup) (AC: #3)

  - [ ] Create empty test table migration: `alembic revision -m "initial"`
  - [ ] Edit migration file to add simple test table
  - [ ] Apply migration: `alembic upgrade head`
  - [ ] Verify alembic_version table created
  - [ ] Verify test table created in database

- [ ] Task 5: Test autogenerate functionality (AC: #3)

  - [ ] Create a simple model in app/models/test.py
  - [ ] Generate migration:
        `alembic revision --autogenerate -m "add test model"`
  - [ ] Review generated migration for correctness
  - [ ] Apply migration: `alembic upgrade head`
  - [ ] Verify table created from model

- [ ] Task 6: Test migration rollback (AC: #3)

  - [ ] Rollback one migration: `alembic downgrade -1`
  - [ ] Verify table removed from database
  - [ ] Reapply migration: `alembic upgrade head`
  - [ ] Clean up test model and migration files

- [ ] Task 7: Document migration workflow (AC: #3)
  - [ ] Create README section for Alembic usage
  - [ ] Document common commands (init, revision, upgrade, downgrade)
  - [ ] Document workflow for creating new models

## Dev Notes

### Critical Architecture Requirements

**Technology Stack (from architecture.md & project-context.md):**

- Alembic (latest stable version, installed in Story 1.2)
- SQLAlchemy 2.0+ with async support
- PostgreSQL connection via sync driver for Alembic
- Auto-generate migrations from model metadata
- UTC timestamps for all migrations

**Migration Configuration Standards:**

- **Migrations Directory**: `backend/alembic/versions/`
- **Config File**: `backend/alembic.ini`
- **Environment Script**: `backend/alembic/env.py`
- **Connection**: Sync PostgreSQL URL (psycopg2)
- **Naming Convention**: `{revision}_{description}.py`
- **Auto-generate**: Use `--autogenerate` for model-based migrations

### Technical Implementation Details

**Step 1: Initialize Alembic**

```bash
# From backend directory
cd backend
source venv/bin/activate

# Initialize Alembic (creates alembic/ directory and alembic.ini)
alembic init alembic

# Expected output:
# Creating directory /path/to/backend/alembic ... done
# Creating directory /path/to/backend/alembic/versions ... done
# Generating /path/to/backend/alembic/script.py.mako ... done
# Generating /path/to/backend/alembic/env.py ... done
# Generating /path/to/backend/alembic.ini ... done
# Please edit configuration/connection/logging settings in '/path/to/backend/alembic.ini' before proceeding.
```

**Expected Directory Structure:**

```
backend/
├── alembic/
│   ├── versions/           # Migration files stored here
│   ├── env.py             # Migration environment configuration
│   ├── script.py.mako     # Migration template
│   └── README             # Alembic documentation
├── alembic.ini            # Alembic configuration file
├── app/
│   └── ...
```

**Step 2: Configure alembic.ini**

Edit `backend/alembic.ini`:

```ini
# alembic.ini

[alembic]
# Path to migration scripts
script_location = alembic

# Template used to generate migration files
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d_%%(rev)s_%%(slug)s

# Timezone for migration timestamps
timezone = UTC

# Database connection URL
# IMPORTANT: Use sync URL (postgresql://) not async (postgresql+asyncpg://)
# Alembic runs in sync mode
sqlalchemy.url = postgresql://%(DB_USER)s:%(DB_PASSWORD)s@%(DB_HOST)s:%(DB_PORT)s/%(DB_NAME)s

[post_write_hooks]
# Hooks for formatting generated migrations (optional)

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**Key Configuration Notes:**

1. **file_template**: Uses timestamp format for migration files
   (YYYYMMDD_HHMM_revision_description.py)
2. **sqlalchemy.url**: Uses sync postgresql:// (not postgresql+asyncpg://)
3. **timezone**: Set to UTC for consistency
4. **script_location**: Points to alembic/ directory

**Step 3: Configure env.py for Async SQLAlchemy**

Replace `backend/alembic/env.py` with:

```python
"""
Alembic migration environment configuration.
Configures Alembic to work with SQLAlchemy models and async engine.
"""
from logging.config import fileConfig
import os
import sys
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy import engine_from_config

from alembic import context

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Import your SQLAlchemy Base and models
from app.core.config import settings
from app.core.database import Base

# Import all models here to ensure they're registered with Base.metadata
# This is CRITICAL for autogenerate to work correctly
# Uncomment and add as you create models in Epic 2+:
# from app.models.user import User
# from app.models.session import InterviewSession
# from app.models.job_posting import JobPosting
# from app.models.message import SessionMessage
# from app.models.feedback import Feedback

# Alembic Config object
config = context.config

# Set SQLAlchemy URL from settings (sync URL for Alembic)
config.set_main_option("sqlalchemy.url", settings.database_url_sync)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine,
    though an Engine is acceptable here as well. By skipping the Engine
    creation we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario we need to create an Engine and associate a
    connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

**Key Implementation Notes:**

1. **Python Path**: Adds backend directory to sys.path for imports
2. **Settings Import**: Uses settings.database_url_sync for sync connection
3. **Base Import**: Imports Base from app.core.database
4. **Model Imports**: Placeholder comments for future model imports (Epic 2+)
5. **target_metadata**: Set to Base.metadata for autogenerate
6. **Compare Options**: Enables type and server default comparison

**Step 4: Test Alembic Setup with Initial Migration**

```bash
# Create initial empty migration
alembic revision -m "initial setup"

# Expected output:
# Generating /path/to/backend/alembic/versions/20251218_1030_abc123_initial_setup.py ... done
```

Edit the generated migration file to test:

```python
"""initial setup

Revision ID: abc123
Revises:
Create Date: 2025-12-18 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abc123'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial test table."""
    op.create_table(
        'alembic_test',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop test table."""
    op.drop_table('alembic_test')
```

**Apply the migration:**

```bash
# Apply migration
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> abc123, initial setup

# Verify migration applied
docker-compose exec postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "\dt"

# Expected output shows:
# - alembic_version table (tracks current migration)
# - alembic_test table (from our test migration)
```

**Step 5: Test Autogenerate Functionality**

Create a test model:

```python
# app/models/test_model.py (temporary, for testing)
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.core.database import Base

class TestModel(Base):
    __tablename__ = "test_models"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
```

Import the model in env.py:

```python
# In alembic/env.py, add to model imports:
from app.models.test_model import TestModel
```

Generate migration automatically:

```bash
# Autogenerate migration from model
alembic revision --autogenerate -m "add test model"

# Expected output:
# INFO  [alembic.autogenerate.compare] Detected added table 'test_models'
# Generating /path/to/backend/alembic/versions/20251218_1035_def456_add_test_model.py ... done
```

Review the generated migration:

```python
"""add test model

Revision ID: def456
Revises: abc123
Create Date: 2025-12-18 10:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'def456'
down_revision: Union[str, None] = 'abc123'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Autogenerated - review before applying!
    op.create_table('test_models',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_test_models_id'), 'test_models', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_test_models_id'), table_name='test_models')
    op.drop_table('test_models')
```

Apply the autogenerated migration:

```bash
# Apply migration
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, add test model

# Verify table created
docker-compose exec postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "\d test_models"

# Should show test_models table structure
```

**Step 6: Test Migration Rollback**

```bash
# Check current migration version
alembic current

# Expected output:
# def456 (head)

# Rollback one migration
alembic downgrade -1

# Expected output:
# INFO  [alembic.runtime.migration] Running downgrade def456 -> abc123, add test model

# Verify table removed
docker-compose exec postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "\dt"

# test_models table should be gone

# Reapply migration
alembic upgrade head

# Roll back to base (remove all migrations)
alembic downgrade base

# Expected output:
# INFO  [alembic.runtime.migration] Running downgrade abc123 -> , initial setup

# All tables removed except alembic_version (which is also removed)
```

**Step 7: Clean Up Test Files**

```bash
# Delete test migration files
rm alembic/versions/*_initial_setup.py
rm alembic/versions/*_add_test_model.py

# Delete test model file
rm app/models/test_model.py

# Reset database (if needed)
docker-compose exec postgres psql -U ai_interviewer_user -d ai_interviewer_db -c "DROP TABLE IF EXISTS alembic_version, alembic_test, test_models;"
```

### Common Alembic Commands Reference

```bash
# Initialize Alembic
alembic init alembic

# Create new migration manually
alembic revision -m "description"

# Create migration with autogenerate (from models)
alembic revision --autogenerate -m "description"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base

# Show current migration version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose

# Generate SQL for migration (don't apply)
alembic upgrade head --sql
```

### Previous Story Learnings

**From Story 1.2 (Backend Setup):**

- Backend structure with app/core/, app/models/ directories
- Alembic already installed in requirements.txt
- Python virtual environment in venv/

**From Story 1.3 (PostgreSQL Docker Compose):**

- PostgreSQL running in Docker container
- Database: ai_interviewer_db
- User: ai_interviewer_user
- Connection available via localhost:5432

**From Story 1.4 (SQLAlchemy Integration):**

- app/core/database.py has Base declarative base
- app/core/config.py has settings with database_url_sync property
- Async SQLAlchemy configured for application
- Alembic will use sync connection (database_url_sync)

**Integration Points:**

- Alembic uses settings.database_url_sync (postgresql://)
- Application uses settings.database_url (postgresql+asyncpg://)
- Alembic imports Base from app.core.database
- Epic 2 will create first real models (User) using Alembic migrations

### Common Issues & Solutions

**Issue: "ImportError: cannot import name 'Base'" when running alembic**

- **Cause**: Python path not configured correctly in env.py
- **Solution**: Ensure sys.path.insert(0, str(backend_dir)) in env.py
- **Verify**: Run `python -c "from app.core.database import Base; print('OK')"`

**Issue: "No changes detected" when running autogenerate**

- **Cause**: Models not imported in env.py
- **Solution**: Import all model classes in env.py before setting
  target_metadata
- **Example**: `from app.models.user import User`

**Issue: "password authentication failed" when running migrations**

- **Cause**: Incorrect database credentials
- **Solution**: Verify .env variables match PostgreSQL configuration
- **Check**: settings.database_url_sync uses correct credentials

**Issue: "relation 'alembic_version' does not exist"**

- **Cause**: Alembic not initialized in database
- **Solution**: Run `alembic upgrade head` to create alembic_version table
- **Note**: This is expected on first run

**Issue: "Target database is not up to date"**

- **Cause**: Database schema doesn't match current migration head
- **Solution**: Run `alembic upgrade head` to apply pending migrations
- **Check**: `alembic current` to see current version

**Issue: "Can't locate revision identified by 'head'"**

- **Cause**: No migrations created yet
- **Solution**: Create first migration with `alembic revision -m "initial"`
- **Note**: This is expected in new projects

### Testing Requirements

**Manual Testing Checklist:**

1. **Alembic Initialization**

   - [ ] alembic/ directory created
   - [ ] alembic.ini file exists
   - [ ] env.py configured correctly
   - [ ] versions/ directory empty (no migrations yet)

2. **Configuration**

   - [ ] alembic.ini has correct sqlalchemy.url format
   - [ ] env.py imports Base from app.core.database
   - [ ] env.py imports settings from app.core.config
   - [ ] target_metadata = Base.metadata in env.py

3. **Manual Migration Creation**

   - [ ] Can create migration: `alembic revision -m "test"`
   - [ ] Migration file created in versions/
   - [ ] Can apply migration: `alembic upgrade head`
   - [ ] alembic_version table created in database

4. **Autogenerate Functionality**

   - [ ] Create test model in app/models/
   - [ ] Import model in env.py
   - [ ] Run `alembic revision --autogenerate -m "test model"`
   - [ ] Migration file detects model changes
   - [ ] Apply migration creates table correctly

5. **Migration Rollback**

   - [ ] Can rollback: `alembic downgrade -1`
   - [ ] Changes reversed in database
   - [ ] Can reapply: `alembic upgrade head`
   - [ ] Changes reapplied correctly

6. **Command Verification**
   - [ ] `alembic current` shows current version
   - [ ] `alembic history` shows migration history
   - [ ] `alembic upgrade head --sql` generates SQL without applying

### Future Considerations

**Dependencies for Upcoming Stories:**

- **Story 1.6**: Docker Compose will mount alembic/ directory for
  container-based migrations
- **Epic 2, Story 2.1**: Will create first real migration for User model
- **All Future Epics**: Every new model requires Alembic migration

**Production Considerations:**

- **Backup Before Migrations**: Always backup production database before running
  migrations
- **Review Autogenerated Migrations**: Always review autogenerated code before
  applying
- **Test Rollback**: Ensure downgrade() works correctly for all migrations
- **Migration Naming**: Use descriptive names that explain what changed
- **Data Migrations**: Separate schema and data migrations for complex changes

**Best Practices:**

- **One Logical Change per Migration**: Don't mix unrelated schema changes
- **Always Test Rollback**: Ensure downgrade() reverses upgrade() correctly
- **Review Before Apply**: Check autogenerated migrations for correctness
- **Commit Migrations**: Commit migration files to version control
- **Document Complex Migrations**: Add comments for non-obvious changes

### Project Structure Notes

**Alignment with Architecture:**

- Alembic standard tool for SQLAlchemy migrations
- Sync connection for Alembic, async for application
- UTC timestamps for all migrations
- Autogenerate from model metadata

**Files Created/Modified:**

```
backend/
├── alembic/                    # NEW - Alembic directory
│   ├── versions/               # NEW - Migration files directory (empty initially)
│   ├── env.py                  # NEW - Migration environment (configured)
│   ├── script.py.mako          # NEW - Migration template
│   └── README                  # NEW - Alembic documentation
├── alembic.ini                 # NEW - Alembic configuration
├── app/
│   ├── core/
│   │   ├── config.py           # Already has database_url_sync property
│   │   └── database.py         # Already has Base for models
│   └── models/                 # Ready for model definitions (Epic 2+)
└── README.md                   # MODIFIED - Add Alembic usage section
```

**No Conflicts Detected:**

- Story 1.4 created database connection, this adds migration layer
- Base already defined in database.py
- settings.database_url_sync already available for Alembic
- Ready for Epic 2 model creation

**Integration Preview (Epic 2, Story 2.1 - User Model):**

```python
# app/models/user.py (to be created in Epic 2)
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Then generate migration:
# alembic revision --autogenerate -m "create users table"
# alembic upgrade head
```

### References

- [Source: _bmad-output/architecture.md - Section "Data Architecture - Database
  Migrations"]
- [Source: _bmad-output/project-context.md - Database patterns]
- [Source:
  _bmad-output/implementation-artifacts/1-4-integrate-backend-with-database-using-sqlalchemy.md
  - SQLAlchemy setup]

## Dev Agent Record

### Agent Model Used

_To be filled by Dev agent during implementation_

### Debug Log References

_To be filled by Dev agent during implementation_

### Completion Notes List

_To be filled by Dev agent during implementation_

- [ ] Alembic initialized with `alembic init alembic`
- [ ] alembic.ini configured with database URL format
- [ ] env.py configured to import Base and settings
- [ ] Initial test migration created and applied
- [ ] Test model migration generated with autogenerate
- [ ] Migration rollback tested successfully
- [ ] Test files cleaned up
- [ ] README updated with Alembic commands
- [ ] alembic_version table exists in database

### File List

_To be filled by Dev agent during implementation_

Expected files created/modified:

- `backend/alembic/` (directory - create)
- `backend/alembic/env.py` (create and configure)
- `backend/alembic/versions/` (directory - create)
- `backend/alembic.ini` (create and configure)
- `backend/README.md` (modify - add Alembic section)
