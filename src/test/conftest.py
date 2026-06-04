# tests/conftest.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base
from src.dependencies.database import get_db
from src.admin.auth import ADMIN_USERNAME, ADMIN_PASSWORD


# In-memory SQLite (fast + isolated)
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,  # important for in-memory DB
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# Setup + teardown DB per test
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


# Override FastAPI DB dependency
@pytest.fixture(scope="function")
def client(db):

    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    return TestClient(app)


# Admin dependency override (for protected routes)
@pytest.fixture
def admin_override():
    from src.admin.auth import require_admin

    def override_admin():
        return ADMIN_USERNAME  # mock admin user

    app.dependency_overrides[require_admin] = override_admin


# Authenticated client (real login flow)
@pytest.fixture
def authenticated_client(client):
    # Login
    response = client.post(
        "/api/admin/login",
        data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
    )

    assert response.status_code == 200

    yield client

    # Logout cleanup
    response = client.post("/api/admin/logout")
    assert response.status_code == 200