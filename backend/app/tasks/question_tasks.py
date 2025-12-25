"""Background tasks for question generation."""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.database import AsyncSessionLocal
from app.models.interview_session import InterviewSession
from app.models.operation import Operation
from app.models.session_message import SessionMessage
from app.models.user import User
from app.services.question_generation_service import generate_question

logger = logging.getLogger(__name__)


async def generate_question_task(operation_id: UUID, session_id: UUID):
    """
    Background task to generate an interview question.

    Args:
        operation_id: UUID of the Operation to update
        session_id: UUID of the InterviewSession
    """
    async with AsyncSessionLocal() as db:
        try:
            # Load operation
            result = await db.execute(select(Operation).where(Operation.id == operation_id))
            operation = result.scalar_one_or_none()

            if not operation:
                logger.error(f"Operation {operation_id} not found")
                return

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
                operation.error_message = "Session not found"
                await db.commit()
                return

            # Generate question
            question_data = await generate_question(session)

            # Store question as SessionMessage (atomic with session update)
            try:
                # Create message record
                message = SessionMessage(
                    session_id=session.id,
                    message_type="question",
                    content=question_data["question_text"],
                    question_type=question_data["question_type"],
                )
                db.add(message)

                # Increment session question number
                session.current_question_number += 1

                # Commit both changes atomically
                await db.commit()
                await db.refresh(message)

                logger.info(
                    f"Question stored as message {message.id} for session {session_id}, "
                    f"question number now {session.current_question_number}"
                )

            except Exception as db_error:
                logger.error(f"Failed to store question in session {session_id}: {str(db_error)}")
                await db.rollback()

                operation.status = "failed"
                operation.error_message = "Failed to store question in database"
                await db.commit()
                return

            # Update operation with result
            operation.status = "completed"
            operation.result = question_data
            await db.commit()

            logger.info(f"Question generated and stored successfully for operation {operation_id}")

        except Exception as e:
            logger.error(
                f"Error in question generation task {operation_id}: {str(e)}",
                exc_info=True,
            )

            # Update operation with error
            try:
                operation.status = "failed"
                operation.error_message = str(e)
                await db.commit()
            except Exception as commit_error:
                logger.error(f"Failed to update operation {operation_id} with error: {commit_error}")
