from fastapi import APIRouter, Form, HTTPException, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from src.dependencies import database
from src.models import user_model, auth_token_model
from src.schemas import user_schemas
from src.services.auth import register_user_service, provide_token_on_login_service, logout_service, create_access_token, create_refresh_token, refresh_access_token_service, SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix="/api",
    tags=["auth"]
)

@router.post("/auth/register")
async def register_user(db: database.db_dependency, username: str = Form(), email: str = Form(...), password: str = Form(...)):
    return register_user_service(
        db=db,
        username=username,
        email=email,
        password=password
    )

@router.post("/token")
def swagger_login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: database.db_dependency
):
    access_token, refresh_token = provide_token_on_login_service(
        email=form_data.username,
        password=form_data.password,
        db=db
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.post("/auth/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: database.db_dependency
):
    access_token, refresh_token = provide_token_on_login_service(
        email=form_data.username,
        password=form_data.password,
        db=db
    )

    return {
        "success": True,
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/auth/logout")
async def logout(db: database.db_dependency, refresh_token: str):
    return logout_service(db=db, refresh_token=refresh_token)

@router.post("/auth/refresh")
def refresh_access_token(refresh_token: str, db: database.db_dependency):
        return refresh_access_token_service(
        refresh_token=refresh_token,
        db=db,
    )

