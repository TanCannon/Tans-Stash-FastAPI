from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime


class ContactBase(BaseModel):
    name: str = Field(..., max_length=80)
    phone_no: str = Field(
        ...,
        max_length=15)
    msg: str = Field(..., max_length=2000)
    email: EmailStr


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    sno: int
    date: datetime

    model_config = ConfigDict(from_attributes=True)
