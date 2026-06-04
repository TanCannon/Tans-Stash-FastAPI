# tests/services/auth/test_create_access_token.py

from datetime import datetime, timezone

from jose import jwt, JWTError
import pytest

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


def test_create_access_token_returns_string(user):
    token = auth.create_access_token(user)

    assert isinstance(token, str)
    assert token


def test_create_access_token_contains_correct_claims(user):
    token = auth.create_access_token(user)

    payload = jwt.decode(
        token,
        auth.SECRET_KEY,
        algorithms=[auth.ALGORITHM],
    )

    assert payload["sub"] == user.username
    assert payload["id"] == user.id
    assert payload["role"] == user.role
    assert payload["type"] == "access"

def test_create_access_token_has_15_minute_expiry(user):
    before = datetime.now(timezone.utc)

    token = auth.create_access_token(user)

    payload = jwt.decode(
        token,
        auth.SECRET_KEY,
        algorithms=[auth.ALGORITHM],
    )

    after = datetime.now(timezone.utc)

    exp_timestamp = payload["exp"]

    expected_min = int(before.timestamp()) + 15 * 60
    expected_max = int(after.timestamp()) + 15 * 60

    assert expected_min <= exp_timestamp <= expected_max


def test_create_access_token_uses_correct_algorithm(user):
    token = auth.create_access_token(user)

    header = jwt.get_unverified_header(token)

    assert header["alg"] == auth.ALGORITHM


def test_token_cannot_be_decoded_with_wrong_secret(user):
    token = auth.create_access_token(user)

    with pytest.raises(JWTError):
        jwt.decode(
            token,
            "wrong-secret",
            algorithms=[auth.ALGORITHM],
        )
