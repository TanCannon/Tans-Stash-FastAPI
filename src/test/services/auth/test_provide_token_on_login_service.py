import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from src.services import auth
from src.models import RefreshToken
from src.schemas import user_schemas
from src.exceptions import InvalidCredentialsError


@pytest.fixture
def user():
    return user_schemas.UserResponse(
        id=123,
        username="tanmaya",
        email="tan@gmail.com",
        role="user",
        password="tan123"
    )


@patch("src.services.auth.authenticate_user")
def test_provide_token_on_login_service_raises_when_authentication_fails(
    mock_authenticate_user,
    db,
):
    mock_authenticate_user.return_value = None

    with pytest.raises(InvalidCredentialsError):
        auth.provide_token_on_login_service(
            "test@example.com",
            "password",
            db,
        )


@patch("src.services.auth.create_refresh_token")
@patch("src.services.auth.create_access_token")
@patch("src.services.auth.authenticate_user")
def test_provide_token_on_login_service_creates_tokens_and_persists_refresh_token(
    mock_authenticate_user,
    mock_create_access_token,
    mock_create_refresh_token,
    db,
    user,
):
    mock_authenticate_user.return_value = user
    mock_create_access_token.return_value = "access-token"
    mock_create_refresh_token.return_value = "refresh-token"

    before = datetime.now(timezone.utc)

    access_token, refresh_token = auth.provide_token_on_login_service(
        user.email,
        "password",
        db,
    )

    after = datetime.now(timezone.utc)

    assert access_token == "access-token"
    assert refresh_token == "refresh-token"

    mock_authenticate_user.assert_called_once_with(
        user.email,
        "password",
        db,
    )
    mock_create_access_token.assert_called_once_with(user)
    mock_create_refresh_token.assert_called_once_with(user)

    db_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.user_id == user.id)
        .first()
    )

    assert db_token is not None
    assert db_token.user_id == user.id
    assert db_token.token == "refresh-token"

    db_expiry = db_token.expiry.replace(tzinfo=timezone.utc)

    expected_min = int((before + timedelta(days=7)).timestamp())
    expected_max = int((after + timedelta(days=7)).timestamp())
    actual = int(db_expiry.timestamp())

    assert expected_min <= actual <= expected_max
