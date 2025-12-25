"""
Pydantic schemas for interview feedback API.
"""

import datetime as dt
from typing import List
from pydantic import BaseModel, ConfigDict, UUID4, field_validator


class FeedbackAnalysisResult(BaseModel):
    """Schema for OpenAI feedback analysis JSON response."""

    technical_accuracy_score: int
    communication_clarity_score: int
    problem_solving_score: int
    relevance_score: int
    technical_feedback: str
    communication_feedback: str
    problem_solving_feedback: str
    relevance_feedback: str
    overall_comments: str | None = None
    knowledge_gaps: List[str]
    learning_recommendations: List[str]

    @field_validator(
        "technical_accuracy_score",
        "communication_clarity_score",
        "problem_solving_score",
        "relevance_score",
    )
    @classmethod
    def clamp_score(cls, v: int) -> int:
        """Clamp scores to 0-100 range."""
        return max(0, min(100, v))


class InterviewFeedbackResponse(BaseModel):
    """Response schema for interview feedback."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    session_id: UUID4
    technical_accuracy_score: int
    communication_clarity_score: int
    problem_solving_score: int
    relevance_score: int
    overall_score: int
    technical_feedback: str
    communication_feedback: str
    problem_solving_feedback: str
    relevance_feedback: str
    overall_comments: str | None
    knowledge_gaps: List[str]
    learning_recommendations: List[str]
    created_at: dt.datetime
    updated_at: dt.datetime
