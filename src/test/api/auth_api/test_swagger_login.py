from unittest.mock import patch

@patch("src.routers.auth_api.provide_token_on_login_service")
def test_swagger_login_success(
    mock_login_service,
    client
):
    mock_login_service.return_value = (
        "access_token_123",
        "refresh_token_123"
    )

    response = client.post(
        "/api/token",
        data={
            "username": "tanmaya@test.com",
            "password": "password123"
        }
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "access_token_123",
        "token_type": "bearer"
    }

    mock_login_service.assert_called_once()


def test_swagger_login_missing_username(client):
    response = client.post(
        "/api/token",
        data={
            "password": "password123"
        }
    )

    assert response.status_code == 422


def test_swagger_login_missing_password(client):
    response = client.post(
        "/api/token",
        data={
            "username": "tanmaya@test.com"
        }
    )

    assert response.status_code == 422


@patch("src.routers.auth_api.provide_token_on_login_service")
def test_swagger_login_passes_correct_arguments(
    mock_login_service,
    client
):
    mock_login_service.return_value = (
        "access_token_123",
        "refresh_token_123"
    )

    client.post(
        "/api/token",
        data={
            "username": "tanmaya@test.com",
            "password": "password123"
        }
    )

    _, kwargs = mock_login_service.call_args

    # Verify db dependency was passed
    assert "db" in kwargs

    assert kwargs["email"] == "tanmaya@test.com"
    assert kwargs["password"] == "password123"

