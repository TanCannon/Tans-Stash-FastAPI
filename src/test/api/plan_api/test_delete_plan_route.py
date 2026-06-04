from unittest.mock import patch
from src.models.user_model import Plan
from datetime import datetime, timezone

from src.test.conftest import authenticated_client, db

# 1. Test: Successful Delete (Mocked)
def test_delete_plan_success(authenticated_client):

    with patch("src.routers.plan_api.delete_plan") as mock_delete:
        mock_delete.return_value = True

        response = authenticated_client.delete("/api/delete-plan/1")

    assert response.status_code == 204
    assert response.content == b""   # IMPORTANT: No body

# 2. Test: Plan Not Found → 404
def test_delete_plan_not_found(authenticated_client):

    with patch("src.routers.plan_api.delete_plan") as mock_delete:
        mock_delete.return_value = False

        response = authenticated_client.delete("/api/delete-plan/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Plan not found."

# 3. Real DB Test
def test_delete_plan_db(authenticated_client, db):
    # Create plan
    plan = Plan(
        name="Delete Me",
        price=100,
        request_limit=1000,
        rate_limit=10,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    # Delete it
    response = authenticated_client.delete(f"/api/delete-plan/{plan.id}")

    assert response.status_code == 204

    # Verify it's gone
    deleted = db.query(Plan).filter(Plan.id == plan.id).first()
    assert deleted is None

# 4. DB: Delete Non-existing
def test_delete_plan_db_not_found(authenticated_client):
    response = authenticated_client.delete("/api/delete-plan/123456")

    assert response.status_code == 404