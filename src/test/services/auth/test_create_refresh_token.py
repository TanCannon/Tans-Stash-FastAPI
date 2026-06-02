# tests/services/auth/test_create_refresh_token.py

from datetime import datetime, timezone

import pytest
from jose import jwt

from src.schemas import user_schemas
from src.services import auth


@pytest.fixture
def user():
    return user_schemas.UserResponse(
        id=123,
        username="tanmaya",
        email="tan@gmail.com",
        role="user",
        password="tan123"
    )


@pytest.fixture(autouse=True)
def mock_secret_key(monkeypatch):
    monkeypatch.setattr(auth, "SECRET_KEY", "test-secret-key")


def test_create_refresh_token_returns_string(user):
    token = auth.create_refresh_token(user)

    assert isinstance(token, str)
    assert token


def test_create_refresh_token_contains_correct_claims(user):
    token = auth.create_refresh_token(user)

    payload = jwt.decode(
        token,
        auth.SECRET_KEY,
        algorithms=[auth.ALGORITHM],
    )

    assert payload["id"] == user.id
    assert payload["type"] == "refresh"


def test_create_refresh_token_does_not_contain_access_claims(user):
    token = auth.create_refresh_token(user)

    payload = jwt.decode(
        token,
        auth.SECRET_KEY,
        algorithms=[auth.ALGORITHM],
    )

    assert "sub" not in payload
    assert "role" not in payload

def test_create_refresh_token_has_7_day_expiry(user):
    before = datetime.now(timezone.utc)

    token = auth.create_refresh_token(user)

    payload = jwt.decode(
        token,
        auth.SECRET_KEY,
        algorithms=[auth.ALGORITHM],
    )

    after = datetime.now(timezone.utc)

    exp_timestamp = payload["exp"]

    expected_min = int(before.timestamp()) + (7 * 24 * 60 * 60)
    expected_max = int(after.timestamp()) + (7 * 24 * 60 * 60)

    assert expected_min <= exp_timestamp <= expected_max


def test_create_refresh_token_uses_correct_algorithm(user):
    token = auth.create_refresh_token(user)

    header = jwt.get_unverified_header(token)

    assert header["alg"] == auth.ALGORITHM


def test_refresh_token_cannot_be_decoded_with_wrong_secret(user):
    token = auth.create_refresh_token(user)

    with pytest.raises(jwt.JWTError):
        jwt.decode(
            token,
            "wrong-secret",
            algorithms=[auth.ALGORITHM],
        )
