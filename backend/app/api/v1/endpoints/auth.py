from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import authenticate_user
from app.services.user_service import create_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", status_code=201, response_model=UserResponse)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)) -> UserResponse:
    try:
        user = await create_user(db, email=str(payload.email), password=payload.password)
        logger.info(
            "User registered successfully",
            extra={"user_id": str(user.id), "email": user.email},
        )
    except IntegrityError as exc:
        logger.warning(
            "Registration failed - email already exists",
            extra={"email": str(payload.email)},
        )
        raise HTTPException(
            status_code=409,
            detail={
                "code": "EMAIL_ALREADY_REGISTERED",
                "message": "A user with that email already exists.",
            },
        ) from exc

    return UserResponse(
        id=user.id,
        email=user.email,
        created_at=user.created_at,
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)) -> TokenResponse:
    user = await authenticate_user(db, email=str(payload.email), password=payload.password)

    if user is None:
        logger.warning(
            "Login failed - invalid credentials",
            extra={"email": str(payload.email)},
        )
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password.",
            },
        )

    logger.info(
        "User logged in successfully",
        extra={"user_id": str(user.id), "email": user.email},
    )
    access_token = create_access_token({"user_id": str(user.id)})
    return TokenResponse(access_token=access_token)
