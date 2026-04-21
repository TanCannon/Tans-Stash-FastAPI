from fastapi import APIRouter, Form, HTTPException, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

from src.dependencies import database
from src.models import user_model, auth_token_model
from src.services import auth
from src.schemas import user_schemas
from src.services.auth import create_access_token, create_refresh_token, SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix="/api",
    tags=["auth"]
)

@router.post("/register")
async def register_user(db: database.db_dependency, username: str = Form(), email: str = Form(...), password: str = Form(...)):
    #step1: check if user exists
    try:
        user = db.query(user_model.User).filter(user_model.User.email == email).first()
        if (user):
            raise HTTPException(status_code=400, detail="User alread exists.")
    except Exception as e:
        print(str(e))
        
    #step2: trying creating the user
    try:
        user_data = user_schemas.UserCreate(
        username=username,
        email=email,
        password=password
        )
        created_user = auth.create_user(db, user_data)
    except Exception as e:
        print(str(e))
        raise HTTPException(status_code=500, detail="Failed to register user")
    
    return {
        "success": True,
        "message": "User created Successfully",
        "user": created_user
    }

@router.post("/token")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: database.db_dependency
):
    result = auth.provide_token_on_login(
        email=form_data.username,
        password=form_data.password,
        db=db
    )

    if result is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, refresh_token = result

    return {
        "succes": True,
        "message": "Login successful.",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(db: database.db_dependency, refresh_token: str):
    return auth.logout(db, refresh_token)

@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: database.db_dependency):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("id")

        # check DB
        db_token = db.query(auth_token_model.RefreshToken).filter(
            auth_token_model.RefreshToken.token == refresh_token,
            auth_token_model.RefreshToken.is_revoked == False
        ).first()

        if not db_token:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        # rotate token (invalidate old one)
        db_token.is_revoked = True

        user = db.query(user_model.User).filter(user_model.User.id == user_id).first()

        new_access_token = create_access_token(user)
        new_refresh_token = create_refresh_token(user)

        # store new refresh token
        db.add(auth_token_model.RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expiry=datetime.now(timezone.utc) + timedelta(days=7)
        ))

        db.commit()

        return {
            "success": True,
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
