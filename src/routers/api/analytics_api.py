from fastapi import Depends, APIRouter, HTTPException, Query
from starlette import status
from src.database import SessionLocal
from sqlalchemy.orm import Session
from typing import Annotated

from src.models.user_usage_model import ToolUsage
from src.admin.auth import require_admin

router = APIRouter(
    prefix='/api',
    tags=['analytics']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''Dependency Injection'''
#The API route depends on the db session to exist
db_dependency = Annotated[Session, Depends(get_db)]

# response_model=List[user_usage_schemas.ToolUsageResponse]
#paginated route
@router.get("/get-paginated-analytics", status_code=status.HTTP_200_OK)
async def read_all_analysis_paginated(db: db_dependency, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100), _: str = Depends(require_admin)):
    skip = (page - 1) * size
    total = db.query(ToolUsage).count()
    tool_usage = (
        db.query(ToolUsage)
        .offset(skip)
        .limit(size)
        .all()
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="No analysis data available.")

    if skip >= total:
        raise HTTPException(status_code=404, detail="Page out of range.")

    return {
        "items": tool_usage,
        "total": total,
        "skip": skip,
        "limit": size,
    }