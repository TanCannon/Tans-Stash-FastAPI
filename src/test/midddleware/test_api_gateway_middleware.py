from unittest.mock import patch, ANY

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from sqlalchemy.exc import SQLAlchemyError

from src.exceptions import RedisUnavailableException

from src.middleware.api_gateway_middleware import (
    APIGatewayMiddleware
)

# -----------------------------------
# Test App Setup
# -----------------------------------

app = FastAPI()

app.add_middleware(APIGatewayMiddleware)


@app.get("/protected")
async def protected_route(request: Request):

    return {
        "message": "success",
        "user_id": request.state.user_id,
        "api_key_id": request.state.api_key_id
    }


@app.get("/public")
async def public_route():

    return {"message": "public"}


client = TestClient(app)


# -----------------------------------
# Public Route Tests
# -----------------------------------

def test_public_route_skips_middleware():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=False
    ):

        response = client.get("/public")

    assert response.status_code == 200

    assert response.json() == {
        "message": "public"
    }


# -----------------------------------
# API Key Tests
# -----------------------------------

def test_missing_api_key():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ):

        response = client.get("/protected")

    assert response.status_code == 401

    assert response.json() == {
        "detail": "API key missing"
    }


def test_invalid_api_key():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_validate_api_key",
        return_value=None
    ) as mock_validate:

        response = client.get(
            "/protected",
            headers={"x-api-key": "invalid"}
        )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Invalid API key"
    }

    mock_validate.assert_called_once()


# -----------------------------------
# Rate Limit Tests
# -----------------------------------

def test_rate_limit_exceeded():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_validate_api_key"
    ) as mock_validate, patch.object(
        APIGatewayMiddleware,
        "_check_rate_limit",
        return_value=False
    ) as mock_rate_limit:

        mock_validate.return_value = {
            "user_id": "user123",
            "api_key_id": "key123"
        }

        response = client.get(
            "/protected",
            headers={"x-api-key": "valid"}
        )

    assert response.status_code == 429

    assert response.json() == {
        "detail": "Rate limit exceeded"
    }

    mock_rate_limit.assert_called_once_with(
        db=ANY,
        key_id="key123"
    )


# -----------------------------------
# Endpoint Mapping Tests
# -----------------------------------

def test_endpoint_not_mapped():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_validate_api_key"
    ) as mock_validate, patch.object(
        APIGatewayMiddleware,
        "_check_rate_limit",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_get_tool_id",
        return_value=None
    ) as mock_tool:

        mock_validate.return_value = {
            "user_id": "user123",
            "api_key_id": "key123"
        }

        response = client.get(
            "/protected",
            headers={"x-api-key": "valid"}
        )

    assert response.status_code == 404

    assert response.json() == {
        "detail": "Endpoint not mapped to any tool"
    }

    mock_tool.assert_called_once_with(
        db=ANY,
        request_path="/protected"
    )


# -----------------------------------
# Access Validation Tests
# -----------------------------------

def test_access_denied():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_validate_api_key"
    ) as mock_validate, patch.object(
        APIGatewayMiddleware,
        "_check_rate_limit",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_get_tool_id",
        return_value="tool123"
    ), patch.object(
        APIGatewayMiddleware,
        "_has_tool_access",
        return_value=False
    ) as mock_access:

        mock_validate.return_value = {
            "user_id": "user123",
            "api_key_id": "key123"
        }

        response = client.get(
            "/protected",
            headers={"x-api-key": "valid"}
        )

    assert response.status_code == 403

    assert response.json() == {
        "detail": "Access denied for this API"
    }

    mock_access.assert_called_once_with(
        db=ANY,
        key_id="key123",
        tool_id="tool123"
    )


# -----------------------------------
# Request Limit Tests
# -----------------------------------

def test_request_limit_exceeded():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_validate_api_key"
    ) as mock_validate, patch.object(
        APIGatewayMiddleware,
        "_check_rate_limit",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_get_tool_id",
        return_value="tool123"
    ), patch.object(
        APIGatewayMiddleware,
        "_has_tool_access",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_check_request_limit",
        return_value=False
    ) as mock_request_limit:

        mock_validate.return_value = {
            "user_id": "user123",
            "api_key_id": "key123"
        }

        response = client.get(
            "/protected",
            headers={"x-api-key": "valid"}
        )

    assert response.status_code == 429

    assert response.json() == {
        "detail": "Monthly request limit exceeded"
    }

    mock_request_limit.assert_called_once_with(
        db=ANY,
        key_id="key123"
    )


# -----------------------------------
# Success Flow Test
# -----------------------------------

def test_successful_request():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_validate_api_key"
    ) as mock_validate, patch.object(
        APIGatewayMiddleware,
        "_check_rate_limit",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_get_tool_id",
        return_value="tool123"
    ), patch.object(
        APIGatewayMiddleware,
        "_has_tool_access",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_check_request_limit",
        return_value=True
    ):

        mock_validate.return_value = {
            "user_id": "user123",
            "api_key_id": "key123"
        }

        response = client.get(
            "/protected",
            headers={"x-api-key": "valid"}
        )

    assert response.status_code == 200

    assert response.json() == {
        "message": "success",
        "user_id": "user123",
        "api_key_id": "key123"
    }


# -----------------------------------
# Redis Exception Tests
# -----------------------------------

def test_redis_error():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_validate_api_key"
    ) as mock_validate, patch.object(
        APIGatewayMiddleware,
        "_check_rate_limit",
        side_effect=RedisUnavailableException()
    ):

        mock_validate.return_value = {
            "user_id": "user123",
            "api_key_id": "key123"
        }

        response = client.get(
            "/protected",
            headers={"x-api-key": "valid"}
        )

    assert response.status_code == 503

    assert response.json() == {
        "detail": "Service temporarily unavailable"
    }


# -----------------------------------
# Database Exception Tests
# -----------------------------------

def test_database_error():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_validate_api_key",
        side_effect=SQLAlchemyError()
    ):

        response = client.get(
            "/protected",
            headers={"x-api-key": "valid"}
        )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Database error"
    }


# -----------------------------------
# Unexpected Exception Tests
# -----------------------------------

def test_internal_server_error():

    with patch(
        "src.middleware.api_gateway_middleware.is_protected_route",
        return_value=True
    ), patch.object(
        APIGatewayMiddleware,
        "_validate_api_key",
        side_effect=Exception()
    ):

        response = client.get(
            "/protected",
            headers={"x-api-key": "valid"}
        )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Internal server error"
    }

