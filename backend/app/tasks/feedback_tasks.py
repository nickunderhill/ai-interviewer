"""
Background tasks for feedback generation.
"""

import datetime as dt
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db_context
from app.models.interview_feedback import InterviewFeedback
from app.models.interview_session import InterviewSession
from app.models.operation import Operation
from app.models.user import User
from app.services import feedback_analysis_service

logger = logging.getLogger(__name__)


async def generate_feedback_task(
    operation_id: UUID,
    session_id: UUID,
    user_id: UUID,
) -> None:
    """
    Background task to generate AI feedback for a completed interview session.

    Args:
        operation_id: UUID of the Operation tracking this task
        session_id: UUID of the InterviewSession to analyze
        user_id: UUID of the user requesting the feedback

    Side effects:
        Updates Operation status and result/error_message
        Creates InterviewFeedback record (in Story 5-4)
    """
    async with get_db_context() as db:
        try:
            # Load operation
            operation = await db.get(Operation, operation_id)
            if not operation:
                logger.error(f"Operation {operation_id} not found")
                return

            # Update status to processing
            operation.status = "processing"
            operation.updated_at = dt.datetime.now(dt.timezone.utc)
            await db.commit()

            # Load user
            user = await db.get(User, user_id)
            if not user:
                logger.error(f"User {user_id} not found for operation {operation_id}")
                operation.status = "failed"
                operation.error_message = "User not found"
                operation.updated_at = dt.datetime.now(dt.timezone.utc)
                await db.commit()
                return

            # Generate feedback using service
            result = await feedback_analysis_service.analyze_session(
                db=db,
                session_id=session_id,
                current_user=user,
            )

            # Calculate overall score (average of 4 dimension scores)
            overall_score = round(
                (
                    result.technical_accuracy_score
                    + result.communication_clarity_score
                    + result.problem_solving_score
                    + result.relevance_score
                )
                / 4
            )

            # Persist feedback to database
            feedback = InterviewFeedback(
                session_id=session_id,
                technical_accuracy_score=result.technical_accuracy_score,
                communication_clarity_score=result.communication_clarity_score,
                problem_solving_score=result.problem_solving_score,
                relevance_score=result.relevance_score,
                overall_score=overall_score,
                technical_feedback=result.technical_feedback,
                communication_feedback=result.communication_feedback,
                problem_solving_feedback=result.problem_solving_feedback,
                relevance_feedback=result.relevance_feedback,
                overall_comments=result.overall_comments,
                knowledge_gaps=result.knowledge_gaps,
                learning_recommendations=result.learning_recommendations,
            )

            try:
                db.add(feedback)
                await db.flush()
            except IntegrityError:
                # Feedback already exists (duplicate session_id)
                logger.warning(f"Feedback already exists for session {session_id}")
                operation.status = "failed"
                operation.error_message = "Feedback already exists for this session"
                operation.updated_at = dt.datetime.now(dt.timezone.utc)
                await db.commit()
                return

            # Convert result to dict for Operation.result, include overall_score
            result_dict = result.model_dump()
            result_dict["overall_score"] = overall_score

            # Mark operation as completed
            operation.status = "completed"
            operation.result = result_dict
            operation.updated_at = dt.datetime.now(dt.timezone.utc)
            await db.commit()

            logger.info(
                f"Feedback generated and stored successfully for operation {operation_id}, "
                f"session {session_id}, overall_score={overall_score}"
            )

        except Exception as e:
            logger.error(
                f"Error in feedback generation task {operation_id}: {e}", exc_info=True
            )

            # Try to update operation status to failed
            try:
                operation = await db.get(Operation, operation_id)
                if operation:
                    operation.status = "failed"
                    operation.error_message = f"Feedback generation failed: {str(e)}"
                    operation.updated_at = dt.datetime.now(dt.timezone.utc)
                    await db.commit()
            except Exception as update_error:
                logger.error(
                    f"Failed to update operation {operation_id} status: {update_error}"
                )
