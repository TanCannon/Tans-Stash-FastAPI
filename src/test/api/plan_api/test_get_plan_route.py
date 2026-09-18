from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import patch

from src.test.conftest import client, db

# 1. Test: Plan Found (DB-based)
def test_get_plan_success(client: client, db: db):
    from src.models import Plan


    # Create plan
    plan = Plan(
        name="Test Plan",
        price=100,
        request_limit=1000,
        rate_limit=10,
        created_at=datetime.now(timezone.utc)
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    # Call API
    response = client.get(f"/api/plans/{plan.id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == plan.id
    assert data["name"] == "Test Plan"
    assert Decimal(data["price"]) == Decimal("100")

# 2. Test: Plan Not Found → 404
def test_get_plan_not_found(client: client):
    response = client.get("/api/plans/999999")  # assuming doesn't exist

    assert response.status_code == 404
    assert response.json()["detail"] == "Plan not found."

# 3. Test: Service Layer Mock (clean isolation)
def test_get_plan_mocked_success(client: client):

    mock_plan = {
        "id": '1',
        "name": "Mock Plan",
        "price": 50,
        "request_limit": 500,
        "rate_limit": 5,
        "created_at": "2024-01-01T00:00:00",
        "tool_ids": []
    }

    with patch("src.routers.plan_api.get_plan") as mock_get_plan:
        mock_get_plan.return_value = mock_plan

        response = client.get("/api/plans/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Mock Plan"

# 4. Test: Service Returns None → 404
def test_get_plan_mocked_not_found(client: client):

    with patch("src.routers.plan_api.get_plan") as mock_get_plan:
        mock_get_plan.return_value = None

        response = client.get("/api/plans/123")

    assert response.status_code == 404
    assert response.json()["detail"] == "Plan not found."