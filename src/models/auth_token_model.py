from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from ..database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, nullable=False)
    expiry = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)