"""Background tasks for question generation."""

import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.interview_session import InterviewSession
from app.models.operation import Operation
from app.models.session_message import SessionMessage
from app.models.user import User
from app.services.question_generation_service import generate_question
from app.utils.error_messages import generate_user_friendly_message
from app.utils.error_handler import mask_secrets

logger = logging.getLogger(__name__)


def _safe_error_message(exc: Exception) -> str:
    if isinstance(exc, HTTPException) and isinstance(exc.detail, dict):
        msg = exc.detail.get("message") or exc.detail.get("code") or str(exc.detail)
        return mask_secrets(str(msg))

    return mask_secrets(str(exc))


def _extract_error_code(exc: Exception) -> str:
    if isinstance(exc, HTTPException) and isinstance(exc.detail, dict):
        code = exc.detail.get("code")
        if isinstance(code, str) and code:
            return code
    return "UNEXPECTED_ERROR"


async def generate_question_task(operation_id: UUID, session_id: UUID):
    """
    Background task to generate an interview question.

    Args:
        operation_id: UUID of the Operation to update
        session_id: UUID of the InterviewSession
    """
    async with AsyncSessionLocal() as db:
        operation: Operation | None = None
        operation_type_value: str = "question_generation"
        try:
            # Load operation
            operation = await db.get(Operation, operation_id)

            if not operation:
                logger.error(f"Operation {operation_id} not found")
                return

            # Avoid ORM attribute access after rollback/expiration.
            operation_type_value = operation.operation_type

            # Update to processing
            operation.status = "processing"
            await db.commit()

            # Load session with relationships
            result = await db.execute(
                select(InterviewSession)
                .where(InterviewSession.id == session_id)
                .options(
                    selectinload(InterviewSession.job_posting),
                    selectinload(InterviewSession.user).selectinload(User.resume),
                )
            )
            session = result.scalar_one_or_none()

            if not session:
                logger.error(f"Session {session_id} not found")
                operation.status = "failed"
                operation.error_message = generate_user_friendly_message(
                    "SESSION_NOT_FOUND",
                    {"operation_type": operation_type_value},
                )
                await db.commit()
                return

            # Generate question
            question_data = await generate_question(session)

            # Persist message + session update + operation completion in one commit.
            message: SessionMessage | None = None
            try:
                message = SessionMessage(
                    session_id=session.id,
                    message_type="question",
                    content=question_data["question_text"],
                    question_type=question_data["question_type"],
                )
                db.add(message)

                session.current_question_number += 1

                operation.status = "completed"
                operation.result = question_data

                # Surface DB issues early and ensure rollback removes partial state.
                await db.flush()
                await db.commit()

                await db.refresh(message)

                logger.info(
                    f"Question generated and stored successfully for operation {operation_id}"
                )
            except Exception as db_error:
                logger.error(
                    f"Failed to store question for session {session_id}: {str(db_error)}"
                )

                try:
                    await db.rollback()
                except Exception:
                    pass

                operation.status = "failed"
                operation.error_message = generate_user_friendly_message(
                    "DB_WRITE_FAILED",
                    {"operation_type": operation_type_value},
                )
                await db.commit()
                return

        except Exception as e:
            error_code = _extract_error_code(e)
            logger.error(
                f"Error in question generation task {operation_id}: {_safe_error_message(e)}",
                exc_info=True,
            )

            try:
                await db.rollback()
            except Exception:
                pass

            # Update operation with error
            try:
                op = operation or await db.get(Operation, operation_id)
                if op:
                    op.status = "failed"
                    op.error_message = generate_user_friendly_message(
                        error_code,
                        {"operation_type": operation_type_value},
                    )
                    await db.commit()
            except Exception as commit_error:
                logger.error(
                    f"Failed to update operation {operation_id} with error: {commit_error}"
                )
