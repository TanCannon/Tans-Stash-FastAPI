from fastapi import APIRouter, Query, status, HTTPException, Depends
from sqlalchemy import or_
from typing import Annotated, Optional
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models.post_model import Post

router = APIRouter(prefix="/api", tags=["search"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

'''Dependency Injection'''
#The API route depends on the db session to exist
db_dependency = Annotated[Session, Depends(get_db)]


@router.get("/search", name="search", status_code=status.HTTP_200_OK)
async def search_posts(
    db: db_dependency,
    q: Optional[str] = Query(None, description="Search keyword"),
    page: int = Query(1, ge=1),
    size: int = Query(10, ge=1, le=100),
):
    skip = (page - 1) * size

    query = db.query(Post)

    # Apply search filter if keyword provided
    if q:
        query = query.filter(
            or_(
                Post.title.ilike(f"%{q}%"),
                Post.content.ilike(f"%{q}%")
            )
        )

    total = query.count()

    if total == 0:
        raise HTTPException(status_code=404, detail="No matching posts found.")

    if skip >= total:
        raise HTTPException(status_code=404, detail="Page out of range.")

    posts = (
        query
        .order_by(Post.date.desc())
        .offset(skip)
        .limit(size)
        .all()
    )

    return {
        "items": posts,
        "total": total,
        "skip": skip,
        "limit": size,
    }
