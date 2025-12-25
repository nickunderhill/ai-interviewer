"""
Schemas for dashboard metrics.
"""

from pydantic import BaseModel, Field


class PracticedRole(BaseModel):
    """A job role that has been practiced."""

    title: str = Field(..., description="Job posting title")
    company: str = Field(..., description="Company name")
    count: int = Field(..., description="Number of sessions for this role", ge=0)


class DashboardMetrics(BaseModel):
    """Aggregated metrics for user dashboard."""

    completed_interviews: int = Field(..., description="Total number of completed interview sessions", ge=0)
    average_score: float | None = Field(
        None,
        description="Average overall score across all feedback (0-100)",
        ge=0,
        le=100,
    )
    total_questions_answered: int = Field(..., description="Total questions answered across all sessions", ge=0)
    most_practiced_roles: list[PracticedRole] = Field(
        default_factory=list, description="Top 5 most practiced job roles"
    )
