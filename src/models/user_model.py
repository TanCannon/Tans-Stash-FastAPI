from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship

from src.database import Base

import uuid

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    role = Column(String(20), nullable=False, default="user")
    password_hash = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
    
class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    key_hash = Column(String)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User")

class Plan(Base):
    __tablename__ = "plans"
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    price = Column(Numeric(precision=10, scale=2))
    request_limit = Column(Integer)
    rate_limit = Column(Integer)

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    plan_id = Column(String, ForeignKey("plans.id"))
    status = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    plan = relationship("Plan")