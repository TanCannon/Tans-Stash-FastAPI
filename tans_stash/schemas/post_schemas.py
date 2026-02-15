from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

### Base → Create → Response pattern ###
class PostBase(BaseModel):
    title: str = Field(..., max_length=255)
    slug: str = Field(..., max_length=255, pattern="^[a-z0-9-]+$")
    content: str
    tag_line: str = Field(..., max_length=255)
    description: Optional[str] = Field(
        default="Tan's Stash",
        max_length=500
    )
    img_file: Optional[str] = Field(
        default=None,
        max_length=500
    )


class PostCreate(PostBase):
    pass


class PostResponse(PostBase):
    sno: int
    date: datetime
    last_modified: Optional[datetime] = None

    class Config:
        from_attributes = True  # Correct for Pydantic v2
