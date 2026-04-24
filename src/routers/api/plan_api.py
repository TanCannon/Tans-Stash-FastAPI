from fastapi import APIRouter, HTTPException, Depends, Query, Path
from datetime import datetime, timezone

from src.dependencies.database import db_dependency
from src.schemas.plan_schemas import PlanResponse, PlanCreate, PaginatedPosts
from src.admin.auth import require_admin
from src.models.user_model import Plan

router = APIRouter(
    prefix="/api",
    tags=["plans"]
)

#create a plan
@router.post("/create-plan", response_model=PlanResponse, status_code=201)
async def create_plan(plan: PlanCreate, db: db_dependency, admin: str = Depends(require_admin)):
    # Check if slug already exists
    existing = db.query(Plan).filter(Plan.name == plan.name).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Plan name already exists"
        )

    new_plan = Plan(**plan.model_dump())

    db.add(new_plan)
    db.commit()
    db.refresh(new_plan)

    return new_plan

#paginated read plan
@router.get("/get-paginated-plans", response_model=PaginatedPosts, status_code=200)
async def read_all_plans_paginated(db: db_dependency, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    skip = (page - 1) * size
    total = db.query(Plan).count()
    plans = (
        db.query(Plan)
        .order_by(Plan.created_at.desc())
        .offset(skip)
        .limit(size)
        .all()
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="No Plans available.")

    if skip >= total:
        raise HTTPException(status_code=404, detail="Page out of range.")

    return {
        "items": plans,
        "total": total,
        "skip": skip,
        "limit": size,
    }

#read a plan
@router.get("/plans/{id}", response_model=PlanResponse, status_code=200)
async def read_a_plan(db: db_dependency, id: str):
    plan = db.query(Plan).filter(Plan.id == id).first()

    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found.")

    return plan

#update a plan
@router.put("/update-plan/{id}", status_code=202)
async def update_plan(id: str, updated_data: PlanCreate, db: db_dependency, admin: str = Depends(require_admin)):
    plan = db.query(Plan).filter(Plan.id == id).first()

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan not found."
        )

    # Prevent name duplication
    if updated_data.name != plan.name:
        existing = db.query(Plan).filter(Plan.name == updated_data.name).first()
        if existing:
            raise HTTPException(
                status_code=400,
                detail="Plan name already exists."
            )

    for key, value in updated_data.model_dump().items():
        setattr(plan, key, value)

    plan.last_modified = datetime.now(timezone.utc)

    db.commit()
    db.refresh(plan)

#delete a plan
@router.delete("/delete-plan/{id}", status_code=204)
async def delete_plan(id: str, db: db_dependency,admin: str = Depends(require_admin)):
    plan = db.query(Plan).filter(Plan.id == id).first()

    if not plan:
        raise HTTPException(
            status_code=404,
            detail="Plan not found."
        )

    db.delete(plan)
    db.commit()

    return None
