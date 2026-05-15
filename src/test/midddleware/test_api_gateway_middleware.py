from unittest.mock import patch

# from src.main import app

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from sqlalchemy.exc import SQLAlchemyError

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

@patch(
    "src.middleware.api_gateway_middleware.is_protected_route",
    return_value=False
)
def test_public_route_skips_middleware(mock_protected):

    response = client.get("/public")

    assert response.status_code == 200
    assert response.json() == {
        "message": "public"
    }


# -----------------------------------
# API Key Tests
# -----------------------------------

@patch(
    "src.middleware.api_gateway_middleware.is_protected_route",
    return_value=True
)
def test_missing_api_key(mock_protected):

    response = client.get("/protected")

    assert response.status_code == 401
    assert response.json() == {
        "detail": "API key missing"
    }


@patch(
    "src.middleware.api_gateway_middleware.is_protected_route",
    return_value=True
)
@patch(
    "src.middleware.api_gateway_middleware.validate_api_key",
    return_value=None
)
def test_invalid_api_key(
    mock_validate,
    mock_protected
):

    response = client.get(
        "/protected",
        headers={"x-api-key": "invalid"}
    )

    assert response.status_code == 403
    assert response.json() == {
        "detail": "Invalid API key"
    }


# -----------------------------------
# Rate Limit Tests
# -----------------------------------
'''
@patch(
    "src.middleware.api_gateway_middleware.is_protected_route",
    return_value=True
)
@patch(
    "src.middleware.api_gateway_middleware.validate_api_key"
)
@patch(
    "src.middleware.api_gateway_middleware.check_rate_limit",
    return_value=False
)
def test_rate_limit_exceeded(
    mock_rate_limit,
    mock_validate,
    mock_protected
):

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

'''
# -----------------------------------
# Endpoint Mapping Tests
# -----------------------------------

@patch(
    "src.middleware.api_gateway_middleware.is_protected_route",
    return_value=True
)
@patch(
    "src.middleware.api_gateway_middleware.validate_api_key"
)

#@patch(
#    "src.middleware.api_gateway_middleware.check_rate_limit",
#    return_value=True
#)

@patch.object(
    APIGatewayMiddleware,
    "_get_tool_id",
    return_value=None
)
def test_endpoint_not_mapped(
    mock_tool,
    # mock_rate_limit,
    mock_validate,
    mock_protected
):

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


# -----------------------------------
# Access Validation Tests
# -----------------------------------

@patch(
    "src.middleware.api_gateway_middleware.is_protected_route",
    return_value=True
)
@patch(
    "src.middleware.api_gateway_middleware.validate_api_key"
)
#@patch(
 #   "src.middleware.api_gateway_middleware.check_rate_limit",
  #  return_value=True
#)
@patch.object(
    APIGatewayMiddleware,
    "_get_tool_id",
    return_value="tool123"
)
@patch(
    "src.middleware.api_gateway_middleware.has_access_to_tool",
    return_value=False
)
def test_access_denied(
    mock_access,
    mock_tool,
    # mock_rate_limit,
    mock_validate,
    mock_protected
):

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


# -----------------------------------
# Success Flow Test
# -----------------------------------

@patch(
    "src.middleware.api_gateway_middleware.is_protected_route",
    return_value=True
)
@patch(
    "src.middleware.api_gateway_middleware.validate_api_key"
)

#@patch(
 #   "src.middleware.api_gateway_middleware.check_rate_limit",
  #  return_value=True
#)
@patch.object(
    APIGatewayMiddleware,
    "_get_tool_id",
    return_value="tool123"
)
@patch(
    "src.middleware.api_gateway_middleware.has_access_to_tool",
    return_value=True
)
def test_successful_request(
    mock_access,
    mock_tool,
    # mock_rate_limit,
    mock_validate,
    mock_protected
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
# Database Exception Tests
# -----------------------------------

@patch(
    "src.middleware.api_gateway_middleware.is_protected_route",
    return_value=True
)
@patch(
    "src.middleware.api_gateway_middleware.validate_api_key",
    side_effect=SQLAlchemyError()
)
def test_database_error(
    mock_validate,
    mock_protected
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

@patch(
    "src.middleware.api_gateway_middleware.is_protected_route",
    return_value=True
)
@patch(
    "src.middleware.api_gateway_middleware.validate_api_key",
    side_effect=Exception()
)
def test_internal_server_error(
    mock_validate,
    mock_protected
):

    response = client.get(
        "/protected",
        headers={"x-api-key": "valid"}
    )

    assert response.status_code == 500

    assert response.json() == {
        "detail": "Internal server error"
    }
  
