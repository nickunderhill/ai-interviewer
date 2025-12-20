from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest


def test_token_contains_user_id_claim():
    from jose import jwt

    from app.core.security import create_access_token, decode_access_token

    token = create_access_token({"user_id": "user-123"})

    header = jwt.get_unverified_header(token)
    assert header["alg"] == "HS256"

    payload = decode_access_token(token)

    assert payload["user_id"] == "user-123"
    assert "exp" in payload

    now_ts = int(datetime.now(timezone.utc).timestamp())
    exp_ts = int(payload["exp"])
    assert (24 * 60 * 60 - 15) <= (exp_ts - now_ts) <= (24 * 60 * 60 + 15)


def test_expired_token_is_rejected():
    from jose import jwt

    from app.core.config import settings
    from app.core.security import decode_access_token

    expired = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode(
        {"user_id": "user-123", "exp": expired},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(ValueError, match="expired"):
        decode_access_token(token)


def test_invalid_signature_is_rejected():
    from jose import jwt

    from app.core.config import settings
    from app.core.security import decode_access_token

    token = jwt.encode(
        {
            "user_id": "user-123",
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        },
        "not-the-real-secret",
        algorithm=settings.ALGORITHM,
    )

    with pytest.raises(ValueError):
        decode_access_token(token)


def test_create_access_token_requires_user_id():
    from app.core.security import create_access_token

    with pytest.raises(ValueError, match="user_id"):
        create_access_token({"sub": "user-123"})
