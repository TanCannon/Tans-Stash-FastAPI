from unittest.mock import patch
from datetime import datetime, timezone, timedelta

from src.models.user_model import User, Plan, Subscription, PlanProduct, APIKey
from src.models.tool_model import Tool

from src.services.api_key_service import (
    check_rate_limit
)

now = datetime.now()
PLAN_DURATION_IN_DAYS = 30

# ---------------------------------------------------------
# 1. Empty Key ID
# ---------------------------------------------------------

def test_check_rate_limit_empty_key_id(db):

    assert check_rate_limit(
        db=db,
        key_id=""
    ) is False


# ---------------------------------------------------------
# 2. Invalid API Key
# ---------------------------------------------------------

def test_check_rate_limit_invalid_key(db):

    assert check_rate_limit(
        db=db,
        key_id="invalid_key"
    ) is False


# ---------------------------------------------------------
# 3. First Request Allowed
# ---------------------------------------------------------

@patch("src.services.api_key_service.redis_client")
def test_check_rate_limit_first_request(
    mock_redis,
    db
):

    # -----------------------------
    # Setup DB Data
    # -----------------------------

    user = User(
        id="user_1",
        username="testuser",
        email="test@mail.com",
        password_hash="hashed"
    )

    db.add(user)

    plan = Plan(
        id="plan_1",
        name="Free",
        request_limit=1000,
        rate_limit=5
    )

    db.add(plan)

    tool = Tool(
        id=1,
        slug="weather-api",
        name="Weather API"
    )

    db.add(tool)

    subscription = Subscription(
        id="sub_1",
        user_id=user.id,
        plan_id=plan.id,
        status="active",
        start_date=now,
        end_date=now + timedelta(days=PLAN_DURATION_IN_DAYS)

    )

    db.add(subscription)

    plan_product = PlanProduct(
        plan_id=plan.id,
        tool_id=tool.id
    )

    db.add(plan_product)

    api_key = APIKey(
        id="key_1",
        user_id=user.id,
        tool_id=tool.id,
        key_hash="hashed_key",
        is_active=True
    )

    db.add(api_key)

    db.commit()

    # -----------------------------
    # Redis Mock
    # -----------------------------

    mock_redis.get.return_value = None

    # -----------------------------
    # Execute
    # -----------------------------

    result = check_rate_limit(
        db=db,
        key_id=api_key.id
    )

    # -----------------------------
    # Assertions
    # -----------------------------

    assert result is True

    mock_redis.set.assert_called_once()


# ---------------------------------------------------------
# 4. Request Within Limit
# ---------------------------------------------------------

@patch("src.services.api_key_service.redis_client")
def test_check_rate_limit_within_limit(
    mock_redis,
    db
):

    user = User(
        id="user_1",
        username="testuser",
        email="test@mail.com",
        password_hash="hashed"
    )

    db.add(user)

    plan = Plan(
        id="plan_1",
        name="Pro",
        request_limit=1000,
        rate_limit=5
    )

    db.add(plan)

    tool = Tool(
        id=1,
        slug="weather-api",
        name="Weather API"
    )

    db.add(tool)

    subscription = Subscription(
        id="sub_1",
        user_id=user.id,
        plan_id=plan.id,
        status="active",
        start_date=now,
        end_date=now + timedelta(days=PLAN_DURATION_IN_DAYS)

    )

    db.add(subscription)

    plan_product = PlanProduct(
        plan_id=plan.id,
        tool_id=tool.id
    )

    db.add(plan_product)

    api_key = APIKey(
        id="key_1",
        user_id=user.id,
        tool_id=tool.id,
        key_hash="hashed_key",
        is_active=True
    )

    db.add(api_key)

    db.commit()

    # Current request count below limit
    mock_redis.get.return_value = "2"

    result = check_rate_limit(
        db=db,
        key_id=api_key.id
    )

    assert result is True

    mock_redis.incr.assert_called_once()


# ---------------------------------------------------------
# 5. Rate Limit Exceeded
# ---------------------------------------------------------

@patch("src.services.api_key_service.redis_client")
def test_check_rate_limit_exceeded(
    mock_redis,
    db
):

    user = User(
        id="user_1",
        username="testuser",
        email="test@mail.com",
        password_hash="hashed"
    )

    db.add(user)

    plan = Plan(
        id="plan_1",
        name="Pro",
        request_limit=1000,
        rate_limit=5
    )

    db.add(plan)

    tool = Tool(
        id=1,
        slug="weather-api",
        name="Weather API"
    )

    db.add(tool)

    subscription = Subscription(
        id="sub_1",
        user_id=user.id,
        plan_id=plan.id,
        status="active",
        start_date=now,
        end_date=now + timedelta(days=PLAN_DURATION_IN_DAYS)
    )

    db.add(subscription)

    plan_product = PlanProduct(
        plan_id=plan.id,
        tool_id=tool.id
    )

    db.add(plan_product)

    api_key = APIKey(
        id="key_1",
        user_id=user.id,
        tool_id=tool.id,
        key_hash="hashed_key",
        is_active=True
    )

    db.add(api_key)

    db.commit()

    # Already at limit
    mock_redis.get.return_value = "5"

    result = check_rate_limit(
        db=db,
        key_id=api_key.id
    )

    assert result is False

    mock_redis.incr.assert_not_called()

