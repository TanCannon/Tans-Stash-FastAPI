from fastapi import Request, APIRouter, Form, Depends, HTTPException, status
# from fastapi.responses import RedirectResponse
from tans_stash.admin.auth import require_admin, ADMIN_USERNAME, ADMIN_PASSWORD

router = APIRouter(
    prefix = '/api',
    tags = ['admin']
)

@router.post("/admin/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        request.session["admin"] = username

        return {
            "message": "Login successful",
            "admin": username
        }

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # return templates.TemplateResponse("login.html", {"request": request})

@router.get("/admin/dashboard")
async def dashboard(request: Request, admin: str = Depends(require_admin)):
    return {
        "message": "Welcome to admin dashboard",
        "admin": admin
    }

    # return templates.TemplateResponse(
    #     "dashboard.html",
    #     {"request": request, "admin": admin}
    # )

@router.post("/admin/logout")
async def logout(request: Request):
    request.session.clear()

    return {
        "message": "Logged out successfully"
    }
