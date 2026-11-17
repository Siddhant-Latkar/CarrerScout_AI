def register_and_login(client, email: str) -> str:
    """Register a user and return their JWT access token."""

    register_response = client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "StrongPassword123",
            "full_name": "Test User",
        },
    )

    assert register_response.status_code == 201

    login_response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "StrongPassword123",
        },
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_get_profile_requires_authentication(client):
    response = client.get("/api/profile")

    assert response.status_code == 401


def test_get_profile_returns_logged_in_user_profile(client):
    token = register_and_login(client, "profile1@example.com")

    response = client.get(
        "/api/profile",
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["email"] == "profile1@example.com"
    assert data["full_name"] == "Test User"
    assert data["degree"] is None
    assert data["branch"] is None
    assert data["skills"] == []
    assert data["preferred_locations"] == []
    assert data["job_types"] == []
    assert data["paid_only"] is True
    assert data["min_monthly_stipend"] is None


def test_put_profile_requires_authentication(client):
    response = client.put(
        "/api/profile",
        json={"full_name": "Updated User"},
    )

    assert response.status_code == 401


def test_put_profile_updates_user_preferences(client):
    token = register_and_login(client, "profile2@example.com")

    payload = {
        "full_name": "Siddhant Latkar",
        "degree": "B.Tech",
        "branch": "AIML",
        "graduation_year": 2027,
        "skills": ["Python", "Machine Learning"],
        "preferred_locations": ["Pune", "Mumbai"],
        "job_types": ["internship", "full_time"],
        "paid_only": True,
        "min_monthly_stipend": 5000,
    }

    response = client.put(
        "/api/profile",
        json=payload,
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["full_name"] == "Siddhant Latkar"
    assert data["degree"] == "B.Tech"
    assert data["branch"] == "AIML"
    assert data["graduation_year"] == 2027
    assert data["skills"] == ["Python", "Machine Learning"]
    assert data["preferred_locations"] == ["Pune", "Mumbai"]
    assert data["job_types"] == ["internship", "full_time"]
    assert data["paid_only"] is True
    assert data["min_monthly_stipend"] == 5000


def test_put_profile_updates_full_name(client):
    token = register_and_login(client, "profile3@example.com")

    response = client.put(
        "/api/profile",
        json={"full_name": "New Test Name"},
        headers=auth_headers(token),
    )

    assert response.status_code == 200
    assert response.json()["full_name"] == "New Test Name"


def test_put_profile_removes_duplicate_skills(client):
    token = register_and_login(client, "profile4@example.com")

    response = client.put(
        "/api/profile",
        json={
            "full_name": "Test User",
            "skills": ["Python", "Machine Learning", "python"],
            "preferred_locations": ["Pune", "Mumbai", "pune"],
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 200

    data = response.json()

    assert data["skills"] == ["Python", "Machine Learning"]
    assert data["preferred_locations"] == ["Pune", "Mumbai"]


def test_put_profile_resets_omitted_fields_to_defaults(client):
    token = register_and_login(client, "profile5@example.com")

    initial_payload = {
        "full_name": "Test User",
        "degree": "B.Tech",
        "branch": "AIML",
        "graduation_year": 2027,
        "skills": ["Python"],
        "preferred_locations": ["Pune"],
        "job_types": ["internship"],
        "paid_only": False,
        "min_monthly_stipend": 10000,
    }

    first_response = client.put(
        "/api/profile",
        json=initial_payload,
        headers=auth_headers(token),
    )

    assert first_response.status_code == 200

    # PUT with only full_name should reset all other fields.
    second_response = client.put(
        "/api/profile",
        json={"full_name": "Updated User"},
        headers=auth_headers(token),
    )

    assert second_response.status_code == 200

    data = second_response.json()

    assert data["full_name"] == "Updated User"
    assert data["degree"] is None
    assert data["branch"] is None
    assert data["graduation_year"] is None
    assert data["skills"] == []
    assert data["preferred_locations"] == []
    assert data["job_types"] == []
    assert data["paid_only"] is True
    assert data["min_monthly_stipend"] is None


def test_put_profile_rejects_invalid_graduation_year(client):
    token = register_and_login(client, "profile6@example.com")

    response = client.put(
        "/api/profile",
        json={
            "full_name": "Test User",
            "graduation_year": 2200,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_put_profile_rejects_invalid_job_type(client):
    token = register_and_login(client, "profile7@example.com")

    response = client.put(
        "/api/profile",
        json={
            "full_name": "Test User",
            "job_types": ["internship", "permanent"],
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_put_profile_rejects_invalid_stipend(client):
    token = register_and_login(client, "profile8@example.com")

    response = client.put(
        "/api/profile",
        json={
            "full_name": "Test User",
            "min_monthly_stipend": -500,
        },
        headers=auth_headers(token),
    )

    assert response.status_code == 422


def test_users_only_access_their_own_profiles(client):
    token_one = register_and_login(client, "user1@example.com")
    token_two = register_and_login(client, "user2@example.com")

    client.put(
        "/api/profile",
        json={
            "full_name": "First User",
            "skills": ["Python"],
        },
        headers=auth_headers(token_one),
    )

    client.put(
        "/api/profile",
        json={
            "full_name": "Second User",
            "skills": ["Java"],
        },
        headers=auth_headers(token_two),
    )

    response_one = client.get(
        "/api/profile",
        headers=auth_headers(token_one),
    )

    response_two = client.get(
        "/api/profile",
        headers=auth_headers(token_two),
    )

    assert response_one.status_code == 200
    assert response_two.status_code == 200

    assert response_one.json()["full_name"] == "First User"
    assert response_one.json()["skills"] == ["Python"]

    assert response_two.json()["full_name"] == "Second User"
    assert response_two.json()["skills"] == ["Java"]
