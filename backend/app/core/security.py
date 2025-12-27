from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
import uuid

from jose import JWTError, jwt
from jose.exceptions import ExpiredSignatureError
from passlib.context import CryptContext
from passlib.exc import UnknownHashError

from app.core.config import settings

_pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def hash_password(password: str) -> str:
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except (ValueError, UnknownHashError):
        return False


def create_access_token(data: dict[str, Any]) -> str:
    """
    Create a JWT access token with standard claims.

    Args:
        data: Token data. Must include 'user_id' which will be stored in 'sub' claim.

    Returns:
        Encoded JWT token string

    Raises:
        ValueError: If user_id is missing from data
    """
    to_encode = dict(data)

    if "user_id" not in to_encode:
        raise ValueError("Token data must include user_id")

    # Store user_id in standard 'sub' claim
    user_id = to_encode.pop("user_id")
    now = datetime.now(UTC)
    expire = now + timedelta(hours=24)

    to_encode.update(
        {
            "sub": user_id,  # Standard JWT subject claim
            "exp": expire,  # Expiration time
            "iat": now,  # Issued at time
            "jti": str(uuid.uuid4()),  # JWT ID for future revocation
        }
    )

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a JWT access token.

    Args:
        token: JWT token string

    Returns:
        Decoded token payload with 'user_id' extracted from 'sub' claim

    Raises:
        ValueError: If token is expired, invalid, or missing required claims
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError as exc:
        raise ValueError("Token expired") from exc
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    # Validate required claims
    if "sub" not in payload:
        raise ValueError("Token missing required 'sub' claim")

    # For backward compatibility, expose user_id
    payload["user_id"] = payload["sub"]

    return payload
