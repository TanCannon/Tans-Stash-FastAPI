from pydantic import BaseModel
from typing import Optional


class ToolBase(BaseModel):
    slug: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class ToolCreate(ToolBase):
    pass


class ToolResponse(ToolBase):
    id: int

    class Config:
        from_attributes = True
