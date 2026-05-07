from src.models.tool_model import Tool
from src.models.user_model import Plan, PlanProduct, Subscription
from src.services.api_key_service import has_access_to_tool

# 1. Test: Empty Inputs
def test_has_access_empty_inputs(db):
    assert has_access_to_tool(db, "", 1) is False
    assert has_access_to_tool(db, 1, "") is False

# 2. Test: User Has Access
def test_has_access_success(db):
    # Create tool
    tool = Tool(slug="tool1", name="Tool1")
    db.add(tool)
    db.commit()

    # Create plan
    plan = Plan(name="Pro", price=100, request_limit=10000, rate_limit=10)
    db.add(plan)
    db.commit()

    # Link tool to plan
    db.add(
        PlanProduct(
            plan_id=plan.id,
            tool_id=tool.id
        )
    )

    # Create active subscription
    db.add(
        Subscription(
            user_id=1,
            plan_id=plan.id,
            status="active"
        )
    )

    db.commit()

    result = has_access_to_tool(db, 1, tool.id)

    assert result is True

# 3. Test: No Subscription
def test_has_access_no_subscription(db):
    tool = Tool(slug="tool1", name="Tool1")
    db.add(tool)
    db.commit()

    result = has_access_to_tool(db, 1, tool.id)

    assert result is False

# 4. Test: Inactive Subscription
def test_has_access_inactive_subscription(db):
    tool = Tool(slug="tool1", name="Tool1")
    db.add(tool)
    db.commit()

    plan = Plan(name="Pro", price=100, request_limit=10000, rate_limit=10)
    db.add(plan)
    db.commit()

    db.add(
        PlanProduct(
            plan_id=plan.id,
            tool_id=tool.id
        )
    )

    db.add(
        Subscription(
            user_id=1,
            plan_id=plan.id,
            status="inactive"
        )
    )

    db.commit()

    result = has_access_to_tool(db, 1, tool.id)

    assert result is False

# 5. Test: Tool Not Included in Plan
def test_has_access_tool_not_in_plan(db):
    tool1 = Tool(slug="tool1", name="Tool1")
    tool2 = Tool(slug="tool2", name="Tool2")

    db.add_all([tool1, tool2])
    db.commit()

    plan = Plan(name="Pro", price=100, request_limit=10000, rate_limit=10)
    db.add(plan)
    db.commit()

    # Only tool1 linked
    db.add(
        PlanProduct(
            plan_id=plan.id,
            tool_id=tool1.id
        )
    )

    db.add(
        Subscription(
            user_id=1,
            plan_id=plan.id,
            status="active"
        )
    )

    db.commit()

    result = has_access_to_tool(db, 1, tool2.id)

    assert result is False

# 6. Test: Multiple Users Isolation
def test_has_access_multiple_users(db):
    tool = Tool(slug="tool1", name="Tool1")
    db.add(tool)
    db.commit()

    plan = Plan(name="Pro", price=100, request_limit=10000, rate_limit=10)
    db.add(plan)
    db.commit()

    db.add(
        PlanProduct(
            plan_id=plan.id,
            tool_id=tool.id
        )
    )

    # User 1 active
    db.add(
        Subscription(
            user_id=1,
            plan_id=plan.id,
            status="active"
        )
    )

    db.commit()

    # User 2 should not have access
    result = has_access_to_tool(db, 2, tool.id)

    assert result is False

# 7. Test: Multiple Plans
def test_has_access_multiple_plans(db):
    tool1 = Tool(slug="tool1", name="Tool1")
    tool2 = Tool(slug="tool2", name="Tool2")

    db.add_all([tool1, tool2])
    db.commit()

    basic = Plan(name="Basic", price=10, request_limit=100, rate_limit=10)
    pro = Plan(name="Pro", price=100, request_limit=10000, rate_limit=100)

    db.add_all([basic, pro])
    db.commit()

    db.add_all([
        PlanProduct(plan_id=basic.id, tool_id=tool1.id),
        PlanProduct(plan_id=pro.id, tool_id=tool2.id),
    ])

    db.add(
        Subscription(
            user_id=1,
            plan_id=basic.id,
            status="active"
        )
    )

    db.commit()

    assert has_access_to_tool(db, 1, tool1.id) is True
    assert has_access_to_tool(db, 1, tool2.id) is False
