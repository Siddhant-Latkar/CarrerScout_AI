from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import Preference, User

USER = {
    "email": "student@example.com",
    "password": "StrongPass123",
    "full_name": "Test Student",
}


def register(client: TestClient, **overrides: str):
    return client.post("/api/auth/register", json={**USER, **overrides})


def login_token(client: TestClient) -> str:
    response = client.post(
        "/api/auth/login",
        json={"email": USER["email"], "password": USER["password"]},
    )
    return response.json()["access_token"]


def test_register_returns_user_without_password(client: TestClient) -> None:
    response = register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == USER["email"]
    assert body["full_name"] == USER["full_name"]
    assert "password" not in body
    assert "hashed_password" not in body


def test_register_lowercases_email(client: TestClient) -> None:
    response = register(client, email="Student@Example.COM")

    assert response.status_code == 201
    assert response.json()["email"] == "student@example.com"


def test_register_stores_hashed_password(
    client: TestClient,
    db_session: Session,
) -> None:
    register(client)

    user = db_session.scalar(select(User).where(User.email == USER["email"]))
    assert user is not None
    assert user.hashed_password != USER["password"]
    assert user.hashed_password.startswith("$argon2")


def test_register_creates_empty_preference(
    client: TestClient,
    db_session: Session,
) -> None:
    user_id = register(client).json()["id"]

    preference = db_session.scalar(select(Preference).where(Preference.user_id == user_id))
    assert preference is not None
    assert preference.paid_only is True
    assert preference.skills == []


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    register(client)

    response = register(client, email="STUDENT@example.com")

    assert response.status_code == 409


def test_register_rejects_short_password(client: TestClient) -> None:
    response = register(client, password="short")

    assert response.status_code == 422


def test_register_rejects_invalid_email(client: TestClient) -> None:
    response = register(client, email="not-an-email")

    assert response.status_code == 422


def test_login_returns_token(client: TestClient) -> None:
    register(client)

    response = client.post(
        "/api/auth/login",
        json={"email": USER["email"], "password": USER["password"]},
    )

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    register(client)

    response = client.post(
        "/api/auth/login",
        json={"email": USER["email"], "password": "WrongPass456"},
    )

    assert response.status_code == 401


def test_login_unknown_email_returns_401(client: TestClient) -> None:
    response = client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "StrongPass123"},
    )

    assert response.status_code == 401


def test_me_requires_token(client: TestClient) -> None:
    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_rejects_garbage_token(client: TestClient) -> None:
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer not.a.token"},
    )

    assert response.status_code == 401


def test_me_returns_current_user(client: TestClient) -> None:
    register(client)
    token = login_token(client)

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == USER["email"]
