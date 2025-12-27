"""Operation schemas for API responses."""

import datetime as dt
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OperationResponse(BaseModel):
    """Response schema for async operations."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    operation_type: str
    status: str
    result: dict | None = None
    error_message: str | None = None
    parent_operation_id: UUID | None = None
    retry_count: int = 0
    created_at: dt.datetime
    updated_at: dt.datetime
