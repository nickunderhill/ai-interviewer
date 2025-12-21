"""
Encryption service for API keys.
Uses Fernet (AES-256) to encrypt and decrypt sensitive data.
"""

from cryptography.fernet import Fernet

from app.core.config import settings


def _get_fernet() -> Fernet:
    """Get Fernet cipher instance using encryption key from settings."""
    # Convert the encryption key string to bytes for Fernet
    key_bytes = settings.ENCRYPTION_KEY.encode()
    return Fernet(key_bytes)


def encrypt_api_key(api_key: str) -> str:
    """
    Encrypt an API key using Fernet (AES-256).

    Each encryption produces different ciphertext due to included IV/nonce.

    Args:
        api_key: Plain text API key to encrypt

    Returns:
        str: Base64-encoded encrypted API key

    Raises:
        ValueError: If encryption fails
    """
    try:
        fernet = _get_fernet()
        encrypted_bytes = fernet.encrypt(api_key.encode())
        return encrypted_bytes.decode()
    except Exception as exc:
        raise ValueError(f"Encryption failed: {str(exc)}") from exc


def decrypt_api_key(encrypted_key: str) -> str:
    """
    Decrypt an encrypted API key using Fernet (AES-256).

    Args:
        encrypted_key: Base64-encoded encrypted API key

    Returns:
        str: Decrypted plain text API key

    Raises:
        ValueError: If decryption fails (wrong key, corrupted data)
    """
    try:
        fernet = _get_fernet()
        decrypted_bytes = fernet.decrypt(encrypted_key.encode())
        return decrypted_bytes.decode()
    except Exception as exc:
        raise ValueError(f"Decryption failed: {str(exc)}") from exc
