from sqlalchemy.orm import Session
from src.models.user_model import Plan, PlanProduct
from src.models.tool_model import Tool
from src.schemas.plan_schemas import PlanCreate

def create_plan(db: Session, data: PlanCreate):
    plan = Plan(
        name=data.name, 
        price=data.price,
        request_limit = data.request_limit,
        rate_limit = data.rate_limit
    )
    db.add(plan)
    db.flush()  # get plan.id

    unique_tool_ids = set(data.tool_ids)

    for pid in unique_tool_ids:
        db.add(PlanProduct(plan_id=plan.id, tool_id=pid))


    db.commit()
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

    tools = db.query(Tool.name).join(
        PlanProduct
    ).filter(
        PlanProduct.plan_id == plan.id
    ).all()

    return {
        "id": plan.id,
        "name": plan.name,
        "price": plan.price,
        "tools": [p[0] for p in tools]
    }

def update_plan(db: Session, plan_id: int, data: PlanCreate):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if not plan:
        return None

    plan.name = data.name
    plan.price = data.price
    plan.request_limit = data.request_limit
    plan.rate_limit = data.rate_limit


    # Update products (IMPORTANT)
    db.query(PlanProduct).filter(
        PlanProduct.plan_id == plan_id
    ).delete()

    unique_tool_ids = set(data.tool_ids)

    valid_tools = db.query(Tool.id).filter(Tool.id.in_(unique_tool_ids)).all()

    for pid in valid_tools:
        db.add(PlanProduct(plan_id=plan.id, tool_id=pid[0]))

    db.commit()
    return plan

def delete_plan(db: Session, plan_id: int):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()

    if not plan:
        return False
    
    db.delete(plan)
    db.commit()

    return True