from fastapi import APIRouter, Request, Query, status, Depends

from src.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

from fastapi.responses import HTMLResponse
from math import ceil

from src.models.post_model import Post

from src.core.templates import templates
from src.core.params import params

from src.core.flash import flash
from src.core.context import get_global_context

router = APIRouter(    
    tags=["pages"]
)

POSTS_PER_PAGE = params['no_of_posts']  # replace with your params['no_of_posts']


def get_db():
    try:
        db = SessionLocal()
        yield db
    except Exception:
        # Yield None if DB fails
        yield None
    finally:
        try:
            db.close()
        except:
            pass


'''Dependency Injection'''
#The API route depends on the db session to exist
db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/", response_class=HTMLResponse, name="home")
async def home(
    request: Request,
    db: db_dependency,
    page: int = Query(1, ge=1),
):
    if db is None:
        flash(request, "Database is currently unavailable.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "params": params,
            "posts": [],
            "prev": "#",
            "next": "#",
        })

        return templates.TemplateResponse(
            "index.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    try:
        per_page = POSTS_PER_PAGE
        skip = (page - 1) * per_page

        total = db.query(Post).count()

        posts = (
            db.query(Post)
            .order_by(Post.date.desc())
            .offset(skip)
            .limit(per_page)
            .all()
        )

        total_pages = ceil(total / per_page)

        prev_page = (
            str(request.url_for("home")) + f"?page={page - 1}"
            if page > 1
            else "#"
        )

        next_page = (
            str(request.url_for("home")) + f"?page={page + 1}"
            if page < total_pages
            else "#"
        )

        return templates.TemplateResponse(
            "index.html",
            {
                "params": params,
                "request": request,
                "posts": posts,
                "prev": prev_page,
                "next": next_page,
            },
        )

    except Exception:
        flash(request, "Something went wrong. Please visit again later.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "params": params,
            "posts": [],
            "prev": "#",
            "next": "#",
        })

        return templates.TemplateResponse(
            "index.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )



