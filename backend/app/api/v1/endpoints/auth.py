from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token
from app.core.database import get_db
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import authenticate_user
from app.services.user_service import create_user

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", status_code=201, response_model=UserResponse)
async def register(
    payload: RegisterRequest, db: AsyncSession = Depends(get_db)
) -> UserResponse:
    try:
        user = await create_user(
            db, email=str(payload.email), password=payload.password
        )
    except IntegrityError as exc:
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
async def login(
    payload: LoginRequest, db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    user = await authenticate_user(
        db, email=str(payload.email), password=payload.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "INVALID_CREDENTIALS",
                "message": "Invalid email or password.",
            },
        )

    access_token = create_access_token({"user_id": str(user.id)})
    return TokenResponse(access_token=access_token)
