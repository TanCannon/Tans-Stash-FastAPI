from fastapi import APIRouter
from starlette import status
from src.schemas import unicode_tree_schemas
from fastapi.responses import FileResponse
import tempfile, os, shutil
from src.services.ascii_tree_to_zip_service import create_structure_from_ascii, zip_folder

router = APIRouter(
    prefix="/api",
    tags=["tools"]
)

@router.post("/ascii-tree-to-zip-api", status_code=status.HTTP_200_OK)
def ascii_tree_download(unicode_tree_request: unicode_tree_schemas.UnicodeTreeProcess):
    
    ascii_tree = unicode_tree_request.unicode_tree
    
    tmpdir = tempfile.mkdtemp()
    base_path = os.path.join(tmpdir, "project")
    os.makedirs(base_path, exist_ok=True)

    create_structure_from_ascii(ascii_tree, base_path)

    zip_path = os.path.join(tmpdir, "project.zip")
    zip_folder(base_path, zip_path)

    #log the tool usage into ToolUsage Table
    # userIP = get_client_ip()
    # recordUsage.putToolUsageInfoIntoDB(ToolUsage, "/tools/ascii-tree-to-zip", userIP, ascii_tree, "200", db)

    return FileResponse(
        path=zip_path,
        filename="project.zip",   # download name
        media_type="application/zip"
    )

    # Cleanup temp files safely
    try:
        if 'tmpdir' in locals():
            shutil.rmtree(tmpdir)
    except Exception:
        pass
