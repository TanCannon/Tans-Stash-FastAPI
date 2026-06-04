from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class ToolBase(BaseModel):
    slug: str = Field(..., max_length=255)
    name: str = Field(..., max_length=255)
    description: Optional[str] = None


class ToolCreate(ToolBase):
    pass


class ToolResponse(ToolBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
