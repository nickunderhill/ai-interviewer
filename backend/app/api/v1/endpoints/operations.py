"""Operations API endpoints for polling async operation status."""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.operation import Operation
from app.models.user import User
from app.schemas.operation import OperationResponse
from app.services.operation_service import retry_operation

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/{operation_id}",
    response_model=OperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get operation status",
)
async def get_operation_status(
    operation_id: UUID = Path(..., description="Operation UUID"),
    db: AsyncSession = Depends(get_db),
) -> OperationResponse:
    """
    Get the current status of an async operation.

    Frontend should poll this endpoint every 2-3 seconds until
    status is 'completed' or 'failed'.

    - **operation_id**: UUID of the operation
    - Returns operation with status and result/error_message
    - Returns 404 if operation not found
    """
    result = await db.execute(select(Operation).where(Operation.id == operation_id))
    operation = result.scalar_one_or_none()

    if not operation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "OPERATION_NOT_FOUND",
                "message": "Operation not found. It may have expired or never existed.",
            },
        )

    return OperationResponse.model_validate(operation)


@router.post(
    "/{operation_id}/retry",
    response_model=OperationResponse,
    status_code=status.HTTP_200_OK,
    summary="Retry failed operation",
)
async def retry_operation_endpoint(
    operation_id: UUID = Path(..., description="Operation UUID to retry"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> OperationResponse:
    """
    Manually retry a failed operation.

    **IMPORTANT LIMITATION**: This endpoint is currently non-functional due to
    architectural constraints. Operations do not store session_id, which is
    required to trigger background tasks. See Story 8.4 review findings.

    Future implementation requires:
    - Add session_id field to Operation model
    - OR redesign retry to work at session level (e.g., /sessions/{id}/retry-generation)

    Creates a new operation with the same parameters and links it to the
    original via parent_operation_id.

    - **operation_id**: UUID of the failed operation
    - Returns new operation with 'pending' status
    - Returns 400 if operation not failed or not found
    """
    try:
        new_operation = await retry_operation(
            operation_id=operation_id,
            user_id=current_user.id,
            db=db,
        )
        return OperationResponse.model_validate(new_operation)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Retry operation failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retry operation",
        )
