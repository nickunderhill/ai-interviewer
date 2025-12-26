# Story 8.7: Implement Password Security Best Practices

Status: ready-for-dev

## Story

As a developer, I want to implement secure password handling, so that user
credentials are protected according to industry standards.

## Acceptance Criteria

1. **Given** the authentication system is implemented **When** a user registers
   or updates their password **Then** the system validates minimum password
   requirements (8+ characters, mix of upper/lower/numbers/symbols recommended
   but not enforced for UX) **And** passwords are hashed using bcrypt with cost
   factor 12 before storage **And** the raw password is never stored or logged
   **And** password fields use type='password' in forms **And** password reset
   uses secure tokens with expiration **And** brute force protection limits
   login attempts **And** follows OWASP password storage guidelines (NFR4,
   NFR10, FR65) ✅

## Tasks / Subtasks

- [ ] Task 1: Verify bcrypt password hashing exists from Story 2.2 (AC: #1)

  - [ ] Check `backend/app/core/security.py` has hash_password function
  - [ ] Verify bcrypt cost factor is 12
  - [ ] Confirm verify_password function exists
  - [ ] Test hashing and verification work correctly

- [ ] Task 2: Implement password validation (AC: #1)

  - [ ] Add `validate_password_strength` function in
        `backend/app/utils/validators.py`
  - [ ] Check minimum length (8+ characters)
  - [ ] Recommend (but don't enforce) complexity for UX
  - [ ] Return helpful validation messages
  - [ ] Add to Pydantic schemas

- [ ] Task 3: Audit user registration/login for password security (AC: #1)

  - [ ] Review POST `/api/v1/auth/register` (Story 2.4)
  - [ ] Review POST `/api/v1/auth/login` (Story 2.5)
  - [ ] Ensure passwords never logged (even in debug mode)
  - [ ] Verify password fields cleared from memory after hashing
  - [ ] Check error messages don't reveal password details

- [ ] Task 4: Implement brute force protection (AC: #1)

  - [ ] Add login attempt tracking (in-memory or Redis)
  - [ ] Limit to 5 failed attempts per email per 15 minutes
  - [ ] Return 429 Too Many Requests after limit exceeded
  - [ ] Log suspicious activity (many failed attempts)
  - [ ] Clear successful login counters on success

- [ ] Task 5: Implement password reset with secure tokens (AC: #1)

  - [ ] Create password reset token generation (UUID + expiration)
  - [ ] POST `/api/v1/auth/password-reset-request` endpoint
  - [ ] POST `/api/v1/auth/password-reset-confirm` endpoint
  - [ ] Tokens expire after 1 hour
  - [ ] One-time use tokens (invalidated after use)
  - [ ] Send reset link via email (placeholder for now)

- [ ] Task 6: Update frontend password forms (AC: #1)
  - [ ] Ensure all password inputs use type="password"
  - [ ] Add password strength indicator (optional)
  - [ ] Show validation errors clearly
  - [ ] Add "Show/Hide Password" toggle
  - [ ] Prevent password autocomplete on registration

## Dev Notes

### Critical Architecture Requirements

**Backend:**

- **Hashing:** bcrypt with cost factor 12 (already implemented in Story 2.2)
- **Validation:** Minimum 8 characters, complexity recommended
- **Storage:** Never store or log raw passwords
- **Tokens:** Secure, expiring, one-time use for password reset
- **Brute Force:** Rate limiting on login attempts

**Frontend:**

- **Forms:** type="password" on all password inputs
- **Validation:** Client-side and server-side
- **UX:** Show password toggle, strength indicator

### File Structure

```
backend/app/
├── core/
│   └── security.py            # Already has bcrypt hashing (Story 2.2)
├── utils/
│   └── validators.py          # Add password validation
├── api/v1/endpoints/
│   ├── auth.py                # Add password reset endpoints
│   └── rate_limiting.py       # Brute force protection middleware
└── models/
    └── password_reset.py      # Password reset token model

frontend/src/
└── features/
    └── auth/
        └── components/
            ├── RegisterForm.tsx    # Update with validation
            └── PasswordResetForm.tsx  # New component
```

### Implementation Details

**Password Validation:**

```python
# backend/app/utils/validators.py (add to existing file)
import re

def validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.

    Requirements:
    - Minimum 8 characters (enforced)
    - Complexity recommended but not enforced for UX

    Returns:
        Tuple of (is_valid, message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    # Recommendations (not enforced)
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_symbol = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    strength_score = sum([has_upper, has_lower, has_digit, has_symbol])

    if strength_score < 2:
        return True, "Password is weak. Consider adding uppercase, lowercase, numbers, and symbols for better security."
    elif strength_score < 3:
        return True, "Password strength is moderate."
    else:
        return True, "Password strength is strong."
```

**Brute Force Protection:**

```python
# backend/app/api/v1/endpoints/rate_limiting.py
from fastapi import Request, HTTPException, status
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio

# In-memory store (use Redis in production)
login_attempts = defaultdict(list)
LOCK = asyncio.Lock()

MAX_ATTEMPTS = 5
WINDOW_MINUTES = 15

async def check_rate_limit(email: str) -> None:
    """
    Check if login attempts for email exceed rate limit.

    Raises:
        HTTPException: If rate limit exceeded
    """
    async with LOCK:
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=WINDOW_MINUTES)

        # Remove old attempts
        login_attempts[email] = [
            attempt for attempt in login_attempts[email]
            if attempt > cutoff
        ]

        # Check limit
        if len(login_attempts[email]) >= MAX_ATTEMPTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Too many login attempts. Please try again in {WINDOW_MINUTES} minutes."
            )

        # Record this attempt
        login_attempts[email].append(now)

async def clear_rate_limit(email: str) -> None:
    """Clear rate limit after successful login."""
    async with LOCK:
        if email in login_attempts:
            del login_attempts[email]
```

**Update Login Endpoint:**

```python
# backend/app/api/v1/endpoints/auth.py (update login endpoint)
from app.api.v1.endpoints.rate_limiting import check_rate_limit, clear_rate_limit

@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with brute force protection."""
    # Check rate limit BEFORE attempting login
    await check_rate_limit(credentials.email)

    # Fetch user
    user = await get_user_by_email(credentials.email, db)

    if not user or not verify_password(credentials.password, user.hashed_password):
        # Record failed attempt (already recorded in check_rate_limit)
        logger.warning(f"Failed login attempt for {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Clear rate limit on successful login
    await clear_rate_limit(credentials.email)

    # Generate JWT
    access_token = create_access_token(data={"sub": str(user.id)})

    return {"access_token": access_token, "token_type": "bearer"}
```

**Password Reset Model:**

```python
# backend/app/models/password_reset.py
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timedelta
import uuid

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    @staticmethod
    def create_token(user_id: str) -> 'PasswordResetToken':
        """Create a new password reset token."""
        return PasswordResetToken(
            user_id=user_id,
            token=str(uuid.uuid4()),
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )

    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return not self.used and datetime.utcnow() < self.expires_at
```

**Password Reset Endpoints:**

```python
# backend/app/api/v1/endpoints/auth.py (add these endpoints)
@router.post("/password-reset-request")
async def request_password_reset(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset token."""
    user = await get_user_by_email(email, db)

    # Don't reveal if email exists (security)
    if not user:
        return {"message": "If the email exists, a reset link has been sent"}

    # Create reset token
    reset_token = PasswordResetToken.create_token(user.id)
    db.add(reset_token)
    await db.commit()

    # TODO: Send email with reset link
    # For now, log token (in production, send via email)
    logger.info(f"Password reset token: {reset_token.token}")

    return {"message": "If the email exists, a reset link has been sent"}

@router.post("/password-reset-confirm")
async def confirm_password_reset(
    token: str,
    new_password: str,
    db: AsyncSession = Depends(get_db)
):
    """Confirm password reset with token."""
    # Validate new password
    is_valid, message = validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)

    # Find token
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == token)
    )
    reset_token = result.scalar_one_or_none()

    if not reset_token or not reset_token.is_valid():
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )

    # Update password
    user = await db.get(User, reset_token.user_id)
    user.hashed_password = hash_password(new_password)

    # Mark token as used
    reset_token.used = True

    await db.commit()

    logger.info(f"Password reset completed for user {user.id}")

    return {"message": "Password reset successful"}
```

### Testing Requirements

**Test Coverage:**

- Password validation catches weak passwords
- bcrypt hashing works correctly (cost factor 12)
- Raw passwords never logged
- Brute force protection limits login attempts
- Password reset tokens expire after 1 hour
- Tokens are one-time use

**Test Files:**

- `backend/tests/utils/test_validators_password.py`
- `backend/tests/api/v1/test_auth_brute_force.py`
- `backend/tests/api/v1/test_password_reset.py`

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.7]
- [Source: Story 2.2 - Password hashing implementation]
- [Source: Story 2.4, 2.5 - Registration and login]
- [NFR4, NFR10: Security requirements]
- [FR65: Password security]
- [OWASP: Password Storage Cheat Sheet]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Story created with comprehensive password security
- bcrypt hashing with cost factor 12
- Brute force protection
- Password reset with secure tokens
- Ready for dev implementation
