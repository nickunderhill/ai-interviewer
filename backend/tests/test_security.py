import re

import pytest


def test_hash_password_produces_non_empty_hash():
    from app.core.security import hash_password

    hashed = hash_password("correct-horse-battery-staple")

    assert isinstance(hashed, str)
    assert hashed
    assert hashed != "correct-horse-battery-staple"
    assert re.match(r"^\$2[aby]\$12\$", hashed) is not None


def test_verify_password_returns_true_for_correct_password():
    from app.core.security import hash_password, verify_password

    password = "p@ssw0rd!"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_returns_false_for_incorrect_password():
    from app.core.security import hash_password, verify_password

    hashed = hash_password("p@ssw0rd!")

    assert verify_password("wrong", hashed) is False


def test_verify_password_returns_false_for_invalid_hash():
    from app.core.security import verify_password

    assert verify_password("p@ssw0rd!", "not-a-bcrypt-hash") is False
