from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


# Content Type Enum
class ContentTypeEnum(str, Enum):
    BLOG = "blog"
    TOOL = "tool"


# Comment Status Enum (consistent lowercase values)
class CommentStatusEnum(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    SPAM = "spam"


class CommentBase(BaseModel):
    content_type: ContentTypeEnum
    content_id: int
    author_name: str = Field(..., max_length=100)
    author_email: Optional[EmailStr] = None
    comment: str
    parent_id: Optional[int] = None


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    id: int
    created_at: datetime
    status: CommentStatusEnum

    class Config:
        from_attributes = True


class CommentWithReplies(CommentResponse):
    replies: List["CommentWithReplies"] = Field(default_factory=list)

    class Config:
        from_attributes = True

CommentWithReplies.model_rebuild()