from fastapi import Depends, HTTPException, status
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer

from src.services.auth import decode_access_token
from src.schemas import auth_token_schemas

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")

def get_current_user(
    token: Annotated[str, Depends(oauth2_bearer)]
) ->  auth_token_schemas.TokenData:
    user_data = decode_access_token(token)

    if user_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_data