from fastapi import APIRouter, Request, Depends, Query

from src.core.templates import templates

from src.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

from sqlalchemy import or_

from src.models.post_model import Post

from src.core.context import get_global_context

from src.core.settings import settings

router = APIRouter(    
    tags=["pages"]
)

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


@router.get("/search")
async def search_page(
    request: Request,
    q: str = Query(default=""),
    page: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
):
    query = q.strip()

    if not query:
        context = get_global_context(request)
        context.update({
                "request": request,
                "query": query,
                "results": [],
                "total_results": 0,
                "prev": "#",
                "next": "#",
            })

        return templates.TemplateResponse(
            "search.html",
            context
        )

    per_page = settings.NO_OF_POSTS

    base_query = db.query(Post).filter(
        or_(
            Post.title.ilike(f"%{query}%"),
            Post.tag_line.ilike(f"%{query}%"),
        )
    ).order_by(Post.date.desc())

    total = base_query.count()

    results = (
        base_query
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    # Pagination URLs
    prev_url = (
        f"/search?q={query}&page={page-1}"
        if page > 1 else "#"
    )

    next_url = (
        f"/search?q={query}&page={page+1}"
        if page * per_page < total else "#"
    )

    context = get_global_context(request)
    context.update({
            "request": request,
            "query": query,
            "results": results,
            "total_results": total,
            "prev": prev_url,
            "next": next_url,
    })

    return templates.TemplateResponse(
        "search.html",
        context
    )
