# Story 2.9: Implement API Key Encryption Service

Status: ready-for-dev

## Story

As a developer, I want to implement API key encryption and decryption using
AES-256, so that OpenAI API keys are never stored in plain text.

## Acceptance Criteria

1. **Given** cryptography library with Fernet is installed **When** I create
   encryption functions in app/services/encryption_service.py **Then** an
   `encrypt_api_key(api_key: str) -> str` function encrypts keys using AES-256
   (Fernet) **And** a `decrypt_api_key(encrypted_key: str) -> str` function
   decrypts keys **And** the encryption key is loaded from environment variable
   ENCRYPTION_KEY **And** encrypted keys cannot be decrypted without the correct
   encryption key **And** the same API key encrypted twice produces different
   ciphertext (includes IV/nonce)

## Tasks / Subtasks

- [ ] Task 1: Implement encryption service helpers (AC: #1)

  - [ ] Load `ENCRYPTION_KEY` from environment/config
  - [ ] Implement `encrypt_api_key`
  - [ ] Implement `decrypt_api_key`

- [ ] Task 2: Add unit tests for encryption (AC: #1)
  - [ ] Round-trip encrypt/decrypt returns original value
  - [ ] Encrypting twice yields different ciphertext
  - [ ] Decrypt fails with wrong key

## Dev Notes

### Critical Architecture Requirements

- Encryption must be AES-256 equivalent; Fernet satisfies this requirement.
- Keys are sensitive: never log API keys (plain or encrypted) in application
  logs.

### Technical Implementation Details

- Suggested files:
  - `backend/app/services/encryption_service.py`
  - `backend/app/core/config.py` (load `ENCRYPTION_KEY`)
  - `backend/tests/services/test_encryption_service.py`
- Fernet key must be urlsafe-base64 encoded 32 bytes.
