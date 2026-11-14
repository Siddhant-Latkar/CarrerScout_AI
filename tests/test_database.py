from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import User


def _count_users(db_session: Session) -> int:
    return db_session.scalar(select(func.count()).select_from(User)) or 0


def test_rows_written_in_one_test_are_visible_in_it(db_session: Session) -> None:
    db_session.add(User(email="isolation@example.com", hashed_password="x", full_name="A"))
    db_session.commit()

    assert _count_users(db_session) == 1


def test_rows_from_previous_test_are_rolled_back(db_session: Session) -> None:
    assert _count_users(db_session) == 0