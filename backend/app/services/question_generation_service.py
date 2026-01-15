"""Question generation service with dual-context approach."""

import logging

from app.models.interview_session import InterviewSession
from app.services.openai_service import OpenAIService

logger = logging.getLogger(__name__)


def get_question_type_for_round(question_number: int) -> str:
    """
    Determine question type based on round number.

    Rotation pattern: technical → behavioral → situational

    Args:
        question_number: Current question number (1-indexed)

    Returns:
        Question type: 'technical', 'behavioral', or 'situational'
    """
    types = ["technical", "behavioral", "situational"]
    # Use modulo to cycle through types (0-indexed)
    index = (question_number - 1) % len(types) if question_number > 0 else 0
    return types[index]


def build_question_prompt(
    job_title: str,
    job_company: str | None,
    job_description: str,
    tech_stack: str | None,
    experience_level: str | None,
    resume_content: str | None,
    question_type: str,
    language: str = "en",
) -> str:
    """
    Build dual-context prompt for question generation.

    Args:
        job_title: Job role title
        job_company: Company name (optional)
        job_description: Full job description
        tech_stack: Required technologies (optional)
        experience_level: Experience level (optional)
        resume_content: Candidate's resume (optional)
        question_type: Type of question to generate

    Returns:
        Formatted prompt string
    """
    company_text = f" at {job_company}" if job_company else ""
    tech_text = f"\nTech Stack: {tech_stack}" if tech_stack else ""
    exp_text = f"\nExperience Level: {experience_level}" if experience_level else ""

    # Build job context section
    job_context = f"""**Job Role:**
{job_title}{company_text}

**Job Description:**
{job_description}{tech_text}{exp_text}"""

    # Build candidate context section
    if resume_content:
        candidate_context = f"""
**Candidate Background:**
{resume_content}"""
    else:
        candidate_context = """
**Candidate Background:**
(No resume provided - generate question based on job requirements only)"""

    # Question type instructions
    type_instructions = {
        "technical": "Generate a technical interview question that tests specific skills, knowledge, or problem-solving ability relevant to the job requirements. If the candidate's resume is available, reference their background to make the question more personalized.",
        "behavioral": "Generate a behavioral interview question using the STAR format (Situation, Task, Action, Result). Ask about past experiences that demonstrate skills relevant to the job. If the candidate's resume is available, reference specific experiences mentioned.",
        "situational": "Generate a situational interview question presenting a hypothetical scenario related to the job role. Ask how the candidate would handle it. If the candidate's resume is available, make the scenario relevant to their experience level.",
    }

    instruction = type_instructions.get(question_type, type_instructions["technical"])

    # Language instruction based on job posting language
    language_instruction = ""
    if language == "ua":
        language_instruction = (
            "\n\n**IMPORTANT: Generate the question in UKRAINIAN language. The entire question must be in Ukrainian.**"
        )
    else:
        language_instruction = "\n\n**IMPORTANT: Generate the question in ENGLISH language.**"

    prompt = f"""You are an expert technical interviewer. Generate ONE interview question based on the context below.{language_instruction}

{job_context}
{candidate_context}

**Task:**
{instruction}

**Requirements:**
- Generate exactly ONE clear, specific question
- The question should be interview-ready (no meta-text or explanations)
- Make it relevant to both the job requirements and candidate's background
- Appropriate difficulty for the experience level
- Question should be open-ended to encourage detailed responses

Generate the question now:"""

    return prompt


async def generate_question(session: InterviewSession) -> dict[str, str]:
    """
    Generate an interview question using dual-context approach.

    Args:
        session: InterviewSession with loaded relationships (job_posting, user.resume)

    Returns:
        Dict with 'question_text' and 'question_type'

    Raises:
        HTTPException: If OpenAI call fails or context is invalid
    """
    # Validate session has required relationships loaded
    if not session.job_posting:
        logger.error(f"Session {session.id} missing job_posting relationship")
        raise ValueError("Session must have job_posting loaded")

    # Determine question type based on round
    question_type = get_question_type_for_round(session.current_question_number + 1)

    # Extract job posting details
    job_posting = session.job_posting
    job_title = job_posting.title
    job_company = job_posting.company
    job_description = job_posting.description
    tech_stack = job_posting.tech_stack
    experience_level = job_posting.experience_level

    # Extract resume content (may be None)
    resume_content = None
    if hasattr(session.user, "resume") and session.user.resume:
        resume_content = session.user.resume.content

    # Build prompt
    prompt = build_question_prompt(
        job_title=job_title,
        job_company=job_company,
        job_description=job_description,
        tech_stack=tech_stack,
        experience_level=experience_level,
        resume_content=resume_content,
        question_type=question_type,
        language=job_posting.language,
    )

    # Call OpenAI service
    openai_service = OpenAIService(session.user)

    try:
        question_text = await openai_service.generate_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=200,  # Single question shouldn't need more
            context={
                "operation_type": "question_generation",
                "session_id": str(session.id),
            },
        )

        # Clean up response (remove quotes or extra whitespace)
        question_text = question_text.strip().strip('"').strip("'")

        logger.info(f"Generated {question_type} question for session {session.id}")

        return {
            "question_text": question_text,
            "question_type": question_type,
        }

    except Exception as e:
        logger.error(f"Failed to generate question for session {session.id}: {str(e)}")
        raise
