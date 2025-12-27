"""Tests for API key validators."""

import pytest

from app.utils.validators import validate_openai_api_key_format


class TestValidateOpenAIAPIKeyFormat:
    """Test cases for validate_openai_api_key_format function."""

    def test_valid_api_key(self):
        """Test validation passes for valid API key."""
        valid_key = "sk-" + "a" * 48  # 51 characters total
        assert validate_openai_api_key_format(valid_key) is True

    def test_valid_api_key_with_hyphens(self):
        """Test validation passes for API key with hyphens."""
        valid_key = "sk-proj-abc123-def456-ghi789-jkl012-mno345"
        assert validate_openai_api_key_format(valid_key) is True

    def test_valid_api_key_with_underscores(self):
        """Test validation passes for API key with underscores."""
        valid_key = "sk-proj_abc123_def456_ghi789_jkl012_mno345"
        assert validate_openai_api_key_format(valid_key) is True

    def test_empty_api_key(self):
        """Test validation fails for empty API key."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            validate_openai_api_key_format("")

    def test_none_api_key(self):
        """Test validation fails for None API key."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            validate_openai_api_key_format(None)

    def test_missing_sk_prefix(self):
        """Test validation fails for API key without sk- prefix."""
        with pytest.raises(ValueError, match="must start with 'sk-'"):
            validate_openai_api_key_format("abc123def456ghi789")

    def test_too_short_api_key(self):
        """Test validation fails for API key shorter than 40 characters."""
        short_key = "sk-short"
        with pytest.raises(ValueError, match="too short"):
            validate_openai_api_key_format(short_key)

    def test_invalid_characters(self):
        """Test validation fails for API key with invalid characters."""
        invalid_key = "sk-" + "a" * 40 + "!@#$%"
        with pytest.raises(ValueError, match="invalid characters"):
            validate_openai_api_key_format(invalid_key)

    def test_api_key_with_spaces(self):
        """Test validation fails for API key with spaces."""
        invalid_key = "sk-abc def ghi jkl mno pqr stu vwx yz0123456"
        with pytest.raises(ValueError, match="invalid characters"):
            validate_openai_api_key_format(invalid_key)

    def test_minimum_length_boundary(self):
        """Test validation at minimum length boundary (40 chars)."""
        min_key = "sk-" + "a" * 37  # 40 characters total
        assert validate_openai_api_key_format(min_key) is True

    def test_below_minimum_length(self):
        """Test validation fails just below minimum length."""
        short_key = "sk-" + "a" * 36  # 39 characters total
        with pytest.raises(ValueError, match="too short"):
            validate_openai_api_key_format(short_key)
