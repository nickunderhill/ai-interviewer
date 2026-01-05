"""
Background tasks for feedback generation.
"""

from contextlib import suppress
import datetime as dt
import logging
from typing import Any, cast
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.database import get_db_context
from app.models.interview_feedback import InterviewFeedback
from app.models.operation import Operation
from app.models.user import User
from app.services import feedback_analysis_service
from app.utils.error_handler import mask_secrets
from app.utils.error_messages import generate_user_friendly_message

logger = logging.getLogger(__name__)


def _safe_error_message(exc: Exception) -> str:
    if isinstance(exc, HTTPException):
        detail = getattr(exc, "detail", None)
        if isinstance(detail, dict):
            detail_dict = cast(dict[str, Any], detail)
            msg = (
                detail_dict.get("message")
                or detail_dict.get("code")
                or str(detail_dict)
            )
            return mask_secrets(str(msg))

    return mask_secrets(str(exc))


def _extract_error_code(exc: Exception) -> str:
    if isinstance(exc, HTTPException):
        detail = getattr(exc, "detail", None)
        if isinstance(detail, dict):
            code = cast(dict[str, Any], detail).get("code")
            if isinstance(code, str) and code:
                return code
    return "UNEXPECTED_ERROR"


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
        operation_type_value: str = "feedback_analysis"
        try:
            # Load operation
            operation = await db.get(Operation, operation_id)
            if not operation:
                logger.error(
                    "Operation not found",
                    extra={"operation_id": str(operation_id)},
                )
                return

            # Avoid ORM attribute access after rollback/expiration.
            operation_type_value = operation.operation_type

            # Update status to processing
            operation.status = "processing"
            operation.updated_at = dt.datetime.now(dt.UTC)
            await db.commit()

            logger.info(
                "Feedback generation started",
                extra={
                    "operation_id": str(operation_id),
                    "session_id": str(session_id),
                    "user_id": str(user_id),
                },
            )

            # Load user
            user = await db.get(User, user_id)
            if not user:
                logger.error(
                    "User not found for operation",
                    extra={
                        "user_id": str(user_id),
                        "operation_id": str(operation_id),
                    },
                )
                operation.status = "failed"
                operation.error_message = generate_user_friendly_message(
                    "USER_NOT_FOUND",
                    {"operation_type": operation_type_value},
                )
                operation.updated_at = dt.datetime.now(dt.UTC)
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
            try:
                feedback = InterviewFeedback(
                    session_id=session_id,
                    technical_accuracy_score=result.technical_accuracy_score,
                    communication_clarity_score=(
                        result.communication_clarity_score
                    ),
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
                db.add(feedback)

                # Convert result to dict for Operation.result
                result_dict = result.model_dump()
                result_dict["overall_score"] = overall_score

                operation.status = "completed"
                operation.result = result_dict
                operation.updated_at = dt.datetime.now(dt.UTC)

                # Persist feedback + operation update in one transaction.
                await db.flush()
                await db.commit()

            except IntegrityError:
                # Feedback already exists (duplicate session_id)
                logger.warning(
                    "Feedback already exists for session",
                    extra={"session_id": str(session_id)},
                )

                with suppress(Exception):
                    await db.rollback()

                operation.status = "failed"
                operation.error_message = generate_user_friendly_message(
                    "FEEDBACK_ALREADY_EXISTS",
                    {"operation_type": operation_type_value},
                )
                operation.updated_at = dt.datetime.now(dt.UTC)
                await db.commit()
                return

            except Exception as db_error:
                logger.error(
                    "Failed to store feedback",
                    extra={
                        "session_id": str(session_id),
                        "error": str(db_error),
                    },
                    exc_info=True,
                )

                with suppress(Exception):
                    await db.rollback()

                operation.status = "failed"
                operation.error_message = generate_user_friendly_message(
                    "DB_WRITE_FAILED",
                    {"operation_type": operation_type_value},
                )
                operation.updated_at = dt.datetime.now(dt.UTC)
                await db.commit()
                return

            logger.info(
                "Feedback generated and stored successfully",
                extra={
                    "operation_id": str(operation_id),
                    "session_id": str(session_id),
                    "overall_score": overall_score,
                },
            )

        except Exception as e:
            error_code = _extract_error_code(e)
            logger.error(
                "Error in feedback generation task",
                extra={
                    "operation_id": str(operation_id),
                    "error": _safe_error_message(e),
                },
                exc_info=True,
            )

            with suppress(Exception):
                await db.rollback()

            # Try to update operation status to failed
            try:
                operation = await db.get(Operation, operation_id)
                if operation:
                    operation.status = "failed"
                    operation.error_message = generate_user_friendly_message(
                        error_code,
                        {"operation_type": operation_type_value},
                    )
                    operation.updated_at = dt.datetime.now(dt.UTC)
                    await db.commit()
            except Exception as update_error:
                logger.error(
                    "Failed to update operation status",
                    extra={
                        "operation_id": str(operation_id),
                        "error": str(update_error),
                    },
                )
