from typing import Any

from sqlalchemy.orm import Session

from app.database.models import Preference, User


def get_or_create_preference(db: Session, user: User) -> Preference:
    """Return the user's preferences, creating an empty row if one is somehow missing."""
    if user.preference is None:
        user.preference = Preference()
        db.commit()
        db.refresh(user.preference)
    return user.preference


def update_profile(
    db: Session,
    user: User,
    *,
    full_name: str,
    preference_data: dict[str, Any],
) -> Preference:
    """Save the new name and preferences, then reload them from the database."""
    preference = get_or_create_preference(db, user)
    user.full_name = full_name
    for field, value in preference_data.items():
        setattr(preference, field, value)
    db.commit()
    db.refresh(user)
    db.refresh(preference)
    return preference
