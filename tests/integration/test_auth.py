from auth.jwt import decode_access_token


def test_login_happy_path(client, test_user):
    response = client.post("/login", json={
        "email": "testuser@example.com",
        "password": "securepassword123",
    })
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_login_token_is_decodable(client, test_user):
    response = client.post("/login", json={
        "email": "testuser@example.com",
        "password": "securepassword123",
    })
    token = response.json()["access_token"]
    payload = decode_access_token(token)
    assert payload["sub"] == str(test_user.id)
    assert payload["email"] == test_user.email


def test_login_wrong_password_returns_401(client, test_user):
    response = client.post("/login", json={
        "email": "testuser@example.com",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_user_not_found_returns_401(client):
    response = client.post("/login", json={
        "email": "nobody@example.com",
        "password": "doesntmatter",
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_missing_email_returns_422(client):
    response = client.post("/login", json={"password": "password"})
    assert response.status_code == 422


def test_login_missing_password_returns_422(client):
    response = client.post("/login", json={"email": "x@y.com"})
    assert response.status_code == 422


def test_login_empty_body_returns_422(client):
    response = client.post("/login", json={})
    assert response.status_code == 422
