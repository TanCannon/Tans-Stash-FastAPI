from datetime import datetime, timezone
from ..database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text, DateTime


class Post(Base):
    __tablename__ = "posts"

    sno = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tag_line = Column(String(255), nullable=False)
    description = Column(String(500), nullable=False, default="Tan's Blogpost")
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_modified = Column(DateTime(timezone=True), nullable=True)
    img_file = Column(String(120), nullable=True)