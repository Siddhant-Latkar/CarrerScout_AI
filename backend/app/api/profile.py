from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.database.repositories.profiles import (
    get_or_create_preference,
    update_profile,
)
from app.schemas.profile import ProfileRead, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=ProfileRead)
def get_profile(
    db: DbSession,
    current_user: CurrentUser,
) -> ProfileRead:
    """Get the logged-in user's profile and job preferences."""

    preference = get_or_create_preference(db, current_user)

    return ProfileRead.from_models(current_user, preference)


@router.put("", response_model=ProfileRead)
def replace_profile(
    profile_data: ProfileUpdate,
    db: DbSession,
    current_user: CurrentUser,
) -> ProfileRead:
    """Replace the logged-in user's complete profile and preferences."""

    preference = update_profile(
        db,
        current_user,
        full_name=profile_data.full_name,
        preference_data=profile_data.model_dump(exclude={"full_name"}),
    )

    return ProfileRead.from_models(current_user, preference)
