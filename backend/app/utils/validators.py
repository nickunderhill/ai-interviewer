"""
Validation utilities for API keys and other data.
"""

import re


def normalize_text(value: str) -> str:
    """Normalize user-provided text safely.

    - Strips leading/trailing whitespace.
    - Rejects NUL bytes which are commonly used in injection payloads.
    """
    if "\x00" in value:
        raise ValueError("Text contains invalid null byte")
    return value.strip()


def normalize_optional_text(value: str | None) -> str | None:
    """Normalize text if provided; leave None unchanged."""
    if value is None:
        return None
    return normalize_text(value)


def ensure_not_blank(value: str) -> str:
    """Ensure a text value is not blank after trimming."""
    normalized = normalize_text(value)
    if not normalized:
        raise ValueError("Value cannot be empty")
    return normalized


def validate_openai_api_key_format(api_key: str) -> bool:
    """
    Validate OpenAI API key format.

    OpenAI keys typically:
    - Start with 'sk-' (or 'sk-proj-' for project keys)
    - Contain 40+ alphanumeric characters and hyphens

    Args:
        api_key: The API key to validate

    Returns:
        True if valid format

    Raises:
        ValueError: If format is invalid with descriptive message
    """
    if not api_key:
        raise ValueError("API key cannot be empty")

    if not api_key.startswith("sk-"):
        raise ValueError("OpenAI API key must start with 'sk-'")

    if len(api_key) < 40:
        raise ValueError("API key appears to be too short (minimum 40 characters)")

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r"^sk-[A-Za-z0-9\-_]+$", api_key):
        raise ValueError("API key contains invalid characters")

    return True
