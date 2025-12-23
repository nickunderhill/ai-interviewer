"""
API endpoints for interview sessions.
"""

from typing import List, Optional
from uuid import UUID
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Path,
    Query,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.interview_session import InterviewSession
from app.models.operation import Operation
from app.models.user import User
from app.schemas.operation import OperationResponse
from app.schemas.session import (
    SessionCreate,
    SessionDetailResponse,
    SessionResponse,
)
from app.services import session_service
from app.tasks.question_tasks import generate_question_task

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


@router.get(
    "",
    response_model=List[SessionResponse],
    status_code=status.HTTP_200_OK,
    summary="List user's interview sessions",
)
async def list_sessions(
    status_param: Optional[str] = Query(
        None,
        alias="status",
        description="Filter by status: active, paused, or completed",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SessionResponse]:
    """
    Get all interview sessions for the authenticated user.

    - **status**: Optional filter by session status
    - Returns sessions ordered by created_at DESC (newest first)
    - Returns empty array if no sessions found
    """
    sessions = await session_service.get_sessions_by_user(
        db, current_user, status_param
    )
    return [SessionResponse.model_validate(session) for session in sessions]


@router.get(
    "/{session_id}",
    response_model=SessionDetailResponse,
    status_code=status.HTTP_200_OK,
    summary="Get session details",
)
async def get_session(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionDetailResponse:
    """
    Get full details of a specific interview session.

    - **session_id**: UUID of the session
    - Returns full session with job posting details and resume content
    - Returns 404 if not found or unauthorized
    """
    session = await session_service.get_session_by_id(db, session_id, current_user)

    # Manually build response to handle the user.resume relationship
    response_data = {
        "id": session.id,
        "user_id": session.user_id,
        "job_posting_id": session.job_posting_id,
        "status": session.status,
        "current_question_number": session.current_question_number,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "job_posting": session.job_posting,
        "resume": (
            session.user.resume if session.user and session.user.resume else None
        ),
    }

    return SessionDetailResponse.model_validate(response_data)


@router.post(
    "/{session_id}/generate-question",
    response_model=OperationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate next interview question",
)
async def generate_question(
    session_id: UUID = Path(..., description="Session UUID"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OperationResponse:
    """
    Generate the next interview question for a session.

    Returns immediately with operation_id. Frontend should poll
    GET /api/v1/operations/{operation_id} to check status.

    - **session_id**: UUID of the active session
    - Returns 202 Accepted with operation_id
    - Returns 400 if session is not active
    - Returns 404 if session not found or unauthorized
    """
    # Load session and validate
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found or you don't have permission to access it",
            },
        )

    # Validate session is active
    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SESSION_NOT_ACTIVE",
                "message": f"Cannot generate questions for {session.status} session. Only active sessions can receive new questions.",
            },
        )

    # Create operation
    operation = Operation(operation_type="question_generation", status="pending")
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    # Start background task
    background_tasks.add_task(generate_question_task, operation.id, session_id)

    return OperationResponse.model_validate(operation)
