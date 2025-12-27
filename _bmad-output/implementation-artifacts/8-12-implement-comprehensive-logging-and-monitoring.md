# Story 8.12: Implement Comprehensive Logging and Monitoring

Status: done

## Story

As a developer, I want to implement structured logging throughout the
application, so that we can diagnose issues and monitor system health.

## Acceptance Criteria

1. **Given** the application is running **When** any significant event occurs
   (user registration, session creation, AI operation start/complete/fail,
   errors) **Then** structured logs are written with timestamp, log level (INFO,
   WARNING, ERROR), context (user_id, session_id, operation_id), and message
   **And** sensitive data (passwords, API keys, PII) is never logged **And**
   logs are written to stdout for container environments **And** log format is
   JSON for easy parsing **And** error logs include stack traces **And** logs
   can be aggregated and searched for troubleshooting **And** follows NFR21,
   NFR22 for observability ✅

## Tasks / Subtasks

- [x] Task 1: Implement JSON logging configuration (AC: #1)

  - [x] Create `backend/app/core/logging.py` with JSON formatter
  - [x] Configure root logger to stdout
  - [x] Ensure `exc_info=True` includes stack traces

- [x] Task 2: Add sensitive data scrubbing (AC: #1)

  - [x] Implement scrubber for keys: password, api_key, token, secret
  - [x] Ensure error contexts never include request bodies containing secrets

- [x] Task 3: Add logging at key lifecycle points (AC: #1)

  - [x] Auth: register/login/logout (without secrets)
  - [x] Sessions: create/complete
  - [x] Operations: start/complete/fail/retry
  - [x] OpenAI calls: start/end/error category

- [x] Task 4: Ensure frontend logs are minimal and safe (AC: #1)

  - [x] Log boundary-caught errors to console
  - [x] Avoid logging tokens or user inputs

- [x] Task 5: Add tests for logging scrubbing (AC: #1)
  - [x] Verify scrubber masks sensitive fields
  - [x] Verify JSON output is valid

## Dev Notes

### Critical Architecture Requirements

- Logs must be JSON and go to stdout (Docker-friendly)
- Never log secrets (passwords, JWTs, API keys)
- Include correlation fields (user_id, session_id, operation_id)
- Prefer structured logging fields over formatted strings

### File Structure

```
backend/app/
├── core/
│   └── logging.py
├── middleware/
│   └── request_logging.py     # optional request/response timing
└── tests/
    └── core/
        └── test_logging.py
```

### Implementation Details

**JSON Formatter + Scrubber:**

```python
# backend/app/core/logging.py
import json
import logging
from datetime import datetime, timezone

SENSITIVE_KEYS = {"password", "api_key", "token", "secret", "authorization"}

def scrub(obj):
    if isinstance(obj, dict):
        return {
            k: ("***MASKED***" if k.lower() in SENSITIVE_KEYS else scrub(v))
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [scrub(v) for v in obj]
    return obj

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Merge structured extras if present
        extras = getattr(record, "extra", None)
        if isinstance(extras, dict):
            payload.update(scrub(extras))

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload)

def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
```

**Usage Example:**

```python
logger.info(
  "AI operation started",
  extra={"operation_id": op_id, "session_id": session_id, "user_id": user_id},
)
```

### Testing Requirements

- Scrubber masks nested sensitive fields
- Formatter produces valid JSON

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.12]
- [Source: _bmad-output/project-context.md#Error-Handling]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Adds JSON logging + sensitive data scrubbing
- Defines where to log key lifecycle events
- Implemented structured logging in Auth, Sessions, Operations, and OpenAI
  services
- Verified sensitive data scrubbing with tests
- Verified frontend logging is minimal and safe
- All backend tests passed (485 tests)

## File List

- backend/app/core/logging_config.py
- backend/app/core/monitoring.py
- backend/app/utils/error_handler.py
- backend/app/api/v1/endpoints/auth.py
- backend/app/services/session_service.py
- backend/app/services/openai_service.py
- backend/app/tasks/question_tasks.py
- backend/app/tasks/feedback_tasks.py
- backend/tests/core/test_logging.py

## Change Log

- 2025-12-27: Implemented structured logging and monitoring (Story 8.12)
