from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter(
    tags=["pages"]
)

@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(
        "src/static/favicon/favicon.ico",
        media_type="image/vnd.microsoft.icon"
    )
