from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import IntegrityError

from app.api.deps import CurrentUser, DbSession
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.models import User
from app.database.repositories.users import create_user, get_user_by_email
from app.schemas.user import LoginRequest, TokenResponse, UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserCreate, db: DbSession) -> User:
    """Create a new account."""
    email_taken = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Email already registered",
    )

    if get_user_by_email(db, payload.email) is not None:
        raise email_taken

    try:
        return create_user(
            db,
            email=payload.email,
            hashed_password=hash_password(payload.password),
            full_name=payload.full_name,
        )
    except IntegrityError as exc:
        # Handle simultaneous registrations with the same email.
        db.rollback()
        raise email_taken from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbSession) -> TokenResponse:
    """Check the email and password and return an access token."""
    user = get_user_by_email(db, payload.email)
    password_hash = user.hashed_password if user is not None else DUMMY_PASSWORD_HASH
    password_ok = verify_password(payload.password, password_hash)

    if user is None or not password_ok or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return TokenResponse(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
def read_current_user(current_user: CurrentUser) -> User:
    """Return the account that owns the token."""
    return current_user
