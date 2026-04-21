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
    
class UsageLog(Base):
    __tablename__ = "usage_logs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String)
    api_key_id = Column(String)
    endpoint_id = Column(String)
    status_code = Column(Integer)
    response_time_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
