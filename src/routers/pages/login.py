from fastapi import APIRouter, Depends, Request, HTTPException, status

from fastapi.templating import Jinja2Templates

from src.core.templates import templates

# from src.core.flash import flash
from src.core.context import get_global_context

router = APIRouter(prefix="/admin/login", tags=["pages"])
# templates = Jinja2Templates(directory="templates")

@router.get("")
async def login(request: Request):

    context = get_global_context(request)

    context.update({
        "request": request
    })

    return templates.TemplateResponse("login.html", context)


