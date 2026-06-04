import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./testdb.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)