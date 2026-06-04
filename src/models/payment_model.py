from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    Numeric,
    String,
    DateTime,
    ForeignKey,
    Enum as SqlEnum,
    Index
)

from sqlalchemy.orm import relationship

from src.database import Base
from src.enums.payment_status import PaymentStatus


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    plan_id = Column(
        String, 
        ForeignKey("plans.id"), 
        nullable=False
    )

    amount = Column(Numeric(precision=10, scale=2),
        nullable=False
    )

    currency = Column(
        String(10),
        nullable=False,
        default="INR"
    )

    payment_gateway = Column(
        String(50),
        nullable=False
    )

    gateway_order_id = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    gateway_payment_id = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )

    gateway_signature = Column(
        String(500),
        nullable=True
    )

    status = Column(
        SqlEnum(PaymentStatus),
        nullable=False,
        default=PaymentStatus.CREATED,
        index=True
    )

    failure_reason = Column(
        String(500),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)    
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)    
    )

    paid_at = Column(
        DateTime,
        nullable=True
    )

    # ORM relationship
    user = relationship(
        "User",
        back_populates="payments"
    )

    __table_args__ = (
        Index("idx_payment_user_status", "user_id", "status"),
    )
