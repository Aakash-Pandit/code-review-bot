import os
from datetime import timedelta

import pytest

# conftest.py runs first and sets DATABASE_URL / JWT_SECRET before any import
from auth.jwt import create_access_token, decode_access_token


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "user-123", "email": "a@b.com"})
    assert isinstance(token, str)
    assert len(token) > 0


def test_create_access_token_encodes_sub():
    token = create_access_token({"sub": "user-abc", "email": "x@y.com"})
    payload = decode_access_token(token)
    assert payload["sub"] == "user-abc"


def test_create_access_token_encodes_email():
    token = create_access_token({"sub": "user-1", "email": "hello@example.com"})
    payload = decode_access_token(token)
    assert payload["email"] == "hello@example.com"


def test_create_access_token_has_exp_claim():
    token = create_access_token({"sub": "user-1"})
    payload = decode_access_token(token)
    assert "exp" in payload


def test_create_access_token_custom_expires_delta():
    from datetime import datetime, timezone

    token = create_access_token({"sub": "u"}, expires_delta=timedelta(minutes=5))
    payload = decode_access_token(token)
    exp = payload["exp"]
    now = datetime.now(timezone.utc).timestamp()
    # Should expire in ~5 minutes, so between 4 and 6 minutes from now
    assert 240 < (exp - now) < 360


def test_decode_access_token_valid_round_trip():
    data = {"sub": "round-trip", "email": "rt@test.com"}
    token = create_access_token(data)
    payload = decode_access_token(token)
    assert payload["sub"] == data["sub"]
    assert payload["email"] == data["email"]


def test_decode_access_token_invalid_token_raises_value_error():
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token("this.is.not.a.valid.jwt")


def test_decode_access_token_wrong_secret_raises_value_error():
    import os
    from jose import jwt as jose_jwt

    token = jose_jwt.encode({"sub": "u"}, "wrong-secret", algorithm="HS256")
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(token)


def test_decode_access_token_expired_raises_value_error():
    token = create_access_token({"sub": "u"}, expires_delta=timedelta(seconds=-1))
    with pytest.raises(ValueError, match="Invalid token"):
        decode_access_token(token)
