from fastapi import APIRouter, Request, Depends

from fastapi.routing import APIRoute

from src.database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session

from src.seo.sitemap_config import EXCLUDED_ROUTES, STATIC_PAGES_LASTMOD

from src.core.templates import templates

from src.models.post_model import Post

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

def get_blog_posts(db: db_dependency):
    posts = db.query(Post.slug, Post.date).all()

    return [
        {
            "slug": slug,
            "lastmod": last_modified.date().isoformat()
        }
        for slug, last_modified in posts
    ]

@router.get("/sitemap.xml", include_in_schema=False)
async def sitemap(
    request: Request,
    db: Session = Depends(get_db)
):
    pages = []

    for route in request.app.routes:
        if isinstance(route, APIRoute) and "GET" in route.methods:
            if "{" in route.path:
                continue
            if route.path.startswith(EXCLUDED_ROUTES):
                continue
            url = request.url_for(route.name)

            page_data = {"loc": str(url)}

            # attach real lastmod only if defined
            lastmod = STATIC_PAGES_LASTMOD.get(route.path)
            if lastmod:
                page_data["lastmod"] = lastmod

            pages.append(page_data)

    for post in get_blog_posts(db):
        pages.append({
            "loc": str(request.url_for("post_route", post_slug=post["slug"])),
            "lastmod": post["lastmod"]
        })

    return templates.TemplateResponse(
        "sitemap_template.xml",
        {"request": request, "pages": pages},
        media_type="application/xml"
    )

