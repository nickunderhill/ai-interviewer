"""
Dashboard metrics endpoints.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.interview_feedback import InterviewFeedback
from app.models.interview_session import InterviewSession
from app.models.job_posting import JobPosting
from app.models.user import User
from app.schemas.metrics import DashboardMetrics, PracticedRole

router = APIRouter()


@router.get("/dashboard", response_model=DashboardMetrics)
async def get_dashboard_metrics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get aggregated dashboard metrics for the current user.

    Returns:
        - Total completed interviews
        - Average overall score (from feedback)
        - Total questions answered
        - Most practiced job roles (top 5)
    """
    # Count completed sessions
    completed_count = await db.scalar(
        select(func.count(InterviewSession.id))
        .where(InterviewSession.user_id == current_user.id)
        .where(InterviewSession.status == "completed")
    )

    # Calculate average score from feedback
    avg_score = await db.scalar(
        select(func.avg(InterviewFeedback.overall_score))
        .join(
            InterviewSession,
            InterviewFeedback.session_id == InterviewSession.id,
        )
        .where(InterviewSession.user_id == current_user.id)
    )

    # Sum total questions answered
    total_questions = await db.scalar(
        select(func.sum(InterviewSession.current_question_number))
        .where(InterviewSession.user_id == current_user.id)
        .where(InterviewSession.status == "completed")
    )

    # Most practiced roles (top 5)
    roles_query = (
        select(
            JobPosting.id,
            JobPosting.title,
            JobPosting.company,
            func.count(InterviewSession.id).label("count"),
        )
        .join(
            InterviewSession,
            InterviewSession.job_posting_id == JobPosting.id,
        )
        .where(InterviewSession.user_id == current_user.id)
        .where(InterviewSession.status == "completed")
        .group_by(JobPosting.id, JobPosting.title, JobPosting.company)
        .order_by(func.count(InterviewSession.id).desc())
        .limit(5)
    )
    roles_result = await db.execute(roles_query)
    most_practiced = [
        PracticedRole(
            job_posting_id=str(r.id),
            title=r.title,
            company=r.company,
            count=r.count,
        )
        for r in roles_result
    ]

    return DashboardMetrics(
        completed_interviews=completed_count or 0,
        average_score=round(avg_score, 1) if avg_score else None,
        total_questions_answered=total_questions or 0,
        most_practiced_roles=most_practiced,
    )
