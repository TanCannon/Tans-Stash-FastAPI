from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from typing import Optional

from src.models import Payment, Subscription, Plan
from src.enums import PaymentStatus, SubscriptionStatus
from src.gateways import MockPaymentGateway
from src.exceptions import (
    InvalidPaymentSignatureError, 
    PaymentNotFoundError, 
    PlanNotFoundError, 
    ActiveSubscriptionExistsError,
    DuplicatePaymentError
)

PLAN_DURATION_IN_DAYS: int = 30
now = datetime.now()

payment_gateway = MockPaymentGateway()

def create_payment_record(
    db: Session,
    user_id: str,
    plan_id: str,
    amount: int,
    gateway_order_id: str
) -> Payment:

    payment = Payment(
        user_id=user_id,
        plan_id=plan_id,
        amount=amount,
        payment_gateway="mock_gateway",
        gateway_order_id=gateway_order_id,
        status=PaymentStatus.CREATED.value
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment

def _mark_payment_success(
    db: Session,
    order_id: str,
    payment_id: str,
    signature: str
)-> Optional[Payment]:
    #check if a payment actually started
    payment = (
        db.query(Payment)
        .filter(Payment.gateway_order_id == order_id)
        .first()
    )


    if not payment:
        raise PaymentNotFoundError()

    # IDEMPOTENCY CHECK
    if payment.status == PaymentStatus.SUCCESS.value:
        return payment

    existing = (
        db.query(Payment)
        .filter(Payment.gateway_payment_id == payment_id)
        .first()
    )

    if existing and existing.id != payment.id:
        raise DuplicatePaymentError()

    payment.gateway_payment_id = payment_id
    payment.gateway_signature = signature

    payment.status = PaymentStatus.SUCCESS.value

    payment.paid_at = datetime.now(timezone.utc)

    return payment

def _create_subscription(
    db: Session,
    user_id: str,
    plan_id: str
) -> Subscription:

    existing_subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
            Subscription.plan_id == plan_id,
            Subscription.status == SubscriptionStatus.ACTIVE.value
        )
        .first()
    )

    if existing_subscription:
        raise ActiveSubscriptionExistsError()

    plan = (
        db.query(Plan)
        .filter(Plan.id == plan_id)
        .first()
    )

    if not plan:
        raise PlanNotFoundError()

    now = datetime.now(timezone.utc)

    subscription = Subscription(
        user_id=user_id,
        plan_id=plan_id,
        status=SubscriptionStatus.ACTIVE.value,
        start_date=now,
        end_date=now + timedelta(days=PLAN_DURATION_IN_DAYS)
    )

    db.add(subscription)

    return subscription

def verify_payment_service(
    db: Session,
    signature: str,
    order_id: str,
    payment_id: str
) -> Subscription:
    try: 
        is_signature_verified = (
            payment_gateway.verify_payment(signature)
        )

        if not is_signature_verified:
            raise InvalidPaymentSignatureError()

        payment = _mark_payment_success(
            db=db,
            order_id=order_id,
            payment_id=payment_id,
            signature=signature
        )

        subscription = _create_subscription(
            db=db,
            user_id=payment.user_id,
            plan_id=payment.plan_id
        )

        db.commit()

        db.refresh(payment)
        db.refresh(subscription)

        return subscription
        '''
        return {
            "message": "Success",
            "detail": "Plan purchased successfully.",
            "subscription_id": subscription.id
        }
        '''

    except Exception: 
        db.rollback()
        raise


