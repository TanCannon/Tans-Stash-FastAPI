from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Numeric, Enum as SqlEnum
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint
from datetime import datetime, timezone

from src.database import Base
from .tool_model import Tool
from src.enums.subscription_status import SubscriptionStatus

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

    payments = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan"
        )

    subscriptions = relationship(
        "Subscription",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role})>"
    
class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    tool_id = Column(String, ForeignKey("tools.id"))
    key_hash = Column(String)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User")

    tool = relationship(
        "Tool",
        back_populates="api_keys"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "tool_id", name="uq_user_tool_key"),
    )

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

    subscriptions = relationship(
        "Subscription",
        back_populates="plan"
    )

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(
        String,
        primary_key=True,
        default=gen_uuid
    )

    user_id = Column(
        String,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    plan_id = Column(
        String,
        ForeignKey(
            "plans.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    status = Column(
        SqlEnum(SubscriptionStatus),
        nullable=False,
        default=SubscriptionStatus.PENDING
    )

    start_date = Column(
        DateTime,
        nullable=False,
        default=datetime.utcnow
    )

    end_date = Column(
        DateTime,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    plan = relationship(
        "Plan",
        back_populates="subscriptions"
    )

    user = relationship(
        "User",
        back_populates="subscriptions"
    )

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
