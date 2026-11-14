from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings
from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


def test_hash_is_not_plain_password() -> None:
    hashed = hash_password("StrongPass123")

    assert hashed != "StrongPass123"
    assert hashed.startswith("$argon2")


def test_same_password_gives_different_hashes() -> None:
    assert hash_password("StrongPass123") != hash_password("StrongPass123")


def test_verify_password_accepts_correct_password() -> None:
    hashed = hash_password("StrongPass123")

    assert verify_password("StrongPass123", hashed) is True


def test_verify_password_rejects_wrong_password() -> None:
    hashed = hash_password("StrongPass123")

    assert verify_password("WrongPass456", hashed) is False


def test_verify_password_rejects_malformed_hash() -> None:
    assert verify_password("StrongPass123", "not-a-hash") is False


def test_access_token_round_trip() -> None:
    token = create_access_token(42)

    assert decode_access_token(token) == 42


def test_garbage_token_is_rejected() -> None:
    assert decode_access_token("not.a.token") is None


def test_token_signed_with_other_secret_is_rejected() -> None:
    forged = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) + timedelta(minutes=5)},
        "x" * 40,
        algorithm=settings.jwt_algorithm,
    )

    assert decode_access_token(forged) is None


def test_expired_token_is_rejected() -> None:
    expired = jwt.encode(
        {"sub": "1", "exp": datetime.now(UTC) - timedelta(minutes=1)},
        settings.secret_key,
        algorithm=settings.jwt_algorithm,
    )

    assert decode_access_token(expired) is None
