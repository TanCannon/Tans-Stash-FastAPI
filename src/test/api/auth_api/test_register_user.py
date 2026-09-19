from unittest.mock import patch


# --------------------------------------------------
# Register User Tests
# --------------------------------------------------

@patch("src.routers.auth_api.register_user_service")
def test_register_user_success(mock_register_service, client):
    mock_register_service.return_value = {
        "success": True,
        "message": "User registered successfully"
    }

    response = client.post(
        "/api/auth/register",
        data={
            "username": "tanmaya",
            "email": "tanmaya@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "User registered successfully"
    }

    mock_register_service.assert_called_once()


def test_register_user_missing_username(client):
    response = client.post(
        "/api/auth/register",
        data={
            "email": "tanmaya@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_register_user_missing_email(client):
    response = client.post(
        "/api/auth/register",
        data={
            "username": "tanmaya",
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_register_user_missing_password(client):
    response = client.post(
        "/api/auth/register",
        data={
            "username": "tanmaya",
            "email": "tanmaya@test.com"
        }
    )

    assert response.status_code == 422


@patch("src.routers.auth_api.register_user_service")
def test_register_user_passes_correct_arguments(
    mock_register_service,
    client
):
    mock_register_service.return_value = {
        "success": True
    }

    client.post(
        "/api/auth/register",
        data={
            "username": "tanmaya",
            "email": "tanmaya@test.com",
            "password": "password123"
        }
    )

    _, kwargs = mock_register_service.call_args

    assert kwargs["username"] == "tanmaya"
    assert kwargs["email"] == "tanmaya@test.com"
    assert kwargs["password"] == "password123"

