from unittest.mock import patch


@patch("src.routers.auth_api.refresh_access_token_service")
def test_refresh_access_token_success(
    mock_refresh_service,
    client
):
    mock_refresh_service.return_value = {
        "success": True,
        "access_token": "new-access-token"
    }

    response = client.post(
        "/api/auth/refresh",
        params={
            "refresh_token": "refresh-token-123"
        }
    )

    assert response.status_code == 200

    assert response.json() == {
        "success": True,
        "access_token": "new-access-token"
    }

    mock_refresh_service.assert_called_once()

@patch("src.routers.auth_api.refresh_access_token_service")
def test_refresh_access_token_passes_correct_arguments(
    mock_refresh_service,
    client
):
    mock_refresh_service.return_value = {
        "success": True
    }

    client.post(
        "/api/auth/refresh",
        params={
            "refresh_token": "refresh-token-123"
        }
    )

    _, kwargs = mock_refresh_service.call_args

    assert kwargs["refresh_token"] == "refresh-token-123"

def test_refresh_access_token_requires_refresh_token(
    client
):
    response = client.post(
        "/api/auth/refresh"
    )

    assert response.status_code == 422

@patch("src.routers.auth_api.refresh_access_token_service")
def test_refresh_access_token_allows_empty_token(
    mock_refresh_service,
    client
):
    mock_refresh_service.return_value = {
        "success": True
    }

    response = client.post(
        "/api/auth/refresh",
        params={
            "refresh_token": ""
        }
    )

    assert response.status_code == 200

    _, kwargs = mock_refresh_service.call_args

    assert kwargs["refresh_token"] == ""
