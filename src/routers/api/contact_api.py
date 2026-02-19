from fastapi import Depends, APIRouter, HTTPException, Path, Query, Request
from src.models.contact_model import Contact
from src.database import SessionLocal
from starlette import status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated, List
from src.schemas import contact_schemas
from src.admin.auth import require_admin

router = APIRouter(
    prefix="/api",
    tags=["contact"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''Dependency Injection'''
#The API route depends on the db session to exist
db_dependency = Annotated[Session, Depends(get_db)]

# response_model=List[contact_schemas.ContactResponse]
@router.get("/read-all-contacts", status_code=status.HTTP_200_OK)
async def read_all_contacts(db: db_dependency, _: str =  Depends(require_admin)):
    return db.query(Contact).all()

@router.get("/read-the-contact/{contact_id}", status_code=status.HTTP_200_OK)
async def read_a_contact(db: db_dependency, contact_id: int = Path(gt=0), _: str =  Depends(require_admin)):
    contact = db.query(Contact).filter(Contact.sno == contact_id).first()

    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found.")

    return contact
    
@router.get("/read-all-contacts-paginated", status_code=status.HTTP_200_OK)
async def read_all_contacts_paginated(db: db_dependency, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100), _: str =  Depends(require_admin)):
    skip = (page - 1) * size
    total = db.query(Contact).count()
    contacts_array = (
        db.query(Contact)
        .offset(skip)
        .limit(size)
        .all()
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="No contacts available.")

    if skip >= total:
        raise HTTPException(status_code=404, detail="Page out of range.")

    return {
        "items": contacts_array,
        "total": total,
        "skip": skip,
        "limit": size,
    }

@router.post("/create-contact", name="contact.contact", status_code=status.HTTP_201_CREATED)
async def create_contact(db: db_dependency, contact_request: contact_schemas.ContactCreate):
    contact_model = Contact(**contact_request.model_dump())

    db.add(contact_model)
    db.commit()

