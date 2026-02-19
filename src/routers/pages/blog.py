from fastapi import APIRouter, Depends, Request, HTTPException, status

from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from src.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

from src.models.post_model import Post

from src.services.table_of_content import generate_toc_and_clean_html
from src.core.params import params

from src.core.templates import templates

from src.core.flash import flash
from src.core.context import get_global_context

router = APIRouter(prefix="/blog", tags=["pages"])
# templates = Jinja2Templates(directory="templates")

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

@router.get("/{post_slug}")
def post_route(
    request: Request,
    post_slug: str,
    db: db_dependency
):
    try:
        post = db.query(Post).filter(Post.slug == post_slug).first()

        if not post:
            raise HTTPException(status_code=404, detail="Post not found")

        clean_html, toc = generate_toc_and_clean_html(post.content)

        context = get_global_context(request)
        context.update({
            "request": request,
            "post": post,
            "content": clean_html,
            "toc": toc,
            "content_type": "blog",
            "content_id": post.sno,
        })

        return templates.TemplateResponse("post.html", context)

    except Exception:
        flash(request, "Something went wrong. Please visit again later.", "danger")

        context = get_global_context(request)
        context.update({
            "request": request,
            "post": None,
            "content": "",
            "toc": [],
            "content_type": "",
            "content_id": "",
        })

        return templates.TemplateResponse(
            "post.html",
            context,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
