from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from src.database import Base
from src.main import app
from fastapi.testclient import TestClient
import pytest
from src.models.contact_model import Contact
from src.admin.auth import ADMIN_USERNAME, ADMIN_PASSWORD

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass = StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def authenticated_client(client):
    # Step 1: Login
    response = client.post(
        "/api/admin/login",
        data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
    )
    assert response.status_code == 200
    assert response.json() == {
            "message": "Login successful",
            "admin": ADMIN_USERNAME
        }

    # Provide logged-in client to test
    yield client

    # Step 2: Logout (after test finishes)
    response = client.post("/api/admin/logout")
    assert response.status_code == 200 
    assert response.json() == {
        "message": "Logged out successfully"
    }

@pytest.fixture
def test_contact_api():
    contact = Contact(
       sno=1,
       name="Harry Potter",
       phone_no="+912345679810",
       msg="Abra cadabra",
       email="harry.potter@hogwarts.com"
    )

    db = TestingSessionLocal()
    db.add(contact)
    db.commit()
    yield contact
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM contacts;"))
        connection.commit()