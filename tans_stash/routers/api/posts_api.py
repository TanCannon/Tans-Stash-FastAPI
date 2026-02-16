from fastapi import Depends, APIRouter, HTTPException, Path, Query, Request
from tans_stash.models.post_model import Post
from tans_stash.database import SessionLocal
from starlette import status
from sqlalchemy.orm import Session
from typing import Annotated, List
from tans_stash.schemas import post_schemas

router = APIRouter(
    prefix="/blogs",
    tags=["blogs"]
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

#paginated route
@router.get("/", response_model=post_schemas.PaginatedPosts, status_code=status.HTTP_200_OK)
async def read_all_posts_paginated(db: db_dependency, page: int = Query(1, ge=1), size: int = Query(10, ge=1, le=100)):
    skip = (page - 1) * size
    total = db.query(Post).count()
    posts = (
        db.query(Post)
        .offset(skip)
        .limit(size)
        .all()
    )
    if total == 0:
        raise HTTPException(status_code=404, detail="No blogs available.")

    if skip >= total:
        raise HTTPException(status_code=404, detail="Page out of range.")

    return {
        "items": posts,
        "total": total,
        "skip": skip,
        "limit": size,
    }

@router.get("/blog/{blog_sno}", response_model=post_schemas.PostResponse, status_code=status.HTTP_200_OK)
async def read_a_post( blog_sno: int = Path(gt=0), db: db_dependency = None):
    post = db.query(Post).filter(Post.sno == blog_sno).first()

    if post is None:
        raise HTTPException(status_code=404, detail="Blog not found")

    return post


