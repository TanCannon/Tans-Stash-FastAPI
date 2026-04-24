from pydantic import BaseModel, ConfigDict
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str
    role: Optional[str] = "user"
    password: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    user_id: int

    model_config = ConfigDict(from_attributes=True)
