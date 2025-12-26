# Story 8.8: Implement Session Security with JWT

Status: ready-for-dev

## Story

As a developer, I want to secure user sessions with JWT tokens, so that
authentication is stateless and secure.

## Acceptance Criteria

1. **Given** the authentication system uses JWT **When** a user logs in **Then**
   the system generates a JWT with 24-hour expiration using HS256 algorithm
   **And** the JWT secret key is stored in environment variables with high
   entropy (256-bit) **And** tokens include user_id and expiration claims
   **And** the frontend stores tokens in httpOnly cookies (preferred) or
   localStorage with XSS protections **And** expired tokens return 401
   Unauthorized **And** the get_current_user dependency validates token
   signature and expiration on every request **And** tokens cannot be tampered
   with or forged **And** follows OWASP JWT security best practices (NFR4,
   NFR10, FR66) ✅

## Tasks / Subtasks

- [ ] Task 1: Audit existing JWT implementation (Stories 2.3 + 2.6) (AC: #1)

  - [ ] Verify token creation uses HS256
  - [ ] Confirm expiration is 24 hours
  - [ ] Ensure JWT secret comes from env var
  - [ ] Verify get_current_user validates signature and exp
  - [ ] Confirm 401 behavior for expired/invalid token

- [ ] Task 2: Harden JWT claims and validation (AC: #1)

  - [ ] Ensure `sub` claim stores user_id
  - [ ] Add `iat` (issued at) claim
  - [ ] Add `jti` (token id) claim for future revocation
  - [ ] Validate `sub` is UUID and exists
  - [ ] Reject tokens with missing required claims

- [ ] Task 3: Ensure frontend token storage matches security requirements (AC:
      #1)

  - [ ] Prefer httpOnly cookie storage (if backend supports it)
  - [ ] If using localStorage, ensure XSS mitigations
  - [ ] Confirm Axios interceptor uses Authorization header
  - [ ] Clear token on logout
  - [ ] Handle 401 globally via response interceptor

- [ ] Task 4: Add CSRF protections if using cookies (AC: #1)

  - [ ] If switching to cookie-based auth, add CSRF token pattern
  - [ ] Add SameSite cookie attribute
  - [ ] Use Secure and HttpOnly flags
  - [ ] Add CSRF middleware for state-changing endpoints

- [ ] Task 5: Implement refresh token pattern (optional, for later) (AC: #1)

  - [ ] Create refresh endpoint
  - [ ] Add refresh token storage (httpOnly cookie)
  - [ ] Rotate refresh tokens on use
  - [ ] Revoke on logout

- [ ] Task 6: Add security tests for JWT (AC: #1)
  - [ ] Test token tampering fails
  - [ ] Test expired token returns 401
  - [ ] Test missing claims returns 401
  - [ ] Test invalid signature returns 401

## Dev Notes

### Critical Architecture Requirements

**Backend:**

- **Algorithm:** HS256
- **Secret:** Environment variable `JWT_SECRET_KEY` (high entropy)
- **Expiration:** 24 hours
- **Validation:** Signature + expiration checked on every request
- **Claims:** user_id in `sub`, include `exp`, `iat`
- **Error Handling:** Return 401 for invalid/expired token

**Frontend:**

- **Storage:** Prefer httpOnly cookies; otherwise localStorage with XSS
  protections
- **Transport:** Authorization: Bearer {token}
- **Interceptors:** Axios request/response interceptors handle auth

### File Structure

```
backend/app/
├── core/
│   ├── security.py            # JWT creation/validation (Story 2.3)
│   └── config.py              # JWT secret from env
├── api/deps.py                # get_current_user dependency (Story 2.6)
└── api/v1/endpoints/
    └── auth.py                # login/logout endpoints

frontend/src/
├── services/
│   ├── authService.ts         # token storage/clearing
│   └── apiClient.ts           # Axios interceptors
└── features/
    └── auth/
        └── hooks/
            └── useAuth.ts      # Auth state handling
```

### Implementation Details

**JWT Settings:**

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24

    def validate_jwt_secret(self):
        if len(self.JWT_SECRET_KEY) < 32:
            raise ValueError("JWT_SECRET_KEY must be at least 32 characters")
```

**Token Creation:**

```python
# backend/app/core/security.py
from datetime import datetime, timedelta
from jose import jwt
import uuid

def create_access_token(user_id: str) -> str:
    now = datetime.utcnow()
    expire = now + timedelta(hours=settings.ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode = {
        "sub": user_id,
        "exp": expire,
        "iat": now,
        "jti": str(uuid.uuid4()),
    }

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    return encoded_jwt
```

**Token Validation:**

```python
# backend/app/api/deps.py
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get(User, user_id)
    if user is None:
        raise credentials_exception

    return user
```

**Frontend Token Storage:**

```ts
// frontend/src/services/authService.ts
const TOKEN_KEY = 'authToken';

export function setToken(token: string) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}
```

**Axios Interceptor:**

```ts
// frontend/src/services/apiClient.ts
apiClient.interceptors.request.use(config => {
  const token = getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response?.status === 401) {
      clearToken();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);
```

### Testing Requirements

**Test Coverage:**

- Token expiration enforced (24h)
- Invalid/tampered token rejected
- Missing required claims rejected
- get_current_user returns 401 for invalid token
- Frontend clears token on 401

**Test Files:**

- `backend/tests/core/test_jwt_security.py`
- `backend/tests/api/test_auth_middleware.py`
- `frontend/src/services/authService.test.ts`
- `frontend/src/services/apiClient.test.ts`

### References

- [Source: _bmad-output/epics.md#Epic-8-Story-8.8]
- [Source: Story 2.3 - JWT token generation and validation]
- [Source: Story 2.6 - Authentication middleware]
- [NFR4, NFR10: Security requirements]
- [FR66: Isolate session data per user]
- [OWASP: JWT Cheat Sheet]

## Dev Agent Record

### Agent Model Used

GPT-5.2

### Completion Notes List

- Story created with JWT hardening checklist
- Audits existing implementation for gaps
- Notes cookie vs localStorage tradeoffs
- Adds security tests for tampering/expiry
- Ready for dev implementation
