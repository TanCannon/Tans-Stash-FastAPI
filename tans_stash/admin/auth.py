import os
from dotenv import load_dotenv

from fastapi import Request, HTTPException, status, APIRouter,Form, Depends

router = APIRouter(
    prefix = '/admin',
    tags = ['admin']
)

load_dotenv()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

def require_admin(request: Request):
    admin = request.session.get("admin")

    if not admin:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    return admin