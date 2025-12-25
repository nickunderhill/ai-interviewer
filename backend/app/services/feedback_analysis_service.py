"""
Feedback analysis service for generating AI-powered interview feedback.
"""

import json
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.interview_session import InterviewSession
from app.models.user import User
from app.schemas.feedback import FeedbackAnalysisResult
from app.services.openai_service import OpenAIService


async def analyze_session(
    db: AsyncSession,
    session_id: UUID,
    current_user: User,
) -> FeedbackAnalysisResult:
    """
    Analyze a completed interview session and generate comprehensive feedback.

    Args:
        db: Database session
        session_id: UUID of the interview session to analyze
        current_user: User requesting the analysis

    Returns:
        FeedbackAnalysisResult with scores, feedback text, gaps, and recommendations

    Raises:
        HTTPException: 404 if session not found, 400 if data missing, 502 if AI parsing fails
    """
    # Load session with all required relationships
    stmt = (
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .where(InterviewSession.user_id == current_user.id)
        .options(
            selectinload(InterviewSession.job_posting),
            selectinload(InterviewSession.messages),
        )
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "SESSION_NOT_FOUND", "message": "Session not found"},
        )

    # Load user's resume
    user_stmt = (
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.resume))
    )
    user_result = await db.execute(user_stmt)
    user = user_result.scalar_one()

    if not user.resume:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "RESUME_REQUIRED",
                "message": "Resume is required for feedback analysis",
            },
        )

    if not session.job_posting:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "JOB_POSTING_REQUIRED",
                "message": "Job posting is required for feedback analysis",
            },
        )

    # Build Q&A transcript
    qa_pairs = []
    for msg in sorted(session.messages, key=lambda m: m.created_at):
        if msg.message_type == "question":
            qa_pairs.append({"question": msg.content, "answer": None})
        elif msg.message_type == "answer" and qa_pairs:
            qa_pairs[-1]["answer"] = msg.content

    if not qa_pairs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "NO_ANSWERS",
                "message": "Session has no Q&A pairs to analyze",
            },
        )

    # Build prompt for OpenAI
    prompt = _build_analysis_prompt(
        job_posting=session.job_posting,
        resume_content=user.resume.content,
        qa_pairs=qa_pairs,
    )

    # Call OpenAI
    openai_service = OpenAIService(current_user)
    raw_response = openai_service.generate_chat_completion(
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse and validate response
    try:
        data = json.loads(raw_response)
        result = FeedbackAnalysisResult.model_validate(data)
        return result
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "code": "FEEDBACK_PARSE_FAILED",
                "message": f"AI feedback response could not be parsed: {str(e)}",
            },
        ) from e


def _build_analysis_prompt(
    job_posting,
    resume_content: str,
    qa_pairs: list[dict],
) -> str:
    """
    Build the prompt for OpenAI feedback analysis.

    Args:
        job_posting: JobPosting model instance
        resume_content: Resume text content
        qa_pairs: List of dicts with 'question' and 'answer' keys

    Returns:
        Formatted prompt string
    """
    tech_stack_str = (
        ", ".join(job_posting.tech_stack) if job_posting.tech_stack else "Not specified"
    )

    qa_transcript = "\n\n".join(
        f"Q{i+1}: {pair['question']}\nA{i+1}: {pair.get('answer', '[No answer provided]')}"
        for i, pair in enumerate(qa_pairs)
    )

    prompt = f"""You are an expert technical interviewer analyzing a candidate's interview performance.

JOB POSTING:
Title: {job_posting.title}
Company: {job_posting.company or 'Not specified'}
Description: {job_posting.description}
Experience Level: {job_posting.experience_level or 'Not specified'}
Tech Stack: {tech_stack_str}

CANDIDATE'S RESUME:
{resume_content}

INTERVIEW TRANSCRIPT:
{qa_transcript}

Analyze this interview across 4 dimensions and provide scores (0-100) and detailed feedback for each:

1. Technical Accuracy: Correctness of technical concepts, algorithms, and implementation details
2. Communication Clarity: Ability to explain complex concepts clearly and structure responses
3. Problem-Solving Approach: Methodology, analytical thinking, and problem decomposition
4. Relevance to Job Requirements: Alignment with the job posting's requirements and tech stack

Also identify:
- Knowledge Gaps: Specific areas where the candidate showed weaknesses or lack of knowledge
- Learning Recommendations: Concrete suggestions for improvement with specific resources or topics

Respond ONLY with a JSON object (no markdown, no additional text) in this exact format:
{{
  "technical_accuracy_score": 0,
  "communication_clarity_score": 0,
  "problem_solving_score": 0,
  "relevance_score": 0,
  "technical_feedback": "Detailed feedback on technical accuracy...",
  "communication_feedback": "Detailed feedback on communication clarity...",
  "problem_solving_feedback": "Detailed feedback on problem-solving approach...",
  "relevance_feedback": "Detailed feedback on relevance to job requirements...",
  "overall_comments": "Summary of overall performance...",
  "knowledge_gaps": ["Gap 1", "Gap 2", "Gap 3"],
  "learning_recommendations": ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
}}

Ensure all scores are integers between 0 and 100, and provide actionable, specific feedback.
"""
    return prompt
