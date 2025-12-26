# Story 8.14: Implement CORS and Security Headers

Status: ready-for-dev

## Story

As a developer, I want to configure CORS and security headers, so that the
application is protected against common web vulnerabilities.

## Acceptance Criteria

1. **Given** the FastAPI backend is deployed **When** the application is
   accessed **Then** CORS is configured to allow only the frontend origin (not
   '\*') **And** security headers are set: X-Content-Type-Options: nosniff,
   X-Frame-Options: DENY, Content-Security-Policy with appropriate directives,
   Strict-Transport-Security for HTTPS **And** CSRF protection is implemented
   for state-changing operations **And** the API rejects requests from
   unauthorized origins **And** follows OWASP security headers best practices
   (NFR5, NFR10) ✅

## Tasks / Subtasks

- [ ] Task 1: Restrict CORS to frontend origin (AC: #1)

  - [ ] Use settings/env var for allowed origin
  - [ ] Do not allow wildcard

- [ ] Task 2: Add security headers middleware (AC: #1)

  - [ ] Add headers on every response
  - [ ] Ensure HSTS only on HTTPS

- [ ] Task 3: Add CSP policy (AC: #1)

  - [ ] Start minimal: default-src 'self'
  - [ ] Allow required script/style/font connections for Vite build
  - [ ] Consider API base URL

- [ ] Task 4: CSRF protection decision (AC: #1)

  - [ ] If auth via Bearer token: CSRF not required (document rationale)
  - [ ] If auth via cookies: implement CSRF token double-submit

- [ ] Task 5: Tests (AC: #1)
  - [ ] Verify CORS rejects unknown origin
  - [ ] Verify headers present on responses

## Dev Notes

### Critical Architecture Requirements

- Config via env vars
- Don’t loosen CORS beyond frontend origin
- Add headers globally

### File Structure

```
backend/app/
├── core/
│   └── config.py
├── middleware/
│   ├── security_headers.py
│   └── cors.py
└── main.py
```

### Implementation Details

**CORS:**

```python
# backend/app/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
```

**Security Headers Middleware:**

```python
# backend/app/middleware/security_headers.py
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Permissions-Policy"] = "geolocation=()"

        # CSP: keep conservative; tune as needed
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # HSTS only if served over HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        return response
```

### Testing Requirements

- Response includes required headers
- CORS allows configured origin and rejects others

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.14]
- OWASP Security Headers

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Defines tight CORS + baseline security headers
- Notes CSRF dependency on auth storage
