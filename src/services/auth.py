import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from src.schemas import user_schemas
from src.models import user_model
from src.models import auth_token_model
from src.exceptions import UserRegistrationError, UserAlreadyExistsError, InvalidCredentialsError, InvalidRefreshTokenError, InvalidTokenTypeError, UserNotFoundError

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

def _create_user(db: Session, create_user_request: user_schemas.UserCreate):
    user = user_model.User(
        username=create_user_request.username,
        email=create_user_request.email,
        # role=create_user_request.role,
        password_hash=bcrypt_context.hash(create_user_request.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(email: str, password: str, db: Session):
    user = db.query(user_model.User).filter(user_model.User.email == email).first()
    if not user:
        return None
    if not bcrypt_context.verify(password, user.password_hash):
        return None
    return user

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        username: str = payload.get("sub")
        user_id: str = payload.get("id")
        user_role: str = payload.get("role")

        if username is None or user_id is None:
            return None

        return {
            "username": username,
            "id": user_id,
            "role": user_role
        }

    except JWTError as e:
        print(str(e))
        return None

def provide_token_on_login_service(email: str, password: str, db: Session):
    user = authenticate_user(email, password, db)
    if user is None:
        raise InvalidCredentialsError()

    access_token = create_access_token(user)
    refresh_token = create_refresh_token(user)

    db_token = auth_token_model.RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expiry=datetime.now(timezone.utc) + timedelta(days=7)
    )
    db.add(db_token)
    db.commit()

    return access_token, refresh_token

def register_user_service(
    db: Session,
    username: str,
    email: str,
    password: str,
):
    # Step 1: Check if user exists
    user = (
        db.query(user_model.User)
        .filter(user_model.User.email == email)
        .first()
    )

    if user:
        raise UserAlreadyExistsError()

    # Step 2: Create user
    try:
        user_data = user_schemas.UserCreate(
            username=username,
            email=email,
            password=password,
        )

        created_user = _create_user(db=db, create_user_request=user_data)

    except Exception as e:
        print(str(e))
        raise UserRegistrationError()

    return {
        "success": True,
        "message": "User created successfully",
        "user": created_user,
    }

def refresh_access_token_service(
    refresh_token: str,
    db: Session,
):
    try:
        payload = jwt.decode(
            refresh_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
    except JWTError:
        raise InvalidRefreshTokenError()

    if payload.get("type") != "refresh":
        raise InvalidTokenTypeError()

    user_id = payload.get("id")

    # Verify refresh token exists and is active
    db_token = (
        db.query(auth_token_model.RefreshToken)
        .filter(
            auth_token_model.RefreshToken.token == refresh_token,
            auth_token_model.RefreshToken.is_revoked == False,
        )
        .first()
    )

    if not db_token:
        raise InvalidRefreshTokenError()

    user = (
        db.query(user_model.User)
        .filter(user_model.User.id == user_id)
        .first()
    )

    if not user:
        raise UserNotFoundError()

    # Revoke old refresh token
    db_token.is_revoked = True

    new_access_token = create_access_token(user)
    new_refresh_token = create_refresh_token(user)

    db.add(
        auth_token_model.RefreshToken(
            user_id=user.id,
            token=new_refresh_token,
            expiry=datetime.now(timezone.utc)
            + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )

    db.commit()

    return {
        "success": True,
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
    }

def logout_service(db: Session, refresh_token: str):
    db_token = (
        db.query(auth_token_model.RefreshToken)
        .filter(
            auth_token_model.RefreshToken.token == refresh_token,
            auth_token_model.RefreshToken.is_revoked == False
        )
        .first()
    )

    if db_token:
        db_token.is_revoked = True
        db.commit()

    return {
        "success": True,
        "message": "Logged out successfully"
    }
