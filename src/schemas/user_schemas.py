from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str
    role: str
    password_hash: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    user_id: int

    class Config:
        from_attributes = True
