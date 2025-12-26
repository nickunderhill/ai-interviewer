# Story 8.10: Implement AI Operation Timeout and Resource Management

Status: ready-for-dev

## Story

As a developer, I want to implement timeouts and resource limits for AI
operations, so that the system remains stable under load.

## Acceptance Criteria

1. **Given** AI operations are running **When** processing question generation
   or feedback analysis **Then** each OpenAI API call has a 30-second timeout
   **And** if timeout is exceeded, the operation is marked as 'failed' with
   appropriate error message **And** background tasks have maximum execution
   time limits (e.g., 2 minutes) **And** connection pools to OpenAI are properly
   managed (max concurrent requests) **And** the system handles concurrent
   operations gracefully without resource exhaustion **And** memory usage
   remains stable during multiple operations **And** follows NFR16, NFR17, NFR19
   for reliability and stability ✅

## Tasks / Subtasks

- [ ] Task 1: Add OpenAI API call timeouts (AC: #1)

  - [ ] Configure OpenAI client with timeout=30s
  - [ ] Wrap API calls with asyncio.wait_for
  - [ ] Handle timeout exceptions as retriable or failed
  - [ ] Map timeout to user-friendly error message (Story 8.2)

- [ ] Task 2: Add background task execution timeout (AC: #1)

  - [ ] Wrap background tasks with max execution time (2 minutes)
  - [ ] Cancel tasks that exceed limit
  - [ ] Mark Operation as failed on timeout
  - [ ] Log timeout events for monitoring

- [ ] Task 3: Implement concurrency limits for OpenAI calls (AC: #1)

  - [ ] Add asyncio.Semaphore for max concurrent OpenAI requests
  - [ ] Configure max concurrency (e.g., 5 concurrent calls)
  - [ ] Queue excess requests
  - [ ] Prevent thundering herd on retries

- [ ] Task 4: Manage OpenAI client lifecycle (AC: #1)

  - [ ] Reuse OpenAI client instances where safe
  - [ ] Ensure clients are properly closed
  - [ ] Prevent connection leaks
  - [ ] Add connection pooling configuration

- [ ] Task 5: Add memory usage monitoring (AC: #1)

  - [ ] Track memory usage during operations
  - [ ] Log memory spikes
  - [ ] Ensure large prompts/responses are handled efficiently
  - [ ] Add limits on prompt size

- [ ] Task 6: Add stress tests for concurrent operations (AC: #1)
  - [ ] Create test for 10 concurrent operations
  - [ ] Verify semaphore limits work
  - [ ] Ensure operations complete or fail gracefully
  - [ ] Verify no resource exhaustion

## Dev Notes

### Critical Architecture Requirements

**Backend:**

- **Timeouts:** 30s per OpenAI API call
- **Task Limits:** 2-minute max execution for background tasks
- **Concurrency:** Limit concurrent OpenAI requests to prevent exhaustion
- **Stability:** Graceful failure with operation status updates
- **Logging:** Log timeouts and resource issues

**Integration with Epic 8:**

- Uses retry logic from Story 8.1
- Uses user-friendly messages from Story 8.2
- Updates operation status from Story 8.3

### File Structure

```
backend/app/
├── services/
│   └── openai_service.py      # Add timeouts and concurrency limits
├── utils/
│   ├── concurrency.py         # Semaphore and resource management
│   └── timeouts.py            # Timeout wrappers
├── services/
│   ├── question_generation.py # Add task execution timeout
│   └── feedback_analysis.py   # Add task execution timeout
└── tests/
    └── stress/
        └── test_concurrent_operations.py
```

### Implementation Details

**OpenAI Timeout Wrapper:**

```python
# backend/app/utils/timeouts.py
import asyncio
from typing import Any, Callable, Awaitable
import logging

logger = logging.getLogger(__name__)

class TimeoutError(Exception):
    """Custom timeout error for AI operations."""
    pass

async def with_timeout(
    coro: Awaitable[Any],
    timeout_seconds: float,
    operation_name: str,
    context: dict | None = None,
) -> Any:
    """Execute coroutine with timeout and logging."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        logger.warning(
            "Operation timed out",
            extra={
                "operation": operation_name,
                "timeout_seconds": timeout_seconds,
                **(context or {}),
            },
        )
        raise TimeoutError(f"{operation_name} timed out after {timeout_seconds}s")
```

**Concurrency Semaphore:**

```python
# backend/app/utils/concurrency.py
import asyncio

# Global semaphore for OpenAI calls
OPENAI_MAX_CONCURRENT = 5
openai_semaphore = asyncio.Semaphore(OPENAI_MAX_CONCURRENT)

async def with_openai_semaphore(coro):
    """Limit concurrent OpenAI API calls."""
    async with openai_semaphore:
        return await coro
```

**Updated OpenAI Service:**

```python
# backend/app/services/openai_service.py (excerpt)
from app.utils.timeouts import with_timeout, TimeoutError
from app.utils.concurrency import with_openai_semaphore

OPENAI_TIMEOUT_SECONDS = 30

class OpenAIService:
    async def generate_completion(self, prompt: str, **kwargs) -> str:
        """Generate completion with timeout and concurrency limits."""
        async def make_request():
            return await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                **kwargs
            )

        try:
            response = await with_openai_semaphore(
                with_timeout(
                    make_request(),
                    timeout_seconds=OPENAI_TIMEOUT_SECONDS,
                    operation_name="openai_chat_completion",
                )
            )
            return response.choices[0].message.content
        except TimeoutError:
            # Map to custom error code for user-friendly messaging
            raise ServerError(
                "AI service timed out. Please try again.",
                "TIMEOUT"
            )
```

**Background Task Execution Timeout:**

```python
# backend/app/services/question_generation.py (excerpt)
from app.utils.timeouts import with_timeout

TASK_TIMEOUT_SECONDS = 120  # 2 minutes

async def generate_question_background(operation_id: str, session_id: str, db: AsyncSession):
    """Background task with execution timeout."""
    async def task_logic():
        # existing question generation logic
        ...

    try:
        await with_timeout(
            task_logic(),
            timeout_seconds=TASK_TIMEOUT_SECONDS,
            operation_name="question_generation_task",
            context={"operation_id": operation_id, "session_id": session_id},
        )
    except TimeoutError:
        # Mark operation as failed
        await mark_operation_failed(
            operation_id,
            error_code="TIMEOUT",
            error_message="Question generation took too long and was cancelled. Please try again.",
            db=db,
        )
```

**Prompt Size Limits:**

```python
# backend/app/utils/validators.py
MAX_PROMPT_CHARS = 20000

def validate_prompt_size(prompt: str) -> None:
    if len(prompt) > MAX_PROMPT_CHARS:
        raise ValueError("Request too large. Please shorten your input.")
```

**Stress Test Example:**

```python
# backend/tests/stress/test_concurrent_operations.py
import pytest
import asyncio

@pytest.mark.asyncio
async def test_concurrent_openai_operations(openai_service):
    """Test that concurrency semaphore prevents resource exhaustion."""
    prompts = [f"Test prompt {i}" for i in range(10)]

    async def run_prompt(prompt):
        return await openai_service.generate_completion(prompt)

    tasks = [asyncio.create_task(run_prompt(p)) for p in prompts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Ensure no crashes and results are handled
    assert len(results) == 10
```

### Testing Requirements

**Test Coverage:**

- OpenAI calls timeout after 30 seconds
- Background tasks timeout after 2 minutes
- Concurrency limits enforced
- Operations marked failed on timeout
- User-friendly timeout messages
- No resource leaks under concurrent load

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.10]
- [NFR16, NFR17: Stability and resource management]
- [NFR19: Graceful error handling]
- [Story 8.1: Retry logic]
- [Story 8.2: User-friendly error messages]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Story created with comprehensive timeout and resource management
- Adds per-call and per-task timeouts
- Adds concurrency semaphore for OpenAI calls
- Adds stress tests
- Ready for dev implementation
