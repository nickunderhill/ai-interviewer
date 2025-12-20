from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

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
    to_encode = dict(data)

    if "user_id" not in to_encode:
        raise ValueError("Token data must include user_id")

    expire = datetime.now(timezone.utc) + timedelta(hours=24)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except ExpiredSignatureError as exc:
        raise ValueError("Token expired") from exc
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    if "user_id" not in payload:
        raise ValueError("Token missing user_id")

    return payload
