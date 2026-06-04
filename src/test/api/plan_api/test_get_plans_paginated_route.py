from src.test.conftest import client, db
from src.models.user_model import Plan

from datetime import datetime, timezone

# 1. Test: No Plans → 404
def test_get_paginated_plans_no_data(client: client):
    response = client.get("/api/get-paginated-plans?page=1&size=10")

    assert response.status_code == 404
    assert response.json()["detail"] == "No Plans available."

# 2. Test: Page Out of Range
def test_get_paginated_plans_out_of_range(client: client, db: db):
    db.add_all([
        Plan(name="Plan1", price=10, request_limit=100, rate_limit=10, created_at=datetime.now(timezone.utc)),
        Plan(name="Plan2", price=20, request_limit=200, rate_limit=20, created_at=datetime.now(timezone.utc))
    ])
    db.commit()

    # Page 2 with size 10 → skip = 10 (out of range)
    response = client.get("/api/get-paginated-plans?page=2&size=10")

    assert response.status_code == 404
    assert response.json()["detail"] == "Page out of range."

# 3. Test: Successful Pagination
def test_get_paginated_plans_success(client: client, db: db):

    db.add_all([
        Plan(name="Plan1", price=10, request_limit=100, rate_limit=10, created_at=datetime.now(timezone.utc)),
        Plan(name="Plan2", price=20, request_limit=200, rate_limit=20, created_at=datetime.now(timezone.utc)),
        Plan(name="Plan3", price=30, request_limit=300, rate_limit=30, created_at=datetime.now(timezone.utc))
    ])
    db.commit()

    response = client.get("/api/get-paginated-plans?page=1&size=2")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert data["skip"] == 0
    assert data["limit"] == 2
    assert len(data["items"]) == 2

# 4. Test: Pagination Logic (Page 2)
def test_get_paginated_plans_second_page(client: client, db: db):

    # Insert 3 plans
    db.add_all([
        Plan(name="Plan1", price=10, request_limit=100, rate_limit=10, created_at=datetime.now(timezone.utc)),
        Plan(name="Plan2", price=20, request_limit=200, rate_limit=20, created_at=datetime.now(timezone.utc)),
        Plan(name="Plan3", price=30, request_limit=300, rate_limit=30, created_at=datetime.now(timezone.utc))
    ])
    db.commit()

    response = client.get("/api/get-paginated-plans?page=2&size=2")

    assert response.status_code == 200

    data = response.json()

    assert data["skip"] == 2
    assert len(data["items"]) == 1   # only one left

