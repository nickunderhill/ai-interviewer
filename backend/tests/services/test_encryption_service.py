"""
Tests for encryption service.
"""


from cryptography.fernet import Fernet
import pytest

from app.services.encryption_service import decrypt_api_key, encrypt_api_key


def test_encrypt_api_key_returns_string() -> None:
    """Test that encrypt_api_key returns a string."""
    api_key = "sk-test123456789"
    encrypted = encrypt_api_key(api_key)

    assert isinstance(encrypted, str)
    assert len(encrypted) > 0
    assert encrypted != api_key  # Should be different from input


def test_decrypt_api_key_returns_original() -> None:
    """Test that encrypt/decrypt round-trip returns original value."""
    original_key = "sk-test123456789abcdef"

    # Encrypt then decrypt
    encrypted = encrypt_api_key(original_key)
    decrypted = decrypt_api_key(encrypted)

    assert decrypted == original_key


def test_encrypting_twice_produces_different_ciphertext() -> None:
    """Test that encrypting the same key twice produces different ciphertext (IV/nonce)."""
    api_key = "sk-test123"

    encrypted1 = encrypt_api_key(api_key)
    encrypted2 = encrypt_api_key(api_key)

    # Ciphertext should be different due to random IV
    assert encrypted1 != encrypted2

    # But both should decrypt to the same value
    assert decrypt_api_key(encrypted1) == api_key
    assert decrypt_api_key(encrypted2) == api_key


def test_decrypt_with_wrong_key_fails() -> None:
    """Test that decryption fails with wrong encryption key."""
    # Generate a different Fernet key
    wrong_key = Fernet.generate_key().decode()

    # Encrypt with correct key
    api_key = "sk-test123"
    encrypted = encrypt_api_key(api_key)

    # Temporarily replace encryption key
    from app.core.config import settings

    original_key = settings.ENCRYPTION_KEY

    try:
        settings.ENCRYPTION_KEY = wrong_key

        # Attempt to decrypt with wrong key should fail
        with pytest.raises(ValueError, match="Decryption failed"):
            decrypt_api_key(encrypted)
    finally:
        settings.ENCRYPTION_KEY = original_key


def test_decrypt_invalid_data_fails() -> None:
    """Test that decryption of invalid data fails gracefully."""
    invalid_encrypted = "not-valid-encrypted-data"

    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt_api_key(invalid_encrypted)


def test_encrypt_empty_string() -> None:
    """Test that encrypting empty string works."""
    encrypted = encrypt_api_key("")
    decrypted = decrypt_api_key(encrypted)

    assert decrypted == ""


def test_encrypt_long_api_key() -> None:
    """Test encrypting a very long API key."""
    long_key = "sk-" + "a" * 500

    encrypted = encrypt_api_key(long_key)
    decrypted = decrypt_api_key(encrypted)

    assert decrypted == long_key


def test_encrypted_key_never_contains_plaintext() -> None:
    """Test that encrypted output doesn't contain plaintext API key."""
    api_key = "sk-secretkey12345"

    encrypted = encrypt_api_key(api_key)

    # Encrypted version should not contain any part of the plaintext
    assert api_key not in encrypted
    assert "secretkey" not in encrypted
