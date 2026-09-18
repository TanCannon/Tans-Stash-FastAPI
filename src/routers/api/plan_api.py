from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import func

from src.dependencies.database import db_dependency
from src.schemas.plan_schemas import PlanResponse, PlanCreate, PaginatedPlans
from src.admin.auth import require_admin
from src.models.user_model import Plan
from src.services.plan_services import InvalidToolIdsException, PlanExistsException, create_plan, get_plan, update_plan, delete_plan
from src.models.tool_model import Tool
from src.models.user_model import Plan, PlanProduct

router = APIRouter(
    prefix="/api",
    tags=["plans"]
)

@router.post("/create-plan", response_model=PlanResponse, status_code=201)
async def create_plan_route(
    plan: PlanCreate,
    db: db_dependency,
    _: str = Depends(require_admin)
):
    # Check if plan already exists
    plan_exists = db.query(Plan).filter(Plan.name == plan.name).first()
    if plan_exists:
        raise HTTPException(
            status_code=400,
            detail="Plan name already exists"
        )

    try:
        # Call service 
        new_plan = create_plan(db, plan)

        mappings = db.query(PlanProduct).filter(
            PlanProduct.plan_id == new_plan.id
        ).all()
        tool_ids = [m.tool_id for m in mappings]

    except InvalidToolIdsException as e:
        # Handle business validation error
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Failed to create plan."
        )
    

    return PlanResponse(
        id=new_plan.id,
        name=new_plan.name,
        price=new_plan.price,
        request_limit=new_plan.request_limit,
        rate_limit=new_plan.rate_limit,
        created_at=new_plan.created_at,
        tool_ids=tool_ids
    )

@router.get("/get-paginated-plans", response_model=PaginatedPlans, status_code=200)
async def get_plans_paginated_route(
    db: db_dependency,
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100)
):
    skip = (page - 1) * size

    total = db.query(func.count(Plan.id)).scalar()

    if total == 0:
        raise HTTPException(status_code=404, detail="No Plans available.")

    if skip >= total:
        raise HTTPException(status_code=404, detail="Page out of range.")

    # Fetch paginated plans
    plans = (
        db.query(Plan)
        .order_by(Plan.created_at.desc())
        .offset(skip)
        .limit(size)
        .all()
    )

    result = []

    for plan in plans:
        tools = (
            db.query(Tool.id)
            .join(PlanProduct, Tool.id == PlanProduct.tool_id)
            .filter(PlanProduct.plan_id == plan.id)
            .all()
        )

        result.append({
            "id": plan.id,
            "name": plan.name,
            "price": plan.price,
            "request_limit": plan.request_limit,
            "rate_limit": plan.rate_limit,
            "created_at": plan.created_at,
            "tool_ids": [p[0] for p in tools]
        })

    return {
        "items": result,
        "total": total,
        "skip": skip,
        "limit": size,
    }

#get plan
@router.get("/plans/{id}", response_model=PlanResponse, status_code=200)
async def get_plan_route(db: db_dependency, id: str):
    plan = get_plan(db, id)

    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found.")

    return plan

#update a plan
@router.put("/update-plan/{id}", response_model=PlanResponse, status_code=202)
async def update_plan_route(id: str, updated_data: PlanCreate, db: db_dependency, admin: str = Depends(require_admin)):
    try:
        plan = update_plan(db, id, updated_data)

    except PlanExistsException as e:
        raise HTTPException(400, str(e))
    
    except ValueError as e:
        raise HTTPException(400, str(e))
    
    except Exception as e:
        raise HTTPException(500, str(e))
    
    return PlanResponse(
        id=plan["id"],
        name=plan["name"],
        price=plan["price"],
        request_limit=plan["request_limit"],
        rate_limit=plan["rate_limit"],
        created_at=plan["created_at"],
        tool_ids=plan["tool_ids"]
    )

#delete a plan
@router.delete("/delete-plan/{id}", status_code=204)
async def delete_plan_route(id: str, db: db_dependency, _: str = Depends(require_admin)):
    flag = delete_plan(db, id)

    if (flag == False):
        raise HTTPException(404, "Plan not found.")
    
    return None
