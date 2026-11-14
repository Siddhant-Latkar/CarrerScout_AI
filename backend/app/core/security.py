from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import settings

_hasher = PasswordHasher()

# Checked when a login email does not exist, so the response time does not reveal
# whether an account is registered.
DUMMY_PASSWORD_HASH = _hasher.hash("not-a-real-password")


def hash_password(password: str) -> str:
    """Return a salted Argon2 hash of the password."""
    return _hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """Return True only if the password matches the stored hash."""
    try:
        return _hasher.verify(hashed_password, password)
    except (VerifyMismatchError, InvalidHashError):
        return False


def create_access_token(user_id: int) -> str:
    """Create a signed token that identifies the user and expires automatically."""
    now = datetime.now(UTC)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> int | None:
    """Return the user id inside a valid token, or None if the token is bad or expired."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["exp", "sub"]},
        )
        return int(payload["sub"])
    except (jwt.InvalidTokenError, ValueError):
        return None
