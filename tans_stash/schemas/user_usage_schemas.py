from pydantic import BaseModel, Field, IPvAnyAddress
from typing import Optional
from datetime import datetime


class ToolUsageBase(BaseModel):
    page_name: str = Field(..., max_length=255)
    user_IP: Optional[IPvAnyAddress] = None
    data: Optional[str] = Field(None, max_length=5000)
    status_code: Optional[int] = Field(None, ge=100, le=599)


class ToolUsageCreate(ToolUsageBase):
    pass


class ToolUsageResponse(ToolUsageBase):
    sno: int
    timestamp: datetime

    class Config:
        from_attributes = True
