"""Tests for OpenAI service."""

from unittest.mock import MagicMock, Mock, patch

from fastapi import HTTPException
from openai import APIConnectionError, APIError, RateLimitError
import pytest

from app.models.user import User
from app.services.openai_service import OpenAIService


@pytest.fixture
def mock_user():
    """Create a mock user with encrypted API key."""
    user = Mock(spec=User)
    user.id = "test-user-id"
    user.openai_api_key_encrypted = b"encrypted_key_data"
    return user


@pytest.fixture
def mock_user_no_key():
    """Create a mock user without API key."""
    user = Mock(spec=User)
    user.id = "test-user-id"
    user.openai_api_key_encrypted = None
    return user


@patch("app.services.openai_service.decrypt_api_key")
@patch("app.services.openai_service.OpenAI")
def test_openai_service_initialization(mock_openai, mock_decrypt, mock_user):
    """Test successful service initialization."""
    mock_decrypt.return_value = "sk-test-key"

    service = OpenAIService(mock_user)

    assert service.user_id == mock_user.id
    mock_decrypt.assert_called_once_with(mock_user.openai_api_key_encrypted)
    mock_openai.assert_called_once_with(api_key="sk-test-key")


def test_openai_service_no_api_key(mock_user_no_key):
    """Test initialization fails when user has no API key."""
    with pytest.raises(HTTPException) as exc_info:
        OpenAIService(mock_user_no_key)

    assert exc_info.value.status_code == 400
    assert "API_KEY_NOT_CONFIGURED" in str(exc_info.value.detail)


@patch("app.services.openai_service.decrypt_api_key")
@patch("app.services.openai_service.OpenAI")
def test_openai_service_decryption_failure(mock_openai, mock_decrypt, mock_user):
    """Test initialization fails when decryption fails."""
    mock_decrypt.side_effect = Exception("Decryption failed")

    with pytest.raises(HTTPException) as exc_info:
        OpenAIService(mock_user)

    assert exc_info.value.status_code == 500
    assert "API_KEY_DECRYPTION_FAILED" in str(exc_info.value.detail)


@patch("app.services.openai_service.decrypt_api_key")
@patch("app.services.openai_service.OpenAI")
def test_generate_chat_completion_success(mock_openai, mock_decrypt, mock_user):
    """Test successful chat completion."""
    mock_decrypt.return_value = "sk-test-key"

    # Mock OpenAI response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Generated response"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)
    result = service.generate_chat_completion(
        messages=[{"role": "user", "content": "Test prompt"}]
    )

    assert result == "Generated response"
    mock_client.chat.completions.create.assert_called_once()

    # Verify called with correct parameters
    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-3.5-turbo"
    assert call_args[1]["temperature"] == 0.7
    assert call_args[1]["messages"] == [{"role": "user", "content": "Test prompt"}]


@patch("app.services.openai_service.decrypt_api_key")
@patch("app.services.openai_service.OpenAI")
def test_generate_chat_completion_with_custom_params(
    mock_openai, mock_decrypt, mock_user
):
    """Test chat completion with custom parameters."""
    mock_decrypt.return_value = "sk-test-key"

    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Custom response"

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)
    result = service.generate_chat_completion(
        messages=[{"role": "user", "content": "Test"}],
        model="gpt-4",
        temperature=0.5,
        max_tokens=100,
    )

    assert result == "Custom response"

    call_args = mock_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4"
    assert call_args[1]["temperature"] == 0.5
    assert call_args[1]["max_tokens"] == 100


@patch("app.services.openai_service.decrypt_api_key")
@patch("app.services.openai_service.OpenAI")
def test_generate_chat_completion_rate_limit(mock_openai, mock_decrypt, mock_user):
    """Test rate limit error handling."""
    mock_decrypt.return_value = "sk-test-key"

    mock_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 429
    rate_limit_error = RateLimitError(
        "Rate limit exceeded",
        response=mock_response,
        body={"error": {"message": "Rate limit exceeded"}},
    )
    mock_client.chat.completions.create.side_effect = rate_limit_error
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)

    with pytest.raises(HTTPException) as exc_info:
        service.generate_chat_completion(messages=[{"role": "user", "content": "Test"}])

    assert exc_info.value.status_code == 429
    assert "OPENAI_RATE_LIMIT" in str(exc_info.value.detail)


@patch("app.services.openai_service.decrypt_api_key")
@patch("app.services.openai_service.OpenAI")
def test_generate_chat_completion_connection_error(
    mock_openai, mock_decrypt, mock_user
):
    """Test connection error handling."""
    mock_decrypt.return_value = "sk-test-key"

    mock_client = MagicMock()
    connection_error = APIConnectionError(request=Mock())
    mock_client.chat.completions.create.side_effect = connection_error
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)

    with pytest.raises(HTTPException) as exc_info:
        service.generate_chat_completion(messages=[{"role": "user", "content": "Test"}])

    assert exc_info.value.status_code == 503
    assert "OPENAI_CONNECTION_ERROR" in str(exc_info.value.detail)


@patch("app.services.openai_service.decrypt_api_key")
@patch("app.services.openai_service.OpenAI")
def test_generate_chat_completion_invalid_key(mock_openai, mock_decrypt, mock_user):
    """Test invalid API key error."""
    mock_decrypt.return_value = "sk-invalid-key"

    mock_client = MagicMock()
    mock_response = Mock()
    mock_response.status_code = 401
    api_error = APIError(
        "Invalid API key",
        request=Mock(),
        body={"error": {"message": "Invalid API key"}},
    )
    api_error.status_code = 401
    mock_client.chat.completions.create.side_effect = api_error
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)

    with pytest.raises(HTTPException) as exc_info:
        service.generate_chat_completion(messages=[{"role": "user", "content": "Test"}])

    assert exc_info.value.status_code == 400
    assert "INVALID_API_KEY" in str(exc_info.value.detail)


@patch("app.services.openai_service.decrypt_api_key")
@patch("app.services.openai_service.OpenAI")
def test_generate_chat_completion_api_error(mock_openai, mock_decrypt, mock_user):
    """Test general API error handling."""
    mock_decrypt.return_value = "sk-test-key"

    mock_client = MagicMock()
    api_error = APIError(
        "API error",
        request=Mock(),
        body={"error": {"message": "Internal error"}},
    )
    api_error.status_code = 500
    mock_client.chat.completions.create.side_effect = api_error
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)

    with pytest.raises(HTTPException) as exc_info:
        service.generate_chat_completion(messages=[{"role": "user", "content": "Test"}])

    assert exc_info.value.status_code == 500
    assert "OPENAI_API_ERROR" in str(exc_info.value.detail)


@patch("app.services.openai_service.decrypt_api_key")
@patch("app.services.openai_service.OpenAI")
def test_generate_chat_completion_unexpected_error(
    mock_openai, mock_decrypt, mock_user
):
    """Test unexpected error handling."""
    mock_decrypt.return_value = "sk-test-key"

    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = ValueError("Unexpected")
    mock_openai.return_value = mock_client

    service = OpenAIService(mock_user)

    with pytest.raises(HTTPException) as exc_info:
        service.generate_chat_completion(messages=[{"role": "user", "content": "Test"}])

    assert exc_info.value.status_code == 500
    assert "UNEXPECTED_ERROR" in str(exc_info.value.detail)
