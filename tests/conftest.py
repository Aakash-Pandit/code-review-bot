import json
import os

# Override unconditionally — docker-compose sets DATABASE_URL to the prod DB,
# and setdefault would not override it, causing tests to hit the real database.
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql://code_review_bot:changeme@localhost:5432/code_review_bot_test",
)
os.environ["BCRYPT_ROUNDS"] = "4"  # keep tests fast regardless of prod setting
os.environ.setdefault("JWT_SECRET", "test-secret-do-not-use-in-production")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")
os.environ.setdefault("OLLAMA_HOST", "http://mock-ollama:11434")
os.environ.setdefault("OLLAMA_MODEL", "test-model")

from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import auth.backend as backend_module
from application.app import app
from auth.jwt import create_access_token
from auth.passwords import hash_password
from database.db import Base, get_db
from users.models import User


@pytest.fixture(scope="session")
def test_engine():
    engine = create_engine(os.environ["DATABASE_URL"])
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(test_engine):
    connection = test_engine.connect()
    transaction = connection.begin()
    session = sessionmaker(autocommit=False, autoflush=False, bind=connection)()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    # auth/backend.py line 54 calls `with SessionLocal() as db:` directly,
    # bypassing the get_db dependency — patch it to use the test session
    original_sl = backend_module.SessionLocal
    mock_sl = MagicMock()
    mock_sl.return_value.__enter__ = MagicMock(return_value=db_session)
    mock_sl.return_value.__exit__ = MagicMock(return_value=None)
    backend_module.SessionLocal = mock_sl

    with TestClient(app, raise_server_exceptions=True) as c:
        yield c

    app.dependency_overrides.clear()
    backend_module.SessionLocal = original_sl


@pytest.fixture
def test_user(db_session):
    user = User(
        first_name="Test",
        last_name="User",
        email="testuser@example.com",
        password_hash=hash_password("securepassword123"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user):
    token = create_access_token({"sub": str(test_user.id), "email": test_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_ollama_stream():
    def _make(chunks=("Hello ", "World")):
        async def aiter_lines():
            for chunk in chunks:
                yield json.dumps({"response": chunk})

        mock_response = MagicMock()
        mock_response.aiter_lines = aiter_lines

        mock_stream_cm = MagicMock()
        mock_stream_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_stream_cm.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_stream_cm)

        mock_client_cm = MagicMock()
        mock_client_cm.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cm.__aexit__ = AsyncMock(return_value=False)

        return mock_client_cm, mock_client

    return _make


@pytest.fixture
def mock_ollama_chat():
    def _make(answer="Test answer from LLM", status_code=200):
        mock_response = MagicMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = {"response": answer}
        mock_response.text = answer

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)

        mock_client_cm = MagicMock()
        mock_client_cm.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client_cm.__aexit__ = AsyncMock(return_value=False)

        return mock_client_cm, mock_client

    return _make
