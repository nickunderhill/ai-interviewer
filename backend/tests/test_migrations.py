import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from app.core.config import settings
import os

# Use sync URL for alembic
ALEMBIC_DB_URL = settings.database_url_sync


@pytest.fixture
def alembic_config():
    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", ALEMBIC_DB_URL)
    return config


def test_migrations_up_and_down(alembic_config):
    """
    Test that migrations can be applied and rolled back.
    This ensures reversibility (AC #1).
    """
    # Upgrade to head
    command.upgrade(alembic_config, "head")

    # Downgrade to base (or -1)
    # We'll downgrade one step to verify the latest migration is reversible
    command.downgrade(alembic_config, "-1")

    # Upgrade back to head to leave DB in good state
    command.upgrade(alembic_config, "head")
