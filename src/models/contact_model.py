from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime, timezone
from ..database import Base  # use your project name

class Contact(Base):
    __tablename__ = "contacts"

    sno = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False)
    phone_no = Column(String(15), nullable=False)
    msg = Column(Text, nullable=False)
    email = Column(String(120), nullable=False)
    date = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Contact {self.name}>"