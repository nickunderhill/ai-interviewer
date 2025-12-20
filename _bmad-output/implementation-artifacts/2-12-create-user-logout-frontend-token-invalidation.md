# Story 2.12: Create User Logout (Frontend Token Invalidation)

Status: ready-for-dev

## Story

As a user, I want to log out of my account, so that my session is ended
securely.

## Acceptance Criteria

1. **Given** I am authenticated with a JWT token stored in the frontend **When**
   I click the logout button in the UI **Then** the frontend removes the JWT
   token from localStorage **And** the user is redirected to the login page
   **And** subsequent API requests without a token return 401 Unauthorized
   **And** the JWT remains valid until expiration (stateless design) but is no
   longer accessible to the frontend

## Tasks / Subtasks

- [ ] Task 1: Implement logout action in auth service (AC: #1)

  - [ ] Remove token from localStorage
  - [ ] Clear any cached auth state

- [ ] Task 2: Add logout UI affordance (AC: #1)

  - [ ] Add logout button in appropriate authenticated layout/header
  - [ ] On click, call logout and redirect to login route

- [ ] Task 3: Verify API client behavior after logout (AC: #1)

  - [ ] Ensure Axios interceptor stops attaching token after logout
  - [ ] Ensure protected API calls fail with 401 and app handles it gracefully

- [ ] Task 4: Add frontend tests where feasible (AC: #1)
  - [ ] Clicking logout clears storage and navigates to login

## Dev Notes

### Critical Architecture Requirements

- Auth tokens are stored in localStorage and attached to requests via Axios
  interceptor.
- Logout is frontend-only token invalidation (JWT remains valid server-side
  until exp).

### Technical Implementation Details

- Suggested files:
  - `frontend/src/services/authService.ts`
  - `frontend/src/services/apiClient.ts`
  - `frontend/src/features/auth/**`
