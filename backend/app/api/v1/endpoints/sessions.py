"""
API endpoints for interview sessions.
"""

import datetime as dt
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
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.interview_session import InterviewSession
from app.models.job_posting import JobPosting
from app.models.operation import Operation
from app.models.user import User
from app.schemas.operation import OperationResponse
from app.schemas.session import (
    AnswerCreate,
    JobPostingBasic,
    MessageResponse,
    SessionCreate,
    SessionDetailResponse,
    SessionResponse,
    SessionWithFeedbackScore,
)
from app.schemas import feedback as schemas
from app.services import session_service
from app.tasks.question_tasks import generate_question_task
from app.tasks.feedback_tasks import generate_feedback_task

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
    start_date: Optional[dt.date] = Query(
        None,
        description="Filter sessions from this date (inclusive)",
    ),
    end_date: Optional[dt.date] = Query(
        None,
        description="Filter sessions until this date (inclusive)",
    ),
    job_posting_id: Optional[UUID] = Query(
        None,
        description="Filter sessions by job posting ID",
    ),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SessionResponse]:
    """
    Get all interview sessions for the authenticated user.

    Filters:
    - **status**: Optional filter by session status
    - **start_date**: Filter sessions created on or after this date
    - **end_date**: Filter sessions created on or before this date
    - **job_posting_id**: Filter sessions for specific job posting

    Returns sessions ordered by created_at DESC (newest first)
    """
    # Validate status parameter
    VALID_STATUSES = {"active", "paused", "completed"}
    if status_param and status_param not in VALID_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_STATUS_FILTER",
                "message": f"Status must be one of: {VALID_STATUSES}",
            },
        )

    # Validate date range
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_DATE_RANGE",
                "message": "start_date must be <= end_date",
            },
        )

    # Verify job posting ownership if filtering by job_posting_id
    if job_posting_id:
        job_result = await db.execute(
            select(JobPosting).where(
                JobPosting.id == job_posting_id,
                JobPosting.user_id == current_user.id,
            )
        )
        if not job_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "JOB_POSTING_NOT_FOUND",
                    "message": "Job posting not found",
                },
            )

    # Build query
    query = (
        select(InterviewSession)
        .options(selectinload(InterviewSession.job_posting))
        .where(InterviewSession.user_id == current_user.id)
    )

    if status_param:
        query = query.where(InterviewSession.status == status_param)

    if start_date:
        start_datetime = dt.datetime.combine(start_date, dt.time.min).replace(
            tzinfo=dt.timezone.utc
        )
        query = query.where(InterviewSession.created_at >= start_datetime)

    if end_date:
        end_datetime = dt.datetime.combine(end_date, dt.time.max).replace(
            tzinfo=dt.timezone.utc
        )
        query = query.where(InterviewSession.created_at <= end_datetime)

    if job_posting_id:
        query = query.where(InterviewSession.job_posting_id == job_posting_id)

    query = query.order_by(InterviewSession.created_at.desc())

    result = await db.execute(query)
    sessions = result.scalars().all()

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
        "messages": session.messages,
    }

    return SessionDetailResponse.model_validate(response_data)


@router.get(
    "/with-feedback",
    response_model=List[SessionWithFeedbackScore],
    status_code=status.HTTP_200_OK,
    summary="Get sessions with feedback scores",
)
async def get_sessions_with_feedback(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[SessionWithFeedbackScore]:
    """
    Get all completed sessions with feedback scores for the authenticated user.

    - Returns sessions ordered by created_at ASC (chronological order)
    - Only includes completed sessions that have feedback
    - Used for score comparison and trend visualization
    """
    from app.models.interview_feedback import InterviewFeedback
    from app.models.job_posting import JobPosting

    query = (
        select(InterviewSession, InterviewFeedback, JobPosting)
        .join(
            InterviewFeedback,
            InterviewSession.id == InterviewFeedback.session_id,
        )
        .join(
            JobPosting,
            InterviewSession.job_posting_id == JobPosting.id,
        )
        .where(InterviewSession.user_id == current_user.id)
        .where(InterviewSession.status == "completed")
        .order_by(InterviewSession.created_at.asc())
    )

    result = await db.execute(query)
    sessions_data = []

    for session, feedback, job_posting in result:
        sessions_data.append(
            SessionWithFeedbackScore(
                session_id=session.id,
                created_at=session.created_at,
                job_posting=JobPostingBasic.model_validate(job_posting),
                overall_score=feedback.overall_score,
            )
        )

    return sessions_data


@router.put(
    "/{session_id}/pause",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Pause an active session",
)
async def pause_session(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionResponse:
    """Pause an active interview session.

    - Returns updated session with status='paused'
    - Returns 400 if session is not active
    - Returns 404 if session not found or unauthorized
    """

    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.job_posting))
        .where(
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

    if session.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_SESSION_STATE",
                "message": f"Cannot pause {session.status} session. Only active sessions can be paused.",
            },
        )

    session.status = "paused"
    await db.commit()

    # Reload with relationship(s) eagerly loaded for response validation
    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.job_posting))
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one()
    return SessionResponse.model_validate(session)


@router.put(
    "/{session_id}/resume",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Resume a paused session",
)
async def resume_session(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionResponse:
    """Resume a paused interview session.

    - Returns updated session with status='active'
    - Returns 400 if session is not paused
    - Returns 404 if session not found or unauthorized
    """

    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.job_posting))
        .where(
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

    if session.status != "paused":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "INVALID_SESSION_STATE",
                "message": f"Cannot resume {session.status} session. Only paused sessions can be resumed.",
            },
        )

    session.status = "active"
    await db.commit()

    result = await db.execute(
        select(InterviewSession)
        .options(selectinload(InterviewSession.job_posting))
        .where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalar_one()
    return SessionResponse.model_validate(session)


@router.post(
    "/{session_id}/complete",
    response_model=SessionResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark session as completed",
)
async def complete_session(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SessionResponse:
    """Mark an interview session as completed."""

    session = await session_service.complete_session(db, session_id, current_user)
    return SessionResponse.model_validate(session)


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


@router.get(
    "/{session_id}/messages",
    response_model=List[MessageResponse],
    status_code=status.HTTP_200_OK,
    summary="Get session messages (Q&A history)",
)
async def get_session_messages(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[MessageResponse]:
    """
    Get all messages (questions and answers) for a session.

    Messages are returned in chronological order (oldest first)
    to show the natural conversation flow.

    - **session_id**: UUID of the session
    - Returns questions and answers interleaved
    - Returns empty array if no messages yet
    - Returns 404 if session not found or unauthorized
    """
    messages = await session_service.get_session_messages(db, session_id, current_user)
    return [MessageResponse.model_validate(msg) for msg in messages]


@router.post(
    "/{session_id}/answers",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit an answer to interview question",
)
async def submit_answer(
    session_id: UUID = Path(..., description="Session UUID"),
    answer_data: AnswerCreate = ...,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MessageResponse:
    """
    Submit an answer to an interview question.

    - **session_id**: UUID of the active session
    - **answer_text**: User's answer (required, non-empty)
    - Returns 201 with message object
    - Returns 400 if session not active
    - Returns 404 if session not found or unauthorized
    """
    message = await session_service.submit_answer(
        db, session_id, answer_data, current_user
    )
    return MessageResponse.model_validate(message)


@router.post(
    "/{session_id}/generate-feedback",
    response_model=OperationResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Generate AI feedback for a completed session",
)
async def generate_feedback(
    session_id: UUID = Path(..., description="Session UUID"),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OperationResponse:
    """
    Generate comprehensive AI-powered feedback for a completed interview session.

    Requirements:
    - Session must belong to the current user
    - Session status must be 'completed'
    - User must have a resume
    - Session must have a job posting
    - Feedback must not already exist for this session

    Returns 202 Accepted with an Operation for tracking the async feedback generation.
    Poll the Operation endpoint to check when feedback is ready.

    Errors:
    - **400 Bad Request**: Session not completed or feedback already exists
    - **404 Not Found**: Session not found or unauthorized
    """
    # Verify session exists, belongs to user, and is completed
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .where(InterviewSession.user_id == current_user.id)
        .options(selectinload(InterviewSession.feedback))
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SESSION_NOT_FOUND", "message": "Session not found"},
        )

    if session.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "SESSION_NOT_COMPLETED",
                "message": "Can only generate feedback for completed sessions",
            },
        )

    # Check if feedback already exists
    if session.feedback:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "FEEDBACK_ALREADY_EXISTS",
                "message": "Feedback already generated for this session",
            },
        )

    # Create operation to track feedback generation
    import datetime as dt

    operation = Operation(
        operation_type="feedback_analysis",
        status="pending",
        created_at=dt.datetime.now(dt.timezone.utc),
        updated_at=dt.datetime.now(dt.timezone.utc),
    )
    db.add(operation)
    await db.commit()
    await db.refresh(operation)

    # Queue background task
    background_tasks.add_task(
        generate_feedback_task,
        operation_id=operation.id,
        session_id=session_id,
        user_id=current_user.id,
    )

    return OperationResponse.model_validate(operation)


@router.get(
    "/{session_id}/feedback",
    response_model=schemas.InterviewFeedbackResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI feedback for a completed session",
    responses={
        200: {"description": "Feedback retrieved successfully"},
        404: {
            "description": "Session or feedback not found",
            "content": {
                "application/json": {
                    "examples": {
                        "session_not_found": {
                            "value": {
                                "detail": {
                                    "code": "SESSION_NOT_FOUND",
                                    "message": "Session not found or access denied",
                                }
                            }
                        },
                        "feedback_not_found": {
                            "value": {
                                "detail": {
                                    "code": "FEEDBACK_NOT_FOUND",
                                    "message": "Feedback has not been generated for this session yet",
                                }
                            }
                        },
                    }
                }
            },
        },
    },
)
async def get_session_feedback(
    session_id: UUID = Path(..., description="Session UUID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.InterviewFeedbackResponse:
    """
    Retrieve AI-generated feedback for a completed interview session.

    Returns comprehensive feedback including:
    - Dimension scores (technical accuracy, communication, problem solving, relevance)
    - Overall score (average of dimensions)
    - Detailed feedback for each dimension
    - Knowledge gaps identified
    - Learning recommendations

    **Authorization**: Requires valid JWT token and session ownership.

    **Prerequisites**:
    - Session must exist and belong to current user
    - Feedback must have been generated via POST /sessions/{id}/generate-feedback
    """
    # Verify session ownership and load feedback
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .where(InterviewSession.user_id == current_user.id)
        .options(selectinload(InterviewSession.feedback))
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "SESSION_NOT_FOUND",
                "message": "Session not found or access denied",
            },
        )

    if not session.feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FEEDBACK_NOT_FOUND",
                "message": "Feedback has not been generated for this session yet",
            },
        )

    return schemas.InterviewFeedbackResponse.model_validate(session.feedback)
