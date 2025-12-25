"""
Alembic migration environment configuration.
Configures Alembic to work with SQLAlchemy models and async engine.
"""

from logging.config import fileConfig
from pathlib import Path
import sys

from sqlalchemy import engine_from_config, pool

from alembic import context

# Add the backend directory to Python path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

# Import your SQLAlchemy Base and models
try:
    from app.core.config import settings
    from app.core.database import Base
    import app.models.user  # noqa: F401
    import app.models.resume  # noqa: F401
    import app.models.job_posting  # noqa: F401
    import app.models.interview_session  # noqa: F401
    import app.models.session_message  # noqa: F401
    import app.models.interview_feedback  # noqa: F401
except ImportError as e:
    raise ImportError(
        f"Failed to import required modules: {e}\n"
        "Make sure you're running from the backend directory and "
        "the virtual environment is activated."
    ) from e

# Import all models here to ensure they're registered with Base.metadata
# This is CRITICAL for autogenerate to work correctly
from app.models.job_posting import JobPosting  # noqa: F401
from app.models.interview_session import InterviewSession  # noqa: F401
from app.models.session_message import SessionMessage  # noqa: F401

# Alembic Config object
config = context.config

# Set SQLAlchemy URL from settings (sync URL for Alembic)
try:
    database_url = settings.database_url_sync
    if not database_url:
        raise ValueError("database_url_sync is empty or None")
    config.set_main_option("sqlalchemy.url", database_url)
except Exception as e:
    raise RuntimeError(
        f"Failed to configure database URL: {e}\n"
        "Check your .env file has correct database configuration:\n"
        "  DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD"
    ) from e

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


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
        config.get_section(config.config_ini_section, {}),
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
