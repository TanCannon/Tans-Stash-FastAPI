from src.test.conftest import authenticated_client

from decimal import Decimal
from unittest.mock import patch

from src.services.plan_services import InvalidToolIdsException

# 1. Test: Successful Plan Creation
def test_create_plan_success(authenticated_client):
    payload = {
        "name": "Basic",
        "price": 99.99,
        "request_limit": 10000,
        "rate_limit": 100,
        "tool_ids": []
    }

    response = authenticated_client.post("/api/create-plan", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "Basic"
    assert Decimal(data["price"]) == Decimal("99.99")

# 2. Test: Duplicate Plan Name
def test_create_plan_duplicate(authenticated_client):
    payload = {
        "name": "Duplicate Plan",
        "price": 100,
        "request_limit": 1000,
        "rate_limit": 10,
        "tool_ids": []
    }

    # First insert
    authenticated_client.post("/api/create-plan", json=payload)

    # Second insert (should fail)
    response = authenticated_client.post("/api/create-plan", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Plan name already exists"

# 3. Test: Invalid Tool IDs
def test_create_plan_invalid_tool_ids(authenticated_client):

    payload = {
        "name": "Invalid Tool Plan",
        "price": 100,
        "request_limit": 1000,
        "rate_limit": 10,
        "tool_ids": [999]  # assume invalid
    }

    #this is a mock, “Whenever create_plan() is called → throw this exception”
    with patch("src.routers.api.plan_api.create_plan") as mock_create:
        mock_create.side_effect = InvalidToolIdsException(999)

        response = authenticated_client.post("/api/create-plan", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid tool IDs: 999"

# 4. Test: Unexpected Exception (500)
def test_create_plan_internal_error(authenticated_client):

    payload = {
        "name": "Crash Plan",
        "price": 100,
        "request_limit": 1000,
        "rate_limit": 10,
        "tool_ids": []
    }

    with patch("src.routers.api.plan_api.create_plan") as mock_create:
        mock_create.side_effect = Exception("DB crash")

        response = authenticated_client.post("/api/create-plan", json=payload)

    assert response.status_code == 500
    assert response.json()["detail"] == "Failed to create plan."

