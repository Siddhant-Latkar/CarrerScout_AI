from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.database.session import get_db
from app.main import app


class WorkingSession:
    def execute(self, *args: object, **kwargs: object) -> None:
        return None


class BrokenSession:
    def execute(self, *args: object, **kwargs: object) -> None:
        raise OperationalError("SELECT 1", {}, Exception("database is down"))


def working_db() -> WorkingSession:
    return WorkingSession()


def broken_db() -> BrokenSession:
    return BrokenSession()


@pytest.fixture(autouse=True)
def clear_overrides() -> Iterator[None]:
    yield
    app.dependency_overrides.clear()


def test_db_health_ok_when_database_works() -> None:
    app.dependency_overrides[get_db] = working_db

    response = TestClient(app).get("/api/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_db_health_returns_503_when_database_fails() -> None:
    app.dependency_overrides[get_db] = broken_db

    response = TestClient(app).get("/api/health/db")

    assert response.status_code == 503
