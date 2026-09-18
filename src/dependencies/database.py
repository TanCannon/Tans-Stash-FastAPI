from fastapi import Depends
from src.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''Dependency Injection'''
#The API route depends on the db session to exist
db_dependency = Annotated[Session, Depends(get_db)]