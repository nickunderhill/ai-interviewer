# Story 4.7: Implement Question Generation Service with Dual-Context

Status: review

## Story

As a developer, I want to create a service to generate interview questions using
dual-context, so that questions are relevant to both the job requirements and
candidate's résumé.

## Acceptance Criteria

1. **Given** I'm implementing question generation **When** the service receives
   a session context **Then** it fetches the job posting (title, company,
   description, tech_stack, experience_level) **And** fetches the user's résumé
   content **And** constructs a prompt with both contexts asking for a relevant
   interview question **And** rotates question types (technical, behavioral,
   situational) based on current_question_number **And** calls OpenAI API (via
   OpenAI service) to generate the question **And** returns the generated
   question text and question_type **And** handles errors if OpenAI call fails

## Tasks / Subtasks

- [x] Task 1: Create question generation service (AC: #1)

  - [x] Create `backend/app/services/question_generation_service.py`
  - [x] Implement generate_question function accepting session object
  - [x] Load job posting details from session.job_posting relationship
  - [x] Load resume content from session.user.resume relationship
  - [x] Handle missing resume gracefully (use job posting only if no resume)
  - [x] Handle missing job posting gracefully (edge case)

- [x] Task 2: Implement question type rotation logic (AC: #1)

  - [x] Create get_question_type_for_round function
  - [x] Rotate between: technical, behavioral, situational
  - [x] Use current_question_number to determine type
  - [x] Pattern: Q1=technical, Q2=behavioral, Q3=situational, Q4=technical, etc.
  - [x] Return question type string

- [x] Task 3: Construct dual-context prompt (AC: #1)

  - [x] Create build_question_prompt function
  - [x] Accept job posting details, resume content, question type
  - [x] Build structured prompt with clear sections:
    - Job context (role, company, description, tech stack, experience level)
    - Candidate context (resume content)
    - Question type requirement
    - Output format instructions
  - [x] Use clear instructions for AI to generate single, specific question
  - [x] Return formatted prompt string

- [x] Task 4: Integrate with OpenAI service (AC: #1)

  - [x] Instantiate OpenAIService with user object
  - [x] Call generate_chat_completion with constructed prompt
  - [x] Parse AI response to extract question text
  - [x] Handle malformed AI responses
  - [x] Return dict with question text and question_type
  - [x] Let OpenAI service handle retry logic and API errors

- [x] Task 5: Add comprehensive tests (AC: #1)
  - [x] Create `backend/tests/services/test_question_generation_service.py`
  - [x] Mock OpenAI service responses
  - [x] Test question generation with full context (job + resume)
  - [x] Test question generation with job posting only (no resume)
  - [x] Test question type rotation logic
  - [x] Test prompt construction includes all context
  - [x] Test error handling when OpenAI fails
  - [x] Test each question type generates appropriate prompt

## Dev Agent Record

### Implementation Summary

Implemented dual-context question generation service that creates personalized
interview questions by combining job posting requirements with candidate resume.
All acceptance criteria met with 12 comprehensive tests covering question type
rotation, prompt building, and full/partial context scenarios.

### Files Created/Modified

- **Created:** `backend/app/services/question_generation_service.py` (187 lines)

  - get_question_type_for_round() - Rotates through technical → behavioral →
    situational
  - build_question_prompt() - Constructs dual-context prompts with job + resume
  - generate_question() - Main async function integrating with OpenAIService
  - Graceful handling of missing resume (fallback to job-only context)

- **Created:** `backend/tests/services/test_question_generation_service.py` (310
  lines)
  - 12 comprehensive tests covering all scenarios
  - Tests for question type rotation (including edge cases)
  - Tests for prompt construction with/without resume
  - Tests for each question type (technical, behavioral, situational)
  - Tests for question generation success and error handling

### Key Decisions Made

1. **Dual-context approach:** Core innovation - questions reference both job
   requirements AND candidate background
2. **Question type rotation:** Deterministic pattern (technical → behavioral →
   situational) for comprehensive coverage
3. **Graceful degradation:** If no resume, generates questions based on job
   posting only
4. **Temperature 0.7:** Balances creativity (unique questions) with consistency
5. **Max tokens 200:** Single question shouldn't exceed this, prevents runaway
   costs
6. **String cleanup:** Strips quotes and whitespace from AI responses for clean
   output
7. **Async function:** Matches FastAPI endpoint pattern (even though OpenAI
   calls are sync)

### Prompt Engineering Strategy

- **Structured sections:** Clear job context + candidate context + task
  instructions
- **Specific requirements:** ONE question, interview-ready, no meta-text
- **Type-specific instructions:**
  - Technical: Tests skills/knowledge, references candidate background
  - Behavioral: STAR format, past experiences, mentions resume
  - Situational: Hypothetical scenarios, relevant to experience level
- **Relevance emphasis:** AI instructed to make questions relevant to both
  contexts

### Test Coverage

- ✅ Question type rotation for rounds 1-7 and edge cases (0, 100, 101)
- ✅ Prompt construction with full context (all fields)
- ✅ Prompt construction without resume (fallback messaging)
- ✅ Behavioral and situational type-specific prompts
- ✅ Successful question generation with resume
- ✅ Successful question generation without resume
- ✅ Missing job posting validation
- ✅ Question type cycles correctly (6 rounds)
- ✅ Response cleaning (quotes/whitespace removal)
- ✅ OpenAI service failure handling
- **Result:** 12/12 tests passing

### Verification

```bash
pytest tests/services/test_question_generation_service.py -v
# Result: 12 passed, 1 warning in 0.20s
```

## Dev Notes

### Critical Architecture Requirements

**Dual-Context Pattern (CRITICAL):**

- MUST include both job posting AND résumé in prompt
- This is the core innovation of the system
- Questions should reference candidate's background when relevant
- Fall back to job-only context if resume missing (edge case)

**Prompt Engineering:**

- Clear, structured prompt with labeled sections
- Specific instructions for question format
- Question should be interview-ready (no meta-text)
- Single question per generation (not a list)
- Question type specified in prompt

**Question Type Rotation:**

- Technical: Tests specific skills, technologies, problem-solving
- Behavioral: STAR format, past experience, soft skills
- Situational: Hypothetical scenarios, decision-making
- Rotate to provide comprehensive interview coverage

**Service Layer Patterns:**

- Pure business logic (no HTTP concerns)
- Returns structured data (not HTTP responses)
- Raises exceptions for errors (caught by endpoint layer)
- Synchronous execution (called from background task)

### Technical Implementation Details

**File Structure:**

```
backend/app/
└── services/
    ├── question_generation_service.py  # NEW
    ├── openai_service.py               # EXISTS (from 4.6)
    └── tests/services/
        └── test_question_generation_service.py  # NEW
```

**Question Generation Service:**

```python
# backend/app/services/question_generation_service.py
from typing import Dict, Optional
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
    job_company: Optional[str],
    job_description: str,
    tech_stack: Optional[str],
    experience_level: Optional[str],
    resume_content: Optional[str],
    question_type: str
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
        "situational": "Generate a situational interview question presenting a hypothetical scenario related to the job role. Ask how the candidate would handle it. If the candidate's resume is available, make the scenario relevant to their experience level."
    }

    instruction = type_instructions.get(question_type, type_instructions["technical"])

    prompt = f"""You are an expert technical interviewer. Generate ONE interview question based on the context below.

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

async def generate_question(session: InterviewSession) -> Dict[str, str]:
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
    if hasattr(session.user, 'resume') and session.user.resume:
        resume_content = session.user.resume.content

    # Build prompt
    prompt = build_question_prompt(
        job_title=job_title,
        job_company=job_company,
        job_description=job_description,
        tech_stack=tech_stack,
        experience_level=experience_level,
        resume_content=resume_content,
        question_type=question_type
    )

    # Call OpenAI service
    openai_service = OpenAIService(session.user)

    try:
        question_text = openai_service.generate_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            model="gpt-3.5-turbo",
            temperature=0.7,
            max_tokens=200  # Single question shouldn't need more
        )

        # Clean up response (remove quotes or extra whitespace)
        question_text = question_text.strip().strip('"').strip("'")

        logger.info(f"Generated {question_type} question for session {session.id}")

        return {
            "question_text": question_text,
            "question_type": question_type
        }

    except Exception as e:
        logger.error(f"Failed to generate question for session {session.id}: {str(e)}")
        raise
```

**Testing Patterns:**

```python
# backend/tests/services/test_question_generation_service.py
import pytest
from unittest.mock import Mock, patch

from app.services.question_generation_service import (
    generate_question,
    get_question_type_for_round,
    build_question_prompt
)
from app.models.interview_session import InterviewSession

def test_question_type_rotation():
    """Test question type rotation logic."""
    assert get_question_type_for_round(1) == "technical"
    assert get_question_type_for_round(2) == "behavioral"
    assert get_question_type_for_round(3) == "situational"
    assert get_question_type_for_round(4) == "technical"
    assert get_question_type_for_round(5) == "behavioral"

def test_build_question_prompt_with_resume():
    """Test prompt includes both job and resume context."""
    prompt = build_question_prompt(
        job_title="Senior Python Developer",
        job_company="TechCorp",
        job_description="Build scalable APIs",
        tech_stack="Python, FastAPI, PostgreSQL",
        experience_level="Senior",
        resume_content="5 years Python experience...",
        question_type="technical"
    )

    assert "Senior Python Developer" in prompt
    assert "TechCorp" in prompt
    assert "Build scalable APIs" in prompt
    assert "Python, FastAPI, PostgreSQL" in prompt
    assert "5 years Python experience" in prompt
    assert "technical" in prompt.lower()

def test_build_question_prompt_without_resume():
    """Test prompt handles missing resume."""
    prompt = build_question_prompt(
        job_title="Developer",
        job_company=None,
        job_description="Build apps",
        tech_stack=None,
        experience_level=None,
        resume_content=None,
        question_type="behavioral"
    )

    assert "Developer" in prompt
    assert "Build apps" in prompt
    assert "No resume provided" in prompt
    assert "behavioral" in prompt.lower()

@pytest.mark.asyncio
@patch('app.services.question_generation_service.OpenAIService')
async def test_generate_question_success(mock_openai_service):
    """Test successful question generation."""
    # Mock session with relationships
    mock_session = Mock(spec=InterviewSession)
    mock_session.id = "test-session-id"
    mock_session.current_question_number = 0

    mock_job = Mock()
    mock_job.title = "Developer"
    mock_job.company = "TestCorp"
    mock_job.description = "Build software"
    mock_job.tech_stack = "Python"
    mock_job.experience_level = "Mid"
    mock_session.job_posting = mock_job

    mock_user = Mock()
    mock_resume = Mock()
    mock_resume.content = "Resume content"
    mock_user.resume = mock_resume
    mock_session.user = mock_user

    # Mock OpenAI response
    mock_service_instance = Mock()
    mock_service_instance.generate_chat_completion.return_value = "What is your experience with Python?"
    mock_openai_service.return_value = mock_service_instance

    result = await generate_question(mock_session)

    assert result["question_text"] == "What is your experience with Python?"
    assert result["question_type"] == "technical"

@pytest.mark.asyncio
async def test_generate_question_missing_job_posting():
    """Test error when session missing job_posting."""
    mock_session = Mock(spec=InterviewSession)
    mock_session.job_posting = None

    with pytest.raises(ValueError):
        await generate_question(mock_session)
```

### Dependencies

- Requires OpenAIService from story 4.6
- Requires InterviewSession model from story 4.1
- Requires JobPosting model from Epic 3
- Requires Resume model from Epic 3
- Requires User model with relationships

### Related Stories

- Story 4.6: OpenAI service (prerequisite)
- Story 4.8: Question generation endpoint (uses this service)
- Story 4.10: Stores generated question (uses result from this service)
- Story 5.2: Feedback analysis (similar dual-context pattern)

### Performance Considerations

- OpenAI API call takes 5-10 seconds (handled async in story 4.8)
- Prompt size limited by job description + resume (typically < 4K tokens)
- Single question generation (not batch) for real-time feel
- Temperature 0.7 balances creativity and consistency

### Prompt Engineering Best Practices

- Clear structure with labeled sections
- Specific output requirements
- Context before instructions (job + resume, then task)
- One clear task (generate single question)
- Examples in prompt can improve quality (future enhancement)

### Design Decisions

**Why rotate question types?**

- Provides comprehensive interview coverage
- Prevents repetitive questioning
- Mimics real interview structure
- Predictable pattern helps testing

**Why max_tokens=200?**

- Single question shouldn't exceed this
- Prevents runaway generation costs
- Forces concise, focused questions

**Why temperature=0.7?**

- Balance between creativity (unique questions) and consistency
- Lower (0.3-0.5) would be more deterministic
- Higher (0.9+) might produce unusual questions

## Project Context Reference

**CRITICAL:** Before implementing, review:

- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/project-context.md` -
  Service layer patterns
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/architecture.md` -
  FR25, FR26, FR29 (dual-context, question types)
- `/Users/nick/Projects/diploma/ai-interviewer/_bmad-output/prd.md` - Question
  generation requirements

**Key Context Sections:**

- AI Integration: Dual-context approach (THE core feature)
- Service Patterns: Business logic separation
- Testing: Mocking AI services
