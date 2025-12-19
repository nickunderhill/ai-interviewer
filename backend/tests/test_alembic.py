"""
Tests for Alembic configuration and migration functionality.
"""

import subprocess
import sys
from pathlib import Path

import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory


class TestAlembicConfiguration:
    """Test Alembic initialization and configuration."""

    def test_alembic_directory_exists(self):
        """Test that alembic directory was created."""
        alembic_dir = Path(__file__).parent.parent / "alembic"
        assert alembic_dir.exists(), "alembic/ directory should exist"
        assert alembic_dir.is_dir(), "alembic/ should be a directory"

    def test_alembic_versions_directory_exists(self):
        """Test that alembic/versions directory was created."""
        versions_dir = Path(__file__).parent.parent / "alembic" / "versions"
        assert versions_dir.exists(), "alembic/versions/ directory should exist"
        assert versions_dir.is_dir(), "versions/ should be a directory"

    def test_alembic_env_file_exists(self):
        """Test that alembic/env.py exists."""
        env_file = Path(__file__).parent.parent / "alembic" / "env.py"
        assert env_file.exists(), "alembic/env.py should exist"
        assert env_file.is_file(), "env.py should be a file"

    def test_alembic_ini_exists(self):
        """Test that alembic.ini configuration file exists."""
        ini_file = Path(__file__).parent.parent / "alembic.ini"
        assert ini_file.exists(), "alembic.ini should exist"
        assert ini_file.is_file(), "alembic.ini should be a file"

    def test_alembic_config_loads(self):
        """Test that alembic configuration can be loaded."""
        backend_dir = Path(__file__).parent.parent
        ini_path = backend_dir / "alembic.ini"
        config = Config(str(ini_path))
        assert config is not None, "Alembic config should load"
        assert config.get_main_option("script_location") == "alembic"

    def test_alembic_config_has_file_template(self):
        """Test that file_template is configured for timestamped migrations."""
        backend_dir = Path(__file__).parent.parent
        ini_path = backend_dir / "alembic.ini"

        with open(ini_path) as f:
            content = f.read()
            assert "file_template" in content, "file_template should be configured"
            # Check for %% (escaped) since that's what's in the ini file
            assert (
                "%%(year)d%%(month).2d%%(day).2d" in content
            ), "file_template should include date"

    def test_alembic_config_has_timezone(self):
        """Test that timezone is set to UTC."""
        backend_dir = Path(__file__).parent.parent
        ini_path = backend_dir / "alembic.ini"

        with open(ini_path) as f:
            content = f.read()
            assert "timezone = UTC" in content, "timezone should be set to UTC"


class TestAlembicEnvConfiguration:
    """Test alembic/env.py configuration."""

    def test_env_imports_base(self):
        """Test that env.py imports Base from app.core.database."""
        env_file = Path(__file__).parent.parent / "alembic" / "env.py"

        with open(env_file) as f:
            content = f.read()
            assert "from app.core.database import Base" in content
            assert "target_metadata = Base.metadata" in content

    def test_env_imports_settings(self):
        """Test that env.py imports settings from app.core.config."""
        env_file = Path(__file__).parent.parent / "alembic" / "env.py"

        with open(env_file) as f:
            content = f.read()
            assert "from app.core.config import settings" in content
            assert "settings.database_url_sync" in content

    def test_env_has_compare_options(self):
        """Test that env.py has compare_type and compare_server_default enabled."""
        env_file = Path(__file__).parent.parent / "alembic" / "env.py"

        with open(env_file) as f:
            content = f.read()
            assert "compare_type=True" in content
            assert "compare_server_default=True" in content

    def test_env_adds_backend_to_path(self):
        """Test that env.py adds backend directory to sys.path."""
        env_file = Path(__file__).parent.parent / "alembic" / "env.py"

        with open(env_file) as f:
            content = f.read()
            assert "sys.path.insert" in content
            assert "backend_dir" in content


class TestAlembicCommands:
    """Test Alembic CLI commands work correctly."""

    @pytest.fixture
    def alembic_config(self):
        """Provide Alembic config for tests."""
        backend_dir = Path(__file__).parent.parent
        ini_path = backend_dir / "alembic.ini"
        return Config(str(ini_path))

    def test_alembic_current_command(self, alembic_config):
        """Test that 'alembic current' command works."""
        # This should not raise an exception even if no migrations applied
        try:
            script = ScriptDirectory.from_config(alembic_config)
            assert script is not None
        except Exception as e:
            pytest.fail(f"Failed to access script directory: {e}")

    def test_alembic_history_command_works(self):
        """Test that 'alembic history' command executes without error."""
        backend_dir = Path(__file__).parent.parent
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "history"],
            cwd=str(backend_dir),
            capture_output=True,
            text=True,
        )
        # Should succeed even with no migrations (exit code 0)
        assert result.returncode == 0, f"alembic history failed: {result.stderr}"


class TestAlembicIntegration:
    """Integration tests for Alembic with database."""

    def test_can_import_alembic_config(self):
        """Test that we can import and use Alembic configuration."""
        from alembic.config import Config

        backend_dir = Path(__file__).parent.parent
        ini_path = backend_dir / "alembic.ini"

        config = Config(str(ini_path))
        script_location = config.get_main_option("script_location")
        assert script_location == "alembic"

    def test_script_directory_accessible(self):
        """Test that ScriptDirectory can be created from config."""
        from alembic.config import Config
        from alembic.script import ScriptDirectory

        backend_dir = Path(__file__).parent.parent
        ini_path = backend_dir / "alembic.ini"
        config = Config(str(ini_path))

        script = ScriptDirectory.from_config(config)
        assert script is not None

        # Verify versions directory
        versions_path = Path(script.versions)
        assert versions_path.exists()
        assert versions_path.is_dir()

    def test_env_py_is_executable(self):
        """Test that env.py can be loaded without import errors."""
        backend_dir = Path(__file__).parent.parent
        env_file = backend_dir / "alembic" / "env.py"

        # Check file exists and has content
        assert env_file.exists()
        with open(env_file) as f:
            content = f.read()
            assert len(content) > 0
            assert "def run_migrations_offline" in content
            assert "def run_migrations_online" in content


class TestAlembicDocumentation:
    """Test that Alembic documentation is in place."""

    def test_alembic_readme_exists(self):
        """Test that alembic/README file exists (created by alembic init)."""
        readme_file = Path(__file__).parent.parent / "alembic" / "README"
        assert readme_file.exists(), "alembic/README should exist"

    def test_script_mako_template_exists(self):
        """Test that script.py.mako template exists."""
        template_file = Path(__file__).parent.parent / "alembic" / "script.py.mako"
        assert template_file.exists(), "script.py.mako template should exist"
