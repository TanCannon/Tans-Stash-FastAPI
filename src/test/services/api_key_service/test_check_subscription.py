from datetime import datetime, timedelta, timezone

from src.services.api_key_service import check_subscription
from src.models.user_model import User, PlanProduct, Plan, Subscription
from src.models.tool_model import Tool
# 1. Test: Empty Inputs
def test_check_subscription_empty_inputs(db):

    assert check_subscription(db, "", "") is False
    assert check_subscription(db, "user1", "") is False
    assert check_subscription(db, "", 1) is False


# 2. Test: Valid Active Subscription
def test_check_subscription_success(db):

    now = datetime.now(timezone.utc)

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    plan = Plan(
        id="plan1",
        name="Pro",
        price=100,
        request_limit=10000,
        rate_limit=100
    )

    db.add_all([user, tool, plan])
    db.commit()

    db.add(
        PlanProduct(
            plan_id=plan.id,
            tool_id=tool.id
        )
    )

    db.add(
        Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status="active",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=30)
        )
    )

    db.commit()

    result = check_subscription(
        db,
        user.id,
        tool.id
    )

    assert result is True


# 3. Test: No Subscription
def test_check_subscription_no_subscription(db):

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    db.add(tool)
    db.commit()

    result = check_subscription(
        db,
        "user1",
        tool.id
    )

    assert result is False


# 4. Test: Inactive Subscription
def test_check_subscription_inactive(db):

    now = datetime.now(timezone.utc)

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    plan = Plan(
        id="plan1",
        name="Pro",
        price=100,
        request_limit=10000,
        rate_limit=100
    )

    db.add_all([user, tool, plan])
    db.commit()

    db.add(
        PlanProduct(
            plan_id=plan.id,
            tool_id=tool.id
        )
    )

    db.add(
        Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status="inactive",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=30)
        )
    )

    db.commit()

    result = check_subscription(
        db,
        user.id,
        tool.id
    )

    assert result is False


# 5. Test: Expired Subscription
def test_check_subscription_expired(db):

    now = datetime.now(timezone.utc)

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    plan = Plan(
        id="plan1",
        name="Pro",
        price=100,
        request_limit=10000,
        rate_limit=100
    )

    db.add_all([user, tool, plan])
    db.commit()

    db.add(
        PlanProduct(
            plan_id=plan.id,
            tool_id=tool.id
        )
    )

    db.add(
        Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status="active",
            start_date=now - timedelta(days=30),
            end_date=now - timedelta(days=1)
        )
    )

    db.commit()

    result = check_subscription(
        db,
        user.id,
        tool.id
    )

    assert result is False


# 6. Test: Subscription Not Started Yet
def test_check_subscription_not_started(db):

    now = datetime.now(timezone.utc)

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    plan = Plan(
        id="plan1",
        name="Pro",
        price=100,
        request_limit=10000,
        rate_limit=100
    )

    db.add_all([user, tool, plan])
    db.commit()

    db.add(
        PlanProduct(
            plan_id=plan.id,
            tool_id=tool.id
        )
    )

    db.add(
        Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status="active",
            start_date=now + timedelta(days=1),
            end_date=now + timedelta(days=30)
        )
    )

    db.commit()

    result = check_subscription(
        db,
        user.id,
        tool.id
    )

    assert result is False


# 7. Test: Tool Not Included In Plan
def test_check_subscription_tool_not_in_plan(db):

    now = datetime.now(timezone.utc)

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool1 = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    tool2 = Tool(
        id=2,
        slug="tool2",
        name="Tool2"
    )

    plan = Plan(
        id="plan1",
        name="Pro",
        price=100,
        request_limit=10000,
        rate_limit=100
    )

    db.add_all([user, tool1, tool2, plan])
    db.commit()

    db.add(
        PlanProduct(
            plan_id=plan.id,
            tool_id=tool1.id
        )
    )

    db.add(
        Subscription(
            user_id=user.id,
            plan_id=plan.id,
            status="active",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=30)
        )
    )

    db.commit()

    result = check_subscription(
        db,
        user.id,
        tool2.id
    )

    assert result is False


# 8. Test: Multiple Subscriptions One Valid
def test_check_subscription_multiple_subscriptions(db):

    now = datetime.now(timezone.utc)

    user = User(
        id="user1",
        username="user1",
        email="user1@mail.com",
        password_hash="123"
    )

    tool = Tool(
        id=1,
        slug="tool1",
        name="Tool1"
    )

    basic = Plan(
        id="basic",
        name="Basic",
        price=10,
        request_limit=100,
        rate_limit=10
    )

    pro = Plan(
        id="pro",
        name="Pro",
        price=100,
        request_limit=10000,
        rate_limit=100
    )

    db.add_all([user, tool, basic, pro])
    db.commit()

    db.add(
        PlanProduct(
            plan_id=pro.id,
            tool_id=tool.id
        )
    )

    # expired basic subscription
    db.add(
        Subscription(
            user_id=user.id,
            plan_id=basic.id,
            status="active",
            start_date=now - timedelta(days=60),
            end_date=now - timedelta(days=30)
        )
    )

    # valid pro subscription
    db.add(
        Subscription(
            user_id=user.id,
            plan_id=pro.id,
            status="active",
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=30)
        )
    )

    db.commit()

    result = check_subscription(
        db,
        user.id,
        tool.id
    )

    assert result is True
