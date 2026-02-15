from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime, timezone
from ..database import Base


class ToolUsage(Base):
    __tablename__ = "tool_usage"  # lowercase is best practice

    sno = Column(Integer, primary_key=True, index=True)
    page_name = Column(String(255), nullable=False, index=True)
    user_ip = Column(String(45), nullable=True)  # supports IPv4 & IPv6
    data = Column(Text, nullable=True)
    status_code = Column(String(10), nullable=True)
    timestamp = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    def __repr__(self):
        return f"<ToolUsage page={self.page_name} ip={self.user_ip}>"
