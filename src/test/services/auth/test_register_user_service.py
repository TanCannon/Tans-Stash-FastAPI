# tests/services/auth/test_register_user_service.py

import pytest
from unittest.mock import Mock, patch

from src.services import register_user_service
from src.schemas import user_schemas
from src.exceptions import (
    UserAlreadyExistsError,
    UserRegistrationError
)


# ==========================================================
# Test: User already exists
# Expected:
#   - Service should not attempt user creation
#   - UserAlreadyExistsError should be raised
# ==========================================================
def test_register_user_raises_if_user_already_exists():
    db = Mock()

    existing_user = Mock()

    # Simulate finding an existing user in DB
    db.query.return_value.filter.return_value.first.return_value = existing_user

    with pytest.raises(UserAlreadyExistsError):
        register_user_service(
            db=db,
            username="tanmaya",
            email="tanmaya@test.com",
            password="password123",
        )


# ==========================================================
# Test: Successful registration
# Expected:
#   - User is created
#   - Success response is returned
# ==========================================================
@patch("src.services.auth._create_user")
def test_register_user_success(mock_create_user):
    db = Mock()

    # No existing user found
    db.query.return_value.filter.return_value.first.return_value = None

    created_user = Mock(
        id="123",
        username="tanmaya",
        email="tanmaya@test.com",
    )

    mock_create_user.return_value = created_user

    result = register_user_service(
        db=db,
        username="tanmaya",
        email="tanmaya@test.com",
        password="password123",
    )

    assert result == {
        "success": True,
        "message": "User created successfully",
        "user": created_user,
    }


# ==========================================================
# Test: Internal user creation failure
# Expected:
#   - Any exception from _create_user
#     should be converted into
#     UserRegistrationError
# ==========================================================
@patch("src.services.auth._create_user")
def test_register_user_raises_registration_error_when_create_user_fails(
    mock_create_user,
):
    db = Mock()

    # No existing user found
    db.query.return_value.filter.return_value.first.return_value = None

    mock_create_user.side_effect = Exception("Database exploded")

    with pytest.raises(UserRegistrationError):
        register_user_service(
            db=db,
            username="tanmaya",
            email="tanmaya@test.com",
            password="password123",
        )


# ==========================================================
# Test: Correct UserCreate schema passed to _create_user
# Expected:
#   - Service constructs UserCreate correctly
#   - Proper values are forwarded
# ==========================================================
@patch("src.services.auth._create_user")
def test_register_user_passes_correct_user_create_schema(
    mock_create_user,
):
    db = Mock()

    # No existing user found
    db.query.return_value.filter.return_value.first.return_value = None

    mock_create_user.return_value = Mock()

    register_user_service(
        db=db,
        username="tanmaya",
        email="tanmaya@test.com",
        password="password123",
    )

    # Inspect arguments passed to _create_user
    _, kwargs = mock_create_user.call_args

    assert kwargs["db"] == db

    user_data = kwargs["create_user_request"]

    assert isinstance(user_data, user_schemas.UserCreate)
    assert user_data.username == "tanmaya"
    assert user_data.email == "tanmaya@test.com"
    assert user_data.password == "password123"


# ==========================================================
# Test: _create_user called exactly once
# Expected:
#   - User creation helper invoked once
# ==========================================================
@patch("src.services.auth._create_user")
def test_register_user_calls_create_user_once(mock_create_user):
    db = Mock()

    db.query.return_value.filter.return_value.first.return_value = None

    mock_create_user.return_value = Mock()

    register_user_service(
        db=db,
        username="tanmaya",
        email="tanmaya@test.com",
        password="password123",
    )

    mock_create_user.assert_called_once()
