from src.routers.api.contact_api import get_db, require_admin
from fastapi import status
from src.models import Contact
from .utils import app, override_get_db, client, TestingSessionLocal, test_contact_api, authenticated_client

app.dependency_overrides[get_db] = override_get_db

def test_delete_contact(test_contact_api, authenticated_client):
    #Step1: login (done in the fixture in utils.py)

    #Step2: delete the contact
    response = authenticated_client.delete('/api/delete-contact/1')
    assert response.status_code == 204

    #Step3: confirm the deletion
    db = TestingSessionLocal()
    try:
        model = db.query(Contact).filter(Contact.sno == 1).first()
        assert model is None
    finally:
        db.close()

def test_delete_contact_no_admin(client):
    response = client.delete('/api/delete-contact/1')

    assert response.status_code == 401

def test_delete_contact_no_db(authenticated_client):
    response = authenticated_client.delete('/api/delete-contact/1')

    
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Contact not found."
    }