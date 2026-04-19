import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.schemas import user_schemas
from src.models import user_model
from src.models import auth_token_model

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 7
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

def create_access_token(user: user_schemas.UserResponse):
    payload = {
        "sub": user.username,
        "id": user.id,
        "role": user.role,
        "type": "access",
        "exp": datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(user: user_schemas.UserResponse):
    payload = {
        "id": user.id,
        "type": "refresh",
        "exp": datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def create_user(db: Session, create_user_request: user_schemas.UserCreate):
    user = user_model.User(
        username=create_user_request.username,
        email=create_user_request.email,
        role=create_user_request.role,
        password_hash=bcrypt_context.hash(create_user_request.password_hash)
    )
    db.add(user)
    db.commit()
    db.refresh()
    return user

def authenticate_user(username: str, password: str, db: Session):
    user = db.query(user_model.User).filter(user_model.User.username == username).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.password_hash):
        return None
    return user

def provide_token_on_login(username: str, password: str, db: Session):
    user = authenticate_user(username, password, db)
    if user is None:
        return None

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    db_token = auth_token_model.RefreshToken(
        user_id=user.id,
        token=bcrypt_context.hash(refresh_token),
        expiry=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_token)
    db.commit()

    return {
        access_token, 
        refresh_token
    }

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None:
            return None

        return {
            "username": username,
            "id": user_id,
            "role": user_role
        }

    except JWTError:
        return None