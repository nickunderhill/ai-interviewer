"""
Security tests for JWT implementation covering token tampering,
expiration, missing claims, and invalid signatures.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from jose import jwt
import pytest

from app.core.config import settings
from app.core.security import create_access_token, decode_access_token


def test_token_tampering_fails():
    """Verify that tampering with token content causes validation to fail."""
    token = create_access_token({"user_id": "user-123"})

    # Decode without verification to tamper with payload
    unverified_payload = jwt.get_unverified_claims(token)

    # Tamper with user_id
    unverified_payload["sub"] = "attacker-456"

    # Re-encode with same algorithm but tampered data
    tampered_token = jwt.encode(
        unverified_payload,
        "wrong-secret",  # Wrong secret
        algorithm="HS256",
    )

    # Should fail validation
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(tampered_token)


def test_expired_token_returns_401_equivalent():
    """Verify that expired tokens are rejected."""
    expired = datetime.now(UTC) - timedelta(minutes=1)
    token = jwt.encode(
        {
            "sub": "user-123",
            "exp": expired,
            "iat": datetime.now(UTC) - timedelta(hours=25),
            "jti": "test-jti",
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="expired"):
        decode_access_token(token)


def test_missing_sub_claim_returns_401_equivalent():
    """Verify that tokens missing the 'sub' claim are rejected."""
    token = jwt.encode(
        {
            "exp": datetime.now(UTC) + timedelta(hours=24),
            "iat": datetime.now(UTC),
            "jti": "test-jti",
            # Missing 'sub' claim
        },
        settings.SECRET_KEY,
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="missing required 'sub' claim"):
        decode_access_token(token)


def test_invalid_signature_returns_401_equivalent():
    """Verify that tokens with invalid signatures are rejected."""
    token = jwt.encode(
        {
            "sub": "user-123",
            "exp": datetime.now(UTC) + timedelta(hours=24),
            "iat": datetime.now(UTC),
            "jti": "test-jti",
        },
        "not-the-real-secret",
        algorithm="HS256",
    )

    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(token)


def test_token_uses_hs256_algorithm():
    """Verify that tokens use HS256 algorithm."""
    token = create_access_token({"user_id": "user-123"})

    header = jwt.get_unverified_header(token)
    assert header["alg"] == "HS256"


def test_token_includes_standard_claims():
    """Verify that tokens include sub, exp, iat, and jti claims."""
    token = create_access_token({"user_id": "user-123"})

    payload = decode_access_token(token)

    # Check standard JWT claims
    assert "sub" in payload
    assert payload["sub"] == "user-123"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload

    # Verify backward compatibility
    assert payload["user_id"] == "user-123"


def test_token_expiration_is_24_hours():
    """Verify that tokens expire after 24 hours."""
    token = create_access_token({"user_id": "user-123"})

    payload = decode_access_token(token)

    exp_ts = int(payload["exp"])
    iat_ts = int(payload["iat"])

    # Should be 24 hours (86400 seconds)
    diff_seconds = exp_ts - iat_ts
    assert 86395 <= diff_seconds <= 86405  # Allow 5 second margin


def test_cannot_use_none_algorithm():
    """Verify that 'none' algorithm is rejected (security vulnerability)."""
    from jose.exceptions import JWSError

    # The library should prevent creation of tokens with 'none' algorithm
    with pytest.raises(JWSError, match="Algorithm none not supported"):
        jwt.encode(
            {
                "sub": "attacker",
                "exp": datetime.now(UTC) + timedelta(hours=24),
            },
            "",
            algorithm="none",
        )


def test_jti_is_unique_across_tokens():
    """Verify that each token gets a unique jti (JWT ID)."""
    token1 = create_access_token({"user_id": "user-123"})
    token2 = create_access_token({"user_id": "user-123"})

    payload1 = decode_access_token(token1)
    payload2 = decode_access_token(token2)

    # JTI should be different
    assert payload1["jti"] != payload2["jti"]
