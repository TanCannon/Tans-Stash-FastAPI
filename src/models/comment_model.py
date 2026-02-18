from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Enum,
    ForeignKey,
    Index,
)
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..database import Base


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)

    # Polymorphic reference
    content_type = Column(
        Enum("blog", "tool", name="content_type_enum"),
        nullable=False,
    )
    content_id = Column(Integer, nullable=False)

    author_name = Column(String(100), nullable=False)
    author_email = Column(String(255), nullable=True)

    comment = Column(Text, nullable=False)

    # Nested replies
    parent_id = Column(
        Integer,
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    status = Column(
        Enum("approved", "pending", "spam", name="comment_status_enum"),
        default="pending",
    )

    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)

    # Self-referencing relationship
    replies = relationship(
        "Comment",
        backref="parent",
        remote_side=[id],
        cascade="all, delete-orphan",
        single_parent=True
    )

    __table_args__ = (
        Index("idx_content", "content_type", "content_id"),
        Index("idx_parent", "parent_id"),
    )

    def __repr__(self):
        return f"<Comment {self.id} on {self.content_type}:{self.content_id}>"
