from fastapi import APIRouter, Request

from src.core.templates import templates

# from src.core.flash import flash
from src.core.context import get_global_context

router = APIRouter(prefix="/about", tags=["pages"])
# templates = Jinja2Templates(directory="templates")

@router.get("")
async def about(request: Request):

    context = get_global_context(request)

    context.update({
        "request": request
    })

    return templates.TemplateResponse("about.html", context)


