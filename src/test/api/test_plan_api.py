from src.test.conftest import *

from decimal import Decimal

#create a plan tests

def test_create_plan_success(authenticated_client):
    payload = {
        "name": "Basic",
        "price": 99.99,
        "request_limit": 10000,
        "rate_limit": 100
    }

    response = authenticated_client.post("/api/create-plan", json=payload)

    assert response.status_code == 201
    data = response.json()

    assert data["name"] == "Basic"
    assert Decimal(data["price"]) == Decimal("99.99")

def test_create_plan_duplicate_name(authenticated_client):
    payload = {
        "name": "Pro",
        "price": 199.99,
        "request_limit": 10000,
        "rate_limit": 2000
    }

    authenticated_client.post("/api/create-plan", json=payload)
    response = authenticated_client.post("/api/create-plan", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Plan name already exists"

# get paginated plans tests

def test_get_paginated_plans_success(client, authenticated_client):
    # Insert plans
    for i in range(15):
        authenticated_client.post("/api/create-plan", json={
            "name": f"Plan{i}",
            "price": 10,
            "request_limit": 10000,
            "rate_limit": 100
        })

    response = client.get("/api/get-paginated-plans?page=1&size=10")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 10
    assert data["total"] == 15
    assert data["skip"] == 0

def test_get_paginated_plans_empty(client):
    response = client.get("/api/get-paginated-plans")

    assert response.status_code == 404
    assert response.json()["detail"] == "No Plans available."

def test_get_paginated_plans_out_of_range(client, authenticated_client):
    for i in range(5):
        authenticated_client.post("/api/create-plan", json={
            "name": f"Plan{i}",
            "price": 10,
            "request_limit": 10000,
            "rate_limit": 100
        })

    response = client.get("/api/get-paginated-plans?page=3&size=10")

    assert response.status_code == 404
    assert response.json()["detail"] == "Page out of range."

def test_read_plan_success(authenticated_client):
    res = authenticated_client.post("/api/create-plan", json={
        "name": "Starter",
        "price": 50,
        "request_limit": 10000,
        "rate_limit": 500
    })

    plan_id = res.json()["id"]

    response = authenticated_client.get(f"/api/plans/{plan_id}")

    assert response.status_code == 200
    assert response.json()["name"] == "Starter"


def test_read_plan_not_found(client):
    response = client.get("/api/plans/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Plan not found."

#update plan tests

def test_update_plan_success(authenticated_client):
    res = authenticated_client.post("/api/create-plan", json={
        "name": "Silver",
        "price": 100,
        "request_limit": 10000,
        "rate_limit": 1000
    })

    plan_id = res.json()["id"]

    response = authenticated_client.put(f"/api/update-plan/{plan_id}", json={
        "name": "Gold",
        "price": 150,
        "request_limit": 10000,
        "rate_limit": 2000
    })

    assert response.status_code == 202

    updated = authenticated_client.get(f"/api/plans/{plan_id}").json()
    assert updated["name"] == "Gold"


def test_update_plan_duplicate_name(authenticated_client):
    authenticated_client.post("/api/create-plan", json={
        "name": "PlanA",
        "price": 10,
        "request_limit": 10000,
        "rate_limit": 100
    })

    res = authenticated_client.post("/api/create-plan", json={
        "name": "PlanB",
        "price": 20,
        "request_limit": 10000,
        "rate_limit": 200
    })

    plan_id = res.json()["id"]

    response = authenticated_client.put(f"/api/update-plan/{plan_id}", json={
        "name": "PlanA",
        "price": 20,
        "request_limit": 10000,
        "rate_limit": 200
    })

    assert response.status_code == 400
    assert response.json()["detail"] == "Plan name already exists."


def test_update_plan_not_found(authenticated_client):
    response = authenticated_client.put("/api/update-plan/999", json={
        "name": "Ghost",
        "price": 10,
        "request_limit": 10000,
        "rate_limit": 100
    })

    assert response.status_code == 404

#delete a plan tests

def test_delete_plan_success(client, authenticated_client):
    res = authenticated_client.post("/api/create-plan", json={
        "name": "DeleteMe",
        "price": 10,
        "request_limit": 10000,
        "rate_limit": 100
    })

    plan_id = res.json()["id"]

    response = authenticated_client.delete(f"/api/delete-plan/{plan_id}")

    assert response.status_code == 204

    check = client.get(f"/api/plans/{plan_id}")
    assert check.status_code == 404


def test_delete_plan_not_found(client, authenticated_client):
    response = client.delete("/api/delete-plan/999")

    assert response.status_code == 404