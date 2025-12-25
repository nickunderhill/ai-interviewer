from pydantic import ValidationError
import pytest

from app.schemas.auth import LoginRequest, TokenResponse


def test_login_request_validates_email_and_password():
    req = LoginRequest(email="user@example.com", password="p@ssw0rd!!")
    assert str(req.email) == "user@example.com"


def test_login_request_invalid_email_raises():
    with pytest.raises(ValidationError):
        LoginRequest(email="not-an-email", password="p@ssw0rd!!")


def test_token_response_defaults_token_type_to_bearer():
    token = TokenResponse(access_token="abc")
    assert token.token_type == "bearer"


def test_token_response_rejects_non_bearer_token_type():
    with pytest.raises(ValidationError):
        TokenResponse(access_token="abc", token_type="basic")
