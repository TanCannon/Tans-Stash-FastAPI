# test/services/auth/test_refresh_access_token_service.py

import pytest
from unittest.mock import Mock, patch
from jose import JWTError

from src.services import refresh_access_token_service
from src.exceptions import (
    InvalidRefreshTokenError,
    InvalidTokenTypeError,
    UserNotFoundError,
)


# ==========================================================
# Test: Invalid JWT
# Expected:
#   - jwt.decode fails
#   - InvalidRefreshTokenError raised
# ==========================================================
@patch("src.services.auth.jwt.decode")
def test_refresh_access_token_invalid_jwt(mock_decode):
    db = Mock()

    mock_decode.side_effect = JWTError()

    with pytest.raises(InvalidRefreshTokenError):
        refresh_access_token_service(
            refresh_token="bad-token",
            db=db,
        )


# ==========================================================
# Test: Wrong token type
# Expected:
#   - Access token supplied instead of refresh token
#   - InvalidTokenTypeError raised
# ==========================================================
@patch("src.services.auth.jwt.decode")
def test_refresh_access_token_invalid_token_type(mock_decode):
    db = Mock()

    mock_decode.return_value = {
        "id": "123",
        "type": "access",
    }

    with pytest.raises(InvalidTokenTypeError):
        refresh_access_token_service(
            refresh_token="token",
            db=db,
        )


# ==========================================================
# Test: Refresh token not found in database
# Expected:
#   - InvalidRefreshTokenError raised
# ==========================================================
@patch("src.services.auth.jwt.decode")
def test_refresh_access_token_not_found(mock_decode):
    db = Mock()

    mock_decode.return_value = {
        "id": "123",
        "type": "refresh",
    }

    db.query.return_value.filter.return_value.first.return_value = None

    with pytest.raises(InvalidRefreshTokenError):
        refresh_access_token_service(
            refresh_token="token",
            db=db,
        )


# ==========================================================
# Test: User not found
# Expected:
#   - Refresh token exists
#   - User lookup fails
#   - UserNotFoundError raised
# ==========================================================
@patch("src.services.auth.jwt.decode")
def test_refresh_access_token_user_not_found(mock_decode):
    db = Mock()

    mock_decode.return_value = {
        "id": "123",
        "type": "refresh",
    }

    db_token = Mock()
    db_token.is_revoked = False

    # first query -> refresh token lookup
    # second query -> user lookup
    db.query.return_value.filter.return_value.first.side_effect = [
        db_token,
        None,
    ]

    with pytest.raises(UserNotFoundError):
        refresh_access_token_service(
            refresh_token="token",
            db=db,
        )


# ==========================================================
# Test: Successful refresh flow
# Expected:
#   - Old refresh token revoked
#   - New tokens generated
#   - New refresh token persisted
#   - Commit executed
# ==========================================================
@patch("src.services.auth.create_refresh_token")
@patch("src.services.auth.create_access_token")
@patch("src.services.auth.jwt.decode")
def test_refresh_access_token_success(
    mock_decode,
    mock_create_access_token,
    mock_create_refresh_token,
):
    db = Mock()

    mock_decode.return_value = {
        "id": "123",
        "type": "refresh",
    }

    db_token = Mock()
    db_token.is_revoked = False

    user = Mock()
    user.id = "123"

    # first lookup -> refresh token
    # second lookup -> user
    db.query.return_value.filter.return_value.first.side_effect = [
        db_token,
        user,
    ]

    mock_create_access_token.return_value = "new-access-token"
    mock_create_refresh_token.return_value = "new-refresh-token"

    result = refresh_access_token_service(
        refresh_token="old-refresh-token",
        db=db,
    )

    assert result == {
        "success": True,
        "access_token": "new-access-token",
        "refresh_token": "new-refresh-token",
    }

    assert db_token.is_revoked is True

    mock_create_access_token.assert_called_once_with(user)
    mock_create_refresh_token.assert_called_once_with(user)

    db.add.assert_called_once()
    db.commit.assert_called_once()


# ==========================================================
# Test: Newly generated refresh token saved
# Expected:
#   - db.add called with token containing
#     correct user_id and token value
# ==========================================================
@patch("src.services.auth.create_refresh_token")
@patch("src.services.auth.create_access_token")
@patch("src.services.auth.jwt.decode")
def test_refresh_access_token_saves_new_refresh_token(
    mock_decode,
    mock_create_access_token,
    mock_create_refresh_token,
):
    db = Mock()

    mock_decode.return_value = {
        "id": "123",
        "type": "refresh",
    }

    db_token = Mock()

    user = Mock()
    user.id = "123"

    db.query.return_value.filter.return_value.first.side_effect = [
        db_token,
        user,
    ]

    mock_create_access_token.return_value = "access"
    mock_create_refresh_token.return_value = "refresh"

    refresh_access_token_service(
        refresh_token="old-token",
        db=db,
    )

    saved_token = db.add.call_args.args[0]

    assert saved_token.user_id == user.id
    assert saved_token.token == "refresh"
