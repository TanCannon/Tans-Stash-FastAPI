from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Numeric
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from src.database import Base
from .tool_model import Tool

import uuid

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=gen_uuid)
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
    id = Column(String, primary_key=True, default=gen_uuid)
    name = Column(String, unique=True, nullable=False)
    price = Column(Numeric(precision=10, scale=2))
    request_limit = Column(Integer, nullable=False)
    rate_limit = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    plan_products = relationship(
        "PlanProduct",
        back_populates="plan",
        cascade="all, delete-orphan"
    )

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    plan_id = Column(String, ForeignKey("plans.id"))
    status = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    plan = relationship("Plan")

class PlanProduct(Base):
    __tablename__ = "plan_products"

    plan_id = Column(
        ForeignKey("plans.id", ondelete="CASCADE"),
        primary_key=True
    )
    tool_id = Column(
        ForeignKey("tools.id", ondelete="CASCADE"),
        primary_key=True
    )

    plan = relationship("Plan", back_populates="plan_products")
    tool = relationship("Tool", back_populates="plan_products")