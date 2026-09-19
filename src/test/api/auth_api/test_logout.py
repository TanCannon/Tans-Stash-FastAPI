from unittest.mock import patch

@patch("src.routers.auth_api.logout_service")
def test_logout_success(
    mock_logout_service,
    client
):
    mock_logout_service.return_value = {
        "success": True,
        "message": "Logged out successfully"
    }

    response = client.post(
        "/api/auth/logout",
        params={
            "refresh_token": "refresh-token-123"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "success": True,
        "message": "Logged out successfully"
    }

    mock_logout_service.assert_called_once()


@patch("src.routers.auth_api.logout_service")
def test_logout_passes_correct_arguments(
    mock_logout_service,
    client
):
    mock_logout_service.return_value = {
        "success": True
    }

    client.post(
        "/api/auth/logout",
        params={
            "refresh_token": "refresh-token-123"
        }
    )

    _, kwargs = mock_logout_service.call_args

    assert kwargs["refresh_token"] == "refresh-token-123"


def test_logout_requires_refresh_token(client):
    response = client.post("/api/auth/logout")

    assert response.status_code == 422


@patch("src.routers.auth_api.logout_service")
def test_logout_allows_empty_refresh_token(
    mock_logout_service,
    client
):
    mock_logout_service.return_value = {
        "success": True
    }

    response = client.post(
        "/api/auth/logout",
        params={
            "refresh_token": ""
        }
    )

    assert response.status_code == 200

    _, kwargs = mock_logout_service.call_args

    assert kwargs["refresh_token"] == ""
