import uuid

from users.models import User


def test_signup_happy_path(client):
    response = client.post("/users", json={
        "first_name": "Alice",
        "last_name": "Smith",
        "email": "alice@example.com",
        "password": "strongpassword",
    })
    assert response.status_code == 201
    body = response.json()
    assert "id" in body
    assert body["first_name"] == "Alice"
    assert body["last_name"] == "Smith"
    assert body["email"] == "alice@example.com"
    assert "created_at" in body


def test_signup_returns_uuid_id(client):
    response = client.post("/users", json={
        "first_name": "Bob",
        "last_name": "Jones",
        "email": "bob@example.com",
        "password": "strongpassword",
    })
    assert response.status_code == 201
    body = response.json()
    uuid.UUID(body["id"])  # raises if not a valid UUID


def test_signup_duplicate_email_returns_409(client):
    payload = {
        "first_name": "Carol",
        "last_name": "White",
        "email": "carol@example.com",
        "password": "password123",
    }
    client.post("/users", json=payload)
    response = client.post("/users", json=payload)
    assert response.status_code == 409
    assert response.json()["detail"] == "Email already registered"


def test_signup_missing_email_returns_422(client):
    response = client.post("/users", json={
        "first_name": "Dave",
        "last_name": "Brown",
        "password": "password123",
    })
    assert response.status_code == 422


def test_signup_missing_password_returns_422(client):
    response = client.post("/users", json={
        "first_name": "Eve",
        "last_name": "Green",
        "email": "eve@example.com",
    })
    assert response.status_code == 422


def test_signup_missing_first_name_returns_422(client):
    response = client.post("/users", json={
        "last_name": "Green",
        "email": "noname@example.com",
        "password": "password123",
    })
    assert response.status_code == 422


def test_signup_empty_body_returns_422(client):
    response = client.post("/users", json={})
    assert response.status_code == 422


def test_signup_password_not_stored_in_plaintext(client, db_session):
    password = "plaintextcheck"
    client.post("/users", json={
        "first_name": "Frank",
        "last_name": "Black",
        "email": "frank@example.com",
        "password": password,
    })
    user = db_session.query(User).filter(User.email == "frank@example.com").first()
    assert user is not None
    assert user.password_hash != password


def test_signup_user_stored_in_db(client, db_session):
    client.post("/users", json={
        "first_name": "Grace",
        "last_name": "Hall",
        "email": "grace@example.com",
        "password": "password123",
    })
    user = db_session.query(User).filter(User.email == "grace@example.com").first()
    assert user is not None
    assert user.first_name == "Grace"
