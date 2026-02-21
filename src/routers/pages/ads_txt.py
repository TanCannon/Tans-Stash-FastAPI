from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(
    tags=["pages"]
)

@router.get("/ads.txt", include_in_schema=False)
async def ads():
    return FileResponse("src/static/ads.txt", media_type="text/plain")
