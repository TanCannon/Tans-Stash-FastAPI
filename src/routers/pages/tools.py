from fastapi import APIRouter, Depends, Request, HTTPException, status

from fastapi.templating import Jinja2Templates

from src.core.templates import templates

# from src.core.flash import flash
from src.core.context import get_global_context

router = APIRouter(prefix="/tools", tags=["pages"])
# templates = Jinja2Templates(directory="templates")

@router.get("", name="tools.toolsHome")
async def tools(request: Request):

    context = get_global_context(request)

    context.update({
        "request": request
    })

    return templates.TemplateResponse("tools.html", context)

@router.get("/ascii-tree-to-zip", name="tools.ascii_tree_to_zip")
async def ascii_tree_page(request: Request):

    context = get_global_context(request)

    context.update({
        "request": request
    })

    return templates.TemplateResponse("generateZip.html", context)

@router.get("/character-counter", name="tools.character_counter")
async def chracterCounter(request: Request):

    context = get_global_context(request)

    context.update({
        "request": request
    })

    return templates.TemplateResponse("characterCounter.html", context)


