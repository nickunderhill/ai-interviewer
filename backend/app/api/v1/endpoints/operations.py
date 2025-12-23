"""Operations API endpoints for polling async operation status."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.operation import Operation
from app.schemas.operation import OperationResponse

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
