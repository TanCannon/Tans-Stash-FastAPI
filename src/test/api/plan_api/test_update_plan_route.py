# 1. Test: Successful Update (Mocked)
from unittest.mock import patch
from datetime import datetime, timezone
from decimal import Decimal

from src.test.conftest import authenticated_client, db
from src.services.plan_services import PlanExistsException
from src.models.user_model import Plan

# 1. Test: Successful Update (Mocked)
def test_update_plan_success(authenticated_client):

    payload = {
        "id": '1',
        "name": "Updated Plan",
        "price": 200,
        "request_limit": 2000,
        "rate_limit": 20,
        "tool_ids": []
    }

    updated_plan = {
        "id": '1',
        "name": "Updated Plan",
        "price": 200,
        "request_limit": 2000,
        "created_at": "2024-01-01T00:00:00",
        "rate_limit": 20,
        "tool_ids": []
    }

    with patch("src.routers.plan_api.update_plan") as mock_update:
        mock_update.return_value = updated_plan

        response = authenticated_client.put("/api/update-plan/1", json=payload)
 
    assert response.status_code == 202
    assert response.json()["name"] == "Updated Plan"

# 2. Test: Plan Already Exists → 400
def test_update_plan_name_exists(authenticated_client):

    payload = {
        "name": "Duplicate Plan",
        "price": 200,
        "request_limit": 2000,
        "rate_limit": 20,
        "tool_ids": []
    }

    with patch("src.routers.plan_api.update_plan") as mock_update:
        mock_update.side_effect = PlanExistsException("Duplicate Plan")

        response = authenticated_client.put("/api/update-plan/1", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == f"Plan name {payload["name"]} already exists."

# 3. Test: ValueError → 400
def test_update_plan_value_error(authenticated_client):

    payload = {
        "name": "",
        "price": 200,
        "request_limit": 2000,
        "rate_limit": 20,
        "tool_ids": []
    }

    with patch("src.routers.plan_api.update_plan") as mock_update:
        mock_update.side_effect = ValueError("Invalid data")

        response = authenticated_client.put("/api/update-plan/1", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid data"

# 4. Test: Unexpected Exception → 500
def test_update_plan_internal_error(authenticated_client):

    payload = {
        "name": "Any Plan",
        "price": 200,
        "request_limit": 2000,
        "rate_limit": 20,
        "tool_ids": []
    }

    with patch("src.routers.plan_api.update_plan") as mock_update:
        mock_update.side_effect = Exception("DB crash")

        response = authenticated_client.put("/api/update-plan/1", json=payload)

    assert response.status_code == 500
    assert response.json()["detail"] == "DB crash"

# 5. (Optional but IMPORTANT) Real DB Test
def test_update_plan_db(authenticated_client, db):

    # Create initial plan
    plan = Plan(
        name="Old Plan",
        price=100,
        request_limit=1000,
        rate_limit=10,
        created_at=datetime.now(timezone.utc)
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    payload = {
        "name": "New Plan",
        "price": 500,
        "request_limit": 5000,
        "rate_limit": 50,
        "tool_ids": []
    }

    response = authenticated_client.put(f"/api/update-plan/{plan.id}", json=payload)

    assert response.status_code == 202

    data = response.json()
    assert data["name"] == "New Plan"
    assert Decimal(data["price"]) == Decimal("500")