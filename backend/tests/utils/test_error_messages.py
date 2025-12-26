import pytest


def test_error_message_templates_include_required_codes():
    from app.utils.error_messages import ERROR_MESSAGE_TEMPLATES

    required_codes = {
        "INVALID_API_KEY",
        "API_KEY_DECRYPTION_FAILED",
        "OPENAI_QUOTA_EXCEEDED",
        "OPENAI_RATE_LIMIT",
        "OPENAI_CONNECTION_ERROR",
        "OPENAI_SERVER_ERROR",
        "OPENAI_INVALID_RESPONSE",
        "UNEXPECTED_ERROR",
    }

    missing = required_codes - set(ERROR_MESSAGE_TEMPLATES.keys())
    assert not missing, f"Missing error codes: {sorted(missing)}"

    for code in required_codes:
        template = ERROR_MESSAGE_TEMPLATES[code]
        assert "message" in template
        assert "action" in template
        assert "retriable" in template
        assert "severity" in template


@pytest.mark.parametrize(
    "operation_type, expected_phrase",
    [
        ("question_generation", "generate your interview question"),
        ("feedback_analysis", "analyze your answer"),
    ],
)
def test_render_template_supports_dynamic_variables(operation_type, expected_phrase):
    from app.utils.error_messages import render_template

    rendered = render_template(
        "Unable to {operation_phrase}. Retry #{retry_count}.",
        {"operation_type": operation_type, "retry_count": 2},
    )

    assert expected_phrase in rendered
    assert "Retry #2" in rendered


def test_render_template_is_safe_for_missing_variables():
    from app.utils.error_messages import render_template

    rendered = render_template("Hello {unknown_key}", {})
    assert rendered == "Hello {unknown_key}"


def test_generate_user_friendly_message_includes_actionable_steps():
    from app.utils.error_messages import generate_user_friendly_message

    message = generate_user_friendly_message(
        "INVALID_API_KEY", {"operation_type": "question_generation"}
    )
    assert "Unable" in message
    assert "generate your interview question" in message
    assert "What to do:" in message
    assert "Check your OpenAI API key" in message


def test_generate_user_friendly_message_uses_default_for_unknown_code():
    from app.utils.error_messages import generate_user_friendly_message

    message = generate_user_friendly_message(
        "SOME_UNKNOWN_CODE", {"operation_type": "feedback_analysis"}
    )
    assert "What to do:" in message
    assert "contact support" in message.lower()
