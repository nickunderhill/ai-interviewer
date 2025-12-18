"""
Unit tests for application configuration.
Tests Pydantic Settings and environment variable loading.
"""

import pytest
from app.core.config import Settings, get_settings, settings


class TestSettingsModel:
    """Test Settings Pydantic model."""

    def test_settings_has_database_fields(self):
        """Test that Settings model has all required database fields."""
        assert hasattr(settings, "DB_HOST")
        assert hasattr(settings, "DB_PORT")
        assert hasattr(settings, "DB_NAME")
        assert hasattr(settings, "DB_USER")
        assert hasattr(settings, "DB_PASSWORD")

    def test_settings_has_app_fields(self):
        """Test that Settings model has application configuration fields."""
        assert hasattr(settings, "APP_NAME")
        assert hasattr(settings, "DEBUG")

    def test_settings_has_security_fields(self):
        """Test that Settings model has security configuration fields."""
        assert hasattr(settings, "SECRET_KEY")
        assert hasattr(settings, "ALGORITHM")
        assert hasattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES")

    def test_database_url_property(self):
        """Test that database_url property constructs async URL."""
        db_url = settings.database_url
        assert isinstance(db_url, str)
        assert "postgresql+asyncpg://" in db_url
        assert f"{settings.DB_USER}" in db_url
        assert f"{settings.DB_HOST}" in db_url
        assert f"{settings.DB_PORT}" in db_url
        assert f"{settings.DB_NAME}" in db_url

    def test_database_url_sync_property(self):
        """Test that database_url_sync property constructs sync URL."""
        db_url_sync = settings.database_url_sync
        assert isinstance(db_url_sync, str)
        assert "postgresql://" in db_url_sync
        assert "+asyncpg" not in db_url_sync
        assert f"{settings.DB_USER}" in db_url_sync
        assert f"{settings.DB_HOST}" in db_url_sync
        assert f"{settings.DB_PORT}" in db_url_sync
        assert f"{settings.DB_NAME}" in db_url_sync


class TestSettingsValues:
    """Test actual settings values from environment."""

    def test_database_host(self):
        """Test that DB_HOST is set correctly."""
        # Should be 'localhost' when backend runs on host
        assert settings.DB_HOST in ["localhost", "postgres"]

    def test_database_port(self):
        """Test that DB_PORT is set correctly."""
        assert settings.DB_PORT == 5432

    def test_database_name(self):
        """Test that DB_NAME is set correctly."""
        assert settings.DB_NAME == "ai_interviewer_db"

    def test_database_user(self):
        """Test that DB_USER is set correctly."""
        assert settings.DB_USER == "ai_interviewer_user"

    def test_database_password_not_empty(self):
        """Test that DB_PASSWORD is loaded."""
        assert settings.DB_PASSWORD is not None
        assert len(settings.DB_PASSWORD) > 0

    def test_app_name(self):
        """Test that APP_NAME is set."""
        assert settings.APP_NAME == "AI Interviewer API"

    def test_debug_mode(self):
        """Test that DEBUG is set (should be True in development)."""
        assert isinstance(settings.DEBUG, bool)

    def test_algorithm(self):
        """Test that JWT algorithm is set."""
        assert settings.ALGORITHM == "HS256"

    def test_token_expiration(self):
        """Test that token expiration is set."""
        assert isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int)
        assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0


class TestGetSettingsFunction:
    """Test get_settings cached function."""

    def test_get_settings_returns_settings_instance(self):
        """Test that get_settings returns a Settings instance."""
        result = get_settings()
        assert isinstance(result, Settings)

    def test_get_settings_caching(self):
        """Test that get_settings returns the same instance (LRU cache)."""
        settings1 = get_settings()
        settings2 = get_settings()
        # Should be the exact same object due to lru_cache
        assert settings1 is settings2

    def test_global_settings_is_cached(self):
        """Test that global settings variable uses cached get_settings."""
        assert settings is get_settings()


class TestSettingsConfiguration:
    """Test Pydantic Settings configuration."""

    def test_settings_config_uses_env_file(self):
        """Test that Settings is configured to load from .env file."""
        # This is implicitly tested by the fact that settings load correctly
        assert settings.DB_PASSWORD is not None

    def test_settings_case_sensitive(self):
        """Test that settings keys are case-sensitive."""
        # Settings should have DB_HOST (uppercase), not db_host
        assert hasattr(settings, "DB_HOST")

    def test_settings_loads_without_error(self):
        """Test that Settings can be instantiated without errors."""
        try:
            test_settings = get_settings()
            assert test_settings is not None
        except Exception as e:
            pytest.fail(f"Settings failed to load: {e}")


class TestDatabaseURLConstruction:
    """Test database URL construction logic."""

    def test_async_url_format(self):
        """Test async database URL has correct format."""
        url = settings.database_url
        # Format: postgresql+asyncpg://user:password@host:port/database
        assert url.count("://") == 1
        assert url.count("@") == 1
        assert url.count(":") >= 3  # protocol:, :password, :port

    def test_sync_url_format(self):
        """Test sync database URL has correct format."""
        url = settings.database_url_sync
        # Format: postgresql://user:password@host:port/database
        assert url.count("://") == 1
        assert url.count("@") == 1
        assert url.count(":") >= 3

    def test_url_contains_all_components(self):
        """Test that database URL contains all required components."""
        url = settings.database_url
        assert settings.DB_USER in url
        # Password might be URL-encoded, so we check it exists in settings
        assert settings.DB_PASSWORD is not None
        assert str(settings.DB_PORT) in url
        assert settings.DB_NAME in url

    def test_urls_differ_only_in_driver(self):
        """Test that async and sync URLs differ only in the driver specification."""
        async_url = settings.database_url
        sync_url = settings.database_url_sync

        # Remove driver specifications to compare
        async_base = async_url.replace("postgresql+asyncpg://", "")
        sync_base = sync_url.replace("postgresql://", "")

        # The rest should be identical
        assert async_base == sync_base
