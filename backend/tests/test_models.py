from app.database.base import Base
from app.database.models import Preference, User


def test_tables_are_registered_in_metadata() -> None:
    assert User.__tablename__ in Base.metadata.tables
    assert Preference.__tablename__ in Base.metadata.tables


def test_user_email_must_be_unique() -> None:
    assert User.__table__.c.email.unique is True


def test_one_preference_row_per_user() -> None:
    assert Preference.__table__.c.user_id.unique is True
