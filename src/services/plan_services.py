from sqlalchemy.orm import Session
from src.models.user_model import Plan, PlanProduct
from src.models.tool_model import Tool
from src.schemas.plan_schemas import PlanCreate

class InvalidToolIdsException(Exception):
    def __init__(self, missing_ids):
        self.missing_ids = missing_ids
        super().__init__(f"Invalid tool IDs: {missing_ids}")

class PlanExistsException(Exception):
    def __init__(self, plan_name):
        self.plan_name = plan_name
        super().__init__(f"Plan name {plan_name} already exists.")

def create_plan(db: Session, data: PlanCreate):
    # 🔹 Step 1: Validate tool IDs
    tool_ids = set(data.tool_ids)

    if tool_ids:
        existing_tools = db.query(Tool.id).filter(Tool.id.in_(tool_ids)).all()
        existing_tool_ids = {t[0] for t in existing_tools}

        missing_ids = tool_ids - existing_tool_ids
        if missing_ids:
            raise InvalidToolIdsException(list(missing_ids))

    # 🔹 Step 2: Create plan
    plan = Plan(
        name=data.name,
        price=data.price,
        request_limit=data.request_limit,
        rate_limit=data.rate_limit
    )
    db.add(plan)
    db.flush()

    # 🔹 Step 3: Insert mappings
    for pid in tool_ids:
        db.add(PlanProduct(plan_id=plan.id, tool_id=pid))

    # 🔹 Step 4: Commit
    db.commit()
    db.refresh(plan)

    return plan

def get_all_plans(db: Session):
    plans = db.query(Plan).all()

    result = []
    for plan in plans:
        tools = db.query(Tool.name).join(
            PlanProduct, Tool.id == PlanProduct.tool_id
        ).filter(
            PlanProduct.plan_id == plan.id
        ).all()

        result.append({
            "id": plan.id,
            "name": plan.name,
            "price": plan.price,
            "tools": [p[0] for p in tools]
        })

    return result

def get_plan(db: Session, plan_id: int):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if not plan:
        return None

    tools = db.query(Tool.id).join(
        PlanProduct
    ).filter(
        PlanProduct.plan_id == plan.id
    ).all()

    return {
        "id": plan.id,
        "name": plan.name,
        "price": plan.price,
        "request_limit": plan.request_limit,
        "rate_limit": plan.rate_limit,
        "created_at": plan.created_at,
        "tool_ids": [p[0] for p in tools]
    }

def update_plan(db: Session, plan_id: int, data: PlanCreate):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    # Check if plan exists
    if not plan:
        return None

    # Prevent name duplication
    if data.name != plan.name:
        existing = db.query(Plan).filter(Plan.name == data.name).first()
        if existing:
            raise PlanExistsException(data.name)

    # 🔥 Validate tool_ids FIRST (before modifying anything)
    unique_tool_ids = set(data.tool_ids)

    valid_tools = db.query(Tool.id).filter(
        Tool.id.in_(unique_tool_ids)
    ).all()

    valid_tool_ids = {t[0] for t in valid_tools}

    invalid_tool_ids = unique_tool_ids - valid_tool_ids

    if invalid_tool_ids:
        raise ValueError(f"Invalid tool IDs: {list(invalid_tool_ids)}")

    # Now safe to update
    plan.name = data.name
    plan.price = data.price
    plan.request_limit = data.request_limit
    plan.rate_limit = data.rate_limit

    # Replace mappings
    db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan_id
    ).delete(synchronize_session=False)

    for tid in valid_tool_ids:
        db.add(PlanProduct(plan_id=plan.id, tool_id=tid))

    db.commit()

    return {
        "id": plan.id,
        "name": plan.name,
        "price": plan.price,
        "request_limit": plan.request_limit,
        "rate_limit": plan.rate_limit,
        "created_at": plan.created_at,
        "tool_ids": list(valid_tool_ids)
    }

def delete_plan(db: Session, plan_id: int):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if not plan:
        return False
    
    db.delete(plan)
    db.commit()

    return True