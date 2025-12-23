"""Operation schemas for API responses."""

import datetime as dt
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OperationResponse(BaseModel):
    """Response schema for async operations."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    operation_type: str
    status: str
    result: Optional[dict] = None
    error_message: Optional[str] = None
    created_at: dt.datetime
    updated_at: dt.datetime
