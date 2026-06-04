import pytest

from unittest.mock import patch
from datetime import datetime, timezone, timedelta

from src.services.billing_service import (
    _create_payment_record,
    _mark_payment_success,
    _create_subscription,
    verify_payment_service,
    PLAN_DURATION_IN_DAYS
)

from src.models import (
    Payment,
    Subscription,
    Plan
)

from src.enums import (
    PaymentStatus,
    SubscriptionStatus
)

from src.exceptions import (
    InvalidPaymentSignatureError,
    PaymentNotFoundError,
    PlanNotFoundError,
    ActiveSubscriptionExistsError,
    DuplicatePaymentError
)

now = datetime.now(timezone.utc)

# ==================================================
# _create_payment_record
# ==================================================

def test_create_payment_record_success(db):
    payment = _create_payment_record(
        db=db,
        user_id="user_1",
        plan_id="plan_1",
        amount=499,
        gateway_order_id="order_123"
    )

    saved_payment = (
        db.query(Payment)
        .filter(Payment.id == payment.id)
        .first()
    )

    assert saved_payment is not None
    assert saved_payment.user_id == "user_1"
    assert saved_payment.plan_id == "plan_1"
    assert saved_payment.amount == 499
    assert saved_payment.gateway_order_id == "order_123"
    assert saved_payment.status == PaymentStatus.CREATED.value


# ==================================================
# _mark_payment_success
# ==================================================

def test_mark_payment_success_success(db):
    payment = Payment(
        user_id="user_1",
        plan_id="plan_1",
        amount=100,
        payment_gateway="mock",
        gateway_order_id="order_123",
        status=PaymentStatus.CREATED.value
    )

    db.add(payment)
    db.commit()

    result = _mark_payment_success(
        db=db,
        order_id="order_123",
        payment_id="pay_123",
        signature="sig_123"
    )

    assert result.status == PaymentStatus.SUCCESS.value
    assert result.gateway_payment_id == "pay_123"
    assert result.gateway_signature == "sig_123"
    assert result.paid_at is not None


def test_mark_payment_success_payment_not_found(db):
    with pytest.raises(PaymentNotFoundError):
        _mark_payment_success(
            db=db,
            order_id="missing_order",
            payment_id="pay_123",
            signature="sig_123"
        )


def test_mark_payment_success_idempotent(db):
    payment = Payment(
        user_id="user_1",
        plan_id="plan_1",
        amount=100,
        payment_gateway="mock",
        gateway_order_id="order_123",
        gateway_payment_id="pay_123",
        status=PaymentStatus.SUCCESS.value
    )

    db.add(payment)
    db.commit()

    result = _mark_payment_success(
        db=db,
        order_id="order_123",
        payment_id="another_payment",
        signature="another_signature"
    )

    assert result.id == payment.id
    assert result.status == PaymentStatus.SUCCESS.value


def test_mark_payment_success_duplicate_payment_id(db):
    payment_1 = Payment(
        user_id="user_1",
        plan_id="plan_1",
        amount=100,
        payment_gateway="mock",
        gateway_order_id="order_1",
        gateway_payment_id="pay_123",
        status=PaymentStatus.SUCCESS.value
    )

    payment_2 = Payment(
        user_id="user_2",
        plan_id="plan_2",
        amount=100,
        payment_gateway="mock",
        gateway_order_id="order_2",
        status=PaymentStatus.CREATED.value
    )

    db.add_all([
        payment_1,
        payment_2
    ])
    db.commit()

    with pytest.raises(DuplicatePaymentError):
        _mark_payment_success(
            db=db,
            order_id="order_2",
            payment_id="pay_123",
            signature="sig"
        )


# ==================================================
# _create_subscription
# ==================================================

def test_create_subscription_success(db):
    plan = Plan(
        id="plan_1",
        name="Premium",
        request_limit=10,
        rate_limit=1
    )

    db.add(plan)
    db.commit()

    subscription = _create_subscription(
        db=db,
        user_id="user_1",
        plan_id="plan_1"
    )

    assert subscription.user_id == "user_1"
    assert subscription.plan_id == "plan_1"
    assert subscription.status == SubscriptionStatus.ACTIVE.value

    duration = (
        subscription.end_date -
        subscription.start_date
    ).days

    assert duration == PLAN_DURATION_IN_DAYS


def test_create_subscription_plan_not_found(db):
    with pytest.raises(PlanNotFoundError):
        _create_subscription(
            db=db,
            user_id="user_1",
            plan_id="invalid_plan"
        )


def test_create_subscription_active_subscription_exists(db):
    plan = Plan(
        id="plan_1",
        name="Premium",
        request_limit=100,
        rate_limit=4
    )

    db.add(plan)

    subscription = Subscription(
        user_id="user_1",
        plan_id="plan_1",
        status=SubscriptionStatus.ACTIVE.value,
        start_date=now,
        end_date=now + timedelta(days=PLAN_DURATION_IN_DAYS)

    )

    db.add(subscription)
    db.commit()

    with pytest.raises(
        ActiveSubscriptionExistsError
    ):
        _create_subscription(
            db=db,
            user_id="user_1",
            plan_id="plan_1"
        )


# ==================================================
# verify_payment_service
# ==================================================

@patch(
    "src.services.billing_service.payment_gateway.verify_payment"
)
@patch(
    "src.services.billing_service._create_subscription"
)
@patch(
    "src.services.billing_service._mark_payment_success"
)
def test_verify_payment_service_success(
    mock_mark_payment,
    mock_create_subscription,
    mock_verify,
    db
):
    mock_verify.return_value = True

    payment = Payment(
        user_id="user_1",
        plan_id="plan_1",
        amount=100,
        payment_gateway="mock",
        gateway_order_id="order_123",
        status=PaymentStatus.SUCCESS.value
    )

    subscription = Subscription(
        user_id="user_1",
        plan_id="plan_1",
        status=SubscriptionStatus.ACTIVE.value
    )

    mock_mark_payment.return_value = payment
    mock_create_subscription.return_value = subscription

    with patch.object(db, "refresh"):
        result = verify_payment_service(
            db=db,
            signature="sig",
            order_id="order",
            payment_id="pay"
        )

    assert result == subscription

    mock_verify.assert_called_once_with("sig")

    mock_mark_payment.assert_called_once_with(
        db=db,
        order_id="order",
        payment_id="pay",
        signature="sig"
    )

    mock_create_subscription.assert_called_once_with(
        db=db,
        user_id="user_1",
        plan_id="plan_1"
    )


@patch(
    "src.services.billing_service.payment_gateway.verify_payment"
)
def test_verify_payment_service_invalid_signature(
    mock_verify,
    db
):
    mock_verify.return_value = False

    with pytest.raises(
        InvalidPaymentSignatureError
    ):
        verify_payment_service(
            db=db,
            signature="bad_sig",
            order_id="order",
            payment_id="pay"
        )


@patch(
    "src.services.billing_service.payment_gateway.verify_payment"
)
@patch(
    "src.services.billing_service._mark_payment_success"
)
def test_verify_payment_service_rollback(
    mock_mark_payment,
    mock_verify,
    db
):
    mock_verify.return_value = True

    mock_mark_payment.side_effect = (
        PaymentNotFoundError()
    )

    with pytest.raises(
        PaymentNotFoundError
    ):
        verify_payment_service(
            db=db,
            signature="sig",
            order_id="order",
            payment_id="pay"
        )
