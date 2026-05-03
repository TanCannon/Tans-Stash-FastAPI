from decimal import Decimal
import pytest

from sqlalchemy.orm import Session
from src.models.user_model import Plan, PlanProduct
# from src.models.tool_model import Tool
from src.schemas.plan_schemas import PlanCreate
from src.services.plan_services import *

from ..conftest import db

'''
============================
create_plan service tests
============================
'''
# 1. Test: Successful Plan Creation
def test_create_plan_success(db: Session):
    # Seed tools in DB
    tools = [
        Tool(id=1, name="Tool1", slug="tool-1"),
        Tool(id=2, name="Tool2", slug="tool-2"),
        Tool(id=3, name="Tool3", slug="tool-3"),
    ]
    db.add_all(tools)
    db.commit()

    data = PlanCreate(
        name="Pro Plan",
        price=199.99,
        request_limit=10000,
        rate_limit=100,
        tool_ids=[1, 2, 3]
    )

    # Call service
    plan = create_plan(db, data)

    # Assertions
    assert plan.id is not None
    assert plan.name == "Pro Plan"
    assert plan.price == Decimal("199.99")

    # Verify DB state
    db_plan = db.query(Plan).filter(Plan.id == plan.id).first()
    assert db_plan is not None

    # Check PlanProduct entries
    mappings = db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan.id
    ).all()

    assert len(mappings) == 3

    tool_ids = [m.tool_id for m in mappings]
    assert set(tool_ids) == {1, 2, 3}
# 1.1 Test: Invalid Tool IDs
def test_create_plan_invalid_tool_ids(db: Session):
    # 🔹 Seed only 1 tool
    db.add(Tool(id=1, name="Tool1", slug="tool-1"))
    db.commit()

    data = PlanCreate(
        name="Invalid Plan",
        price=99.99,
        request_limit=1000,
        rate_limit=10,
        tool_ids=[1, 2]  # 2 does not exist
    )

    with pytest.raises(InvalidToolIdsException):
        create_plan(db, data)

#2. Test: Empty tool_ids
def test_create_plan_without_tools(db):
    data = PlanCreate(
        name="Basic Plan",
        price=49.99,
        request_limit=1000,
        rate_limit=10,
        tool_ids=[]
    )

    plan = create_plan(db, data)

    mappings = db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan.id
    ).all()

    assert len(mappings) == 0

#3. Test: Plan ID generated before commit, This verifies your flush() usage is correct.
def test_plan_id_generated_before_commit(db):
    # Seed tools in DB
    tools = Tool(id=1, name="Tool1", slug="tool-1")
    db.add(tools)
    db.commit()

    data = PlanCreate(
        name="Flush Test",
        price=10,
        request_limit=100,
        rate_limit=5,
        tool_ids=[1]
    )

    plan = create_plan(db, data)

    # If flush didn't work, this would fail
    assert plan.id is not None

    mapping = db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan.id
    ).first()

    assert mapping is not None

'''
=============================
get_all_plans services tests
=============================
'''
#1. Test: No Plans
def test_get_all_plans_empty(db):
    result = get_all_plans(db)

    assert result == []

#2. Test: Single Plan, No Tools
def test_get_plan_without_tools(db):
    plan = Plan(name="Basic", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    result = get_all_plans(db)

    assert len(result) == 1
    assert result[0]["name"] == "Basic"
    assert result[0]["tool_ids"] == []

# 3. Test: Single Plan with Tools
def test_get_plan_with_tools(db):
    # Create tools
    tool1 = Tool(slug="t1", name="Tool1")
    tool2 = Tool(slug="t2", name="Tool2")

    db.add_all([tool1, tool2])
    db.commit()

    # Create plan
    plan = Plan(name="Pro", price=100, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    # Link tools
    db.add_all([
        PlanProduct(plan_id=plan.id, tool_id=tool1.id),
        PlanProduct(plan_id=plan.id, tool_id=tool2.id),
    ])
    db.commit()

    result = get_all_plans(db)

    assert len(result) == 1

    tools = result[0]["tools"]

    assert len(tools) == 2
    assert set(tools) == {1, 2}

# 4. Test: Multiple Plans with Different Tools    
def test_multiple_plans_with_tools(db):
    # Tools
    t1 = Tool(slug="t1", name="Tool1")
    t2 = Tool(slug="t2", name="Tool2")
    t3 = Tool(slug="t3", name="Tool3")

    db.add_all([t1, t2, t3])
    db.commit()

    # Plans
    p1 = Plan(name="Basic", price=10, request_limit=100, rate_limit=10)
    p2 = Plan(name="Pro", price=100, request_limit=100, rate_limit=10)

    db.add_all([p1, p2])
    db.commit()

    # Mapping
    db.add_all([
        PlanProduct(plan_id=p1.id, tool_id=t1.id),
        PlanProduct(plan_id=p1.id, tool_id=t2.id),
        PlanProduct(plan_id=p2.id, tool_id=t3.id),
    ])
    db.commit()

    result = get_all_plans(db)

    assert len(result) == 2

    plan_dict = {p["name"]: p for p in result}

    assert set(plan_dict["Basic"]["tools"]) == {"Tool1", "Tool2"}
    assert set(plan_dict["Pro"]["tools"]) == {"Tool3"}

# 5. Test: Plan with Invalid Mapping (Edge Case)
def test_plan_with_missing_tool(db):
    plan = Plan(name="Edge", price=50, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    # Insert mapping without valid tool
    db.add(PlanProduct(plan_id=plan.id, tool_id=999))
    db.commit()

    result = get_all_plans(db)

    # Should return empty tool list (join fails)
    assert result[0]["tools"] == []

# 6. Test: Order Independence
def test_tools_order_not_assumed(db):
    t1 = Tool(slug="t1", name="A")
    t2 = Tool(slug="t2", name="B")

    db.add_all([t1, t2])
    db.commit()

    plan = Plan(name="Test", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    db.add_all([
        PlanProduct(plan_id=plan.id, tool_id=t2.id),
        PlanProduct(plan_id=plan.id, tool_id=t1.id),
    ])
    db.commit()

    result = get_all_plans(db)

    assert set(result[0]["tools"]) == {"A", "B"}

'''
=============================
get_plan services tests
=============================
'''
# 1. Test: Plan Not Found
def test_get_plan_not_found(db):
    result = get_plan(db, 999)

    assert result is None

# 2. Test: Plan Without Tools
def test_get_plan_without_tools(db):
    plan = Plan(name="Basic", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    result = get_plan(db, plan.id)

    assert result is not None
    assert result["name"] == "Basic"
    assert result["tool_ids"] == []

#3. Test: Plan With Tools
def test_get_plan_with_tools(db):
    # Create tools
    t1 = Tool(slug="t1", name="Tool1")
    t2 = Tool(slug="t2", name="Tool2")

    db.add_all([t1, t2])
    db.commit()

    # Create plan
    plan = Plan(name="Pro", price=100, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    # Link tools
    db.add_all([
        PlanProduct(plan_id=plan.id, tool_id=t1.id),
        PlanProduct(plan_id=plan.id, tool_id=t2.id),
    ])
    db.commit()

    result = get_plan(db, plan.id)

    assert result["name"] == "Pro"
    assert len(result["tool_ids"]) == 2
    assert set(result["tool_ids"]) == {1, 2}

# 4. Test: Invalid Tool Mapping (Edge Case)
def test_get_plan_with_invalid_tool_mapping(db):
    plan = Plan(name="Edge", price=50, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    # Invalid tool_id
    db.add(PlanProduct(plan_id=plan.id, tool_id=999))
    db.commit()

    result = get_plan(db, plan.id)

    # Join fails → no tools returned
    assert result["tool_ids"] == []

# 5. Test: Multiple Plans Isolation
def test_get_plan_isolated(db):
    # Tools
    t1 = Tool(slug="t1", name="Tool1")
    t2 = Tool(slug="t2", name="Tool2")

    db.add_all([t1, t2])
    db.commit()

    # Plans
    p1 = Plan(name="Basic", price=10, request_limit=100, rate_limit=10)
    p2 = Plan(name="Pro", price=100, request_limit=100, rate_limit=10)

    db.add_all([p1, p2])
    db.commit()

    # Mapping
    db.add(PlanProduct(plan_id=p1.id, tool_id=t1.id))
    db.add(PlanProduct(plan_id=p2.id, tool_id=t2.id))
    db.commit()

    result = get_plan(db, p1.id)

    assert result["name"] == "Basic"
    assert result["tool_ids"] == [1]

'''
=============================
update_plan services tests
=============================
'''
# 1. Test: Plan Not Found
def test_update_plan_not_found(db):
    data = PlanCreate(
        name="New",
        price=100,
        request_limit=1000,
        rate_limit=100,
        tool_ids=[1]
    )

    result = update_plan(db, 999, data)

    assert result is None

# 2. Test: Basic Field Update
def test_update_plan_basic_fields(db):
    plan = Plan(name="Old", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    data = PlanCreate(
        name="Updated",
        price=50,
        request_limit=500,
        rate_limit=50,
        tool_ids=[]
    )

    updated = update_plan(db, plan.id, data)

    assert updated["name"] == "Updated"
    assert updated["price"] == 50
    assert updated["request_limit"] == 500
    assert updated["rate_limit"] == 50

# 3. Test: Replace Tools Completely (CORE LOGIC)
def test_update_plan_replaces_tools(db):
    # Create tools
    t1 = Tool(slug="t1", name="Tool1")
    t2 = Tool(slug="t2", name="Tool2")
    t3 = Tool(slug="t3", name="Tool3")

    db.add_all([t1, t2, t3])
    db.commit()

    # Create plan
    plan = Plan(name="Plan", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    # Initial mapping
    db.add_all([
        PlanProduct(plan_id=plan.id, tool_id=t1.id),
        PlanProduct(plan_id=plan.id, tool_id=t2.id),
    ])
    db.commit()

    # Update with new tools
    data = PlanCreate(
        name="Plan",
        price=10,
        request_limit=100,
        rate_limit=10,
        tool_ids=[t3.id]
    )

    update_plan(db, plan.id, data)

    mappings = db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan.id
    ).all()

    assert len(mappings) == 1
    assert mappings[0].tool_id == t3.id

# update plans with invalid/non existing tool ids
def test_update_plan_invalid_tools(db):
    # Create plan
    plan = Plan(name="Plan", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    #update with invalid tool ids
    data = PlanCreate(
        name="Plan",
        price=10,
        request_limit=100,
        rate_limit=10,
        tool_ids=[2,3]
    )

    with pytest.raises(Exception):
        update_plan(db, plan.id, data)

# 4. Test: Duplicate tool_ids handled
def test_update_plan_duplicate_tool_ids(db):
    t1 = Tool(slug="t1", name="Tool1")
    db.add(t1)
    db.commit()

    plan = Plan(name="Plan", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    data = PlanCreate(
        name="Plan",
        price=10,
        request_limit=100,
        rate_limit=10,
        tool_ids=[t1.id, t1.id, t1.id]  # duplicates
    )

    update_plan(db, plan.id, data)

    mappings = db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan.id
    ).all()

    # Should only insert once due to set()
    assert len(mappings) == 1

# 5. Test: Remove All Tools
def test_update_plan_remove_all_tools(db):
    t1 = Tool(slug="t1", name="Tool1")
    db.add(t1)
    db.commit()

    plan = Plan(name="Plan", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    db.add(PlanProduct(plan_id=plan.id, tool_id=t1.id))
    db.commit()

    # Update with empty tools
    data = PlanCreate(
        name="Plan",
        price=10,
        request_limit=100,
        rate_limit=10,
        tool_ids=[]
    )

    update_plan(db, plan.id, data)

    mappings = db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan.id
    ).all()

    assert len(mappings) == 0

# 6. Test: Partial Change (fields + tools)
def test_update_plan_fields_and_tools(db):
    t1 = Tool(slug="t1", name="Tool1")
    t2 = Tool(slug="t2", name="Tool2")

    db.add_all([t1, t2])
    db.commit()

    plan = Plan(name="Old", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    data = PlanCreate(
        name="New",
        price=99,
        request_limit=999,
        rate_limit=99,
        tool_ids=[t1.id, t2.id]
    )

    updated = update_plan(db, plan.id, data)

    assert updated["name"] == "New"
    assert updated["price"] == 99

    mappings = db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan.id
    ).all()

    assert len(mappings) == 2

'''
=============================
delete_plan services tests
=============================
'''
# 1. Test: Plan Not Found
def test_delete_plan_not_found(db):
    result = delete_plan(db, 999)

    assert result is False

# 2. Test: Successful Deletion
def test_delete_plan_success(db):
    plan = Plan(name="DeleteMe", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    result = delete_plan(db, plan.id)

    assert result is True

    # Verify deletion
    db_plan = db.query(Plan).filter(Plan.id == plan.id).first()
    assert db_plan is None

# 3. Test: Deleting Twice (Idempotency-like behavior)
def test_delete_plan_twice(db):
    plan = Plan(name="Temp", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    first = delete_plan(db, plan.id)
    second = delete_plan(db, plan.id)

    assert first is True
    assert second is False

# 4. Test: Cascade Delete (VERY IMPORTANT)
def test_delete_plan_cascade_plan_products(db):
    # Create tool
    tool = Tool(slug="t1", name="Tool1")
    db.add(tool)
    db.commit()

    # Create plan
    plan = Plan(name="Cascade", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    # Link
    db.add(PlanProduct(plan_id=plan.id, tool_id=tool.id))
    db.commit()

    # Delete plan
    delete_plan(db, plan.id)

    # Check PlanProduct also deleted
    mappings = db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan.id
    ).all()

    assert len(mappings) == 0

# 5. Test: Deleting Plan Does Not Affect Tools
def test_delete_plan_does_not_delete_tools(db):
    tool = Tool(slug="t1", name="Tool1")
    db.add(tool)
    db.commit()

    plan = Plan(name="Plan", price=10, request_limit=100, rate_limit=10)
    db.add(plan)
    db.commit()

    db.add(PlanProduct(plan_id=plan.id, tool_id=tool.id))
    db.commit()

    delete_plan(db, plan.id)

    # Tool should still exist
    db_tool = db.query(Tool).filter(Tool.id == tool.id).first()
    assert db_tool is not None
