from fastapi import APIRouter, Form, HTTPException, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm

from src.dependencies import database
from src.models import user_model
from src.services import auth
from src.schemas import user_schemas

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


