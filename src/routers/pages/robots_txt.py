from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(
    tags=["pages"]
)
@router.get("/robots.txt")
async def robots():
    return FileResponse("src/static/robots.txt", media_type="text/plain")