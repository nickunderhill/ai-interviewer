"""User-friendly error message templates.

This module provides:
- A mapping from stable error codes to user-facing message + action templates
- Helper to render templates with simple dynamic context (operation type, retry count)

The generated strings must avoid technical jargon and never include sensitive
information like API keys.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.utils.error_handler import mask_secrets

_OPERATION_PHRASES: dict[str, str] = {
    "question_generation": "generate your interview question",
    "feedback_analysis": "analyze your answer",
}


ERROR_MESSAGE_TEMPLATES: dict[str, dict[str, Any]] = {
    "RESUME_REQUIRED": {
        "message": "Unable to {operation_phrase}. A resume is required.",
        "action": "Add your resume in your profile settings, then try again.",
        "retriable": False,
        "severity": "error",
    },
    "JOB_POSTING_REQUIRED": {
        "message": "Unable to {operation_phrase}. This session is missing its job posting.",
        "action": "Create or select a job posting for this session, then try again.",
        "retriable": False,
        "severity": "error",
    },
    "NO_ANSWERS": {
        "message": "Unable to {operation_phrase}. There are no answers to analyze.",
        "action": "Complete at least one interview question, then try again.",
        "retriable": False,
        "severity": "error",
    },
    "API_KEY_NOT_CONFIGURED": {
        "message": "Unable to {operation_phrase}. No OpenAI API key is configured.",
        "action": "Add your OpenAI API key in your profile settings, then try again.",
        "retriable": False,
        "severity": "error",
    },
    "INVALID_API_KEY": {
        "message": "Unable to {operation_phrase}. Your OpenAI API key appears to be invalid.",
        "action": "Check your OpenAI API key configuration in your profile settings.",
        "retriable": False,
        "severity": "error",
    },
    "API_KEY_DECRYPTION_FAILED": {
        "message": "Unable to {operation_phrase}. Your OpenAI API key needs to be reconfigured.",
        "action": "Re-enter your OpenAI API key in your profile settings.",
        "retriable": False,
        "severity": "error",
    },
    "OPENAI_QUOTA_EXCEEDED": {
        "message": "Unable to {operation_phrase}. Your OpenAI account has exceeded its quota.",
        "action": "Check your OpenAI billing/usage and update your plan, then try again.",
        "retriable": False,
        "severity": "error",
    },
    "OPENAI_RATE_LIMIT": {
        "message": "{operation_capitalized} is taking longer than expected due to high demand.",
        "action": "Wait a moment and try again.",
        "retriable": True,
        "severity": "warning",
    },
    "OPENAI_CONNECTION_ERROR": {
        "message": "Unable to {operation_phrase} because the AI service could not be reached.",
        "action": "Check your internet connection and try again.",
        "retriable": True,
        "severity": "warning",
    },
    "OPENAI_SERVER_ERROR": {
        "message": "The AI service is temporarily unavailable.",
        "action": "Try again in a few moments.",
        "retriable": True,
        "severity": "warning",
    },
    "OPENAI_INVALID_RESPONSE": {
        "message": "The AI service returned an unexpected response.",
        "action": "Try again. If the problem persists, contact support.",
        "retriable": True,
        "severity": "error",
    },
    "UNEXPECTED_ERROR": {
        "message": "An unexpected error occurred while contacting the AI service.",
        "action": "Try again. If the problem persists, contact support.",
        "retriable": True,
        "severity": "error",
    },
    "SESSION_NOT_FOUND": {
        "message": "Unable to {operation_phrase}. The session could not be found.",
        "action": "Refresh the page. If the problem persists, return to your sessions list and try again.",
        "retriable": False,
        "severity": "error",
    },
    "USER_NOT_FOUND": {
        "message": "Unable to {operation_phrase}. Your account could not be loaded.",
        "action": "Try again. If the problem persists, log out and log back in.",
        "retriable": False,
        "severity": "error",
    },
    "FEEDBACK_ALREADY_EXISTS": {
        "message": "Feedback has already been generated for this session.",
        "action": "Refresh the page to view the existing feedback.",
        "retriable": False,
        "severity": "info",
    },
    "DB_WRITE_FAILED": {
        "message": "We couldn't save the result of this AI operation.",
        "action": "Try again. If the problem persists, contact support.",
        "retriable": True,
        "severity": "error",
    },
    "FEEDBACK_PARSE_FAILED": {
        "message": "We couldn't process the AI feedback response.",
        "action": "Try again. If the problem persists, contact support.",
        "retriable": True,
        "severity": "error",
    },
}


_DEFAULT_TEMPLATE: dict[str, Any] = {
    "message": "An unexpected error occurred while contacting the AI service.",
    "action": "Try again. If the problem persists, contact support.",
    "retriable": True,
    "severity": "error",
}


class _SafeFormatDict(dict[str, Any]):
    def __missing__(self, key: str) -> str:  # pragma: no cover
        return "{" + key + "}"


def _normalized_context(context: Mapping[str, Any] | None) -> dict[str, Any]:
    ctx: dict[str, Any] = dict(context or {})

    operation_type = str(ctx.get("operation_type") or "")
    operation_phrase = _OPERATION_PHRASES.get(operation_type, "complete your request")

    # Used by some templates that want a subject-like string.
    if operation_type == "question_generation":
        operation_capitalized = "Question generation"
    elif operation_type == "feedback_analysis":
        operation_capitalized = "Feedback analysis"
    else:
        operation_capitalized = "This operation"

    # Always overwrite these keys to avoid caller-controlled injection.
    ctx["operation_phrase"] = operation_phrase
    ctx["operation_capitalized"] = operation_capitalized

    retry_count = ctx.get("retry_count")
    if retry_count is not None:
        try:
            ctx["retry_count"] = int(retry_count)
        except Exception:
            # If it's not usable, drop it (avoid leaking arbitrary strings).
            ctx.pop("retry_count", None)

    return ctx


def render_template(template: str, context: Mapping[str, Any] | None = None) -> str:
    """Safely render a format-string template with best-effort context.

    Missing keys are left as `{key}`.
    """

    ctx = _normalized_context(context)
    try:
        return template.format_map(_SafeFormatDict(ctx))
    except Exception:
        # If template is malformed, fail closed by returning it untouched.
        return template


def get_error_template(error_code: str) -> dict[str, Any]:
    """Return the template entry for an error code (or the default)."""

    return ERROR_MESSAGE_TEMPLATES.get(error_code, _DEFAULT_TEMPLATE)


def generate_user_friendly_message(
    error_code: str,
    context: Mapping[str, Any] | None = None,
) -> str:
    """Generate a user-friendly error message string.

    Output format is intentionally simple so the frontend can display it as plain
    text without needing access to internal error details.
    """

    template = get_error_template(error_code)
    message = render_template(str(template.get("message", "")), context)
    action = render_template(str(template.get("action", "")), context)

    combined = message.strip()
    if action.strip():
        combined = f"{combined}\n\nWhat to do: {action.strip()}"

    # Ensure secrets never leak through dynamic context.
    return mask_secrets(combined)


def is_retriable(error_code: str) -> bool:
    return bool(get_error_template(error_code).get("retriable", False))


def get_error_severity(error_code: str) -> str:
    severity = str(get_error_template(error_code).get("severity", "error"))
    return severity if severity in {"error", "warning", "info"} else "error"
