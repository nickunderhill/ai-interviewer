"""
API endpoints for interview sessions.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.schemas.session import SessionCreate, SessionResponse
from app.services import session_service

router = APIRouter()


@router.post(
    "",
    response_model=SessionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new interview session",
)
async def create_session(
    session_data: SessionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionResponse:
    """
    Create a new interview session for a job posting.

    - **job_posting_id**: UUID of the job posting to practice for
    - Returns 201 with session details
    - Returns 404 if job posting not found or not owned by user
    """
    session = await session_service.create_session(db, session_data, current_user)
    return SessionResponse.model_validate(session)
