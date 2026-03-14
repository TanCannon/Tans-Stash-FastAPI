from fastapi import Request, APIRouter, Form, HTTPException, status, Query, Depends
# from fastapi.responses import RedirectResponse
from src.admin.auth import ADMIN_USERNAME, ADMIN_PASSWORD

from typing import Annotated
from sqlalchemy.orm import Session

from src.database import SessionLocal
from src.models.post_model import Post

from src.admin.auth import require_admin

import math

router = APIRouter(
    prefix = '/api',
    tags = ['admin']
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

@router.post("/admin/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["admin"] = username

        return {
            "message": "Login successful",
            "admin": username
        }

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # return templates.TemplateResponse("login.html", {"request": request})

@router.post("/admin/logout")
async def logout(request: Request):
    request.session.clear()

    return {
        "message": "Logged out successfully"
    }

@router.get("/admin-get-posts")
async def admin_get_posts(
    request: Request,
    db: db_dependency,
    page: int = Query(1, ge=1),
    _: str = Depends(require_admin)
):
    limit = 5
    skip = (page - 1) * limit

    total = db.query(Post).count()
    posts = (
        db.query(Post)
            .order_by(Post.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    total_pages = math.ceil(total / limit)

    return {
        "posts": posts,
        "total_pages": total_pages,
        "current_page": page
    }
