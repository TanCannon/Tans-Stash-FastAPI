from datetime import datetime, timezone
from ..database import Base
from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum as SAEnum

class PostStatus(str, PyEnum):
    PUBLIC = "public"
    PRIVATE = "private"
    DRAFT = "draft"

class Post(Base):
    __tablename__ = "posts"

    sno = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    content = Column(Text, nullable=False)
    tag_line = Column(String(255), nullable=False)
    description = Column(String(500), nullable=False, default="Tan's Stash")
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_modified = Column(DateTime(timezone=True), nullable=True)
    img_file = Column(String(120), nullable=True)
    status = Column(
        SAEnum(
            PostStatus,
            name="poststatus",
            values_callable=lambda enum: [item.value for item in enum],
        ),
        nullable=False,
        default=PostStatus.DRAFT,
        server_default=PostStatus.DRAFT.value,
    )
    def __repr__(self):
        return f"<Post {self.slug}>"
